# Ollama + Hermes integration notes

- `ollama-windows-setup` skill covers portable Ollama install on Windows, auto-start via scheduled task, and pointing Hermes at the local API.
- Hermes config keys: set `model.provider = ollama-launch` and `model.base_url = http://127.0.0.1:11434/v1`.
- Hermes slash `/model qwen3:8b` works once the provider block is configured.
