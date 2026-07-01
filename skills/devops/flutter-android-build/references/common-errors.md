# Common Errors — Flutter APK Build on Windows

## 1. Private constants not accessible

**Symptom:**
```
Error: Undefined name '_kChannel'.
```

**Root cause:** Dart identifiers prefixed with `_` are library-private. When `main.dart` imports `background_poller.dart`, it cannot see `_kChannel` or any other `_` constant.

**Fix:** Rename to a public constant (remove the underscore):
```dart
// Before
const _kChannel = 'sismos.background';
// After
const kBackgroundChannel = 'sismos.background';
```
Then reference `kBackgroundChannel` in `main.dart` and `background_poller.dart`.

## 2. Missing imports after refactoring

**Symptom:**
```
Error: Method not found: 'Workmanager'.
Error: Method not found: 'EarthquakeRepository'.
```

**Root cause:** The file uses classes from other packages/files without importing them.

**Fix:** Add the missing imports:
```dart
import 'package:workmanager/workmanager.dart';
import '../data/repository.dart';
```

## 3. AndroidManifest.xml — package attribute deprecated

**Symptom:**
```
Incorrect package="..." found in source AndroidManifest.xml
Setting the namespace via the package attribute is no longer supported.
```

**Root cause:** Android Gradle Plugin 7+ requires `namespace` in `build.gradle`, not `package` in `AndroidManifest.xml`.

**Fix:** 
1. Remove `package` attribute from `<manifest>` tag in `android/app/src/main/AndroidManifest.xml`:
```xml
<!-- Before -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">
<!-- After -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
```

2. Ensure `namespace` is set in `android/app/build.gradle`:
```groovy
android {
    namespace = "com.your.package"
    defaultConfig {
        applicationId = "com.your.package"
    }
}
```

## 4. Gradle distribution download timeout / file lock

**Symptom:**
```
Timeout of 120000 reached waiting for exclusive access to file: gradle-8.3-all.zip
```

**Root cause:** A previous Gradle invocation is still holding a lock on the distribution ZIP (`.lck` file), or a partial download (`.part` file) prevents the new run.

**Fix sequence:**
```bash
# 1. Kill all Java/Gradle processes
ps -W | grep -iE 'java|gradle' | awk '{print $1}' | while read pid; do
  taskkill //F //PID $pid 2>/dev/null || true
done
sleep 3

# 2. Remove lock and partial files
rm -rf ~/.gradle/wrapper/dists/gradle-8.3-all/*/

# 3. OR switch to -bin distribution (different cache path)
sed -i 's|gradle-8.3-all|gradle-8.3-bin|g' android/gradle/wrapper/gradle-wrapper.properties
```

## 5. `flutter create --platforms android .` AFTER first `pub get`

Run `flutter create --platforms android .` from the project root **before** `flutter build apk`. This generates:
- `android/build.gradle`
- `android/app/build.gradle`
- `android/app/src/main/AndroidManifest.xml`
- `android/gradle/wrapper/`
- All mipmap icons and drawable resources

If you already have a custom `AndroidManifest.xml` or `build.gradle`, `flutter create` will **not** overwrite them (skips existing files).

## 6. Building the `java` command not found

**Symptom:**
```
ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
```

**Fix:** Install JDK and set env vars:
```bash
export JAVA_HOME="/c/Users/JRCPU/jdk-17.0.19+10"
export PATH="$JAVA_HOME/bin:$PATH"
```

## 7. `processReleaseMainManifest FAILED` — applicationId mismatch

If `build.gradle` has a different `applicationId` than the one expected by plugins, sync them:
```groovy
defaultConfig {
    applicationId = "com.juancito8812.venezuela_sismos_app"
    namespace = "com.juancito8812.venezuela_sismos_app"
}
```

## 8. Environment variables lost between terminal calls

In git-bash/MSYS2, each `terminal()` call starts a fresh shell. You must re-export all vars in the same command as `flutter build`:

```bash
export JAVA_HOME="/c/Users/JRCPU/jdk-17.0.19+10"
export ANDROID_HOME="/c/Users/JRCPU/android-sdk"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$HOME/flutter/bin:$PATH"
flutter build apk --release
```

## 9. Chocolatey access denied

**Symptom:** `choco install` fails with access denied.

**Root cause:** git-bash/MSYS2 doesn't run with admin privileges by default; chocolatey requires admin.

**Alternative:** Download JDK directly via the Adoptium API (works without admin):
```bash
curl -L -o jdk.zip \
  "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse"
```

## 10. App installs but crashes on launch — MainActivity.kt in wrong package
## 10. App installs but crashes on launch — MainActivity.kt in wrong package

**Symptom:** APK installs successfully on device but immediately crashes on open. No Flutter/Dart error visible in build log.

**Root cause:** `flutter create --platforms android .` generates `MainActivity.kt` under `com/example/yourapp/`. If you later change `namespace` and `applicationId` in `build.gradle`, the compiled `MainActivity` class lives at the wrong package path and Android's ActivityManager can't find it at runtime. The crash happens before any Dart code runs.

