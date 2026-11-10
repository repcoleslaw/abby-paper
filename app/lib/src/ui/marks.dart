import 'package:flutter/material.dart';
import 'package:paper_abby/src/theme.dart';

void paintWaves(Canvas canvas, Rect rect) {
  final paint = Paint()
    ..color = AbbyColors.wave
    ..style = PaintingStyle.stroke
    ..strokeWidth = rect.width * 0.035
    ..strokeCap = StrokeCap.round;
  for (final t in const [0.38, 0.55, 0.72]) {
    final y = rect.top + rect.height * t;
    final path = Path()..moveTo(rect.left + rect.width * 0.16, y);
    path.quadraticBezierTo(
      rect.left + rect.width * 0.32,
      y - rect.height * 0.08,
      rect.left + rect.width * 0.5,
      y,
    );
    path.quadraticBezierTo(
      rect.left + rect.width * 0.68,
      y + rect.height * 0.08,
      rect.left + rect.width * 0.84,
      y,
    );
    canvas.drawPath(path, paint);
  }
}

void paintArch(Canvas canvas, Rect rect) {
  final left = rect.left + rect.width * 0.22;
  final right = rect.right - rect.width * 0.22;
  final bottom = rect.bottom - rect.height * 0.18;
  final spring = rect.top + rect.height * 0.52;
  final path = Path()
    ..moveTo(left, bottom)
    ..lineTo(left, spring)
    ..quadraticBezierTo(
      (left + right) / 2,
      rect.top + rect.height * 0.08,
      right,
      spring,
    )
    ..lineTo(right, bottom)
    ..close();
  canvas.drawPath(path, Paint()..color = AbbyColors.arch);
  canvas.drawPath(
    path,
    Paint()
      ..color = AbbyColors.ink
      ..style = PaintingStyle.stroke
      ..strokeWidth = rect.width * 0.035,
  );
}

void paintTree(Canvas canvas, Rect rect) {
  final center = rect.center;
  final size = rect.width;
  canvas.drawLine(
    center + Offset(0, size * 0.02),
    center + Offset(0, size * 0.30),
    Paint()
      ..color = AbbyColors.trunk
      ..strokeWidth = size * 0.045
      ..strokeCap = StrokeCap.round,
  );
  final canopy = Paint()..color = AbbyColors.canopy;
  final edge = Paint()
    ..color = AbbyColors.trunk
    ..style = PaintingStyle.stroke
    ..strokeWidth = size * 0.02;
  final big = center + Offset(size * 0.03, -size * 0.08);
  final small = center + Offset(-size * 0.12, size * 0.02);
  canvas.drawCircle(big, size * 0.2, canopy);
  canvas.drawCircle(small, size * 0.13, canopy);
  canvas.drawCircle(big, size * 0.2, edge);
  canvas.drawCircle(small, size * 0.13, edge);
}

void paintDot(Canvas canvas, Offset center, double cell) {
  final radius = cell * 0.055;
  canvas.drawCircle(center, radius, Paint()..color = AbbyColors.card);
  canvas.drawCircle(
    center,
    radius,
    Paint()
      ..color = AbbyColors.ink
      ..style = PaintingStyle.stroke
      ..strokeWidth = cell * 0.028,
  );
}

void paintPaw(Canvas canvas, Offset center, double cell) {
  final paint = Paint()..color = AbbyColors.ink;
  const toes = <Offset>[
    Offset(-0.13, -0.16),
    Offset(-0.045, -0.21),
    Offset(0.05, -0.20),
    Offset(0.135, -0.14),
  ];
  for (final toe in toes) {
    canvas.drawCircle(center + toe * cell, cell * 0.045, paint);
  }
  canvas.drawOval(
    Rect.fromCenter(
      center: center + Offset(0, cell * 0.02),
      width: cell * 0.26,
      height: cell * 0.2,
    ),
    paint,
  );
}

