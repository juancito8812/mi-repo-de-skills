---
name: flutter-android-build
description: "Build Flutter APK on Windows: SDK setup, Gradle fixes, PowerShell env vars, common compilation errors."
version: 1.1.0
author: Hermes Agent
platforms: [windows]
---

# Flutter APK Build — Windows

Build a Flutter Android APK on a bare Windows machine with no pre-installed SDKs. Covers the full chain from zero to `app-release.apk`.

## Prerequisites

- Windows 10/11
- curl, unzip (available in git-bash / MSYS2)
- At least 4 GB free disk

## Step 1 — Install Flutter SDK

```bash
# Download latest stable Flutter for Windows
curl -L -o flutter_windows.zip \
  "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.27.1-stable.zip"

# Extract
unzip -q flutter_windows.zip -d "$HOME"
export PATH="$HOME/flutter/bin:$PATH"
```

## Step 2 — Install JDK 17

Preferred: download via Adoptium API (fastest mirror).

```bash
curl -L -o jdk.zip \
  "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse"
unzip -q jdk.zip -d "$HOME"
export JAVA_HOME="$HOME/jdk-17.0.19+10"
export PATH="$JAVA_HOME/bin:$PATH"
```

## Step 3 — Install Android SDK Command Line Tools

```bash
# Get latest tools version from developer.android.com
curl -sS "https://developer.android.com/studio" | grep -oP 'commandlinetools-win-[^"]+' | head -1

# Download
curl -L -o android-cmdline-tools.zip \
  "https://dl.google.com/android/repository/commandlinetools-win-<VERSION>_latest.zip"

# Extract to android-sdk/cmdline-tools/latest/
unzip -q android-cmdline-tools.zip -d android-sdk-tmp
mkdir -p "$HOME/android-sdk/cmdline-tools"
mv android-sdk-tmp/cmdline-tools "$HOME/android-sdk/cmdline-tools/latest"
rm -rf android-sdk-tmp android-cmdline-tools.zip

export ANDROID_HOME="$HOME/android-sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

# Install required SDK packages
yes | sdkmanager.bat "build-tools;34.0.0" "platforms;android-34" "platform-tools"

# Para plugins que requieren SDK 35 (torch_light, etc.):
yes | sdkmanager.bat "platforms;android-35"
```

## Step 4 — Build the APK

```bash
cd /path/to/flutter/project

# Ensure all env vars are set
export JAVA_HOME="$HOME/jdk-17.0.19+10"
export ANDROID_HOME="$HOME/android-sdk"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$HOME/flutter/bin:$PATH"

# Install Dart dependencies
flutter pub get

# Generate Android platform files (first time only)
flutter create --platforms android .

# Build
flutter build apk --release

# APK location:
# build/app/outputs/flutter-apk/app-release.apk
```

## Step 5 — Post-build: commit + deliver

```bash
git add -A
git commit -m "feat: built APK release"
git push origin main
```

### APK size optimization (abiFilters)

The `torch_light` plugin bundles native `.so` files for all CPU architectures, inflating the APK from ~23 MB to ~50 MB. Shrink it back by restricting to the two architectures covering 99% of Android devices:

```groovy
android {
    defaultConfig {
        ndk {
            abiFilters 'arm64-v8a', 'armeabi-v7a'
        }
    }
}
```

Result: APK drops from ~50 MB back to ~31 MB.

### Flashlight/torch permissions

When using `torch_light`, add these to `AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.FLASHLIGHT" />
<uses-permission android:name="android.permission.CAMERA" />
```

The `CAMERA` permission is needed because `torch_light` controls the camera LED flash.

### Dynamic build number (avoid hardcoding)

Instead of `int get _buildNumber => 13;` (goes stale after first release), use `package_info_plus`:

```yaml
dependencies:
  package_info_plus: ^8.0.0
```

```dart
import 'package:package_info_plus/package_info_plus.dart';

PackageInfo? _pkg;

Future<void> _loadPackageInfo() async {
  _pkg = await PackageInfo.fromPlatform();
  setState(() {});
}

int get _buildNumber => int.tryParse(_pkg?.buildNumber ?? '0') ?? 0;
```

### Local audio assets over network URLs

In production apps (especially SOS/torch scenarios where network may be down), prefer `AssetSource` over `SourceUrl`:

```dart
// In pubspec.yaml:
// assets:
//   - assets/sounds/

// In Dart:
await _player.setSource(AssetSource('sounds/sos_beep.wav'));  // works offline
```

