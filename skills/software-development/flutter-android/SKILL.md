---
name: flutter-android
description: Build, debug, and ship Flutter Android apps on Windows. Covers SDK setup, crash fixes, APK builds, and CI/CD workflows.
version: 1.0.0
author: juancito8812
license: MIT
platforms: [windows]
metadata:
  tags: [flutter, android, apk, gradle, ci-cd]
---

# Flutter Android

## Prerequisites

- Flutter SDK (ZIP, no MSI) — extract to `C:\Users\<user>\flutter`
- JDK 17+ — download via [Adoptium API](https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse) (fast)
- Android cmdline-tools — needed for `sdkmanager`

## Setup on Windows (First Time)

```bash
# 1. Flutter SDK
cd ~ && curl -LO https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_<version>-stable.zip
unzip flutter_windows_<version>-stable.zip
export PATH="$HOME/flutter/bin:$PATH"

# 2. JDK 17
curl -L -o jdk.zip "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse"
unzip jdk.zip
export JAVA_HOME=/c/Users/<user>/jdk-17.0.x+xx

# 3. Android SDK (cmdline-tools)
curl -L -o cmdline-tools.zip "https://dl.google.com/android/repository/commandlinetools-win-<hash>_latest.zip"
mkdir -p android-sdk/cmdline-tools/latest
unzip cmdline-tools.zip -d /tmp && mv /tmp/cmdline-tools/* android-sdk/cmdline-tools/latest/
export ANDROID_HOME=/c/Users/<user>/android-sdk

# 4. Install SDK components
yes | sdkmanager.bat "build-tools;34.0.0" "platforms;android-34" "platform-tools"
```

## Project Setup

```bash
flutter create --platforms android .
flutter pub get
```

## Common Crash Fixes

### 🔴 App closes immediately after install (`MainActivity.kt` package mismatch)
**Symptom:** APK installs but app crashes before showing anything.
**Fix:** `MainActivity.kt` must be in the SAME package as `namespace` in `build.gradle`. Move the file from `com.example.*` to the correct package directory:

```bash
mkdir -p android/app/src/main/kotlin/com/<your>/<package>/
mv MainActivity.kt android/app/src/main/kotlin/com/<your>/<package>/
```

### 🔴 Workmanager causes crash on startup
**Symptom:** App crashes immediately on launch.
**Fix:** Wrap Workmanager init in try-catch:

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    await Workmanager().initialize(callbackDispatcher, isInDebugMode: false);
    await Workmanager().registerPeriodicTask(...);
  } catch (e) {
    print('[main] Workmanager init error (non-fatal): $e');
  }
  runApp(const MyApp());
}
```

### ⚠️ R8/ProGuard build failures
**Symptom:** `minifyReleaseWithR8 FAILED` with cryptic errors.
**Fix:** Build with `--no-shrink` flag:
```bash
flutter build apk --release --no-shrink
```

### ⚠️ Torch/flashlight plugin (`torch_light`) requires higher SDK
**Symptom:** `The plugin torch_light requires a higher Android SDK version.`
**Fix:** Set compileSdk and minSdk explicitly:
```groovy
android {
    compileSdk = 35              // not flutter.compileSdkVersion
    defaultConfig {
        minSdk = 23              // torch_light requires 23
        targetSdk = 35
    }
}
```
Also install platform: `sdkmanager.bat "platforms;android-35"`
And add to `AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.FLASHLIGHT" />
<uses-permission android:name="android.permission.CAMERA" />
```

### ⚠️ Manifest `package` attribute deprecated
**Error:** `Setting the namespace via the package attribute in source AndroidManifest.xml is no longer supported.`
**Fix:** Remove `package` from AndroidManifest.xml and use `namespace` in `build.gradle` instead.

## Build Commands

```bash
# Debug APK (fast)
flutter build apk --debug

# Release APK (no minification)
flutter build apk --release --no-shrink

