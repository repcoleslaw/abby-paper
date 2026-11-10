import 'package:flutter/material.dart';
import 'package:paper_abby/src/copy.dart';
import 'package:paper_abby/src/level_library.dart';
import 'package:paper_abby/src/model/level.dart';
import 'package:paper_abby/src/progress.dart';
import 'package:paper_abby/src/theme.dart';
import 'package:paper_abby/src/ui/play_page.dart';
import 'package:paper_abby/src/ui/sheet.dart';

class LevelSelectPage extends StatefulWidget {
  const LevelSelectPage({required this.progress, super.key});

  final ProgressStore progress;

  @override
  State<LevelSelectPage> createState() => _LevelSelectPageState();
}

class _LevelSelectPageState extends State<LevelSelectPage> {
  final Future<List<LevelSource>> _load = LevelLibrary.load();

  @override
  void initState() {
    super.initState();
    widget.progress.addListener(_onProgress);
  }

  @override
  void dispose() {
    widget.progress.removeListener(_onProgress);
    super.dispose();
  }

  void _onProgress() {
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AbbyColors.page,
      body: PaperSheet(
        child: FutureBuilder<List<LevelSource>>(
          future: _load,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(child: Text('Opening the walks.'));
            }
            if (snapshot.hasError) {
              return Padding(
                padding: const EdgeInsets.all(24),
                child: Text('${snapshot.error}'),
              );
            }
            final sources = snapshot.data ?? const <LevelSource>[];
            final levels = [
              for (final source in sources)
                if (source.level != null) source.level!,
            ];
            final errors = [
              for (final source in sources)
                if (source.error != null) source,
            ];
            return _Catalog(
              levels: levels,
              errors: errors,
              progress: widget.progress,
              onOpen: (index) {
                Navigator.of(context).push(
                  MaterialPageRoute<void>(
                    builder: (context) => PlayPage(
                      campaign: levels,
                      index: index,
                      progress: widget.progress,
                    ),
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
}

class _Catalog extends StatelessWidget {
  const _Catalog({
    required this.levels,
    required this.errors,
    required this.progress,
    required this.onOpen,
  });

  final List<Level> levels;
  final List<LevelSource> errors;
  final ProgressStore progress;
  final ValueChanged<int> onOpen;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (levels.isEmpty && errors.isEmpty) {
      return const Padding(
        padding: EdgeInsets.all(24),
        child: Text(
          'No walks in the app yet. Save puzzles from the map editor into '
          'Paper Abby/levels, then from the app folder run '
          'dart run tool/sync_levels.dart.',
        ),
      );
    }
    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 28),
      children: [
        Text(
          'Paper Abby',
          style: theme.textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.w600,
            letterSpacing: -0.4,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'A walk with a step budget.',
          style: theme.textTheme.bodyMedium?.copyWith(color: AbbyColors.muted),
        ),
        const SizedBox(height: 16),
        for (final rule in rules)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(rule, style: theme.textTheme.bodySmall),
          ),
        const SizedBox(height: 8),
        for (var i = 0; i < levels.length; i += 1) ...[
          _LevelCard(
            level: levels[i],
            best: progress.best(levels[i].number),
            onTap: () => onOpen(i),
          ),
          const SizedBox(height: 8),
        ],
        for (final error in errors)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(
              '${error.fileName}: ${error.error}',
              style: theme.textTheme.bodySmall?.copyWith(
                color: AbbyColors.muted,
              ),
            ),
          ),
      ],
    );
  }
}

class _LevelCard extends StatelessWidget {
  const _LevelCard({
    required this.level,
    required this.best,
    required this.onTap,
  });

  final Level level;
  final int? best;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Material(
      color: AbbyColors.card,
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          child: Row(
            children: [
              SizedBox(
                width: 36,
                child: Text(
                  '${level.number}',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(level.name, style: theme.textTheme.titleSmall),
                    if (level.blurb.isNotEmpty)
                      Text(
                        level.blurb,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: AbbyColors.muted,
                        ),
                      ),
                  ],
                ),
              ),
              if (best != null) ...[
                const SizedBox(width: 8),
                Text(formatScore(best!), style: theme.textTheme.titleSmall),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
