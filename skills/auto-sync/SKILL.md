---
name: auto-sync
description: Use after completing any code change, bug fix, or feature implementation in the tasa-del-dia-app project. Automates git commit, push, and AI_HANDOFF.md updates so the repo and handoff doc stay in sync.
version: "1.1.0"
license: MIT
metadata:
  author: juancito8812
  project: tasa-del-dia-app-
---

# Auto-Sync

## Checklist

- [ ] All tests pass (mobile + desktop)
- [ ] AI_HANDOFF.md updated with changes
- [ ] On correct git branch (main unless otherwise specified)
- [ ] No uncommitted experimental changes
- [ ] Commit message follows conventional commits format

## Workflow

Run from the repo root (`tasa-del-dia-app-`):

### 1. Update AI_HANDOFF.md

Append or update the "Últimos Cambios" section with:
- What changed (feature, bug fix, refactor)
- Files modified
- Tests result

### 2. Verify tests

```bash
# Mobile (from repo root)
cd tasa-del-dia && npx jest && cd ..

# Desktop (from repo root)
cd tasa-del-dia-desktop && pytest && cd ..
```

### 3. Commit and push

```bash
git add -A
git commit -m "tipo: descripción concisa del cambio"
git push
```

## Template

```
## feature: [nombre]

| Archivo | Cambio |
|---------|--------|
| `path/to/file.js` | qué se hizo |

Tests: [N]/[N] passing (156 total)
```

## When NOT to auto-sync

- Exploratory changes not ready for commit
- Changes that break tests (fix tests first)
- Experimental branches not yet pushed

## Exit Criteria

- [ ] Code committed with descriptive message
- [ ] AI_HANDOFF.md reflects latest state
- [ ] Tests verified at 100% passing
- [ ] Push confirmed successful
