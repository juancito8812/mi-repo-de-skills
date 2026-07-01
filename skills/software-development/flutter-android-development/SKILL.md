---
name: flutter-android-development
description: "Build, debug, and ship Flutter Android apps. Covers project setup, platform config, release build errors, APK compilation, and multi-screen app architecture."
version: 1.2.0
author: juancito8812
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [flutter, android, apk, mobile, dart, gradle]
    related_skills: [test-driven-development, systematic-debugging, interface-design]
---

# Flutter Android Development

## Overview

Flutter Android development requires: Flutter SDK + JDK 17+ + Android SDK (cmdline-tools + build-tools + platform).

## Prerequisites

### Install Flutter SDK
```bash
# Download latest stable from Flutter's release archive
curl -L -o flutter_windows.zip \
  "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.27.1-stable.zip"
unzip -q flutter_windows.zip
export PATH="$HOME/flutter/bin:$PATH"
```

### Install JDK 17+
```bash
# Via Adoptium API (fastest download)
curl -sS "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse" \
  -o jdk.zip -L
unzip -q jdk.zip
export JAVA_HOME=/c/Users/<user>/jdk-17.0.19+10
```

### Install Android SDK (cmdline-tools)
```bash
# Get the latest version tag from developer.android.com
curl -sS "https://developer.android.com/studio" | grep -oP 'commandlinetools-win-[^"]+'
# Download and extract
curl -L -o android-cmdline-tools.zip \
  "https://dl.google.com/android/repository/commandlinetools-win-<version>_latest.zip"
unzip -q android-cmdline-tools.zip -d android-sdk-tmp
mkdir -p android-sdk/cmdline-tools
mv android-sdk-tmp/cmdline-tools android-sdk/cmdline-tools/latest
export ANDROID_HOME=/c/Users/<user>/android-sdk
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
# Install required components
yes | sdkmanager.bat "build-tools;34.0.0" "platforms;android-34" "platform-tools"
```

## Project Setup

```bash
flutter create --project-name sismos_app --platforms android .
flutter pub get
```

## APK Build

```bash
# Debug
flutter build apk --debug

# Release (without ProGuard/R8 to avoid issues)
flutter build apk --release --no-shrink

# Output: build/app/outputs/flutter-apk/app-release.apk
```

## Common Release Build Errors

See `references/release-build-errors.md` for specific error symptoms and fixes.

### 1. App crashes on startup ("se cerró")
- **MainActivity.kt in wrong package** — The generated file uses `com.example.*` but your namespace is different. Move the file and update its package declaration.
- **Workmanager exception before runApp** — Wrap `Workmanager().initialize()` and `registerPeriodicTask()` in a try-catch so the UI loads even if background scheduling fails.
- **minSdk too low/high** — Explicitly set in `build.gradle`: `minSdk = 21` (covers 99% of devices).

### 2. Gradle build fails
- **Manifest package attribute** — Remove `package="..."` from AndroidManifest.xml (AGP 8+ uses `namespace` in build.gradle).
- **Namespace mismatch** — Ensure `namespace` in `android/app/build.gradle` matches your `applicationId`.
- **Gradle wrapper lock** — Delete `.gradle/wrapper/dists/<version>/*.lck` and `.part` files if a previous download was interrupted.
- **Timeout downloading Gradle** — Download the distribution ZIP manually into the wrapper cache directory and create the `.ok` marker file.

### 3. R8/ProGuard minification fails
- **Don't use ProGuard for Flutter apps** — Flutter handles code shrinking differently. Use `--no-shrink` flag or omit ProGuard config from `build.gradle`.
- If you must use it, add keep rules: `-keep class dev.fluttercommunity.workmanager.** { *; }`

## Multi-Screen App Architecture (sismos-app style)

This project template uses the patterns from `juancito8812/mi-repo-de-skills` skills (`interface-design`, `frontend-design`): signature color token (red for seismic events), hierarchical icon+label cards, maps as signature visual element, squint-testable layout hierarchy.

### Recommended file structure
```
lib/
├── main.dart                 # Entry point + Workmanager init
├── data/
│   ├── earthquake.dart       # Model class (with ==/hashCode)
│   ├── local_db.dart         # SQLite singleton
│   └── repository.dart       # Data sources (API, scraping)
├── screens/
│   ├── home.dart             # Main screen with list + filters
│   ├── detail_screen.dart    # Item detail view
│   ├── map_screen.dart       # Map view (flutter_map)
│   └── settings_screen.dart  # Settings + export
└── services/
    ├── background_poller.dart  # Periodic worker
    └── notification_service.dart # Local notifications
```

### Key patterns
- **Singleton data layer** — `LocalDb.instance` for DB access
- **FutureBuilder for async data** — Load data in `initState`, build UI with `FutureBuilder`
- **Navigation** — `Navigator.push(MaterialPageRoute(...))` between screens
- **Filters** — Return `Map<String, dynamic>` from settings screen via `Navigator.pop(context, filterMap)`, apply filters in home's `_load()` using `queryFiltered()` on the DB layer
- **Map** — `flutter_map` + OpenStreetMap tiles, `MarkerLayer` with `GestureDetector` on each marker. Use `Container` with `BoxDecoration` (circle) for markers, not `Icons.circle`
- **DB migrations** — Always define `_dbVersion` as a top-level const. Add `onUpgrade` callback in `openDatabase()` even if empty, so future schema changes don't break existing installs
- **Shared utilities** — Extract shared functions (e.g. `magnitudeColor()`) as `static` methods on the model class to avoid duplicating identical logic across 3+ screen files

