---
name: external-skill-repo-integration
description: >
  Integrate an external Git repository of skills into Hermes by cloning it and linking
  its SKILL.md files into ~/.hermes/skills/. Use when the user says "quiero que uses
  mis skills", "agregá este repo de skills", "clona mis skills", or references a personal
  skill library.
---

# External skill repo integration

## Goal

Make a user's personal skill library (from a Git repo) available inside Hermes as
first-class skills, without overwriting builtins.

## When to use

- User asks you to use skills from their own GitHub repo
- User provides a URL like `https://github.com/<owner>/<repo>` containing `.agents/skills/` or `skills/`
- User wants their project-specific skills active in every session

## Steps

### Method 1 (preferred): Hermes built-in `skills tap add`

Use when the user says "usa las skills de mi repo" and provides a GitHub URL:

```bash
# Add the repo as a skill tap
hermes skills tap add https://github.com/<owner>/<repo>

# Verify it's registered
hermes skills tap list

# Skills from the tap become available via `hermes skills install <name>`
# or via skill_view(name='<skill-name>') — but skills may need explicit install first
```

If `skill_view()` doesn't find the tapped skill, install it explicitly:

```bash
hermes skills install <skill-name>
```

**Pitfall:** Tapped skills use `skills/` as the default path in the repo. If the repo uses `.agents/skills/` instead, configure the path when tapping (or fall back to Method 2).

### Method 2 (fallback): Manual git clone + symlink

Use when `hermes skills tap add` times out or the repo has a non-standard structure.

1. **Inspect the repo structure**
   ```bash
   curl -s https://api.github.com/repos/<owner>/<repo>/contents/ | head -200
   ```
   Look for:
   - `.agents/skills/` — Superpowers-framework skills
   - `skills/` — simple flat skill directories
   - `.opencode/plugins/` — OpenCode plugins (separate concern)

2. **Clone the repo**
   ```bash
   git clone https://github.com/<owner>/<repo>.git "$HOME/<repo-name>"
   ```
   If the user is inside WSL, clone to the WSL filesystem (`~/<repo-name>`), not `/mnt/c/...`.

3. **Create the skills directory if missing**
   ```bash
   mkdir -p "$HOME/.hermes/skills"
   ```

4. **Link skills by exact name, not globs**
   Use absolute symlinks to avoid globbing bugs:
   ```bash
   cd "$HOME/.hermes/skills"
   ln -sf "$HOME/<repo-name>/.agents/skills/<skill-name>" "<skill-name>"
   ln -sf "$HOME/<repo-name>/skills/<skill-name>" "<skill-name>"
   ```
   **Do NOT use wildcards** (`changelog*`, `vercel*`) — they can match unintended files and break `hermes skills list`.

5. **Verify load**
   ```bash
   hermes skills list | grep -E "<skill1>|<skill2>|..."
   ```
   Each skill should show `local` source and `enabled` status.

6. **Optional: keep repo fresh**
   Add a cron or manual `git pull` in the cloned repo so skills update automatically.

## Pitfalls

- **WSL vs Windows paths**: If Hermes runs inside WSL, skills must be linked inside the WSL filesystem (`~/.hermes/skills`), not on `/mnt/c/`. Windows paths are invisible to the Linux side of Hermes.
- **Glob symlinks**: `ln -s source/skill* skill*` matches directories too and creates broken links. Always use exact names.
- **Protected skills**: Do NOT link over builtin Hermes skills (computer-use, dogfood, etc.) — they are bundled and should not be shadowed.
- **Naming collisions**: If a skill name matches a builtin, the local symlink wins. Verify with `hermes skills list`.
- **Plugin vs skill**: OpenCode plugins (`.opencode/plugins/`) and Hermes plugins (`hermes plugins install`) are separate from skills. Don't confuse them.
- **Ponytail special case**: Ponytail is both a plugin (install with `hermes plugins install`) and a skill (comes from the user's Superpowers repo). If both exist, the plugin provides slash commands; the skill provides the reasoning rules. Both are needed.

## Quick reference

```bash
# Full integration for a Superpowers-style repo
git clone https://github.com/<owner>/<repo>.git ~/<repo>
mkdir -p ~/.hermes/skills
cd ~/.hermes/skills
ln -sf ~/<repo>/.agents/skills/brainstorming brainstorming
ln -sf ~/<repo>/.agents/skills/writing-plans writing-plans
ln -sf ~/<repo>/skills/auto-sync auto-sync
hermes skills list | grep -E "brainstorming|writing-plans|auto-sync"
```
