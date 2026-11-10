import 'package:flutter/material.dart';
import 'package:paper_abby/src/model/cell.dart';
import 'package:paper_abby/src/model/level.dart';
import 'package:paper_abby/src/model/walk.dart';
import 'package:paper_abby/src/theme.dart';
import 'package:paper_abby/src/ui/marks.dart';

class BoardMetrics {
  BoardMetrics({required this.cell, required this.rows, required this.cols})
    : gutter = cell * 0.42;

  final double cell;
  final double gutter;
  final int rows;
  final int cols;

  Size get size => Size(gutter + cols * cell, gutter + rows * cell);

  Offset centerOf(Cell cell) => Offset(
    gutter + (cell.col + 0.5) * this.cell,
    gutter + (cell.row + 0.5) * this.cell,
  );

  Rect cellRect(Cell cell) => Rect.fromLTWH(
    gutter + cell.col * this.cell,
    gutter + cell.row * this.cell,
    this.cell,
    this.cell,
  );

  Cell? cellAt(Offset local) {
    final x = local.dx - gutter;
    final y = local.dy - gutter;
    if (x < 0 || y < 0) return null;
    final col = (x / cell).floor();
    final row = (y / cell).floor();
    if (row < 0 || col < 0 || row >= rows || col >= cols) return null;
    return Cell(row, col);
  }
}

class Board extends StatefulWidget {
  const Board({
    required this.level,
    required this.line,
    required this.cell,
    required this.onCell,
    super.key,
  });

  final Level level;
  final Line line;
  final double cell;
  final void Function(Cell cell, {required bool drag}) onCell;

  @override
  State<Board> createState() => _BoardState();
}

class _BoardState extends State<Board> {
  Cell? _last;
  Cell? _hover;

  BoardMetrics get _metrics => BoardMetrics(
    cell: widget.cell,
    rows: widget.level.rows,
    cols: widget.level.cols,
  );

  void _down(Offset local) {
    final cell = _metrics.cellAt(local);
    _last = cell;
    if (cell != null) widget.onCell(cell, drag: false);
  }

  void _move(Offset local) {
    final cell = _metrics.cellAt(local);
    if (cell == null || cell == _last) return;
    final drag = _last != null;
    _last = cell;
    widget.onCell(cell, drag: drag);
  }

  @override
  Widget build(BuildContext context) {
    final metrics = _metrics;
    final scale = MediaQuery.textScalerOf(context).scale(1).clamp(1.0, 1.3);
    return MouseRegion(
      cursor: SystemMouseCursors.precise,
      onHover: (event) =>
          setState(() => _hover = metrics.cellAt(event.localPosition)),
      onExit: (_) => setState(() => _hover = null),
      child: Listener(
        behavior: HitTestBehavior.opaque,
        onPointerDown: (event) => _down(event.localPosition),
        onPointerMove: (event) => _move(event.localPosition),
        onPointerUp: (_) => _last = null,
        onPointerCancel: (_) => _last = null,
        child: Semantics(
          label: 'Walk. Abby is on ${widget.line.path.last.name}.',
          child: CustomPaint(
            size: metrics.size,
            painter: _BoardPainter(
              level: widget.level,
              line: widget.line,
              metrics: metrics,
              hover: _hover,
              labelScale: scale,
            ),
          ),
        ),
      ),
    );
  }
}

class _BoardPainter extends CustomPainter {
  _BoardPainter({
    required this.level,
    required this.line,
    required this.metrics,
    required this.hover,
    required this.labelScale,
  });

  final Level level;
  final Line line;
  final BoardMetrics metrics;
  final Cell? hover;
  final double labelScale;