Generate a simple WAV beep with Python (22050 Hz, 880 Hz, 0.2s, mono):

```python
import struct, math
samples = [int(200 * math.sin(2*math.pi*880*i/22050) * math.sin(math.pi*i/(22050*0.2)))
           for i in range(int(22050*0.2))]
# write WAV with RIFF header, fmt chunk, data chunk
```

## Build flags

| Flag | Use case |
|------|----------|
| --release | Production APK (signed with debug keys by default) |
| --no-shrink | Skip R8/ProGuard when minification breaks the build |
| --debug | Debug APK with hot reload, larger size |

## build.gradle version pins

Set these explicitly to avoid plugin compatibility issues:

```groovy
android {
    compileSdk = 35           // no usar flutter.compileSdkVersion
    defaultConfig {
        minSdk = 23           // no usar flutter.minSdkVersion (torch_light requiere 23)
        targetSdk = 35        // no usar flutter.targetSdkVersion
    }
}
```

### APK size notes

| Plugin | Size impact | Reason |
|--------|-------------|--------|
| torch_light | 23 MB → 50 MB | Incluye .so para 4 arquitecturas ARM |
| (base Flutter) | ~20 MB | Engine + Dart code |

## Runtime crash diagnosis

See `references/common-errors.md` section 14 for `adb logcat` debugging workflow.

## Emergency contacts with device picker + pre-configured messages

Use `flutter_contacts` to let the user pick contacts from their device address book, and `url_launcher` to send pre-configured messages via SMS or WhatsApp.

```yaml
dependencies:
  flutter_contacts: ^1.1.0
  url_launcher: ^6.2.0
  shared_preferences: ^2.2.0    # persistence
```

```dart
// Pick from device contacts
if (!await FlutterContacts.requestPermission()) return;
final contact = await FlutterContacts.openExternalPick();
if (contact != null) {
  final phone = contact.phones.isNotEmpty ? contact.phones.first.number : '';
  _saveToPrefs(contact.displayName, phone);
}

// Send pre-configured message via SMS
final uri = Uri.parse('sms:$number?body=${Uri.encodeComponent(text)}');
await launchUrl(uri);

// Send pre-configured message via WhatsApp
final uri = Uri.parse('https://wa.me/$number?text=${Uri.encodeComponent(text)}');
await launchUrl(uri);
```

Pre-configured messages for emergency scenarios:
```dart
const _quickMessages = [
  'Estoy bien 🙏',
  'Necesito ayuda 🆘',
  '¿Estás bien? ¿Dónde estás?',
  'Voy al punto de encuentro',
  'Llámame cuando puedas',
];
```

**Key pattern:** Use a bottom sheet chain: pick message → pick SMS/WhatsApp → launch. Save custom contacts to `SharedPreferences` as pipe-separated strings.

## Settings screen: organization in card sections

Replace a flat `ListView` with grouped card sections for better visual hierarchy:

```dart
_section(theme, Icons.filter_alt, 'Filtros', [ /* widgets */ ])
_section(theme, Icons.sync, 'Background', [ /* widgets */ ])
_section(theme, Icons.storage, 'Datos', [ /* widgets */ ])
_section(theme, Icons.system_update, 'Actualizaciones', [ /* widgets */ ])

Widget _section(ThemeData theme, IconData icon, String title, List<Widget> children) {
  return Card(
    margin: const EdgeInsets.only(bottom: 12),
    child: Padding(
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Icon(icon, size: 18, color: theme.colorScheme.primary),
            const SizedBox(width: 8),
            Text(title, style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
          ]),
          const Divider(),
          ...children,
        ],
      ),
    ),
  );
}
```

## Dark theme for Flutter apps

```dart
MaterialApp(
  theme: ThemeData(
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.red),
    useMaterial3: true,
  ),
  darkTheme: ThemeData(
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.red, brightness: Brightness.dark),
    useMaterial3: true,
  ),
  themeMode: ThemeMode.system,  // follows device setting
  home: const MyHome(),
);
```

## Auto-update checker via GitHub Releases

Check the latest release from a public GitHub repo and prompt the user to download:

