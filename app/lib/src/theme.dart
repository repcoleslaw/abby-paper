import 'package:flutter/material.dart';

abstract final class AbbyColors {
  static const ink = Color(0xFF1C1915);
  static const muted = Color(0xFF5E564C);
  static const paper = Color(0xFFFBF6EE);
  static const page = Color(0xFFE7DCC8);
  static const card = Color(0xFFFFFDF8);
  static const grid = Color(0xFFCFC6B8);
  static const tree = Color(0xFFE4F0DA);
  static const canopy = Color(0xFFD5E7C6);
  static const trunk = Color(0xFF243024);
  static const water = Color(0xFFD5EAF2);
  static const wave = Color(0xFF1D4C5C);
  static const cave = Color(0xFFE7E0D6);
  static const arch = Color(0xFFD4CDC2);
  static const cliff = Color(0xFF3A2C1E);
}

const abbyFontFallback = <String>[
  'Palatino Linotype',
  'Palatino',
  'Times New Roman',
  'serif',
];

ThemeData abbyTheme() {
  final base = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    scaffoldBackgroundColor: AbbyColors.page,
    colorScheme: const ColorScheme.light(
      primary: AbbyColors.ink,
      onPrimary: AbbyColors.card,
      surface: AbbyColors.paper,
      onSurface: AbbyColors.ink,
      secondary: AbbyColors.muted,
    ),
    fontFamily: 'Georgia',
    fontFamilyFallback: abbyFontFallback,
  );
  return base.copyWith(
    textTheme: base.textTheme.apply(
      bodyColor: AbbyColors.ink,
      displayColor: AbbyColors.ink,
      fontFamily: 'Georgia',
      fontFamilyFallback: abbyFontFallback,
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(foregroundColor: AbbyColors.ink),
    ),
  );
}
