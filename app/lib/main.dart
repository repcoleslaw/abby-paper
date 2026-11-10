import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:paper_abby/src/progress.dart';
import 'package:paper_abby/src/theme.dart';
import 'package:paper_abby/src/ui/level_select.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await SystemChrome.setPreferredOrientations(const [
    DeviceOrientation.portraitUp,
  ]);
  final progress = await ProgressStore.open();
  runApp(PaperAbbyApp(progress: progress));
}

class PaperAbbyApp extends StatelessWidget {
  const PaperAbbyApp({required this.progress, super.key});

  final ProgressStore progress;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Paper Abby',
      debugShowCheckedModeBanner: false,
      theme: abbyTheme(),
      home: LevelSelectPage(progress: progress),
    );
  }
}