## Code Review Checklist (Flutter)

When reviewing Flutter Android code, check for these common bugs:

### 🔴 Crash on startup
- `MainActivity.kt` package matches the `namespace` in `build.gradle`?
- `Workmanager().initialize()` wrapped in try-catch? (Exception before `runApp()` = instant crash)
- Background channel constant is `public` (no `_` prefix) if referenced from another file?

### 🔴 Compiled but broken
- `final` local variables that might not be assigned in all switch branches? (Use `non-final` for safety)
- DB schema can be migrated? (Missing `onUpgrade` callback = crash on future schema changes)
- Android manifest has no `package` attribute? (AGP 8+ requires `namespace` in build.gradle)

### ⚠️ Maintainability
- Color, style, or size constants duplicated across screen files? (Extract to model or theme)
- Dead code (unused imports, constants, commented blocks)?
- Export/report methods have artificial limits (e.g. `limit: 10000`) that silently truncate data?

### 💡 Structure
- Private method prefixed with `_` not accessible from other files? (Make public or move to shared utility)
- FutureBuilder properly checks `mounted` before `setState` inside async methods?
- Navigation result types are consistent (e.g. `Map<String, dynamic>` for filter results)
- Empty/dead async methods left behind? Check for `_initBackground()` or similar TODO stubs that do nothing after Workmanager was moved to `main.dart`.
- `_dbVersion` declared as top-level const? `onUpgrade` callback present in `openDatabase()` even if empty? (Without it, future schema changes crash existing installs.)

## Data Seeding (Historical Test Data)

Use the USGS FDSN API to seed the local database with historical events for testing filters, map, and export:

```dart
// In EarthquakeRepository
Future<List<Earthquake>> fetchHistorical({
  required DateTime since, DateTime? until,
}) async {
  final url =
    'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson'
    '&starttime=${since.toIso8601String().split('T')[0]}'
    '${until != null ? '&endtime=${until.toIso8601String().split('T')[0]}' : ''}'
    '&minlatitude=-5&maxlatitude=15&minlongitude=-75&maxlongitude=-60'
    '&minmagnitude=2.5&orderby=time&limit=20000';
  // ... parse and return List<Earthquake>
}
```

Add a "Seed historical data" button in settings that calls this and inserts each event via `db.insertOrUpdate()`.

## Filters + Settings Navigation Pattern

Propagate filter values from Settings screen back to Home via `Navigator.pop`:

```dart
// Home screen
Future<void> _openSettings() async {
  final result = await Navigator.push<Map<String, dynamic>>(
    context,
    MaterialPageRoute(builder: (_) => const SettingsScreen()),
  );
  if (result != null) {
    setState(() {
      _minMag = (result['minMagnitude'] as num?)?.toDouble() ?? 0;
      _source = result['source'] as String? ?? 'Todas';
    });
    _refresh();
  }
}

// Settings screen (when user taps "Apply")
Navigator.pop(context, {
  'minMagnitude': _minMagnitude,
  'since': since?.millisecondsSinceEpoch,
  'source': _sourceFilter == 'Todas' ? null : _sourceFilter,
});
```

Use `queryFiltered()` on the DB layer to apply filters as WHERE clauses:

```dart
Future<List<Earthquake>> queryFiltered({
  double? minMagnitude,
  int? sinceEpochMs,
  String? source,
}) async {
  final conditions = <String>[];
  final args = <dynamic>[];
  if (minMagnitude != null) { conditions.add('magnitude >= ?'); args.add(minMagnitude); }
  if (sinceEpochMs != null) { conditions.add('time >= ?'); args.add(sinceEpochMs); }
  if (source != null) { conditions.add('source = ?'); args.add(source); }
  // ... execute query with WHERE + ORDER BY + LIMIT
}
```

```dart
// main.dart — ALWAYS wrap in try-catch to prevent crash on startup
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    await Workmanager().initialize(callbackDispatcher, isInDebugMode: false);
    await Workmanager().registerPeriodicTask(
      'task.name',
      kBackgroundChannel,
      frequency: const Duration(minutes: 15),
      constraints: Constraints(networkType: NetworkType.connected),
    );
  } catch (e) {
    print('[main] Workmanager init error (non-fatal): $e');
  }
  runApp(const MyApp());
}
```

Key rules:
- `callbackDispatcher` MUST be a top-level function with `@pragma('vm:entry-point')`
- The background channel constant MUST be public (no `_` prefix) since it's referenced from `main.dart`
- The dispatcher file needs imports for: `workmanager`, the repository, local_db, notification_service

## Export CSV

```dart
import 'package:csv/csv.dart';
import 'package:path_provider/path_provider.dart';

Future<String> exportToCsv(List<Earthquake> events) async {
  final rows = <List<String>>[['ID', 'Magnitud', ...]];
  for (final e in events) {
    rows.add([e.id, e.magnitude.toString(), ...]);
  }
  final csv = const ListToCsvConverter().convert(rows);
  final dir = await getApplicationDocumentsDirectory();
  final file = File('${dir.path}/sismos_export.csv');
  await file.writeAsString(csv);
  return file.path;
}
```

## GitHub Actions

```yaml
# .github/workflows/build-apk.yml
- uses: subosito/flutter-action@v2
  with:
    flutter-version: '3.24.x'
- run: flutter pub get
- run: flutter create --platforms android .
- run: flutter build apk --release --no-shrink
- uses: actions/upload-artifact@v4
  with:
    path: build/app/outputs/flutter-apk/app-release.apk
```