```dart
Future<void> _checkForUpdate() async {
  final uri = Uri.parse('https://api.github.com/repos/OWNER/REPO/releases/latest');
  final response = await http.get(uri, headers: {'Accept': 'application/vnd.github+json'});
  final data = jsonDecode(response.body) as Map<String, dynamic>;
  final tag = data['tag_name'] as String? ?? '';
  // compare with current build number
  final versionNum = int.tryParse(tag.replaceAll(RegExp(r'[^\d]'), ''));
  if (versionNum != null && versionNum > currentBuild) {
    // show update available UI
  }
}
```

The associated GitHub Actions workflow (see `templates/build-apk-github-workflow.yml`) creates a release with the APK on every push to main, so the update checker always finds the latest build.

## GitHub Actions (CI)

`skill_view(name="flutter-android-build", file_path="templates/build-apk-github-workflow.yml")` — a complete workflow that builds the APK on every push and creates a GitHub Release with the APK attached.

## ProGuard keep rules

`skill_view(name="flutter-android-build", file_path="templates/proguard-rules.pro")` — rules to prevent R8 from stripping plugin classes.

## USGS Earthquake API (Venezuela app reference)

`skill_view(name="flutter-android-build", file_path="references/usgs-earthquake-api.md")` — FDSN query parameters, bounding box, GeoJSON parsing for Venezuelan earthquake data.

## UI/UX Review Checklist

`skill_view(name="flutter-android-build", file_path="references/ui-review-checklist.md")` — per-screen checklist for systematic mobile app UI reviews. Covers homes, lists, maps, settings, and emergency screens. Use before every release or after major feature additions.

## Code review philosophy (Ponytail)

`skill_view(name="flutter-android-build", file_path="references/ponytail-code-review.md")` — minimalist code review approach used by this user. Forces simplest solution, YAGNI, no over-engineering. Used on every code review pass.

## Common Errors & Fixes

See `references/common-errors.md` for a full list (private constants, missing imports, Manifest namespace, Gradle locks, package mismatch, crash-on-launch).

### App crashes immediately on open ("app has stopped")

**Five most common causes, in order of probability:**

1. **MainActivity.kt in wrong package** — `flutter create` puts it under `com/example/` but your `build.gradle` uses a different namespace. Fix: move the file to `com/<your-domain>/<app>/MainActivity.kt` with matching `package` declaration.
2. **minSdk not explicit** — `flutter.minSdkVersion` may evaluate differently than expected. Fix: set `minSdk = 21` explicitly in `defaultConfig` (23 if using torch_light).
3. **Workmanager blocks UI thread** — `Workmanager().initialize()` throws on Android 14+ before `runApp()`. Fix: wrap in try-catch in `main()`.
4. **compileSdk too low for plugin** — e.g. `torch_light` needs compileSdk ≥ 35. Fix: set `compileSdk = 35` explicitly and install `platforms;android-35`.
5. **ProGuard/R8 stripping** — Minification removes plugin classes. Fix: build with `--no-shrink` or add proper keep rules.

### `_kChannel` / private constant not accessible from main.dart
Dart `_` prefixed identifiers are library-private — not visible outside their file.
**Fix:** rename to public constant (e.g. `kBackgroundChannel`).

### `EarthquakeRepository` / `Workmanager` not found
Missing import in the file that uses them.
**Fix:** add `import 'package:workmanager/workmanager.dart'` and `import 'package:.../data/repository.dart'`.

### `processReleaseMainManifest FAILED`
`package` attribute in `AndroidManifest.xml` is no longer supported — namespace goes in `build.gradle`.
**Fix:** remove `package="..."` from `android/app/src/main/AndroidManifest.xml` and set `namespace = "com.your.package"` in `android/app/build.gradle`.

### Gradle timeout / lock file
`Timeout of 120000 reached waiting for exclusive access to file: gradle-8.3-all.zip`
**Fix:** kill all java/gradle processes (`taskkill //F //PID <pid>`), remove `.lck` and `.part` files from `~/.gradle/wrapper/dists/gradle-8.3-all/<hash>/`, then retry. Alternatively, switch from `-all` to `-bin` distribution in `gradle-wrapper.properties` to use a different cache path.

### `Gradle threw an error while downloading artifacts`
Usually caused by a stale `.lck` or `.part` file from a previous interrupted download.
**Fix:** `rm -rf ~/.gradle/wrapper/dists/gradle-8.3-all/*` and retry.

### `processReleaseMainManifest FAILED` — incorrect namespace
**Fix:** Update `android/app/build.gradle`:
```groovy
android {
    namespace = "com.your.package"
    defaultConfig {
        applicationId = "com.your.package"
    }
}
```
