import 'package:paper_abby/src/model/cell.dart';
import 'package:paper_abby/src/model/tools.dart';

enum Terrain { dot, tree, water, cave }

class Pickup {
  const Pickup({required this.at, required this.kind});

  final Cell at;
  final String kind;

  AbbyTool get tool => toolById(kind)!;
}

class Ridge {
  const Ridge(this.a, this.b);

  final Cell a;
  final Cell b;

  bool blocks(Cell from, Cell to) =>
      (from == a && to == b) || (from == b && to == a);
}

/// One paper map, in the shape the editor saves.
class Level {
  Level._({
    required this.number,
    required this.name,
    required this.blurb,
    required this.rows,
    required this.cols,
    required this.start,
    required this.flag,
    required this.energy,
    required this.treatEnergy,
    required this.energyCap,
    required this._terrain,
    required List<Ridge> ridges,
    required List<Pickup> pickups,
  }) : ridges = List.unmodifiable(ridges),
       pickups = List.unmodifiable(pickups),
       _pickupAt = {for (final item in pickups) item.at: item};

  final int number;
  final String name;
  final String blurb;
  final int rows;
  final int cols;
  final Cell start;
  final Cell flag;
  final int energy;
  final int treatEnergy;
  final int energyCap;
  final List<Ridge> ridges;
  final List<Pickup> pickups;

  final Map<Cell, Terrain> _terrain;
  final Map<Cell, Pickup> _pickupAt;

  bool contains(Cell cell) =>
      cell.row >= 0 && cell.col >= 0 && cell.row < rows && cell.col < cols;

  Terrain terrainAt(Cell cell) => _terrain[cell] ?? Terrain.dot;

  Pickup? pickupAt(Cell cell) => _pickupAt[cell];

  bool ridgeBlocks(Cell from, Cell to) {
    for (final ridge in ridges) {
      if (ridge.blocks(from, to)) return true;
    }
    return false;
  }

