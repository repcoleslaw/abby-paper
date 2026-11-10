import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:paper_abby/src/model/cell.dart';
import 'package:paper_abby/src/model/level.dart';
import 'package:paper_abby/src/model/walk.dart';

void main() {
  final source = Directory('../Paper Abby/levels');
  final assets = Directory('assets/levels');

  test('every editor line still reaches the flag under the app rules', () {
    expect(source.existsSync(), isTrue);
    final files = _jsonFiles(source);
    expect(files, isNotEmpty);
    for (final file in files) {
      final data = jsonDecode(file.readAsStringSync()) as Map<String, dynamic>;
      final level = Level.fromPaper(data);
      final expectPath = data['expect'];
      if (expectPath is! List || expectPath.isEmpty) continue;
      final cells = [
        for (final token in expectPath)
          Cell.parse('$token', rows: level.rows, cols: level.cols),
      ];
      expect(cells.first, level.start, reason: file.path);
      expect(cells.last, level.flag, reason: file.path);
      var line = Line.start(level);
      for (final cell in cells.skip(1)) {
        final next = line.pushed(level, cell);
        expect(next.message, isNull, reason: '${file.path} ${cell.name}');
        expect(next.path.last, cell, reason: file.path);
        line = next;
      }
      expect(line.state(level).finished, isTrue, reason: file.path);
    }
  });

  test('the app copy has the maps and not the answer lines', () {
    expect(
      assets.existsSync(),
      isTrue,
      reason: 'Run dart run tool/sync_levels.dart',
    );
    final copied = _jsonFiles(assets);
    expect(copied.length, _jsonFiles(source).length);
    for (final file in copied) {
      final data = jsonDecode(file.readAsStringSync()) as Map<String, dynamic>;
      expect(data.containsKey('expect'), isFalse, reason: file.path);
      expect(data.containsKey('aside'), isFalse, reason: file.path);
      expect(data.containsKey('checks'), isFalse, reason: file.path);
      expect(Level.fromPaper(data).number, greaterThan(0));
    }
  });
}

List<File> _jsonFiles(Directory directory) {
  return directory
      .listSync()
      .whereType<File>()
      .where((file) => file.path.toLowerCase().endsWith('.json'))
      .toList()
    ..sort((a, b) => a.path.compareTo(b.path));
}
