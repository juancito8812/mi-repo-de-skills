---
name: local-ollama-workstation
description: "Set up fully automatic local LLM runtime on Windows: portable Ollama, Hermes auto-start, model management, and Windows scheduled tasks for power-loss recovery."
version: 1.0.0
author: Hermes Agent + user
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [ollama, local-llm, windows, auto-start, hermes, setup]
    homepage: https://ollama.com
    related_skills: [hermes-agent]
---

# Local Ollama Workstation

Target: configure a Windows PC so that after a power failure, both Ollama and Hermes Gateway come online automatically, and the user can switch between multiple local models without manual steps.

## Scope

- Deploy Ollama as a portable app (no MSI).
- Create Windows Scheduled Tasks that fire at system startup (before interactive logon).
- Wire Hermes config to use Ollama as a provider.
- Enable model switching via a small Python script.

## Key constraints

- **Do NOT run the MSI installer.** On many Windows PCs it fails with `1603`/`1620` due to MSI service provider errors or permissions. The portable ZIP is reliable.
- **Scheduled tasks for Ollama must use `AtStartup` trigger** with `S4U` logon type so they trigger on system boot before interactive logon.
- **Do NOT require interactive credentials** during setup; write a `.ps1` that calls `New-ScheduledTask` and run it non-interactively, or use `schtasks.exe /create` hardcoded for the user account if the user explicitly requests that tradeoff.
- The secrets stored by Task Scheduler are encrypted by Windows and acceptable for auto-login scenarios. Mention this to the user only once if they ask.

## Step-by-step

### 1. Portable Ollama

```powershell
$url = "https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip"
$zip = "$env:TEMP\ollama-windows-amd64.zip"
$dest = "$env:USERPROFILE\AppData\Local\Ollama"
Invoke-WebRequest -Uri $url -OutFile $zip
Expand-Archive -Path $zip -DestinationPath $dest -Force
```

Write `start_ollama.cmd` at the same location:

```cmd
@echo off
set "OLLAMA_HOST=127.0.0.1"
set "OLLAMA_PORT=11434"
start \"\" /min \"%USERPROFILE%\\AppData\\Local\\Ollama\\ollama.exe\" serve
```

### 2. Windows Scheduled Tasks (system startup)

Prefer `schtasks.exe` to avoid PowerShell quoting pitfalls, or use a `.ps1` file if `New-ScheduledTask` is needed (e.g., for `S4U` logon).

Example using `schtasks.exe` for a logon trigger (acceptable when `AtStartup` + `S4U` fails due to privilege rules):

```cmd
schtasks /create /tn "Ollama Auto Start" ^
  /tr "cmd.exe /c \"%USERPROFILE%\AppData\Local\Ollama\start_ollama.cmd\"" ^
  /sc ONSTART /ru "%USERDOMAIN%\%USERNAME%" /rl HIGHEST /f
```

**Recommended:** a separate `.ps1` that creates two tasks with these settings:

- Trigger: `AtStartup`
- Principal: `UserId = $env:USERDOMAIN\$env:USERNAME`, `LogonType = S4U`, `RunLevel = Highest`
- Settings: `AllowStartIfOnBatteries = $true`, `DontStopIfGoingOnBatteries = $true`, `ExecutionTimeLimit = 0` (infinite)

### 3. Hermes config

Edit `~/.hermes/config.yaml`:

```yaml
model:
  provider: ollama-local
  base_url: http://127.0.0.1:11434/v1
  default: qwen3:8b
providers:
  ollama-local:
    api: http://127.0.0.1:11434/v1
    default_model: qwen3:8b
    models: [qwen3:8b, qwen3:1.7b, llama3.2:3b, phi4-mini]
```

### 4. Model switcher

A small Python helper should:

- Call `GET http://127.0.0.1:11434/api/tags` to list installed models.
- Rewrite the Hermes config (`model.default`, `providers.ollama-local.default_model`) to the selected model.
- Optionally run a short test prompt to verify.

## Verification

- `curl http://127.0.0.1:11434/api/tags` returns installed models.
- `schtasks /query /fo LIST /v` shows the Ollama and Hermes tasks with trigger `At startup`.
- `hermes status --all` shows provider `ollama-local`.

## Pitfalls and anti-patterns

- **MSI on Windows:** Fails on many consumer PCs; always prefer the portable ZIP for Ollama on Windows.
- **PowerShell quoting:** Embedding `New-ScheduledTask` calls in one-liners from bash/MSYS is brittle; write a `.ps1` file and run it via `powershell -ExecutionPolicy Bypass -File script.ps1`.
- **S4U vs password:** `S4U` does not accept blank passwords. If the user account uses a blank password, the task must run under the user’s interactive logon type instead, or the account needs a password for service logon.

## References

See `references/windows_msi_failure_notes.md` and `references/scheduled_task_templates.md`.