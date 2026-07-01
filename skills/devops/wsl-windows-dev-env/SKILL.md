---
name: wsl-windows-dev-env
description: Manage WSL2 development environments bridged to Windows. Covers systemd service setup inside WSL, Windows Task Scheduler integration for auto-start without login, path translation between /mnt/c and Windows paths, detached process spawning from constrained shells, and Hermes Gateway persistent deployment on WSL2.
version: 0.1.0
tags: [wsl, windows, systemd, automation, devops, hermestooling]
---

# WSL + Windows Dev Env

Automate the full stack: WSL2 services that survive reboots without interactive login, Windows-side scheduled tasks that trigger WSL execution, Ollama portable deployment on Windows, and Hermes Gateway running as a WSL systemd service.

## When to use this skill

- Setting up Hermes Gateway or other services to auto-start after power loss
- Creating Windows scheduled tasks that execute WSL commands "At startup" without login
- Managing cross-boundary paths and process spawning between WSL and Windows
- Deploying local LLM tooling (Ollama + Hermes) as an always-on system

## Prerequisites

- WSL2 with a Linux distro (Ubuntu 22.04+ recommended)
- Admin access to Windows Task Scheduler (one-time credential entry)
- `systemd` enabled in WSL (`/etc/wsl.conf` with `[boot] systemd=true`)
- User knows Windows password (for S4U task logon)

## Core workflow

### 1. WSL systemd service

Create `/etc/systemd/system/<service>.service` inside WSL with:
- `User=<linux-user>`
- `ExecStart=<absolute-path-to-binary> <args>`
- `Restart=always` for resilience
- `Environment=HOME` and `PATH` set explicitly

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable <service>
sudo systemctl start <service>
sudo systemctl status <service>
```

### 2. Windows task for WSL auto-start

Use a `.ps1` script (not inline command) to capture credentials once and register the task:

```powershell
$Action = New-ScheduledTaskAction -Execute 'wsl.exe' -Argument '-d Ubuntu -e bash -lc "export PATH=\$HOME/.local/bin:\$PATH && /home/juan/.local/bin/hermes gateway run"'
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Highest
Register-ScheduledTask -TaskName "Hermes Auto Start" -Action $Action -Trigger $Trigger -Principal $Principal -Force
```

Key flags:
- `-LogonType S4U`: runs without password at boot (password stored encrypted in Task Scheduler)
- `-RunLevel Highest`: avoids UAC prompt
- `-Argument`: pass full command string to `wsl.exe`

### 3. Path bridging

WSL sees Windows filesystem under `/mnt/c/`. Windows sees WSL filesystem at `\\wsl.localhost\Ubuntu\`.

| Direction | Pattern |
|-----------|---------|
| WSL → Windows file | `/mnt/c/Users/JRCPU/file.txt` |
| Windows → WSL file | `wsl -d Ubuntu cat /home/juan/file.txt` |
| Run Windows .cmd from WSL | `cmd.exe /c "C:\\path\\to\\script.cmd"` |
| Run WSL script from Windows | `wsl -d Ubuntu bash /home/juan/script.sh` |

**Pitfall:** Do NOT use forward slash paths in Windows Task Scheduler arguments. WSL handles POSIX paths, but Windows spawn with `cmd.exe` may interpret `/` as flags.

### 4. Detached process spawning from inside Hermes

When Hermes Gateway is running, child processes receive SIGTERM if Gateway restarts. To launch a one-shot script that survives:

```powershell
# From Windows (outside Hermes process tree)
Start-Process -FilePath 'wscript.exe' -ArgumentList '//B //Nologo C:\path\launch.vbs' -WindowStyle Hidden
```

Where `launch.vbs` contains:
```vbscript
Set sh = CreateObject("WScript.Shell")
sh.Run "powershell -WindowStyle Hidden -Command ""<command>""", 0, False
```

**Alternative (simpler):** use `cmd.exe /c "start \"\" /b <command>"` — the empty title `""` is mandatory.

### 5. Ollama portable on Windows

Ollama for Windows can run as a portable binary:
- Download ZIP from ollama.com
- Extract `ollama.exe` to `%LOCALAPPDATA%\Ollama\`
- Set `OLLAMA_HOST=127.0.0.1:11434` for local-only binding
- Create Windows scheduled task (At startup) to run the .cmd start script

**No MSI installer needed.** Avoids Windows Installer error 2203 (permission denied on protected paths).

### 6. Verifying the full chain

```bash
# WSL: service active?
sudo systemctl is-active hermes

