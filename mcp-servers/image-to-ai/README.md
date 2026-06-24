# MCP Image to AI Server

MCP server that exposes image-to-AI conversion tools for multimodal LLMs and ML pipelines.

## Tools

| Tool | Description |
|------|-------------|
| `image_to_base64` | Convert image to Base64 data URI (for GPT-4V, Claude, Gemini) |
| `image_to_tensor` | Convert image to NumPy/PyTorch tensor (for ML pipelines) |
| `image_to_text` | Extract text via Tesseract OCR |

## Usage

```bash
# Run the server
python -m mcp_servers.image_to_ai
```

## Dependencies

- `mcp>=1.0.0`
- `Pillow>=10.0.0`
- `numpy>=1.24.0`
- `pytesseract>=0.3.10` (for OCR)
- `torch>=2.0.0` (optional, for PyTorch tensors)
