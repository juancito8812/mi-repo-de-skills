# Flutter Android Release Build Errors

## Error: App crashes on startup — "se cerró debido a que esta aplicación tiene un error"

### Cause 1: MainActivity.kt package mismatch
**Symptom:** APK installs but immediately crashes with generic Android error.

**Root cause:** `flutter create --platforms android .` generates `MainActivity.kt` under `com/example/<app_name>/` but the app's actual namespace is different.

**Fix:**
```bash
mkdir -p android/app/src/main/kotlin/com/juancito8812/<app_name>
cat > android/app/src/main/kotlin/com/juancito8812/<app_name>/MainActivity.kt << 'EOF'
package com.juancito8812.<app_name>

import io.flutter.embedding.android.FlutterActivity

class MainActivity: FlutterActivity()
EOF
rm -rf android/app/src/main/kotlin/com/example/
```

Also update `applicationId` and `namespace` in `android/app/build.gradle`:
```gradle
android {
    namespace = "com.juancito8812.<app_name>"
    defaultConfig {
        applicationId = "com.juancito8812.<app_name>"
        minSdk = 21
    }
}
```

### Cause 2: Workmanager exception before runApp
**Symptom:** Same generic crash, but only on release builds.

**Root cause:** `Workmanager().initialize()` throws an exception (e.g., missing permissions on Android 14+) before `runApp()` is called, crashing the app before any UI renders.

**Fix:** Wrap ALL Workmanager calls in try-catch:
```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    await Workmanager().initialize(callbackDispatcher, isInDebugMode: false);
    await Workmanager().registerPeriodicTask(
      'sismos.background', kBackgroundChannel,
      frequency: const Duration(minutes: 15),
      constraints: Constraints(networkType: NetworkType.connected),
    );
  } catch (e) {
    print('[main] Workmanager error (non-fatal): $e');
  }
  runApp(const MyApp());
}
```

### Cause 3: Private channel constant (_kChannel)
**Symptom:** `Error: Undefined name '_kChannel'` at compile time.

**Root cause:** The channel constant uses Dart's `_` prefix making it library-private, but it's referenced from `main.dart` (a different library).

**Fix:** Remove the `_` prefix: `const _kChannel` → `const kBackgroundChannel`.

---

## Error: `processReleaseMainManifest FAILED`

**Message:**
```
Incorrect package="com.example.app" found in source AndroidManifest.xml
Setting the namespace via the package attribute is no longer supported.
```

**Root cause:** AGP 8+ requires `namespace` in `build.gradle`, not `package` in `AndroidManifest.xml`.

**Fix:** Remove `package="..."` from `android/app/src/main/AndroidManifest.xml`. The manifest should start with just:
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
```

Ensure `namespace` is set in `android/app/build.gradle`:
```gradle
android {
    namespace = "com.your.app.id"
}
```

---

## Error: `minifyReleaseWithR8 FAILED`

**Symptom:** Build fails at R8/ProGuard step when adding custom `proguard-rules.pro`.

**Root cause:** R8 conflicts with Flutter's own code shrinking. Some Flutter plugins don't provide ProGuard keep rules.

**Fix:** Build with `--no-shrink` flag:
```bash
flutter build apk --release --no-shrink
```

Or remove ProGuard config from `build.gradle` entirely. Flutter handles dead code elimination at the Dart level, so Android-level minification is often unnecessary for release builds.

---

## Error: `Gradle threw an error while downloading artifacts from the network`

**Cause 1: Lock contention.** Another Gradle process has a lock on the distribution ZIP. The Gradle wrapper uses exclusive file access with a 120-second timeout.

**Fix:**
```bash
# Kill all Java/Gradle processes
ps -W | grep -iE 'java|gradle' | awk '{print $1}' | while read pid; do taskkill //F //PID $pid 2>/dev/null; done

# Delete lock files
rm -f ~/.gradle/wrapper/dists/gradle-8.3-all/*/*.lck
rm -f ~/.gradle/wrapper/dists/gradle-8.3-all/*/*.part
```

**Cause 2: Slow download.** First build needs to download Gradle (~190MB). If it times out, download manually:
```bash
DIST_DIR=~/.gradle/wrapper/dists/gradle-8.3-all/<hash>
mkdir -p "$DIST_DIR"
curl -L -o "$DIST_DIR/gradle-8.3-all.zip" \
  "https://services.gradle.org/distributions/gradle-8.3-all.zip"
touch "$DIST_DIR/gradle-8.3-all.zip.ok"
```

**Fast bypass:** Switch from `-all` to `-bin` in `gradle-wrapper.properties` — uses a different cache hash path, bypassing existing locks AND downloads a smaller file (~100MB vs ~190MB):
```properties
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.3-bin.zip
```

If the lock file won't delete (`Device or resource busy`), the `-bin` switch is the cleanest workaround.

---

## Android Studio Not Found Warning

```
Android Studio version could not be detected, skipping Gradle-Java version compatibility check.
```

**This is safe to ignore.** The build works without Android Studio installed. The warning only means the build won't auto-detect the right Gradle-Java version pairing. For release APK builds with JDK 17, this is fine.
