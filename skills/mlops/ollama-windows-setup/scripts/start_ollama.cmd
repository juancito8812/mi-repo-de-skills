@echo off
set OLLAMA_HOST=127.0.0.1
set OLLAMA_PORT=11434
start "" /min "%LOCALAPPDATA%\Ollama\ollama.exe" serve