# With verbose logging
flutter build apk --release --no-shrink -v
```

## GitHub Actions Workflow

Create `.github/workflows/build-apk.yml`:

```yaml
name: Build APK
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.27.x'
          channel: 'stable'
      - run: flutter pub get
      - run: flutter build apk --release --no-shrink
      - uses: actions/upload-artifact@v4
        with:
          name: app-release
          path: build/app/outputs/flutter-apk/app-release.apk
          retention-days: 30

  release:
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with: { name: app-release, path: ./apk }
      - uses: softprops/action-gh-release@v2
        with:
          tag_name: v${{ github.run_number }}
          files: ./apk/app-release.apk
```

## Auto-Update Checker

Add to settings screen to let users download latest APK:

```dart
Future<void> _checkForUpdate() async {
  final uri = Uri.parse('https://api.github.com/repos/<user>/<repo>/releases/latest');
  final response = await http.get(uri, headers: {'Accept': 'application/vnd.github+json'});
  final data = jsonDecode(response.body);
  final tag = data['tag_name'];
  final apkUrl = (data['assets'] as List).firstWhere((a) => a['name'].endsWith('.apk'))['browser_download_url'];
  final versionNum = int.tryParse(tag.replaceAll(RegExp(r'[^\\d]'), ''));
  if (versionNum != null && versionNum > currentBuildNumber) {
    // Show "Update available" with download button
    launchUrl(Uri.parse(apkUrl));
  }
}
```

## SOS Flash + Sound

See `references/sos-flash-sound.md` for the full implementation of:
- Camera LED flash control via `torch_light`
- Audio alarm via `audioplayers`
- SOS Morse pattern (··· −−− ···) with recursive Timer
- minSdk 23 + compileSdk 35 requirements

## Reducing APK Size

The `torch_light` plugin adds native .so files for 4 CPU architectures, inflating the APK from ~23MB to ~50MB. Add `abiFilters` to include only the two most common:

```groovy
android {
    defaultConfig {
        ndk {
            abiFilters 'arm64-v8a', 'armeabi-v7a'
        }
    }
}
```

This reduces APK from ~50MB → ~31MB (covers ~99% of modern Android devices).

## Dynamic Build Number (for update checker)

Don't hardcode `_buildNumber`. Use `package_info_plus`:

```yaml
dependencies:
  package_info_plus: ^8.0.0
```

```dart
import 'package:package_info_plus/package_info_plus.dart';

PackageInfo? _pkg;

Future<void> _loadPackageInfo() async {
  _pkg = await PackageInfo.fromPlatform();
}

int get _buildNumber => int.tryParse(_pkg?.buildNumber ?? '') ?? 0;
```

## Slider `onChangeEnd` Pattern

For sliders that trigger expensive operations (like re-registering Workmanager), use `onChangeEnd` not just `onChanged`:

```dart
Slider(
  value: _interval.toDouble(), min: 5, max: 60, divisions: 11,
  onChangeEnd: (v) => _savePollInterval(v.round()),  // called once on release
  onChanged: (v) => setState(() => _interval = v.round()),  // real-time preview
);
```

## SQLite `onUpgrade` — Always Include

Even if empty, provide an `onUpgrade` callback. Without it, schema changes in future versions will crash existing users:

```dart
return openDatabase(
  path,
  version: _dbVersion,
  onCreate: (db, version) { /* create tables */ },
  onUpgrade: (db, oldVersion, newVersion) async {
    if (oldVersion < 2) { /* add column X */ }
  },
);
```

## Pitfalls

- **`flutter.minSdkVersion` can be unreliable** — always set `minSdk = 21` (or 23 for torch_light) explicitly in `build.gradle`
- **Gradle lock files** after failed builds: delete `~/.gradle/wrapper/dists/gradle-*/*/*.lck` and `.part` files
- **Windows Git line endings**: warnings `LF will be replaced by CRLF` are cosmetic — `.gitattributes` normalizes
- **AGENTS.md / CLAUDE.md**: create for project-level agent instructions (auto-loaded by Hermes)
- **`flutter.compileSdkVersion` / `flutter.targetSdkVersion`**: avoid these macros — set explicit values like `compileSdk = 35` and `targetSdk = 35` for reproducibility
