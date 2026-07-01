---
name: github-api-via-curl
description: "GitHub REST API interaction via curl — robust JSON payloads, complex body content, fallback when gh CLI is unavailable."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, API, Curl, REST, JSON, Auth]
    related_skills: [github-auth, github-issues, github-code-review, github-pr-workflow, github-repo-management]
---

# GitHub API via Curl

Companion skill for the bundled GitHub workflow skills (`github-issues`, `github-code-review`, `github-pr-workflow`, `github-repo-management`). Covers the curl fallback pattern when `gh` CLI is not installed, and the robust temp-file JSON approach for complex body content.

## When to Use This

- `gh` CLI is not installed on the machine
- The bundled GitHub skills' inline `-d '{...}'` JSON fails with complex multiline content (backticks, special characters)
- You need to set up `GITHUB_TOKEN` from the Hermes `.env` file

## Quick Auth Detection

```bash
# Determine method and extract token
if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
  AUTH="gh"
else
  AUTH="curl"
  # Fall through multiple sources for GITHUB_TOKEN
  if [ -n "$GITHUB_TOKEN" ]; then
    : # already set
  elif _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
    GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
  elif [ -f "$HOME/.hermes/.env" ] && grep -q "^GITHUB_TOKEN=" "$HOME/.hermes/.env"; then
    GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$HOME/.hermes/.env" | head -1 | cut -d= -f2 | tr -d '\n\r')
  elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
    GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
  fi
fi
echo "Auth method: $AUTH"
```

### Extracting Owner/Repo

```bash
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

## The Temp-File JSON Pattern

**Never use inline `-d '{...}'` for complex body content.** Always write to a temp file first.

### Why Inline Fails

```bash
# ❌ This breaks with backticks, $vars, newlines, backslashes:
curl -s -X POST -d '{"body": "`code` and $HOME and \"quotes\""}' ...
```

### The Robust Pattern

```bash
# ✅ Write to temp file (QUOTED delimiter prevents shell expansion)
cat > /tmp/payload.json << 'EOF'
{
  "title": "Bug: login redirect broken",
  "body": "## Description\nFound a bug in the `auth` middleware.\n\n### Steps\n1. Navigate to `/settings` while logged out\n2. Get redirected to `/login?next=/settings`\n3. After login: lands on `/dashboard` instead of `/settings`\n\n**Expected:** Respect the `?next=` parameter.\n\nCloses #42"
}
EOF

# ✅ Post with --data @file
curl -s -w "\nHTTP=%{http_code}" -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/$OWNER/$REPO/issues \
  --data @/tmp/payload.json
```

### Key Rules

1. **QUOTED heredoc delimiter:** `<< 'EOF'` not `<< EOF` — prevents bash from expanding `$`, backticks, and backslashes
2. **`--data @file`** not `-d @file` (both work, but `--data` is more explicit)
3. **Clean up** with `rm /tmp/payload.json` if you want
4. **Check the response code** with `-w "\nHTTP=%{http_code}"` to see if the API call succeeded

## Setting Up GITHUB_TOKEN from Hermes .env

If `gh` is not installed, add a GitHub token to the Hermes `.env` file:

```bash
# Append to .env (or edit manually with $EDITOR)
GIT_TOKEN_VALUE="ghp_XXXXXXXXXXXXXXX"

# Check if token already exists
if grep -q "^GITHUB_TOKEN=" "$HOME/.hermes/.env" 2>/dev/null; then
  sed -i "s|^GITHUB_TOKEN=.*|GITHUB_TOKEN=$GIT_TOKEN_VALUE|" "$HOME/.hermes/.env"
else
  printf '\nGITHUB_TOKEN=%s\n' "$GIT_TOKEN_VALUE" >> "$HOME/.hermes/.env"
fi
```

On Windows (git-bash), the `.env` file may be at `$HOME/.hermes/.env` or `$HERMES_HOME/.env` where `HERMES_HOME` resolves to `C:\Users\<user>\AppData\Local\hermes`. Check both.

## Verifying Authentication

```bash
. "$HOME/.hermes/.env" 2>/dev/null
# Or source the Hermes-specific env:
if [ -f "$HOME/.hermes/.env" ]; then
  source "$HOME/.hermes/.env"
fi

curl -s -w "HTTP=%{http_code}" \
  -H "Authorization: token ${GITHUB_TOKEN:-}" \
  https://api.github.com/user | grep -E '"login"|HTTP='
```

Expected: `HTTP=200` and your username.

## Session-Specific Examples

For session-specific recipes and error-resolution transcripts, see:

```
skill_view(name="github-api-via-curl", file_path="references/session-recipes.md")
```
