---
name: changelog-generator
description: Automatically creates user-facing changelogs from git commits by analyzing commit history, categorizing changes, and transforming technical commits into clear, customer-friendly release notes.
version: "1.1.0"
license: MIT
metadata:
  author: juancito8812
  commit-format: Conventional Commits (feat, fix, chore, docs, refactor, test, style, perf, ci, build, revert)
---

# Changelog Generator

## Checklist

- [ ] Git repo with conventional commits
- [ ] Tag or reference point identified (last release tag, date range, or commit hash)
- [ ] Output format determined (markdown, plain text, app store format)
- [ ] Internal commits filtered out (refactor, test, chore, ci)

## When to Use

- Preparing release notes for a new version
- Creating weekly or monthly product update summaries
- Documenting changes for customers
- Writing changelog entries for app store submissions
- Generating update notifications
- Creating internal release documentation
- Maintaining a public changelog/product updates page

## Execution

### 1. Get commits since last tag

```bash
# From repo root
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LAST_TAG" ]; then
  git log "$LAST_TAG..HEAD" --oneline --no-decorate
else
  git log --oneline --no-decorate -30
fi
```

### 2. Categorize by conventional commit type

| Prefix | Category |
|--------|----------|
| `feat` | New Features |
| `fix` | Bug Fixes |
| `perf` | Performance |
| `docs` | Documentation |
| `refactor` | Internal Changes |
| `test` | (filter out) |
| `chore` | (filter out) |
| `ci` | (filter out) |
| `BREAKING` / `!` | Breaking Changes |

### 3. Format output

```markdown
# v{version}

## ✨ New Features
- {user-friendly description of feat commits}

## 🐛 Fixes
- {user-friendly description of fix commits}

## ⚡ Improvements
- {user-friendly description of perf/refactor commits}
```

## Example

**Input commits:**
```
2a4d7ef feat: add dark mode toggle
61f7fb3 fix: resolve crash on empty state
22a9ba7 chore: update dependencies
```

**Output:**
```markdown
# v1.1.0

## ✨ New Features
- **Dark Mode**: Toggle between light and dark themes in settings

## 🐛 Fixes
- Fixed app crash when no data is available
```

## Tips

- Run from your git repository root
- Specify date ranges for focused changelogs
- Review and adjust before publishing
- Translate technical details into user benefits

## Exit Criteria

- [ ] Commits categorized correctly
- [ ] Technical language translated to user-friendly terms
- [ ] Internal commits filtered out
- [ ] Output saved to CHANGELOG.md or release notes
