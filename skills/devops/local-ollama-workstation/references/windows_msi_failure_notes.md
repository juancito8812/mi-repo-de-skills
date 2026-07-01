# Windows MSI Failure Notes

## Symptom
`OllamaSetup.exe` exits with code 1620/1603. Verbose log shows:
- `MSI (s) ... Note: 1: 2203 2: ...`
- `MainEngineThread is returning 1620`

## Root cause
Windows Installer (`msiserver`) cannot open the package in the given security context. Typical triggers:
- Running MSI from a path owned by a different user context.
- Windows Installer service restrictions on this Windows SKU.
- Per-user install path containing spaces/non-ASCII.

## Fix
Do NOT retry the MSI. Use portable ZIP:
1. `Invoke-WebRequest -Uri https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip -OutFile $zip`
2. `Expand-Archive -Path $zip -DestinationPath "$env:USERPROFILE\AppData\Local\Ollama" -Force`
3. Run `ollama.exe serve` directly.

## Why this was captured
First session hit exact 2203/1620 while installing. The ZIP path worked without admin rights and without touching Windows Installer.