void paintFlag(Canvas canvas, Offset center, double cell) {
  final poleX = center.dx - cell * 0.04;
  canvas.drawLine(
    Offset(poleX, center.dy + cell * 0.18),
    Offset(poleX, center.dy - cell * 0.2),
    Paint()
      ..color = AbbyColors.ink
      ..strokeWidth = cell * 0.03
      ..strokeCap = StrokeCap.round,
  );
  final flag = Path()
    ..moveTo(poleX, center.dy - cell * 0.2)
    ..lineTo(poleX + cell * 0.22, center.dy - cell * 0.1)
    ..lineTo(poleX, center.dy)
    ..close();
  canvas.drawPath(flag, Paint()..color = AbbyColors.ink);
}

void paintItem(Canvas canvas, String kind, Offset center, double cell) {
  switch (kind) {
    case 'stick':
      _stick(canvas, center, cell);
    case 'ball':
      _ball(canvas, center, cell);
    case 'vest':
      _vest(canvas, center, cell);
    case 'lamp':
      _lamp(canvas, center, cell);
    case 'treat':
      _treat(canvas, center, cell);
    default:
      paintDot(canvas, center, cell);
  }
}

void _stick(Canvas canvas, Offset center, double cell) {
  final paint = Paint()
    ..color = AbbyColors.ink
    ..strokeWidth = cell * 0.03
    ..strokeCap = StrokeCap.round;
  canvas.drawLine(
    center + Offset(-cell * 0.08, cell * 0.07),
    center + Offset(cell * 0.09, -cell * 0.08),
    paint,
  );
  canvas.drawLine(
    center + Offset(cell * 0.01, -cell * 0.01),
    center + Offset(cell * 0.07, cell * 0.02),
    paint,
  );
}

void _ball(Canvas canvas, Offset center, double cell) {
  final radius = cell * 0.09;
  canvas.drawCircle(center, radius, Paint()..color = AbbyColors.card);
  canvas.drawCircle(
    center,
    radius,
    Paint()
      ..color = AbbyColors.ink
      ..style = PaintingStyle.stroke
      ..strokeWidth = cell * 0.02,
  );
  final seam = Paint()
    ..color = AbbyColors.ink
    ..style = PaintingStyle.stroke
    ..strokeWidth = cell * 0.015
    ..strokeCap = StrokeCap.round;
  canvas.drawPath(
    Path()
      ..moveTo(center.dx - radius * 0.7, center.dy)
      ..quadraticBezierTo(
        center.dx,
        center.dy - radius * 0.85,
        center.dx + radius * 0.7,
        center.dy,
      ),
    seam,
  );
}

void _vest(Canvas canvas, Offset center, double cell) {
  final paint = Paint()..color = AbbyColors.ink;
  final panel = Size(cell * 0.07, cell * 0.16);
  for (final dx in [-cell * 0.05, cell * 0.05]) {
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromCenter(
          center: center + Offset(dx, cell * 0.01),
          width: panel.width,
          height: panel.height,
        ),
        const Radius.circular(2),
      ),
      paint,
    );
  }
  canvas.drawLine(
    center + Offset(-cell * 0.08, -cell * 0.05),
    center + Offset(cell * 0.08, -cell * 0.05),
    Paint()
      ..color = AbbyColors.ink
      ..strokeWidth = cell * 0.025
      ..strokeCap = StrokeCap.round,
  );
}

void _lamp(Canvas canvas, Offset center, double cell) {
  final head = center + Offset(0, -cell * 0.02);
  canvas.drawCircle(head, cell * 0.07, Paint()..color = AbbyColors.ink);
  canvas.drawCircle(head, cell * 0.032, Paint()..color = AbbyColors.card);
  canvas.drawLine(
    center + Offset(0, cell * 0.05),
    center + Offset(0, cell * 0.12),
    Paint()
      ..color = AbbyColors.ink
      ..strokeWidth = cell * 0.025
      ..strokeCap = StrokeCap.round,
  );
}

void _treat(Canvas canvas, Offset center, double cell) {
  final paint = Paint()..color = AbbyColors.ink;
  final knob = cell * 0.04;
  for (final dx in [-cell * 0.055, cell * 0.055]) {
    for (final dy in [-cell * 0.035, cell * 0.035]) {
      canvas.drawCircle(center + Offset(dx, dy), knob, paint);
    }
  }
  canvas.drawRRect(
    RRect.fromRectAndRadius(
      Rect.fromCenter(center: center, width: cell * 0.1, height: cell * 0.045),
      const Radius.circular(2),
    ),
    paint,
  );
}
