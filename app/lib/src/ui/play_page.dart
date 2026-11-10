import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:paper_abby/src/copy.dart';
import 'package:paper_abby/src/model/cell.dart';
import 'package:paper_abby/src/model/level.dart';
import 'package:paper_abby/src/model/walk.dart';
import 'package:paper_abby/src/progress.dart';
import 'package:paper_abby/src/theme.dart';
import 'package:paper_abby/src/ui/board.dart';
import 'package:paper_abby/src/ui/sheet.dart';

class PlayPage extends StatefulWidget {
  const PlayPage({
    required this.campaign,
    required this.index,
    required this.progress,
    super.key,
  });

  final List<Level> campaign;
  final int index;
  final ProgressStore progress;

  Level get level => campaign[index];

  @override
  State<PlayPage> createState() => _PlayPageState();
}

class _PlayPageState extends State<PlayPage> {
  late Line _line = Line.start(widget.level);

  Level get level => widget.level;

  void _apply(Line next) {
    if (_same(_line, next)) return;
    final moved = next.path.length != _line.path.length;
    final state = next.state(level);
    setState(() => _line = next);
    if (state.finished) {
      unawaited(widget.progress.record(level.number, state.score));
    }
    if (moved) HapticFeedback.selectionClick();
  }

  void _onCell(Cell cell, {required bool drag}) {
    _apply(drag ? _line.follow(level, cell) : _line.pushed(level, cell));
  }

  void _step(int dRow, int dCol) {
    final head = _line.path.last;
    _apply(_line.pushed(level, head.shift(dRow, dCol)));
  }

  void _undo() => _apply(_line.undo());

  void _restart() => _apply(Line.start(level));

