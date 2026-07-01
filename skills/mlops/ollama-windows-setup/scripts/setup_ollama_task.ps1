# scripts/setup_ollama_task.ps1
# Creates / refreshes the 'Ollama Auto Start' Windows scheduled task.
# Run once after confirming ollama.exe is installed in $env:LOCALAPPDATA\Ollama\ollama.exe
param(
  [string]$TaskName = 'Ollama Auto Start',
  [string]$OllamaDir = Join-Path $env:LOCALAPPDATA 'Ollama',
  [string]$Launcher  = Join-Path $env:LOCALAPPDATA 'Ollama\start_ollama.cmd',
  [string]$User      = $env:USERNAME
)

$ErrorActionPreference='SilentlyContinue'

if (-not (Test-Path (Join-Path $OllamaDir 'ollama.exe'))) {
  Write-Error "ollama.exe missing in $OllamaDir"; exit 1
}
if (-not (Test-Path $Launcher)) {
  Write-Error "Missing launcher script: $Launcher"; exit 1
}

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) { Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false | Out-Null }

$action   = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument "/c `"$Launcher`""
$trigger  = New-ScheduledTaskTrigger -AtLogOn -User $User
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable:$false

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description 'Launch local Ollama serve at logon for offline/fallback AI after power recovery' -Force | Out-Null
Write-Host "Scheduled task '$TaskName' registered for user '$User'."
