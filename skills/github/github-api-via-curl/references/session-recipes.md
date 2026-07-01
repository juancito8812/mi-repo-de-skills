# Session Recipes — Creating GitHub Issues via Curl

## Situation
- `gh` CLI not installed on Windows (git-bash)
- GitHub PAT available but needs to go into `$HOME/.hermes/.env`
- Need to create issues and comments on a repo

## Recipe 1: Auth Setup from Pat Token

```bash
# Store token in ~/.hermes/.env (durable across sessions)
# Check HERMES_HOME first — may point to AppData\Local\hermes
echo "HERMES_HOME=$HERMES_HOME"
ls "$HOME/.hermes/.env" 2>/dev/null && echo "found in ~/.hermes/.env"
ls "${HERMES_HOME:-$HOME/.hermes}/.env" 2>/dev/null && echo "found in HERMES_HOME/.env"

# Add GITHUB_TOKEN if missing (single-line append)
if grep -q "^GITHUB_TOKEN=" "$HOME/.hermes/.env"; then
  : # already there
else
  echo '' >> "$HOME/.hermes/.env"
  echo '# GitHub PAT for API access' >> "$HOME/.hermes/.env"
  echo "GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE" >> "$HOME/.hermes/.env"
fi
```

## Recipe 2: Create Issue (Robust)

When inline JSON fails with 400 "Problems parsing JSON" (common when body has newlines/backticks):

```bash
# 1. Source the env
. "$HOME/.hermes/.env"

# 2. Get owner/repo from git remote
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')

# 3. Write payload to temp file (QUOTED delimiter!)
cat > /tmp/issue.json << 'BODYEOF'
{
  "title": "Issue title",
  "body": "### Section\nDetails here with `code` and special chars.\n\n**Commit:** abc1234"
}
BODYEOF

# 4. POST with --data @file
curl -s -w "\nHTTP=%{http_code}" -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$OWNER_REPO/issues" \
  --data @/tmp/issue.json
```

**Success signal:** `HTTP=201` with JSON response containing `"html_url"`.
**Failure:** `HTTP=400` with message like `"Problems parsing JSON"` or `HTTP=401` (bad token).

## Recipe 3: Add Comment to Issue

Same pattern, different endpoint:

```bash
ISSUE_NUMBER=2

cat > /tmp/comment.json << 'COMMENTEOF'
{
  "body": "### Code Review Summary\n- ✅ Fix applied in `commit abc1234`\n- All checks passed"
}
COMMENTEOF

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$OWNER_REPO/issues/$ISSUE_NUMBER/comments" \
  --data @/tmp/comment.json
```

**Success signal:** `HTTP=201` with JSON containing `"html_url"`.

## Recipe 4: Auth Verification

```bash
. "$HOME/.hermes/.env"
curl -s -w "\nHTTP=%{http_code}" \
  -H "Authorization: token ${GITHUB_TOKEN:-}" \
  https://api.github.com/user | grep -E '"login"|HTTP='
```

Expected output:
```
  "login": "yourusername",
HTTP=200
```

## Troubleshooting

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| `HTTP=401` Bad credentials | Token expired or revoked | Generate new PAT at github.com/settings/tokens |
| `HTTP=400` Problems parsing JSON | Unquoted heredoc or inline `${}` in body | Use `<< 'EOF'` (quoted) and `--data @file` |
| `HTTP=404` Not found | Wrong owner/repo or private repo without access | Check `$OWNER_REPO` and scope |
| Token "works" for git pull but not curl | Token scopes may only allow read | Regenerate with `repo` scope |
| `HTTP=0` or no response | Network issue or wrong URL | Check the endpoint URL |
