# USGS Earthquake API — Venezuela

## FDSN Event Query

Base URL: `https://earthquake.usgs.gov/fdsnws/event/1/query`

### Venezuela bounding box

```dart
const venezuelaUrl =
    'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson'
    '&minlatitude=-5&maxlatitude=15&minlongitude=-75&maxlongitude=-60'
    '&minmagnitude=2.5&orderby=time';
```

| Param | Value | Notes |
|-------|-------|-------|
| `minlatitude` | -5 | Southern Colombia / N. Brazil |
| `maxlatitude` | 15 | Caribbean / N. Venezuela coast |
| `minlongitude` | -75 | Colombia border |
| `maxlongitude` | -60 | Guyana / Trinidad border |
| `minmagnitude` | 2.5 | Smallest felt quake |
| `orderby` | time | Newest first |

### Historical data (seed)

```dart
Future<List<Earthquake>> fetchHistorical({
  required DateTime since,
  DateTime? until,
}) async {
  final untilStr = until != null
      ? '&endtime=${until.toIso8601String().split('T')[0]}'
      : '';
  final url =
      'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson'
      '&starttime=${since.toIso8601String().split('T')[0]}$untilStr'
      '&minlatitude=-5&maxlatitude=15&minlongitude=-75&maxlongitude=-60'
      '&minmagnitude=2.5&orderby=time&limit=20000';
  // timeout: 30 seconds
}
```

### Typical results

- Venezuela area (Jan–Jun 2026): **42 events** (M3.8–7.5)
- Most events are M4.0–4.9 offshore in the Caribbean
- Larger events (M6+) occur in the Caribbean sea north of Venezuela

## Dart Parsing

```dart
factory Earthquake.fromJson(Map<String, dynamic> json) {
  final props = json['properties'] ?? {};
  final geom = json['geometry'] ?? {};
  final coords = geom['coordinates'] ?? [];
  return Earthquake(
    id: json['id']?.toString() ?? '',
    magnitude: (props['mag'] ?? 0).toDouble(),
    place: props['place']?.toString() ?? '',
    time: DateTime.fromMillisecondsSinceEpoch((props['time'] ?? 0)),
    latitude: (coords.isNotEmpty ? coords[1] : 0).toDouble(),
    longitude: (coords.isNotEmpty ? coords[0] : 0).toDouble(),
    depthKm: (coords.isNotEmpty ? coords[2] : 0).toDouble(),
  );
}
```

**GeoJSON structure from USGS:**
```json
{
  "type": "Feature",
  "properties": {
    "mag": 4.6,
    "place": "27 km N of Caraballeda, Venezuela",
    "time": 1782730863516
  },
  "geometry": {
    "type": "Point",
    "coordinates": [-66.8435, 10.8601, 10.0]
  }
}
```

Note: Coordinate array is `[longitude, latitude, depth_km]` (GeoJSON standard).
