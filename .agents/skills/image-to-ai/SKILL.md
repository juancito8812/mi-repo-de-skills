---
name: image-to-ai
description: Use when converting local images to AI-ready formats (Base64 for multimodal models, NumPy/PyTorch tensors for ML, or OCR text extraction). Supports PNG, JPEG, WebP, BMP, TIFF.
license: MIT
---

# Image to AI

Converts local image files into formats consumable by any AI model.

## When to Use

- Sending images to multimodal LLMs (GPT-4V, Claude, Gemini) → **base64**
- Feeding images to ML pipelines (PyTorch, TensorFlow, JAX) → **tensor**
- Extracting text from screenshots, documents, diagrams → **text** (OCR)
- Batch preprocessing images for training/inference

## Quick Reference

| Mode | Output | Use Case |
|------|--------|----------|
| `base64` | `data:image/png;base64,iVBORw0K...` | Multimodal LLM APIs |
| `tensor` | `np.ndarray` / `torch.Tensor` | ML training/inference |
| `text` | Extracted string | Document OCR, OCR, screenshots |

## Usage

```python
from image_to_ai import ImageToAI

converter = ImageToAI()

# Base64 for multimodal LLMs
b64 = converter.to_base64("./screenshot.png")
# Returns: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."

# Tensor for ML (NumPy array, shape HWC, uint8 [0-255])
arr = converter.to_tensor("./image.jpg")
# Returns: numpy.ndarray (H, W, C)

# Tensor for PyTorch (CHW, float32 [0-1])
tensor = converter.to_tensor("./image.jpg", framework="pytorch", normalize=True)
# Returns: torch.Tensor (C, H, W)

# OCR text extraction
text = converter.to_text("./document.png", lang="spa+eng")
# Returns: "Texto extraído de la imagen..."
```

## CLI Usage

```bash
# Base64 (default)
python -m image_to_ai ./image.png --mode base64

# Tensor (NumPy)
python -m image_to_ai ./image.png --mode tensor --framework numpy

# Tensor (PyTorch, normalized)
python -m image_to_ai ./image.png --mode tensor --framework pytorch --normalize

# OCR (Spanish + English)
python -m image_to_ai ./doc.png --mode text --lang spa+eng

# Save output to file
python -m image_to_ai ./image.png --mode base64 --output result.txt
```

## API Reference

### `ImageToAI()`

Initialize converter. Auto-detects available backends.

### `to_base64(image_path: str, mime_type: str = None) -> str`

Encode image as Base64 data URI.

- `image_path`: Path to local image file
- `mime_type`: Optional override (auto-detected from extension)
- Returns: Data URI string (`data:image/png;base64,...`)

**Errors:** `FileNotFoundError`, `ValueError` (unsupported format)

### `to_tensor(image_path: str, framework: str = "numpy", normalize: bool = False, dtype: str = None) -> np.ndarray | torch.Tensor`

Convert image to numerical tensor.

- `framework`: `"numpy"` (default), `"pytorch"`, `"torch"`
- `normalize`: If True, scale to `[0, 1]` float32; else `uint8 [0, 255]`
- `dtype`: Override dtype (`"float32"`, `"float16"`, `"uint8"`)
- Returns: NumPy array (H, W, C) or PyTorch tensor (C, H, W)

**Errors:** `FileNotFoundError`, `ImportError` (PyTorch not installed), `ValueError`

### `to_text(image_path: str, lang: str = "eng", config: str = "") -> str`

Extract text via Tesseract OCR.

- `lang`: Language code(s) - `"eng"`, `"spa"`, `"spa+eng"`, `"chi_sim"`, etc.
- `config`: Tesseract config string (e.g., `"--psm 6"` for single block)
- Returns: Extracted text string

**Errors:** `FileNotFoundError`, `RuntimeError` (Tesseract not installed)

## Requirements

```bash
pip install -r requirements.txt
```

**System dependency:** Tesseract OCR for `text` mode
- Ubuntu/Debian: `apt-get install tesseract-ocr tesseract-ocr-spa`
- macOS: `brew install tesseract tesseract-lang`
- Windows: [UB Mannheim installer](https://github.com/UB-Mannheim/tesseract/wiki)

## Supported Formats

PNG, JPEG, JPG, WebP, BMP, TIFF, GIF (first frame)

## Common Mistakes

| Issue | Fix |
|-------|-----|
| `FileNotFoundError` | Check path exists and is readable |
| `ImportError: torch` | Install PyTorch: `pip install torch` |
| `TesseractNotFoundError` | Install system Tesseract + add to PATH |
| Empty OCR result | Try `--psm` config, check image quality/contrast |
| Wrong tensor shape | `framework="numpy"` → HWC; `pytorch` → CHW |

## Implementation

Core logic in `image_to_ai.py`. Single class, ~150 lines, no external deps beyond requirements.