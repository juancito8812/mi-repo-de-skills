"""Tests for ImageToAI converter class."""
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image

# Add the skill path to import the converter
skill_path = Path(__file__).parent.parent.parent / ".agents" / "skills" / "image-to-ai"
sys.path.insert(0, str(skill_path))
from image_to_ai import ImageToAI


class TestImageToAI(unittest.TestCase):
    """Test suite for ImageToAI converter."""

    @classmethod
    def setUpClass(cls):
        """Create a temporary test image once for all tests."""
        cls.temp_dir = tempfile.mkdtemp()
        # Create a small RGBA test image
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        cls.png_path = os.path.join(cls.temp_dir, "test.png")
        img.save(cls.png_path)

        # Create a JPEG test image
        img_rgb = Image.new("RGB", (100, 100), (0, 255, 0))
        cls.jpg_path = os.path.join(cls.temp_dir, "test.jpg")
        img_rgb.save(cls.jpg_path)

        # Create a WebP test image
        cls.webp_path = os.path.join(cls.temp_dir, "test.webp")
        img_rgb.save(cls.webp_path, format="WEBP")

        # Create a BMP test image
        cls.bmp_path = os.path.join(cls.temp_dir, "test.bmp")
        img_rgb.save(cls.bmp_path, format="BMP")

        # Non-image file
        cls.txt_path = os.path.join(cls.temp_dir, "test.txt")
        with open(cls.txt_path, "w") as f:
            f.write("not an image")

    @classmethod
    def tearDownClass(cls):
        """Clean up temp files."""
        for f in [cls.png_path, cls.jpg_path, cls.webp_path, cls.bmp_path, cls.txt_path]:
            if os.path.exists(f):
                os.remove(f)
        os.rmdir(cls.temp_dir)

    def setUp(self):
        """Create a fresh converter for each test."""
        self.converter = ImageToAI()

    # --- Constructor tests ---

    def test_init_success(self):
        """Converter initializes without error."""
        self.assertIsInstance(self.converter, ImageToAI)

    # --- _get_mime_type tests ---

    def test_get_mime_type_png(self):
        """PNG file returns correct MIME type."""
        mime = self.converter._get_mime_type("image.png")
        self.assertEqual(mime, "image/png")

    def test_get_mime_type_jpg(self):
        """JPG file returns correct MIME type."""
        mime = self.converter._get_mime_type("photo.jpg")
        self.assertEqual(mime, "image/jpeg")

    def test_get_mime_type_jpeg(self):
        """JPEG file returns correct MIME type."""
        mime = self.converter._get_mime_type("photo.jpeg")
        self.assertEqual(mime, "image/jpeg")

    def test_get_mime_type_webp(self):
        """WebP file returns correct MIME type."""
        mime = self.converter._get_mime_type("image.webp")
        self.assertEqual(mime, "image/webp")

    def test_get_mime_type_bmp(self):
        """BMP file returns correct MIME type."""
        mime = self.converter._get_mime_type("image.bmp")
        self.assertEqual(mime, "image/bmp")

    def test_get_mime_type_tiff(self):
        """TIFF file returns correct MIME type."""
        mime = self.converter._get_mime_type("image.tiff")
        self.assertEqual(mime, "image/tiff")

    def test_get_mime_type_unknown(self):
        """Unknown extension returns octet-stream."""
        mime = self.converter._get_mime_type("image.xyz")
        self.assertEqual(mime, "application/octet-stream")

    # --- _load_image tests ---

    def test_load_image_file_not_found(self):
        """Loading non-existent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.converter._load_image("/nonexistent/path.png")

    def test_load_image_unsupported_format(self):
        """Loading unsupported format raises ValueError."""
        with self.assertRaises(ValueError):
            self.converter._load_image(self.txt_path)

    def test_load_image_png(self):
        """Loading a valid PNG returns an Image object."""
        img = self.converter._load_image(self.png_path)
        # RGBA should be composited onto white → RGB
        self.assertIn(img.mode, ("RGB", "RGBA"))
        self.assertEqual(img.size, (100, 100))

    def test_load_image_converts_grayscale(self):
        """Grayscale image is converted to RGB."""
        gray = Image.new("L", (50, 50), 128)
        gray_path = os.path.join(self.temp_dir, "gray.png")
        gray.save(gray_path)
        try:
            img = self.converter._load_image(gray_path)
            self.assertEqual(img.mode, "RGB")
        finally:
            if os.path.exists(gray_path):
                os.remove(gray_path)

    # --- to_base64 tests ---

    def test_to_base64_file_not_found(self):
        """to_base64 with non-existent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.converter.to_base64("/nonexistent/path.png")

    def test_to_base64_unsupported_format(self):
        """to_base64 with unsupported format raises ValueError."""
        with self.assertRaises(ValueError):
            self.converter.to_base64(self.txt_path)

    def test_to_base64_png(self):
        """to_base64 returns a valid data URI for PNG."""
        result = self.converter.to_base64(self.png_path)
        self.assertTrue(result.startswith("data:image/png;base64,"))
        # Base64 encoded content should be non-empty
        encoded = result.split(",")[1]
        self.assertTrue(len(encoded) > 0)

    def test_to_base64_jpg(self):
        """to_base64 returns a valid data URI for JPEG."""
        result = self.converter.to_base64(self.jpg_path)
        self.assertTrue(result.startswith("data:image/jpeg;base64,"))

    def test_to_base64_webp(self):
        """to_base64 returns a valid data URI for WebP."""
        result = self.converter.to_base64(self.webp_path)
        self.assertTrue(result.startswith("data:image/webp;base64,"))

    def test_to_base64_bmp(self):
        """to_base64 returns a valid data URI for BMP."""
        result = self.converter.to_base64(self.bmp_path)
        self.assertTrue(result.startswith("data:image/bmp;base64,"))

    def test_to_base64_with_mime_override(self):
        """to_base64 respects explicit MIME type override."""
        result = self.converter.to_base64(self.png_path, mime_type="image/webp")
        self.assertTrue(result.startswith("data:image/webp;base64,"))

    # --- to_tensor tests ---

    def test_to_tensor_numpy_default(self):
        """to_tensor returns numpy uint8 array by default."""
        result = self.converter.to_tensor(self.png_path)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.dtype, np.uint8)
        # RGB image → shape (H, W, 3)
        self.assertEqual(len(result.shape), 3)
        self.assertEqual(result.shape[2], 3)

    def test_to_tensor_numpy_normalized(self):
        """to_tensor with normalize=True returns float32 [0, 1]."""
        result = self.converter.to_tensor(self.png_path, normalize=True)
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.dtype, np.float32)
        self.assertGreaterEqual(result.min(), 0.0)
        self.assertLessEqual(result.max(), 1.0)

    def test_to_tensor_numpy_dtype_override(self):
        """to_tensor respects explicit dtype for numpy."""
        result = self.converter.to_tensor(self.png_path, dtype="float16")
        self.assertEqual(result.dtype, np.float16)

    def test_to_tensor_file_not_found(self):
        """to_tensor with non-existent file raises error."""
        with self.assertRaises(FileNotFoundError):
            self.converter.to_tensor("/nonexistent/path.png")

    # --- to_text tests (requires Tesseract) ---

    def test_to_text_file_not_found(self):
        """to_text with non-existent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.converter.to_text("/nonexistent/path.png")


if __name__ == "__main__":
    unittest.main()
