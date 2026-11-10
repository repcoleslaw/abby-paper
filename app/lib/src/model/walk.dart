import 'dart:math' as math;

import 'package:paper_abby/src/model/cell.dart';
import 'package:paper_abby/src/model/level.dart';
import 'package:paper_abby/src/model/tools.dart';

enum Block { side, tree, cliff, water, cave, reuse, energy, flag }

String messageFor(Block block) {
  return switch (block) {
    Block.side => 'Step to a dot that shares a side.',
    Block.tree => 'Trees have no dot.',
    Block.cliff => 'That edge is a cliff.',
    Block.water => 'Waves need the vest first.',
    Block.cave => 'The arch needs the lamp first.',
    Block.reuse => 'That dot is already in the line.',
    Block.energy => 'No circles left. Erase and redraw.',
    Block.flag => 'The flag is the last dot.',
  };
}

/// Why [next] cannot be appended to [path]. Null when the step is legal.
Block? blockFor(Level level, List<Cell> path, Cell next) {
  final head = path.last;
  if (head == level.flag) return Block.flag;
  if (!level.contains(next) || !head.sharesSide(next)) return Block.side;
  if (path.contains(next)) return Block.reuse;
  final ground = level.terrainAt(next);
  if (ground == Terrain.tree) return Block.tree;
  if (level.ridgeBlocks(head, next)) return Block.cliff;
  if (ground == Terrain.water && !_holds(level, path, gateItem('water'))) {
    return Block.water;
  }
  if (ground == Terrain.cave && !_holds(level, path, gateItem('cave'))) {
    return Block.cave;
  }
  if (energyAfter(level, path) < 1) return Block.energy;
  return null;
}

bool _holds(Level level, List<Cell> path, String? kind) {
  if (kind == null) return true;
  for (final cell in path.skip(1)) {
    if (level.pickupAt(cell)?.kind == kind) return true;
  }
  return false;
}

int energyAfter(Level level, List<Cell> path) {
  var energy = level.energy;
  for (final cell in path.skip(1)) {
    energy -= 1;
    final item = level.pickupAt(cell);
    if (item == null) continue;
    final bonus = grantFor(item.kind, treatEnergy: level.treatEnergy);
    if (bonus != 0) {
      energy = math.min(level.energyCap, energy + bonus);
    }
  }
  return energy;
}

class WalkState {
  WalkState(this.level, this.path) : energy = energyAfter(level, path);

  final Level level;
  final List<Cell> path;
  final int energy;

  int get steps => path.length - 1;

  bool get finished => path.last == level.flag;

  int get score {
    var finds = 0;
    for (final cell in path.skip(1)) {
      final item = level.pickupAt(cell);
      if (item != null) finds += pointsFor(item.kind);
    }
    return finds - steps;
  }

  /// Sticks, balls, treats, then steps. Tools that do not score are omitted.
  String get breakdown {
    final counts = <String, int>{};
    for (final cell in path.skip(1)) {
      final item = level.pickupAt(cell);
      if (item == null || pointsFor(item.kind) == 0) continue;
      counts[item.kind] = (counts[item.kind] ?? 0) + 1;
    }
    final parts = <String>[];
    for (final tool in abbyTools) {
      final count = counts[tool.id] ?? 0;
      if (count == 0 || !tool.scores) continue;
      final word = count == 1 ? tool.label.toLowerCase() : tool.plural;
      parts.add('$count $word');
    }
    parts.add(steps == 1 ? '1 step' : '$steps steps');
    return parts.join(', ');
  }
}

/// The pencil line. Undo is dropping a dot. The flag ends the walk.
class Line {
  Line._(List<Cell> path, this.note) : path = List.unmodifiable(path);

  factory Line.start(Level level) => Line._([level.start], null);

  final List<Cell> path;
  final Block? note;

  String? get message => note == null ? null : messageFor(note!);

  WalkState state(Level level) => WalkState(level, path);

  Line pushed(Level level, Cell cell) {
    if (!level.contains(cell)) return this;
    if (cell == path.last) {
      return note == null ? this : Line._(path, null);
    }
    final index = path.indexOf(cell);
    if (index >= 0) {
      return Line._(path.sublist(0, index + 1), null);
    }
    final block = blockFor(level, path, cell);
    if (block != null) return Line._(path, block);
    return Line._([...path, cell], null);
  }

  /// Drag. A straight stroke fills the dots in between. A miss to the side
  /// does not replace a real reason such as a tree or a cliff.
  Line follow(Level level, Cell target) {
    if (!level.contains(target)) return this;
    if (path.contains(target)) return pushed(level, target);

    final head = path.last;
    final dRow = target.row - head.row;
    final dCol = target.col - head.col;
    if (dRow == 0 || dCol == 0) return _walkStraight(level, target);

    if (dRow.abs() == 1 && dCol.abs() == 1) {
      final corner = dRow.abs() >= dCol.abs()
          ? head.shift(dRow.sign, 0)
          : head.shift(0, dCol.sign);
      final stepped = pushed(level, corner);
      if (stepped.path.last != corner) {
        return stepped.note == Block.side ? this : stepped;
      }
      final next = stepped.pushed(level, target);
      if (next.note == Block.side && next.path.length == stepped.path.length) {
        return stepped;
      }
      return next;
    }

    final direct = pushed(level, target);
    if (direct.note == Block.side && direct.path.length == path.length) {
      return this;
    }
    return direct;
  }

  Line _walkStraight(Level level, Cell target) {
    final stepRow = (target.row - path.last.row).sign;
    final stepCol = (target.col - path.last.col).sign;
    var line = this;
    var cursor = path.last;
    while (cursor != target) {
      cursor = cursor.shift(stepRow, stepCol);
      final next = line.pushed(level, cursor);
      if (next.path.last != cursor) return next;
      line = next;
      if (line.path.length > level.rows * level.cols) return line;
    }
    return line;
  }

  Line undo() {
    if (path.length <= 1) {
      return note == null ? this : Line._(path, null);
    }
    return Line._(path.sublist(0, path.length - 1), null);
  }
}