**Fix:**
1. Create the correct directory structure:
```bash
mkdir -p android/app/src/main/kotlin/com/yourorg/yourapp
```
2. Move and update `MainActivity.kt`:
```bash
cat > android/app/src/main/kotlin/com/yourorg/yourapp/MainActivity.kt << 'EOF'
package com.yourorg.yourapp

import io.flutter.embedding.android.FlutterActivity

class MainActivity: FlutterActivity()
EOF
# Remove the old default location
rm -rf android/app/src/main/kotlin/com/example/
```
3. Rebuild:
```bash
flutter build apk --release
```

## 10b. App crashes on launch — minSdk too low or not explicit

**Symptom:** App installs but crashes with "Failure to initialize" or generic crash. Not always reproducible on newer devices.

**Root cause:** Doing nothing (relying on `flutter.minSdkVersion`) can cause issues — the value may evaluate differently than expected, or some Play Services / plugin dependencies require a minimum SDK higher than the default Flutter value.

**Fix — set minSdk explicitly:**
```groovy
// In android/app/build.gradle
defaultConfig {
    applicationId = "com.your.package"
    minSdk = 21           // ← explicit, not flutter.minSdkVersion
    targetSdk = flutter.targetSdkVersion
    versionCode = flutter.versionCode
    versionName = flutter.versionName
}
```

Value 21 covers ≥99% of active Android devices.

**Verification:** After applying this fix, the APK opens normally on the device.

## 11. Custom launcher icon (no Android Studio)

Generate a minimal icon with Python/Pillow when no designer assets are needed:

```python
from PIL import Image, ImageDraw
sizes = [('mipmap-mdpi',48),('mipmap-hdpi',72),('mipmap-xhdpi',96),
         ('mipmap-xxhdpi',144),('mipmap-xxxhdpi',192)]
for folder, size in sizes:
    img = Image.new('RGBA', (size,size), (220,30,30,255))
    draw = ImageDraw.Draw(img)
    m = size // 6
    draw.ellipse([m, m, size-m, size-m], fill=(255,255,255,200))
    # Optional: add a simple shape in the center
    cx, cy = size//2, size//2
    w, h = max(3,size//12), size//3
    draw.rectangle([cx-w//2, cy-h//2, cx+w//2, cy+h//2], fill=(220,30,30,255))
    img.save(f'android/app/src/main/res/{folder}/ic_launcher.png')
```

Requires: `pip install Pillow`

## 12. App crashes immediately — Workmanager init throws before runApp()

**Symptom:** App installs and crashes on launch. No Dart errors in build log. `adb logcat` shows a Flutter/Dart exception during engine startup, not an Android ActivityNotFoundException.

**Root cause:** `Workmanager().initialize()` or `registerPeriodicTask()` throws (e.g. due to missing permissions on Android 14+, or Workmanager internal errors). Because these are called in `main()` **before** `runApp()`, the exception kills the app before any Flutter UI renders.

**Fix — wrap in try-catch:**
```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    await Workmanager().initialize(callbackDispatcher, isInDebugMode: false);
  } catch (e) {
    // ignore: avoid_print
    print('[main] Workmanager init error (non-fatal): $e');
    // App still opens — background polling just won't work this session
  }
  runApp(const SismosApp());
}
```

**Verification:** After this fix, the app opens even if Workmanager fails. The background task won't run, but the UI is usable.

## 13. R8/ProGuard minification breaks the build

**Symptom:**
```
> Task :app:minifyReleaseWithR8 FAILED
BUILD FAILED in 42s
```

**Root cause:** R8 attempts to shrink/optimize code but encounters unresolved references for plugin classes, or the ProGuard rules added in `build.gradle` conflict with plugin libraries.

**Fix — build without shrinking:**
```bash
flutter build apk --release --no-shrink
```

This disables R8 entirely. The APK will be slightly larger but fully functional. Add `--no-shrink` to the CI workflow too.

**If you need shrinking** (smaller APK size), use `templates/proguard-rules.pro` from this skill:

```bash
cp <skill-dir>/templates/proguard-rules.pro android/app/
```

Then add to `android/app/build.gradle`:
```groovy
buildTypes {
    release {
        signingConfig = signingConfigs.debug
        proguardFiles(
            getDefaultProguardFile('proguard-android-optimize.txt'),
            'proguard-rules.pro',
        )
    }
}
```

## 14. Crash diagnosis with adb logcat

When an APK installs but crashes on the device immediately, the build log won't show the error. Capture the runtime crash:

```bash
# Connect device via USB (enable USB debugging in Developer Options)

# Filter for crash-related output
adb logcat -b crash | grep -E 'AndroidRuntime|FATAL|flutter'

# Or stream all errors live
adb logcat | grep -E 'AndroidRuntime|FATAL|flutter|Exception|crash'

# Clear the log first for a clean capture
adb logcat -c
# Then open the app
adb logcat | grep -E 'AndroidRuntime|FATAL'
```

**What to look for:**

| Log pattern | Likely cause |
|-------------|-------------|
| `AndroidRuntime: java.lang.RuntimeException: Unable to instantiate activity` | MainActivity.kt in wrong package |
| `Flutter : java.lang.RuntimeException: Could not launch` | Flutter engine init failure |
| `AndroidRuntime: Caused by: java.lang.ClassNotFoundException` | R8 stripped a class, or missing dependency |
| `Flutter : Unhandled Exception: ...` | Dart-side uncaught exception (e.g. Workmanager) |