  factory Level.fromPaper(Map<String, dynamic> data) {
    final rows = _intField(data, 'rows', 10);
    final cols = _intField(data, 'cols', 6);
    if (rows < 1 || cols < 1 || cols > Cell.columns.length || rows > 40) {
      throw LevelParseException('The board is $cols by $rows.');
    }

    Cell cellOf(Object? token) => Cell.parse(token, rows: rows, cols: cols);

    final startToken = data['start'];
    final flagToken = data['flag'];
    if (startToken is! String || flagToken is! String) {
      throw LevelParseException('A level needs Abby and the flag.');
    }
    final start = cellOf(startToken);
    final flag = cellOf(flagToken);

    final treesRaw = data['trees'];
    final openRaw = data['open'];
    if (treesRaw != null && treesRaw is! List) {
      throw LevelParseException('trees should be a list.');
    }
    if (openRaw != null && openRaw is! List) {
      throw LevelParseException('open should be a list.');
    }
    final hasTrees = treesRaw is List;
    final hasOpen = openRaw is List;
    if (hasTrees && hasOpen) {
      throw LevelParseException('Use open or trees, not both.');
    }

    final terrain = <Cell, Terrain>{};
    if (hasTrees) {
      for (final token in treesRaw) {
        terrain[cellOf(token)] = Terrain.tree;
      }
    } else if (hasOpen) {
      final open = <Cell>{for (final token in openRaw) cellOf(token)};
      for (var row = 0; row < rows; row += 1) {
        for (var col = 0; col < cols; col += 1) {
          final cell = Cell(row, col);
          if (!open.contains(cell)) terrain[cell] = Terrain.tree;
        }
      }
    }

    void paintGate(Object? token, Terrain kind) {
      final cell = cellOf(token);
      final current = terrain[cell] ?? Terrain.dot;
      if (current == Terrain.tree) {
        throw LevelParseException('${cell.name} is a tree and a gate.');
      }
      if (current != Terrain.dot && current != kind) {
        throw LevelParseException('A tile cannot be water and a cave.');
      }
      terrain[cell] = kind;
    }

    final waterRaw = data['water'];
    if (waterRaw != null && waterRaw is! List) {
      throw LevelParseException('water should be a list.');
    }
    if (waterRaw is List) {
      for (final token in waterRaw) {
        paintGate(token, Terrain.water);
      }
    }
    final cavesRaw = data['caves'];
    if (cavesRaw != null && cavesRaw is! List) {
      throw LevelParseException('caves should be a list.');
    }
    if (cavesRaw is List) {
      for (final token in cavesRaw) {
        paintGate(token, Terrain.cave);
      }
    }

    final ridges = <Ridge>[];
    final cliffsRaw = data['cliffs'];
    if (cliffsRaw != null && cliffsRaw is! List) {
      throw LevelParseException('cliffs should be a list.');
    }
    if (cliffsRaw is List) {
      for (final pair in cliffsRaw) {
        if (pair is! List || pair.length != 2) {
          throw LevelParseException('A ridge needs two cells.');
        }
        final a = cellOf(pair[0]);
        final b = cellOf(pair[1]);
        final left = _first(a, b);
        final right = left == a ? b : a;
        if (!left.sharesSide(right)) {
          throw LevelParseException(
            'The ridge ${left.name}–${right.name} is not a side.',
          );
        }
        final leftGround = terrain[left] ?? Terrain.dot;
        final rightGround = terrain[right] ?? Terrain.dot;
        if (leftGround == Terrain.tree || rightGround == Terrain.tree) {
          throw LevelParseException(
            'The ridge ${left.name}–${right.name} touches a tree.',
          );
        }
        ridges.add(Ridge(left, right));
      }
    }

    final pickups = <Pickup>[];
    final seen = <Cell>{};
    final pickupsRaw = data['pickups'];
    if (pickupsRaw != null && pickupsRaw is! List) {
      throw LevelParseException('pickups should be a list.');
    }
    if (pickupsRaw is List) {
      for (final item in pickupsRaw) {
        if (item is! Map) {
          throw LevelParseException('A pickup needs a cell and a kind.');
        }
        final at = item['at'];
        final kindRaw = item['kind'];
        if (at is! String || kindRaw is! String || kindRaw.trim().isEmpty) {
          throw LevelParseException('A pickup needs a cell and a kind.');
        }
        final kind = kindRaw.trim().toLowerCase();
        final cell = cellOf(at);
        if (!seen.add(cell)) {
          throw LevelParseException('Two items on ${cell.name}.');
        }
        final tool = toolById(kind);
        if (tool == null || tool.group != 'item') {
          throw LevelParseException('Unknown item: $kind.');
        }
        final ground = terrain[cell] ?? Terrain.dot;
        if (ground == Terrain.tree) {
          throw LevelParseException('$kind on a tree at ${cell.name}.');
        }
        if (ground == Terrain.water || ground == Terrain.cave) {
          throw LevelParseException(
            '$kind is sitting inside a gate at ${cell.name}.',
          );
        }
        if (cell == start || cell == flag) {
          throw LevelParseException('$kind is on Abby or the flag.');
        }
        pickups.add(Pickup(at: cell, kind: kind));
      }
    }

    if (start == flag) {
      throw LevelParseException('Abby is already on the flag.');
    }
    final startGround = terrain[start] ?? Terrain.dot;
    final flagGround = terrain[flag] ?? Terrain.dot;
    if (startGround == Terrain.tree || flagGround == Terrain.tree) {
      throw LevelParseException('Abby or the flag is on a tree.');
    }

    final nameRaw = data['name'];
    final name = nameRaw is String && nameRaw.trim().isNotEmpty
        ? nameRaw.trim()
        : 'Untitled';
    final blurbRaw = data['blurb'];
    final blurb = blurbRaw is String ? blurbRaw.trim() : '';

    return Level._(
      number: _intField(data, 'level', 1),
      name: name,
      blurb: blurb,
      rows: rows,
      cols: cols,
      start: start,
      flag: flag,
      energy: _intField(data, 'energy', 12),
      treatEnergy: _intField(data, 'treat_energy', 3),
      energyCap: _intField(data, 'energy_cap', 24),
      terrain: terrain,
      ridges: ridges,
      pickups: pickups,
    );
  }
}

int _intField(Map<String, dynamic> data, String key, int fallback) {
  final value = data[key];
  if (value == null) return fallback;
  if (value is int) return value;
  if (value is num) return value.toInt();
  throw LevelParseException('$key should be a number.');
}

Cell _first(Cell a, Cell b) {
  if (a.row < b.row || (a.row == b.row && a.col <= b.col)) return a;
  return b;
}
