import 'package:flutter_test/flutter_test.dart';
import 'package:paper_abby/main.dart';
import 'package:paper_abby/src/progress.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  testWidgets('the walks from the editor are on the shelf', (tester) async {
    SharedPreferences.setMockInitialValues({});
    final progress = await ProgressStore.open();
    await tester.pumpWidget(PaperAbbyApp(progress: progress));
    await tester.pumpAndSettle();

    expect(find.text('Paper Abby'), findsOneWidget);
    expect(find.text('The whole walk'), findsOneWidget);

    await tester.tap(find.text('The whole walk'));
    await tester.pumpAndSettle();
    expect(find.text('Draw to a neighboring dot.'), findsOneWidget);
    expect(find.text('1. The whole walk'), findsOneWidget);
  });
}
