# Ponytail Code Review Approach

Ponytail is a code review philosophy from the user's skill repo (`juancito8812/mi-repo-de-skills`). It forces the laziest solution that actually works — simplest, shortest, most minimal.

## Core principle: The Ladder

Stop at the first rung that holds:

1. **Does this need to exist at all?** (YAGNI) — speculative need = skip it
2. **Stdlib does it?** — use it
3. **Native platform feature covers it?** — CSS over JS, DB constraint over app code
4. **Already-installed dependency solves it?** — use it
5. **Can it be one line?** — one line
6. **Only then:** the minimum code that works

## Rules

- No unrequested abstractions (no interface with one implementation, no factory for one product)
- Deletion over addition. Boring over clever.
- Fewest files possible. Shortest working diff wins.
- Mark deliberate simplifications with a `ponytail:` comment.

## Intensity levels

| Level | What changes |
|-------|-------------|
| **lite** | Build what's asked, name the lazier alternative |
| **full** | Ladder enforced. Stdlib and native first. Default. |
| **ultra** | YAGNI extremist. Deletion before addition. |

## When NOT to be lazy

Never simplify away: input validation, error handling that prevents data loss, security measures, accessibility, anything explicitly requested.

## Example ponytail saves from SismoVE

| File | Before | After | ponytail reason |
|------|--------|-------|-----------------|
| `earthquake.dart` | `import 'package:flutter/material.dart'` for `Colors.red` | `import 'dart:ui' show Color` + hex values | No importar Material en modelo |
| `repository.dart` | `_scrapeFunvisis()` with regex never producing useful data | `return {}` | YAGNI — nunca funciona |
| `local_db.dart` | Empty `onUpgrade` callback | Removed | Agregar cuando haya migración real |
| `pubspec.yaml` | 11 unused dependencies (`geolocator*`, `permission_handler*`, `html`) | Removed | No usar lo que no se necesita |
