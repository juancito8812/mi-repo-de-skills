# Hardware Matching for Local LLM Inference

How to profile a Windows/macOS/Linux machine and match it to appropriate quantized local LLMs via Ollama or llama.cpp.

## Hardware profiling commands

### Windows (PowerShell or git-bash)

```powershell
# CPU
wmic cpu get Name,NumberOfCores,NumberOfLogicalProcessors /format:list

# Total RAM (GB)
[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 1)

# GPU (discrete)
Get-CimInstance Win32_VideoController | Select Name, AdapterRAM, DriverVersion

# CPU flags (does this CPU support AVX-512?)
(Get-CimInstance Win32_Processor).SecondLevelAddressTranslationExtensions -match "AVX512" # indirect
# or in git-bash:
cat /proc/cpuinfo | grep flags | head -1
```

### macOS / Linux (terminal)

```bash
# CPU + cores
sysctl -n machdep.cpu.brand_string
sysctl -n hw.physicalcpu hw.logicalcpu

# RAM
sysctl -n hw.memsize    # macOS (bytes)
grep MemTotal /proc/meminfo   # Linux (kB)

# Free RAM usable for LLM (subtract OS overhead)
# rule of thumb: leave 4-6 GB for OS
```

## RAM tier rules (Ollama)

Ollama loads the entire model into RAM. Plan size = model file + KV cache + overhead.

| Tier | Usable RAM for model | Max recommended model class | Example Q4 sizes | Expected speed (CPU-only, modern i5/Ryzen) |
|------|---------------------|----------------------------|------------------|--------------------------------------------|
| 4 GB | ~2–3 GB | 1.7B–3B | 1.2–2.5 GB | 25–40 tok/s |
| 8 GB | ~4–5 GB | 3.8B–7B | 3–5.5 GB | 15–25 tok/s |
| 16 GB | ~10–12 GB | 7B–8B | 5.5–6 GB | 8–15 tok/s |
| 32 GB | ~22–26 GB | 14B–32B | 11–19 GB | 3–8 tok/s |
| 64 GB | ~52–58 GB | 70B–80B | 35–45 GB | varies |

> For CPU-only inference, avoid loading more than ~10 GB of model weight on a 16 GB system; anything larger forces swapping and kills throughput.

## Quantization tradeoffs

- **Q4_K_M** — standard default (~1% quality loss, 4-bit)
- **Q5_K_M** — slight quality boost (~0.5% better than Q4, ~20% larger)
- **Q3_K_M** — acceptable for chat, ~3% quality loss
- **Q2_K_M** — last resort, ~10% quality loss
- **Q8_0** — rarely worth it on CPU; 2× size for ~2% quality gain

## Per-hardware model tiers (June 2026)

### Tier A: 4 GB RAM
| Model | Ollama command | Notes |
|-------|----------------|-------|
| Qwen3 1.7B | `ollama run qwen3:1.7b` | Fastest, good reasoning for size |
| Phi-4-mini 3.8B | `ollama run phi4-mini` | Better code, slightly slower |

### Tier B: 8 GB RAM
| Model | Ollama command | Notes |
|-------|----------------|-------|
| Phi-4-mini 3.8B | `ollama run phi4-mini` | Sweet spot for coding |
| Qwen3 4B | `ollama run qwen3:4b` | Good all-rounder |
| Llama 3.2 3B | `ollama run llama3.2:3b` | Fast, lightweight |

### Tier C: 16 GB RAM
| Model | Ollama command | Notes |
|-------|----------------|-------|
| Qwen3 8B | `ollama run qwen3:8b` | Best coding/agentic, 8-12 tok/s |
| Llama 3.3 8B | `ollama run llama3.3:8b` | Best all-round balance |
| Mistral Small 3 7B | `ollama run mistral-small3` | Fastest of the 7B class |
| Qwen3 1.7B | `ollama run qwen3:1.7b` | Ultra-fast fallback for simple queries |

### Tier D: 32 GB RAM
| Model | Ollama command | Notes |
|-------|----------------|-------|
| Qwen3.6 35B A3B | `ollama run qwen3.6:35b-a3b` | Best agentic (MoE, ~22 GB at Q4) |
| Gemma 4 E4B 4B | `ollama run gemma4:e4b` | Multimodal, ~8 GB at Q4 |
| Phi-4 14B | `ollama run phi4:14b` | ~11 GB at Q5 |

### Tier E: 64 GB+
| Model | Notes |
|-------|-------|
| Llama 3.3 70B | ~40 GB at Q4 |
| Qwen3 72B | ~42 GB at Q4, top multilingual/code |

## CPU feature flags

Ollama/llama.cpp will auto-detect, but these can be set explicitly on Windows:

```powershell
$env:LLAMACPP_AVX512 = "1"
$env:OLLAMA_NUM_PARALLEL = "2"
$env:OLLAMA_CTX_SIZE = "1024"  # smaller context = faster
ollama run qwen3:8b
```

- **AVX-512**: ~20% speedup on supported CPUs (Skylake-X+ and many Xeons). Most consumer Intel CPUs (i5-6400 era) **do not** have AVX-512.
- **AVX2**: widely supported; llama.cpp uses it automatically.
- **OLLAMA_NUM_PARALLEL**: controls request parallelism; `1` on weak CPUs, `2` on medium.

## iGPU offload (integrated graphics)

Even Intel UHD/Iris Xe can act as an offload target via OpenVINO or Vulkan in llama.cpp builds that support it. Ollama limited GPU offload support; prefer:
- `OLLAMA_NUM_GPU=1` Ollama env var (experimental)
- Direct `llama-server --n-gpu-layers 10` for partial offload with a build that has OpenVINO/Vulkan enabled

For most Intel iGPU users, pure CPU inference is simpler and performs acceptably.

## Common Windows pitfalls

- **Ollama not starting after install**: add to user PATH, or launch from Start Menu. The daemon listens on `127.0.0.1:11434`.
- **Long install times on slow CPUs**: Windows Defender may scan every downloaded model blob. Exclude `C:\Users\<name>\.ollama` in Windows Security > Virus & threat protection > Manage settings > Exclusions.
- **Model path in Hermes config**: if using `provider: ollama-launch`, verify `base_url` is `http://127.0.0.1:11434/v1` and `default` matches an Ollama tag.

## Decision flow

1. Profile RAM → pick tier
2. Use Q4_K_M as starting point
3. If CPU flags support AVX-512, mention the env var for extra speed
4. Recommend 2 models: primary + fast fallback
5. If user wants agentic tool use (web search, code exec), prefer Qwen3 or Llama 3.3 8B over smaller 3B models
6. For basic chat/translation, 1.7B–3B is plenty and noticeably snappier
