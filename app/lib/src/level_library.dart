import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:paper_abby/src/model/cell.dart';
import 'package:paper_abby/src/model/level.dart';

class LevelSource {
  const LevelSource._({required this.path, this.level, this.error});

  final String path;
  final Level? level;
  final String? error;

  String get fileName {
    final slash = path.lastIndexOf('/');
    return slash < 0 ? path : path.substring(slash + 1);
  }

  factory LevelSource.ok(Level level, String path) =>
      LevelSource._(level: level, path: path);

  factory LevelSource.failed(String path, String error) =>
      LevelSource._(path: path, error: error);
}

class LevelLibrary {
  static Future<List<LevelSource>> load() async {
    final manifest = await AssetManifest.loadFromAssetBundle(rootBundle);
    final paths = manifest.listAssets().where((path) {
      return path.startsWith('assets/levels/') && path.endsWith('.json');
    }).toList()..sort();

    final loaded = <LevelSource>[];
    for (final path in paths) {
      loaded.add(await _read(path));
    }
    loaded.sort((a, b) {
      final an = a.level?.number ?? 1 << 20;
      final bn = b.level?.number ?? 1 << 20;
      final byNumber = an.compareTo(bn);
      if (byNumber != 0) return byNumber;
      return a.path.compareTo(b.path);
    });
    return loaded;
  }

  static Future<LevelSource> _read(String path) async {
    try {
      final data = jsonDecode(await rootBundle.loadString(path));
      if (data is! Map<String, dynamic>) {
        return LevelSource.failed(path, 'That file is not a level.');
      }
      return LevelSource.ok(Level.fromPaper(data), path);
    } on LevelParseException catch (error) {
      return LevelSource.failed(path, error.message);
    } on FormatException {
      return LevelSource.failed(
        path,
        '${path.split('/').last} is not a level.',
      );
    }
  }
}
