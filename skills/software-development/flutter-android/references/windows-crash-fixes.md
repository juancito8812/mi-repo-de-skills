# Windows Crash Fixes — Flutter Android

## Session: SismoVE (jun 2026)

### 🔴 Crash: App closes immediately on launch

**Root cause:** `MainActivity.kt` was generated in `com.example.venezuela_sismos_app` but the app's `namespace` (set in `build.gradle`) was `com.juancito8812.venezuela_sismos_app`. Android could not find the activity class at runtime.

**Fix:**
1. Update `package` declaration in `MainActivity.kt` to match `namespace`
2. Move the `.kt` file to the corresponding directory path
3. Remove old directory

```bash
mkdir -p android/app/src/main/kotlin/com/juancito8812/<appname>
# Update package line in the kt file, then:
cp MainActivity.kt android/app/src/main/kotlin/com/juancito8812/<appname>/
rm -rf android/app/src/main/kotlin/com/example/
```

### 🔴 Crash: Blank screen / error before UI renders

**Root cause:** `Workmanager().initialize()` throws an exception (permissions, scheduling constraints) BEFORE `runApp()` executes. Since `main()` is `async`, the exception propagates and the Flutter engine never starts.

**Fix:** Wrap Workmanager calls in try-catch so the app always starts:

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

### ⚠️ R8 Build failure

**Symptom:** `minifyReleaseWithR8 FAILED` with no clear error in output.
**Fix:** Disable R8 completely:
```bash
flutter build apk --release --no-shrink
```

### ⚠️ AndroidManifest `package` attribute error

**Error:** `Setting the namespace via the package attribute in source AndroidManifest.xml is no longer supported.`
**Fix:** Remove `package` attribute from `<manifest>` tag in `AndroidManifest.xml` and use `android/app/build.gradle` namespace.

### 📝 Package rename checklist

When renaming an app's package:
1. `pubspec.yaml` — `name:` field
2. `android/app/build.gradle` — `namespace` and `applicationId`
3. `android/app/src/main/AndroidManifest.xml` — `android:label`
4. `android/app/src/main/kotlin/.../MainActivity.kt` — `package` declaration + move file
5. `lib/main.dart` — `title:` and `package:` imports
6. All `userAgentPackageName` strings in map tile layers
7. Test files — `package:` imports
