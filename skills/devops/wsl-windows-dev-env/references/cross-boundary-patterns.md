# Cross-Boundary Patterns: WSL ⇄ Windows

Command recipes discovered during WSL2 + Windows integration sessions.

## Spawn detached Windows process from inside WSL

Problem: Hermes Gateway kills child processes on restart via SIGTERM.

```powershell
# From inside WSL:
cmd.exe /c "start "" /b powershell.exe -Command \"<command>\""
```

The empty `""` is the window title; required when the command contains quotes.

## Write a .ps1 and run it from WSL

Problem: Inline PowerShell with heredocs and complex quoting fails from `terminal`.

```bash
write_file path="C:/Users/JRCPU/script.ps1" content="..."
# Then in WSL:
cmd.exe /c "powershell -ExecutionPolicy Bypass -File C:\\Users\\JRCPU\\script.ps1"
```

## Create Windows AtStartup task (non-interactive)

```powershell
$ErrorActionPreference='SilentlyContinue'
$TaskName="My Task"
$Action=New-ScheduledTaskAction -Execute 'wsl.exe' -Argument '-d Ubuntu -e bash -lc "do_something"'
$Principal=New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Highest
$Trigger=New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Force
```

## Verify from WSL without sudo

```bash
systemctl is-active hermes     # returns "active" or "inactive"
```

## Git in WSL with remote on Windows filesystem

Avoid: `/mnt/c/...` paths in large git repos — performance is terrible.
Prefer: keep repos in `/home/juan/` and access Windows files via `/mnt/c/` only for small scripts.
