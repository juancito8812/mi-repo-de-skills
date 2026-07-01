---
name: wsl-windows-autostart
description: >
  Make a WSL2 service start automatically when Windows boots, with no interactive login required.
  Covers systemd enablement inside WSL, AtStartup scheduled task creation in Windows,
  and the full boot chain verification. Use when the user asks "arranca solo cuando
  vuelva la luz", "auto-start WSL", "arranque automático sin login", or any task that
  requires a WSL-hosted service (Hermes, Ollama, etc.) to survive power loss.
---

# WSL2 + Windows autostart bridge

## Goal

Windows boots → WSL2 starts → systemd inside WSL launches the target service → no login needed.

## When to use

- User has WSL2 with a long-running service (Hermes gateway, Ollama, database, etc.)
- User wants the service to survive power outages without manual login
- User has already enabled auto-power-on in BIOS/UEFI

## Prerequisites

- WSL2 with a Linux distro running
- `systemd` enabled in `/etc/wsl.conf` (see references/wsl.conf.example)
- The service is working inside WSL before automating it

## Steps

1. **Verify systemd in WSL**
   ```bash
   cat /etc/wsl.conf
   # Must contain:
   # [boot]
   # systemd=true
   # [user]
   # default=<linux-username>
   ```
   If missing, add it and restart WSL from PowerShell:
   ```powershell
   wsl --shutdown
   ```

2. **Create systemd service inside WSL**
   Write `/etc/systemd/system/<service>.service` with:
   - `After=network.target`
   - `Restart=always`
   - `RestartSec=10`
   - Correct `User=` and `WorkingDirectory=`
   See references/systemd-service-template.service for a known-good example.

3. **Enable and start the service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable <service>
   sudo systemctl start <service>
   sudo systemctl is-active <service>  # must return "active"
   ```

4. **Create Windows AtStartup task**
   Run this PowerShell script **once** as Administrator:
   ```powershell
   powershell -ExecutionPolicy Bypass -File "$HOME\enable_system_startup.ps1"
   ```
   It will prompt for the Windows password once, store it encrypted in the Task Scheduler,
   and register the task with `-AtStartup` trigger (no login required).

   Alternatively, create the task manually with:
   - Trigger: **At startup**
   - Action: `wsl.exe -d <distro-name>`
   - Check "Run with highest privileges"

5. **Verify the full chain**
   ```bash
   # From Windows (in WSL):
   wsl -d <distro> -e bash -c 'systemctl is-active <service>'
   ```
   Should return `active`. If inactive, check:
   ```bash
   wsl -d <distro> -e sudo journalctl -u <service> -n 20 --no-pager
   ```

## Pitfalls

- **PowerShell quoting hell**: Inline PowerShell with nested quotes breaks the Hermes terminal almost every time. Always write the script to a `.ps1` file and execute it with `-File`.
- **sudo interactivity**: `sudo` inside WSL may prompt for a password when called non-interactively from Windows. Use root-owned scripts or pre-configure `NOPASSWD` if needed.
- **WSL network timing**: WSL2 may not have network ready when the first systemd unit starts. Add `After=network-online.target` or a small `ExecStartPre=/bin/sleep 10`.
- **Task Scheduler history**: Enable history in Task Scheduler UI if tasks silently fail.
- **service vs run**: For WSL2 foreground services, `hermes gateway run` is recommended over `start` (which expects a system service that may not behave correctly inside WSL).
- **service file location**: Must be `/etc/systemd/system/<service>.service`, not `~/.config/systemd/user/`.

## Support files

- `references/wsl.conf.example` — known-good wsl.conf with systemd enabled
- `references/systemd-service-template.service` — tested Hermes gateway unit file

## Quick reference

```bash
# Windows side
wsl --list --verbose
wsl --shutdown

# WSL side
sudo systemctl enable <service>
sudo systemctl start <service>
sudo systemctl status <service>
sudo journalctl -u <service> -f
```
