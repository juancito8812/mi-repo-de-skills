# Windows Ollama Setup Reference

Ollama ships GGUF inference under the hood. On Windows, prefer a portable install over the MSI when you do not have admin rights or when the MSI errors out with 1620 / 2203.

## Portable installation (ZIP)

```powershell
# 1. Download release ZIP
Invoke-WebRequest -Uri 'https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip' -OutFile "$env:USERPROFILE\ollama-windows-amd64.zip"

# 2. Extract portable tree
New-Item -Path "$env:LOCALAPPDATA\Ollama" -ItemType Directory -Force
Expand-Archive -Path "$env:USERPROFILE\ollama-windows-amd64.zip" -DestinationPath "$env:LOCALAPPDATA\Ollama" -Force

# 3. Verify
& "$env:LOCALAPPDATA\Ollama\ollama.exe" --version
```

Do **not** install with `msiexec /i OllamaSetup.exe /qn` if it has already failed with code 1620 or 2203. That indicates an MSI state that cannot be repaired from the current session.

## Detached local server

```powershell
$env:OLLAMA_HOST='127.0.0.1'
$env:OLLAMA_PORT='11434'
Start-Process -FilePath "$env:LOCALAPPDATA\Ollama\ollama.exe" -ArgumentList 'serve' -WindowStyle Hidden
```

Check API:

```powershell
curl.exe http://127.0.0.1:11434/api/tags
```

## Auto-start after power failure (Windows scheduled task)

```powershell
$ScriptPath = Join-Path $env:LOCALAPPDATA 'Ollama\start_ollama.cmd'

Set-Content -Path $ScriptPath -Value @"
@echo off
set OLLAMA_HOST=127.0.0.1
set OLLAMA_PORT=11434
start "" /min "%LOCALAPPDATA%\Ollama\ollama.exe" serve
"@

$action    = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument "/c `"$ScriptPath`""
$trigger   = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName 'Ollama Auto Start' -Action $action -Trigger $trigger -Settings $settings -Force
```

Verify:

```powershell
schtasks.exe /query /tn "Ollama Auto Start" /fo LIST
```

This satisfies the recovery expectation: BIOS auto-power-on -> Windows login -> Ollama serve in background.

## Pull a model

```powershell
curl.exe -s -X POST http://127.0.0.1:11434/api/pull -H "Content-Type: application/json" -d "{`"name`":`"qwen3:8b`",`"stream`":false}"
```

List installed models:

```powershell
curl.exe http://127.0.0.1:11434/api/tags
```

## Point Hermes at local Ollama

Edit `~/.hermes/config.yaml`:

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

Restart Hermes after the config change.

## Hardware tiers for model selection

| Tier | CPU | RAM | Recommended models (Ollama tag) |
|------|-----|-----|---------------------------------|
| Low-end | 4c/4t | 8 GB | `qwen3:1.7b`, `phi4-mini` |
| Mid | 4c/4t+ | 16 GB | `qwen3:8b`, `llama3.2:3b` |
| Mid-high | 8c+ | 32 GB | `qwen3:8b`, `llama3.3:8b`, `qwen3:1.7b` (fast sidecar) |

Use Q4_K_M by default. Only consider Q3 / Q2 if the model bytes cannot fit into available RAM after the OS is accounted for.

## Pitfalls

- `ollama run` is interactive. Use the OpenAI-compatible `/v1/chat/completions` endpoint when invoking from Hermes or other agents.
- The MSI installer fails on restricted Windows hosts. The portable ZIP avoids registry and Program Files writes.
- `start` from `cmd.exe` is synchronous under some shells. Use PowerShell `Start-Process -WindowStyle Hidden` or bash background `(cmd &)` semantics.
- Windows firewall can prompt on first `ollama.exe` serve. Allow on private networks only; do not expose `0.0.0.0` on untrusted networks.
