// Copies Paper Abby/levels into this app's assets.
//
// The map editor stays the place puzzles are written. After Save to folder
// (the Paper Abby/levels folder), run this from the app folder:
//
//   dart run tool/sync_levels.dart
//
// Answer lines, asides, and solver checks stay in the editor copies. The
// app gets the map only, so a puzzle can be played without the best line
// sitting in the bundle.

import 'dart:convert';
import 'dart:io';

const _dropped = {'aside', 'expect', 'checks', 'answer'};

void main() {
  final repo = _findRepo(Directory.current);
  final source = Directory(_join([repo.path, 'Paper Abby', 'levels']));
  final dest = Directory(_join([repo.path, 'app', 'assets', 'levels']));
  if (!source.existsSync()) {
    stderr.writeln('No levels at ${source.path}.');
    exitCode = 1;
    return;
  }
  dest.createSync(recursive: true);

  final encoder = const JsonEncoder.withIndent('  ');
  final kept = <String>{};
  var failed = 0;
  final files =
      source
          .listSync()
          .whereType<File>()
          .where((file) => file.path.toLowerCase().endsWith('.json'))
          .toList()
        ..sort((a, b) => a.path.compareTo(b.path));

  for (final file in files) {
    final name = _baseName(file.path);
    Object? data;
    try {
      data = jsonDecode(file.readAsStringSync());
    } on FormatException {
      stderr.writeln('$name is not JSON.');
      failed += 1;
      continue;
    }
    if (data is! Map<String, dynamic>) {
      stderr.writeln('$name is not a level.');
      failed += 1;
      continue;
    }
    data.removeWhere((key, _) => _dropped.contains(key));
    File(_join([dest.path, name]))
        .writeAsStringSync('${encoder.convert(data)}\n');
    kept.add(name);
  }

  for (final file in dest.listSync().whereType<File>()) {
    if (!file.path.toLowerCase().endsWith('.json')) continue;
    if (!kept.contains(_baseName(file.path))) file.deleteSync();
  }

  stdout.writeln('Synced ${kept.length} levels into app/assets/levels.');
  if (failed != 0) {
    stderr.writeln('$failed files were skipped.');
    exitCode = 1;
  }
}

Directory _findRepo(Directory start) {
  var dir = start.absolute;
  for (var i = 0; i < 5; i += 1) {
    final levels = Directory(_join([dir.path, 'Paper Abby', 'levels']));
    if (levels.existsSync()) return dir;
    final parent = dir.parent;
    if (parent.path == dir.path) break;
    dir = parent;
  }
  stderr.writeln(
    'Run this from the app folder. Paper Abby/levels was not found.',
  );
  exit(1);
}

String _join(List<String> parts) {
  final separator = Platform.pathSeparator;
  return parts.join(separator);
}

String _baseName(String path) {
  final slash = path.lastIndexOf(Platform.pathSeparator);
  return slash < 0 ? path : path.substring(slash + 1);
}
