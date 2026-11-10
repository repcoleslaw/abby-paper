# Paper Abby

The phone version of the walk. Web first, then iOS, then Android. Maps still come from the editor in `Paper Abby/`.

## Play on the web

From this folder, with Flutter on your PATH:

```
dart run tool/sync_levels.dart
flutter run -d chrome
```

`flutter build web` writes a static site to `build/web`.

## New puzzles

Paint them in the map editor and save into `Paper Abby/levels`, the same folder as before. Then run `dart run tool/sync_levels.dart` again and restart the app. The script copies the maps and leaves the answer lines, asides, and solver checks out of the app.

iOS needs a Mac: open `ios/Runner.xcworkspace`. Android is the `android` project, when you want it.
