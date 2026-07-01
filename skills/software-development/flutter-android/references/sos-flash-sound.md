# SOS Flash + Sound — Flutter Android

Implements a physical flash LED strobe + audible alarm + vibration pattern for emergency situations.

## Dependencies

```yaml
dependencies:
  audioplayers: ^6.0.0    # sound playback
  torch_light: ^1.0.0     # camera LED flash control
```

## AndroidManifest permissions

```xml
<uses-permission android:name="android.permission.FLASHLIGHT" />
<uses-permission android:name="android.permission.CAMERA" />
```

## Build Config

In `android/app/build.gradle`:

```groovy
android {
    compileSdk = 35            // torch_light needs 34+
    defaultConfig {
        minSdk = 23            // torch_light needs 23+
        targetSdk = 35
    }
}
```

## Generate a Local Sound Asset

Create a simple WAV beep and bundle it so the app works offline (critical in disasters):

```python
import struct, math, os
sr = 22050
samples = [int(200 * math.sin(2*math.pi*880*i/sr) * math.sin(math.pi*i/(sr*0.2)))
           for i in range(int(sr*0.2))]
os.makedirs('assets/sounds', exist_ok=True)
with open('assets/sounds/sos_beep.wav', 'wb') as f:
    f.write(b'RIFF' + struct.pack('<I', 36+len(samples)) + b'WAVE')
    f.write(struct.pack('<IHHIIHH', 16, 1, 1, sr, sr, 1, 8))
    f.write(b'data' + struct.pack('<I', len(samples)) + bytes((s&255) for s in samples))
```

Register in `pubspec.yaml`:
```yaml
flutter:
  assets:
    - assets/sounds/
```

## Core Pattern

### 1. Detect torch availability (show status to user)

```dart
bool _torchOk = false;
bool _torchChecked = false;

Future<void> _checkTorch() async {
  try {
    await TorchLight.enableTorch();
    await TorchLight.disableTorch();
    _torchOk = true;
  } catch (_) {
    _torchOk = false;  // Device has no flash
  }
  _torchChecked = true;
}
```

### 2. Local sound (offline-safe, no URL dependency)

```dart
final _player = AudioPlayer();
bool _audioOk = false;

Future<void> _initAudio() async {
  try {
    await _player.setSource(AssetSource('sounds/sos_beep.wav'));
    await _player.setVolume(1.0);
    _audioOk = true;
  } catch (_) {
    _audioOk = false;
  }
}
```

### 3. Flash toggle + vibration (vibration always works)

```dart
// vibration works on ALL Android devices — use as primary alert
void _vibrate() => HapticFeedback.heavyImpact();

Future<void> _torchSet(bool on) async {
  if (!_torchOk) return;  // skip if no flash hardware
  try { on ? await TorchLight.enableTorch() : await TorchLight.disableTorch(); }
  catch (_) {}
}
```

### 4. SOS Morse Pattern (··· −−− ···)

```dart
// Compact: S=3 short, O=3 long, S=3 short
const _sosPatternMs = [
  200, 200, 200, 200, 200, 600, // S
  600, 200, 600, 200, 600, 600, // O
  200, 200, 200, 200, 200, 200, // S
];

void _runSos() {
  _sosTimer = Timer.periodic(const Duration(milliseconds: 30), (timer) {
    if (_sosStep >= _sosPatternMs.length) { _sosStep = 0; }
    final isOn = _sosStep.isEven;
    final duration = _sosPatternMs[_sosStep];
    if (isOn) { _torchSet(true); _playBeep(); _vibrate(); }
    else      { _torchSet(false); _stopBeep(); }
    _sosStep++;
    timer.cancel();
    Future.delayed(Duration(milliseconds: duration), _runSos);
  });
}
```

## Status UI (show what works before user activates)

```dart
Widget _statusChip(String label, bool ok) {
  return Container(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
    decoration: BoxDecoration(
      color: ok ? Colors.green.shade50 : Colors.grey.shade100,
      border: Border.all(color: ok ? Colors.green : Colors.grey.shade300),
      borderRadius: BorderRadius.circular(12),
    ),
    child: Row(mainAxisSize: MainAxisSize.min, children: [
      Icon(ok ? Icons.check_circle : Icons.cancel, size: 14,
           color: ok ? Colors.green : Colors.grey),
      const SizedBox(width: 4),
      Text(label, style: TextStyle(fontSize: 12,
           color: ok ? Colors.green.shade800 : Colors.grey.shade600)),
    ]),
  );
}

// Usage:
Row(children: [
  _statusChip('Flash', _torchOk),
  _statusChip('Sonido', _audioOk),
  _statusChip('Vibración', true),  // always available
]);
```

## Pitfalls

- **`torch_light` blocks main thread briefly** on `enableTorch()` — acceptable for SOS frequency
- **Sound asset vs URL**: use `AssetSource()` not `setSourceUrl()` — URL won't work offline
- **No reliable way to read flashlight state** — track `_isTorch` bool yourself
- **Activity lifecycle** — stop SOS in `didChangeAppLifecycleState(AppLifecycleState.paused)`
- **Show status chips** before user activates SOS so they know what to expect
- **Vibration fallback**: `HapticFeedback.heavyImpact()` works on **all** Android devices
