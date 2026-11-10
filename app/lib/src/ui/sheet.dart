import 'package:flutter/material.dart';
import 'package:paper_abby/src/theme.dart';

/// The phone-width sheet, centered on the desk color when the window is wide.
class PaperSheet extends StatelessWidget {
  const PaperSheet({required this.child, super.key});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: AbbyColors.page,
      child: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 480),
            child: SizedBox.expand(
              child: ColoredBox(color: AbbyColors.paper, child: child),
            ),
          ),
        ),
      ),
    );
  }
}
