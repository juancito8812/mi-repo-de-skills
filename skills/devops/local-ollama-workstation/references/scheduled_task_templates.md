# Windows Scheduled Task Templates

## Exact CLI patterns that worked

### Logon-trigger task (fires when user logs on interactively)

```
schtasks /create ...
  /tn "Ollama Auto Start"
  /tr "cmd.exe /c \"start_ollama.cmd\""
  /sc ONLOGON
  /ru "%USERDOMAIN%\%USERNAME%"
  /rl HIGHEST
  /f
```

### Startup-trigger task (fires when Windows boots, before logon)

```
schtasks /create ...
  /tn "Ollama Auto Start"
  /tr "cmd.exe /c \"start_ollama.cmd\""
  /sc ONSTART
  /ru "%USERDOMAIN%\%USERNAME%"
  /rl HIGHEST
  /f
```

If `S4U` is needed (service-type logon), use PowerShell:
```powershell
$action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c "start_ollama.cmd"'
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Seconds 0)
Register-ScheduledTask -TaskName 'Ollama Auto Start' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
```

## Pitfalls

- `schtasks` quoting is brittle from bash/MSYS; wrap in a `.cmd` or `.ps1` file instead.
- `AtStartup` + blank-password accounts fail with `S4U`. Either assign a password or switch to `OnLogon`.