# Windows: task exists and ready?
schtasks /query /tn "Hermes Auto Start" /fo LIST

# Network: Ollama responds?
curl -s http://127.0.0.1:11434/api/tags | head

# Hermes: model correct?
hermes status --all | grep -E "Model:|Provider:"
```

## Pitfalls

- **SIGTERM propagation:** Hermes Gateway kills child processes on restart. Never rely on `terminal(background=true)` to restart Hermes from inside its own session. Use `wmic process call create` or external `cmd.exe /c start`.
- **PowerShell quoting:** Multi-line PowerShell heredocs inside `terminal` tool calls corrupt due to nested quoting. Always write `.ps1` to disk via `write_file`, then execute `powershell -File path.ps1`.
- **Scheduled task delay:** `New-ScheduledTaskSettingsSet` supports `-Delay (New-TimeSpan -Seconds N)` for dependent services (Ollama first, Hermes after).
- **Path casing:** WSL path `/mnt/c/Users/JRCPU/...` and Windows `C:\Users\JRCPU\...` are interchangeable in most Windows commands, but PowerShell scripts may fail with mixed slashes. Stick to backslashes in `.cmd` / `.ps1`, forward slashes in WSL shell commands.
-- **Flet Desktop scroll:** `expand=True` on a `ft.Container` inside a scrollable `ft.Column` steals all height. Put `expand=True` on the outer `ft.Column` of `page.add()`, not on intermediate containers.
- **Compiling Windows .exe from WSL project:** Flet's `flet pack` produces a `.exe` and requires a Windows Python environment. If the project lives in WSL, copy it to a Windows path (`C:\\Users\\<user>\\`) and run the build script from Windows-side Python. Do NOT try to cross-compile `.exe` artifacts from inside WSL.
- **Terminal tool path resolution:** On Windows hosts, the `terminal` tool runs Git Bash. `/home/juan/...` paths resolve through `/c/Users/JRCPU/...` but Git Bash may interpret them differently when passed through nested shells or `wsl -d Ubuntu`. Prefer `wsl -d Ubuntu -e bash -lc 'commands'` for reliable WSL execution rather than chaining through Git Bash.
- **GitHub automation from WSL:** Install `gh` CLI (`sudo apt install gh`) and run `gh auth login` once. This stores the token encrypted in `~/.config/gh/` and enables `git push`, PR creation, and release management without further credential prompts. Token scopes needed: `repo` and `workflow`.
- **Flet Desktop scroll:** `expand=True` on a `ft.Container` inside a scrollable `ft.Column` steals all height. Put `expand=True` on the outer `ft.Column` of `page.add()`, not on intermediate containers.
- **Compiling Windows .exe from WSL project:** Flet’s `flet pack` requires a Windows Python environment. If the project lives in WSL, copy it to a Windows path (`C:\Users\<user>\`) and run the build script from Windows-side Python. Do NOT try to cross-compile `.exe` artifacts from inside WSL.
- **Terminal tool path resolution on Windows:** Git Bash resolves `/home/juan/...` through `/c/Users/JRCPU/...`, but nested shells and `wsl -d Ubuntu` can reinterpret paths differently. Prefer `wsl -d Ubuntu -e bash -lc '...'` for reliable WSL execution rather than chaining through Git Bash.
- **Copying build artifacts with non-ASCII paths:** Use PowerShell `Copy-Item -LiteralPath` or `robocopy` with quoted NT paths. `cmd.exe /c copy` may fail on accented characters such as `ADMINISTRACIÒN` and spaces. `robocopy` with `/NFL /NDL /NJH /NJS` suppresses noisy output.
- **Verifying compiled .exe contains code changes:** After building, run `strings dist/TasaDelDiaFlet.exe | grep -i 'expected_text'` or search for a known new function/symbol to confirm the build actually picked up the latest source. This catches stale-checkout or caching issues that silent rebuilds can hide.
*** End Patch
