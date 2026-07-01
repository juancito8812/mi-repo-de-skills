# SismoVE — App Architecture Reference

A Flutter Android earthquake monitoring + preparedness app for Venezuela.

## Structure

```
lib/
├── main.dart                           # Entry + Workmanager init
├── data/
│   ├── earthquake.dart                 # Model + static helpers (Color by magnitude)
│   ├── local_db.dart                   # SQLite singleton with migrations
│   └── repository.dart                 # USGS API + scraping + historical seed
├── screens/
│   ├── home.dart                       # Main screen + prep bar + filter bar
│   ├── event_detail.dart               # Detail with embedded mini-map
│   ├── map_screen.dart                 # Full map with magnitude markers
│   ├── settings_screen.dart            # Filters, seed, export, update checker
│   ├── safety_guide.dart               # Before/During/After guide
│   ├── emergency_kit.dart              # 20-item checklist (shared_prefs)
│   ├── emergency_contacts.dart         # Venezuela emergency numbers (url_launcher)
│   ├── torch_sos.dart                  # Morse code SOS flash
│   ├── family_plan.dart                # Meeting point + contacts + "I'm OK"
│   ├── felt_report.dart                # "Did you feel it?" form
│   ├── first_aid.dart                  # 6-section first aid guide
│   └── risk_zones.dart                 # Risk zone map with legend
└── services/
    ├── background_poller.dart          # Workmanager periodic task
    └── notification_service.dart       # Local push notifications
```

## Key Decisions

- **Offline-first**: All data in SQLite, API calls happen in background
- **No backend**: Everything runs on-device, no server needed
- **USGS as primary source**: `earthquake.usgs.gov/fdsnws/event/1/query`
- **FUNVISIS scraping**: Falls back to text regex if structured HTML unavailable
- **No ProGuard**: Using `--no-shrink` because R8 caused conflicts
- **minSdk = 23**: Required by `torch_light` plugin for flash LED
- **compileSdk = 35**: Explicit, for `torch_light` compatibility

## Version Info

- pubspec: `1.0.0+13`
- App name: SismoVE
- Package: `com.juancito8812.sismo_ve`