  void _next() {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute<void>(
        builder: (context) => PlayPage(
          campaign: widget.campaign,
          index: widget.index + 1,
          progress: widget.progress,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = _line.state(level);
    final theme = Theme.of(context);
    final hasNext = widget.index + 1 < widget.campaign.length;
    return CallbackShortcuts(
      bindings: {
        const SingleActivator(LogicalKeyboardKey.arrowUp): () => _step(-1, 0),
        const SingleActivator(LogicalKeyboardKey.arrowDown): () => _step(1, 0),
        const SingleActivator(LogicalKeyboardKey.arrowLeft): () => _step(0, -1),
        const SingleActivator(LogicalKeyboardKey.arrowRight): () => _step(0, 1),
        const SingleActivator(LogicalKeyboardKey.backspace): _undo,
        const SingleActivator(LogicalKeyboardKey.keyZ, control: true): _undo,
        const SingleActivator(LogicalKeyboardKey.escape): () =>
            Navigator.of(context).maybePop(),
      },
      child: Focus(
        autofocus: true,
        child: Scaffold(
          backgroundColor: AbbyColors.page,
          body: PaperSheet(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      TextButton(
                        onPressed: () => Navigator.of(context).maybePop(),
                        child: const Text('Walks'),
                      ),
                      const Spacer(),
                      Text(
                        state.finished ? 'Score' : 'So far',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: AbbyColors.muted,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        formatScore(state.score),
                        style: theme.textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                  Text(
                    '${level.number}. ${level.name}',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  if (level.blurb.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(top: 2),
                      child: Text(
                        level.blurb,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: AbbyColors.muted,
                        ),
                      ),
                    ),
                  const SizedBox(height: 10),
                  Text(
                    'Energy ${state.energy}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: AbbyColors.muted,
                    ),
                  ),
                  const SizedBox(height: 6),
                  _EnergyDots(filled: state.energy, total: level.energyCap),
                  const SizedBox(height: 8),
                  Expanded(
                    child: LayoutBuilder(
                      builder: (context, constraints) {
                        final metrics = BoardMetrics(
                          cell: 1,
                          rows: level.rows,
                          cols: level.cols,
                        );
                        final gutterRatio = metrics.gutter;
                        final cell = math.min(
                          (constraints.maxWidth) / (level.cols + gutterRatio),
                          (constraints.maxHeight) / (level.rows + gutterRatio),
                        );
                        return Align(
                          alignment: Alignment.topCenter,
                          child: Board(
                            level: level,
                            line: _line,
                            cell: cell.clamp(16, 72),
                            onCell: _onCell,
                          ),
                        );
                      },
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(_status(state), style: theme.textTheme.bodyMedium),
                  if (state.finished)
                    Padding(
                      padding: const EdgeInsets.only(top: 2),
                      child: Text(
                        state.breakdown,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: AbbyColors.muted,
                        ),
                      ),
                    ),
                  if (level.pickups.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Text(
                      'Journal',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: AbbyColors.muted,
                      ),
                    ),
                    const SizedBox(height: 6),
                    _Journal(level: level, path: _line.path),
                  ],
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _SheetButton(
                          label: 'Back',
                          onPressed: _line.path.length > 1 ? _undo : null,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _SheetButton(
                          label: 'Start over',
                          onPressed: _line.path.length > 1 || _line.note != null
                              ? _restart
                              : null,
                        ),
                      ),
                      if (state.finished && hasNext) ...[
                        const SizedBox(width: 8),
                        Expanded(
                          child: _SheetButton(
                            label: 'Next',
                            primary: true,
                            onPressed: _next,
                          ),
                        ),
                      ],
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  String _status(WalkState state) {
    final message = _line.message;
    if (message != null) return message;
    if (state.finished) return 'She made the flag.';
    if (state.steps == 0) return 'Draw to a neighboring dot.';
    return state.breakdown;
  }
}

bool _same(Line a, Line b) {
  if (a.note != b.note || a.path.length != b.path.length) return false;
  for (var i = 0; i < a.path.length; i += 1) {
    if (a.path[i] != b.path[i]) return false;
  }
  return true;
}

class _EnergyDots extends StatelessWidget {
  const _EnergyDots({required this.filled, required this.total});

  final int filled;
  final int total;

  @override
  Widget build(BuildContext context) {
    final count = math.max(total, filled);
    return Semantics(
      label: 'Energy $filled',
      child: Wrap(
        spacing: 5,
        runSpacing: 5,
        children: [
          for (var i = 0; i < count; i += 1)
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: i < filled ? AbbyColors.ink : Colors.transparent,
                border: Border.all(
                  color: i < filled ? AbbyColors.ink : AbbyColors.muted,
                  width: 1.2,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _Journal extends StatelessWidget {
  const _Journal({required this.level, required this.path});

  final Level level;
  final List<Cell> path;

  @override
  Widget build(BuildContext context) {
    final items = [...level.pickups]
      ..sort((a, b) {
        final byRow = a.at.row.compareTo(b.at.row);
        if (byRow != 0) return byRow;
        return a.at.col.compareTo(b.at.col);
      });
    return Wrap(
      spacing: 6,
      runSpacing: 6,
      children: [
        for (final item in items)
          _Chip(
            label: '${item.tool.label} ${item.at.name}',
            checked: path.contains(item.at),
          ),
      ],
    );
  }
}

class _Chip extends StatelessWidget {
  const _Chip({required this.label, required this.checked});

  final String label;
  final bool checked;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: checked ? AbbyColors.ink : AbbyColors.card,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: checked ? AbbyColors.ink : AbbyColors.grid),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.bodySmall
            ?.copyWith(color: checked ? AbbyColors.card : AbbyColors.ink),
      ),
    );
  }
}

class _SheetButton extends StatelessWidget {
  const _SheetButton({
    required this.label,
    required this.onPressed,
    this.primary = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool primary;

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(
      onPressed: onPressed,
      style: OutlinedButton.styleFrom(
        foregroundColor: primary ? AbbyColors.card : AbbyColors.ink,
        backgroundColor: primary ? AbbyColors.ink : AbbyColors.card,
        disabledForegroundColor: AbbyColors.muted,
        side: BorderSide(
          color: onPressed == null ? AbbyColors.grid : AbbyColors.ink,
        ),
        minimumSize: const Size(0, 44),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
      child: Text(label),
    );
  }
}
