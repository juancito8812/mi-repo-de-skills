#!/usr/bin/env python3
"""
Image to AI — Convert local images to AI-ready formats.

Modes:
  - base64: Data URI for multimodal LLMs (GPT-4V, Claude, Gemini)
  - tensor: NumPy array or PyTorch tensor for ML pipelines
  - text: OCR text extraction via Tesseract

Usage:
  python -m image_to_ai ./image.png --mode base64
  python -m image_to_ai ./image.png --mode tensor --framework pytorch --normalize
  python -m image_to_ai ./doc.png --mode text --lang spa+eng
"""
from __future__ import annotations
import argparse
import base64
import mimetypes
import sys
from pathlib import Path
from typing import Literal, Optional, Union

import numpy as np
from PIL import Image

# Optional imports
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class ImageToAI:
    """Convert images to AI-consumable formats."""

    SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif", ".gif"}

    def __init__(self):
        self._verify_tesseract()

    def _verify_tesseract(self) -> None:
        """Check if Tesseract is available for OCR mode."""
        if TESSERACT_AVAILABLE:
            try:
                pytesseract.get_tesseract_version()
            except Exception:
                # Tesseract binary not in PATH
                pass

    def _load_image(self, image_path: str) -> Image.Image:
        """Load and validate image file."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {image_path}")
        if path.suffix.lower() not in self.SUPPORTED_EXTS:
            raise ValueError(
                f"Unsupported format: {path.suffix}. Supported: {', '.join(self.SUPPORTED_EXTS)}"
            )

        img = Image.open(path)
        # Convert to RGB for consistency (handles RGBA, P, L, etc.)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        elif img.mode == "RGBA":
            # Composite on white background
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        return img

    def _get_mime_type(self, image_path: str) -> str:
        """Get MIME type from file extension."""
        mime, _ = mimetypes.guess_type(image_path)
        if mime:
            return mime
        ext = Path(image_path).suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
            ".tiff": "image/tiff",
            ".tif": "image/tiff",
            ".gif": "image/gif",
        }
        return mime_map.get(ext, "application/octet-stream")

    def to_base64(self, image_path: str, mime_type: Optional[str] = None) -> str:
        """
        Encode image as Base64 data URI.

        Args:
            image_path: Path to local image file
            mime_type: Optional MIME type override

        Returns:
            Data URI string (data:image/png;base64,...)
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        if path.suffix.lower() not in self.SUPPORTED_EXTS:
            raise ValueError(
                f"Unsupported format: {path.suffix}. Supported: {', '.join(self.SUPPORTED_EXTS)}"
            )

        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")

        mime = mime_type or self._get_mime_type(image_path)
        return f"data:{mime};base64,{encoded}"

    def to_tensor(
        self,
        image_path: str,
        framework: Literal["numpy", "pytorch", "torch"] = "numpy",
        normalize: bool = False,
        dtype: Optional[str] = None,
    ) -> Union[np.ndarray, "torch.Tensor"]:
        """
        Convert image to numerical tensor.

        Args:
            image_path: Path to local image file
            framework: "numpy" (HWC), "pytorch"/"torch" (CHW)
            normalize: If True, scale to [0, 1] float32; else uint8 [0, 255]
            dtype: Override dtype ("float32", "float16", "uint8")

        Returns:
            NumPy array (H, W, C) or PyTorch tensor (C, H, W)
        """
        img = self._load_image(image_path)
        arr = np.array(img, dtype=np.uint8)  # HWC, uint8 [0, 255]

        if framework in ("pytorch", "torch"):
            if not TORCH_AVAILABLE:
                raise ImportError("PyTorch not installed. Run: pip install torch")
            tensor = torch.from_numpy(arr).permute(2, 0, 1)  # CHW
            if normalize:
                tensor = tensor.to(torch.float32) / 255.0
            elif dtype:
                tensor = tensor.to(getattr(torch, dtype))
            return tensor

        # NumPy output
        if normalize:
            arr = arr.astype(np.float32) / 255.0
        elif dtype:
            arr = arr.astype(dtype)
        return arr

    def to_text(
        self,
        image_path: str,
        lang: str = "eng",
        config: str = "",
    ) -> str:
        """
        Extract text from image using Tesseract OCR.

        Args:
            image_path: Path to local image file
            lang: Language code(s) - "eng", "spa", "spa+eng", "chi_sim", etc.
            config: Tesseract config string (e.g., "--psm 6" for single block)

        Returns:
            Extracted text string
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError(
                "pytesseract not installed. Run: pip install pytesseract\n"
                "Also install Tesseract binary: https://github.com/UB-Mannheim/tesseract/wiki"
            )

        img = self._load_image(image_path)
        try:
            text = pytesseract.image_to_string(img, lang=lang, config=config)
            return text.strip()
        except pytesseract.TesseractNotFoundError:
            raise RuntimeError(
                "Tesseract binary not found. Install it:\n"
                "  Ubuntu: apt-get install tesseract-ocr tesseract-ocr-spa\n"
                "  macOS: brew install tesseract tesseract-lang\n"
                "  Windows: https://github.com/UB-Mannheim/tesseract/wiki"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Convert images to AI-ready formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m image_to_ai ./image.png --mode base64
  python -m image_to_ai ./image.png --mode tensor --framework pytorch --normalize
  python -m image_to_ai ./doc.png --mode text --lang spa+eng
  python -m image_to_ai ./image.png --mode base64 --output result.txt
        """,
    )
    parser.add_argument("image", help="Path to input image file")
    parser.add_argument(
        "--mode",
        choices=["base64", "tensor", "text"],
        default="base64",
        help="Output format (default: base64)",
    )
    parser.add_argument(
        "--framework",
        choices=["numpy", "pytorch", "torch"],
        default="numpy",
        help="Tensor framework (default: numpy)",
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Normalize tensor to [0, 1] float32",
    )
    parser.add_argument(
        "--dtype",
        choices=["float32", "float16", "uint8"],
        help="Override tensor dtype",
    )
    parser.add_argument(
        "--lang",
        default="eng",
        help="OCR language(s) (default: eng). Use 'spa+eng' for Spanish+English",
    )
    parser.add_argument(
        "--config",
        default="",
        help="Tesseract config (e.g., '--psm 6')",
    )
    parser.add_argument(
        "--output", "-o",
        help="Save output to file instead of stdout",
    )

    args = parser.parse_args()

    converter = ImageToAI()

    try:
        if args.mode == "base64":
            result = converter.to_base64(args.image)
        elif args.mode == "tensor":
            result = converter.to_tensor(
                args.image,
                framework=args.framework,
                normalize=args.normalize,
                dtype=args.dtype,
            )
            # For tensor output, print shape and dtype info
            if hasattr(result, "shape"):
                info = f"Shape: {result.shape}, Dtype: {result.dtype}"
                if hasattr(result, "device"):
                    info += f", Device: {result.device}"
                print(info, file=sys.stderr)
        elif args.mode == "text":
            result = converter.to_text(args.image, lang=args.lang, config=args.config)
        else:
            parser.error(f"Unknown mode: {args.mode}")

        if args.output:
            Path(args.output).write_text(str(result), encoding="utf-8")
            print(f"Saved to {args.output}", file=sys.stderr)
        else:
            print(result)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()