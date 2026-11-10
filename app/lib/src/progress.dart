import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Best score for each walk. Higher is better, and a minus still counts.
class ProgressStore extends ChangeNotifier {
  ProgressStore(this._prefs);

  final SharedPreferences _prefs;

  static Future<ProgressStore> open() async {
    return ProgressStore(await SharedPreferences.getInstance());
  }

  int? best(int level) => _prefs.getInt('best.$level');

  Future<void> record(int level, int score) async {
    final key = 'best.$level';
    final previous = _prefs.getInt(key);
    if (previous != null && previous >= score) return;
    await _prefs.setInt(key, score);
    notifyListeners();
  }
}
