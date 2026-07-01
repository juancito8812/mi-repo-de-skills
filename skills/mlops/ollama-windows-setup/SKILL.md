---
name: ollama-windows-setup
description: "Instalar Ollama portable en Windows sin MSI, aprovisionar modelos locales, y configurar arranque automático post-apagón/falla eléctrica vía tarea programada."
version: "1.0.0"
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [ollama, windows, local-inference, GGUF, auto-start, recovery, offline]
---

# Ollama Windows Setup

Portable Ollama + Windows scheduled-task auto-start for unattended power-fail recovery.

## When to use

- User has Windows 10/11 and the MSI installer fails (error 1620 / 2203)
- User wants local LLM available again automatically after power returns
- User wants an OpenAI-compatible local endpoint for Hermes or other tools

## What this covers

- Portable ZIP install (no admin rights needed)
- Starting `ollama serve` detached as a background service
- Creating a Windows Scheduled Task for logon auto-start
- Switching Hermes to use the local Ollama backend
- Verifying the service is healthy

## Quick recipes

```powershell
# Install portable
Invoke-WebRequest 'https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip' -OutFile $env:USERPROFILE\ollama-windows-amd64.zip
New-Item "$env:LOCALAPPDATA\Ollama" -ItemType Directory -Force | Out-Null
Expand-Archive $env:USERPROFILE\ollama-windows-amd64.zip -DestinationPath "$env:LOCALAPPDATA\Ollama" -Force
& "$env:LOCALAPPDATA\Ollama\ollama.exe" --version
```

```powershell
# Start service detached
$env:OLLAMA_HOST='127.0.0.1'; $env:OLLAMA_PORT='11434'
Start-Process -FilePath "$env:LOCALAPPDATA\Ollama\ollama.exe" -ArgumentList 'serve' -WindowStyle Hidden
curl.exe http://127.0.0.1:11434/api/tags
```

```powershell
# Auto-start task (run once)
$ScriptPath = Join-Path $env:LOCALAPPDATA 'Ollama\start_ollama.cmd'
Set-Content $ScriptPath "@echo off`r`nset OLLAMA_HOST=127.0.0.1`r`nset OLLAMA_PORT=11434`r`nstart `"`" /min `"%LOCALAPPDATA%\Ollama\ollama.exe`" serve"
$action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument "/c `"$ScriptPath`""
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName 'Ollama Auto Start' -Action $action -Trigger $trigger -Settings $settings -Force
schtasks.exe /query /tn "Ollama Auto Start" /fo LIST
```

## Hermes config

```yaml
model:
  provider: ollama-launch
  default: qwen3:8b
  base_url: http://127.0.0.1:11434/v1
  api_key: ollama
providers:
  ollama-launch:
    name: Ollama
    api: http://127.0.0.1:11434/v1
    default_model: qwen3:8b
    models:
      - qwen3:8b
```

## Hardware-tier model map

| Tier | Usable RAM | Pick |
|------|-----------|------|
| 4 GB | ~2–3 GB | `qwen3:1.7b`, `phi4-mini` |
| 8 GB | ~4–5 GB | `phi4-mini`, `qwen3:4b` |
| 16 GB | ~10–12 GB | `qwen3:8b`, `llama3.3:8b` |

Default to Q4_K_M. Smaller context → faster speed.

## Executing commands on Windows from this agent

The Hermes `terminal` tool runs **bash (MSYS/Git-Bash)**, not PowerShell. This matters for any auto-start logic.

- `start "" /min ...` from bash blocks the foreground and does not return to the shell; use `cmd.exe //c start "" /min ...` instead.
- PowerShell one-liners with `New-ScheduledTask` are brittle when passed through bash quoting; **always write a `.ps1` file** and run it with `powershell -ExecutionPolicy Bypass -File script.ps1`.
- Escaping double-quotes inside double-quoted bash strings is fragile. Prefer file-based scripts over inline `-Command` blocks.
- `schtasks.exe` syntax differs from PowerShell's `ScheduledTasks` module. Use `schtasks.exe //query //fo LIST` or `//fo CSV` for reliability.

## Reliable process detachment patterns

To launch a background daemon from a foreground command:

```bash
# Background via bash subshell (works for ollama serve)
(OLLAMA_HOST=127.0.0.1 OLLAMA_PORT=11434 "$HOME/AppData/Local/Ollama/ollama.exe" serve >/dev/null 2>&1 &) && echo "OK"
```

To restart the Hermes gateway from outside the gateway process tree:

```bash
# Write a script, then spawn it via wmic (completely detached)
cmd.exe //c "echo hermes gateway restart > C:\\Users\\JRCPU\\restart_hermes_now.cmd"
wmic process call create "cmd.exe /c \"C:\\Users\\JRCPU\\restart_hermes_now.cmd\""
```

```powershell
# PowerShell equivalent (from a separate shell session)
Start-Process cmd.exe -ArgumentList '/c', 'hermes gateway restart' -WindowStyle Hidden
```

## Pitfalls

- **MSI installer failure:** The official Ollama MSI often fails on Windows 10 with `1603` / `1620` / `2203` (Windows Installer service errors or locked MSI database). Always fall back to the portable ZIP from GitHub releases.
- `ollama serve` blocks in some shells when started with `start`/`cmd /c start`. Use PowerShell `Start-Process -WindowStyle Hidden` or background the process explicitly.
- **Cannot restart gateway from inside the gateway process:** The Hermes gateway blocks `hermes gateway restart` when called from within its own process tree. Use `wmic process call create`, a separate `cmd.exe /c start`, or `schtasks /run` to trigger an independent restart.
- **S4U logon type requires a non-blank password.** If the Windows account has an empty password, the scheduled task must use a different logon type (e.g., interactive) or the account must be given a password before `S4U` can be used.

## Files

- **Scripts**: `scripts/setup_ollama_task.ps1`, `scripts/start_ollama.cmd`
- **Template**: `templates/ollama_hermes_config.yaml`
