import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:paper_abby/src/model/cell.dart';
import 'package:paper_abby/src/model/level.dart';
import 'package:paper_abby/src/model/walk.dart';

void main() {
  late Level level;

  setUp(() {
    final file = File('../Paper Abby/levels/01.json');
    level = Level.fromPaper(
      jsonDecode(file.readAsStringSync()) as Map<String, dynamic>,
    );
  });

  Cell n(String name) => Cell.parse(name, rows: level.rows, cols: level.cols);

  test('level 1 trace spends and returns energy the way the page does', () {
    const trace = [
      'A10',
      'B10',
      'C10',
      'D10',
      'D9',
      'C9',
      'C8',
      'D8',
      'E8',
      'E7',
      'D7',
      'D6',
      'D5',
      'D4',
      'D3',
      'E3',
      'F3',
      'F2',
    ];
    const energies = [
      12,
      11,
      13,
      12,
      11,
      10,
      9,
      8,
      7,
      9,
      8,
      7,
      6,
      5,
      4,
      3,
      2,
      1,
    ];
    var line = Line.start(level);
    expect(line.state(level).energy, energies.first);
    for (var i = 1; i < trace.length; i += 1) {
      line = line.pushed(level, n(trace[i]));
      expect(line.message, isNull, reason: trace[i]);
      expect(line.state(level).energy, energies[i], reason: trace[i]);
    }
    final state = line.state(level);
    expect(state.finished, isTrue);
    expect(state.steps, 17);
    expect(state.score, -11);
    expect(state.breakdown, '1 stick, 1 ball, 2 treats, 17 steps');

    final undone = line.undo();
    expect(undone.path.last.name, 'F3');
    expect(undone.state(level).energy, 2);
    expect(undone.state(level).finished, isFalse);
  });

  test('trees, cliffs, gates, and a used dot stop the pencil', () {
    final atB10 = Line.start(level).pushed(level, n('B10'));
    expect(atB10.pushed(level, n('B9')).note, Block.tree);

    final toD9 = _walk(level, ['B10', 'C10', 'D10', 'D9']);
    expect(blockFor(level, toD9.path, n('D8')), Block.water);

    final toD8 = toD9
        .pushed(level, n('C9'))
        .pushed(level, n('C8'))
        .pushed(level, n('D8'));
    expect(toD8.message, isNull);
    expect(blockFor(level, toD8.path, n('D7')), Block.cliff);

    expect(blockFor(level, [n('D4')], n('D5')), Block.cave);
    expect(atB10.pushed(level, n('A10')).path.last.name, 'A10');
    expect(blockFor(level, atB10.path, n('A10')), Block.reuse);
  });

  test('a treat refills after the step and stops at the cap', () {
    final tiny = Level.fromPaper({
      'level': 99,
      'name': 'Tiny',
      'start': 'A1',
      'flag': 'A3',
      'open': ['A1', 'A2', 'A3'],
      'energy': 1,
    });
    final stuck = Line.start(tiny)
        .pushed(tiny, Cell.parse('A2', rows: 10, cols: 6));
    expect(stuck.state(tiny).energy, 0);
    expect(
      stuck.pushed(tiny, Cell.parse('A3', rows: 10, cols: 6)).note,
      Block.energy,
    );

    final treats = Level.fromPaper({
      'level': 98,
      'name': 'Treats',
      'start': 'A1',
      'flag': 'B3',
      'open': ['A1', 'A2', 'B2', 'B3'],
      'pickups': [
        {'at': 'A2', 'kind': 'treat'},
        {'at': 'B2', 'kind': 'treat'},
      ],
      'energy': 22,
      'energy_cap': 24,
    });
    final walked = _walk(treats, ['A2', 'B2', 'B3']);
    expect(walked.state(treats).energy, 23);
    expect(walked.state(treats).score, 2 - 3);
  });

  test('a straight drag fills the dots and a side miss stays quiet', () {
    final row = Level.fromPaper({
      'level': 97,
      'name': 'Row',
      'start': 'A1',
      'flag': 'A4',
      'open': ['A1', 'A2', 'A3', 'A4', 'B3'],
    });
    Cell t(String name) => Cell.parse(name, rows: 10, cols: 6);
    final drawn = Line.start(row).follow(row, t('A4'));
    expect(drawn.path.map((cell) => cell.name), ['A1', 'A2', 'A3', 'A4']);

    final erased = drawn.follow(row, t('A1'));
    expect(erased.path.map((cell) => cell.name), ['A1']);

    final missed = Line.start(row).follow(row, t('B3'));
    expect(missed.message, isNull);
    expect(missed.path.length, 1);
  });

  test('a map cannot be a tree and a gate at once', () {
    expect(
      () => Level.fromPaper({
        'start': 'A1',
        'flag': 'A2',
        'open': ['A1', 'A2'],
        'trees': ['B1'],
      }),
      throwsA(isA<LevelParseException>()),
    );
  });
}

Line _walk(Level level, List<String> steps) {
  var line = Line.start(level);
  for (final step in steps) {
    line = line.pushed(
      level,
      Cell.parse(step, rows: level.rows, cols: level.cols),
    );
    expect(line.message, isNull, reason: step);
  }
  return line;
}