  @override
  void paint(Canvas canvas, Size size) {
    final cell = metrics.cell;
    final gutter = metrics.gutter;

    for (var row = 0; row < level.rows; row += 1) {
      for (var col = 0; col < level.cols; col += 1) {
        final dot = Cell(row, col);
        final rect = metrics.cellRect(dot);
        final color = switch (level.terrainAt(dot)) {
          Terrain.tree => AbbyColors.tree,
          Terrain.water => AbbyColors.water,
          Terrain.cave => AbbyColors.cave,
          Terrain.dot => AbbyColors.card,
        };
        canvas.drawRect(rect, Paint()..color = color);
      }
    }

    final grid = Paint()
      ..color = AbbyColors.grid
      ..strokeWidth = 1;
    for (var col = 0; col <= level.cols; col += 1) {
      final x = gutter + col * cell;
      canvas.drawLine(
        Offset(x, gutter),
        Offset(x, gutter + level.rows * cell),
        grid,
      );
    }
    for (var row = 0; row <= level.rows; row += 1) {
      final y = gutter + row * cell;
      canvas.drawLine(
        Offset(gutter, y),
        Offset(gutter + level.cols * cell, y),
        grid,
      );
    }

    if (hover != null && hover != line.path.last) {
      final onPath = line.path.contains(hover);
      final blocked = blockFor(level, line.path, hover!);
      if (onPath || blocked == null) {
        canvas.drawRect(
          metrics.cellRect(hover!).deflate(1.5),
          Paint()..color = const Color(0x141C1915),
        );
      }
    }

    for (final ridge in level.ridges) {
      _paintRidge(canvas, ridge);
    }

    for (var row = 0; row < level.rows; row += 1) {
      for (var col = 0; col < level.cols; col += 1) {
        final dot = Cell(row, col);
        final rect = metrics.cellRect(dot);
        switch (level.terrainAt(dot)) {
          case Terrain.tree:
            paintTree(canvas, rect);
          case Terrain.water:
            paintWaves(canvas, rect);
          case Terrain.cave:
            paintArch(canvas, rect);
          case Terrain.dot:
            break;
        }
      }
    }

    if (line.path.length >= 2) {
      final pencil = Path()
        ..moveTo(
          metrics.centerOf(line.path.first).dx,
          metrics.centerOf(line.path.first).dy,
        );
      for (final dot in line.path.skip(1)) {
        final point = metrics.centerOf(dot);
        pencil.lineTo(point.dx, point.dy);
      }
      canvas.drawPath(
        pencil,
        Paint()
          ..color = AbbyColors.ink
          ..style = PaintingStyle.stroke
          ..strokeWidth = cell * 0.075
          ..strokeCap = StrokeCap.round
          ..strokeJoin = StrokeJoin.round,
      );
    }

    for (var row = 0; row < level.rows; row += 1) {
      for (var col = 0; col < level.cols; col += 1) {
        final dot = Cell(row, col);
        if (level.terrainAt(dot) == Terrain.tree) continue;
        paintDot(canvas, metrics.centerOf(dot), cell);
      }
    }

    for (final item in level.pickups) {
      paintItem(
        canvas,
        item.kind,
        metrics.centerOf(item.at) + Offset(0, -cell * 0.16),
        cell,
      );
    }

    paintPaw(canvas, metrics.centerOf(level.start), cell);
    paintFlag(canvas, metrics.centerOf(level.flag), cell);

    final head = metrics.centerOf(line.path.last);
    canvas.drawCircle(
      head,
      cell * 0.2,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = cell * 0.03
        ..color = AbbyColors.ink.withValues(alpha: 0.45),
    );

    final fontSize = (cell * 0.24 * labelScale).clamp(9.0, 14.0);
    for (var col = 0; col < level.cols; col += 1) {
      _label(
        canvas,
        Cell.columns[col],
        Offset(gutter + (col + 0.5) * cell, gutter * 0.48),
        fontSize,
      );
    }
    for (var row = 0; row < level.rows; row += 1) {
      _label(
        canvas,
        '${row + 1}',
        Offset(gutter * 0.45, gutter + (row + 0.5) * cell),
        fontSize,
      );
    }
  }

  void _paintRidge(Canvas canvas, Ridge ridge) {
    final a = metrics.centerOf(ridge.a);
    final b = metrics.centerOf(ridge.b);
    final mid = Offset((a.dx + b.dx) / 2, (a.dy + b.dy) / 2);
    final vertical = (a.dx - b.dx).abs() > (a.dy - b.dy).abs();
    final along = vertical ? const Offset(0, 1) : const Offset(1, 0);
    final across = vertical ? const Offset(1, 0) : const Offset(0, 1);
    final cell = metrics.cell;
    final length = cell * 0.62;
    canvas.drawLine(
      mid - along * (length / 2),
      mid + along * (length / 2),
      Paint()
        ..color = AbbyColors.cliff
        ..strokeWidth = cell * 0.11
        ..strokeCap = StrokeCap.round,
    );
    final tick = Paint()
      ..color = AbbyColors.paper
      ..strokeWidth = cell * 0.02
      ..strokeCap = StrokeCap.round;
    for (final t in const [-0.16, 0.0, 0.16]) {
      final point = mid + along * (cell * t);
      canvas.drawLine(
        point - across * cell * 0.055,
        point + across * cell * 0.055,
        tick,
      );
    }
  }

  void _label(Canvas canvas, String text, Offset center, double fontSize) {
    final painter = TextPainter(
      text: TextSpan(
        text: text,
        style: TextStyle(
          color: AbbyColors.muted,
          fontSize: fontSize,
          fontFamily: 'Georgia',
          fontFamilyFallback: abbyFontFallback,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    painter.paint(
      canvas,
      center - Offset(painter.width / 2, painter.height / 2),
    );
  }

  @override
  bool shouldRepaint(_BoardPainter oldDelegate) => true;
}
