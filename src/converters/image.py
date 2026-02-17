"""Image file converter using Pillow and pillow-heif."""

from pathlib import Path

from PIL import Image
from pillow_heif import register_heif_opener

from .base import BaseConverter

# Register HEIF/HEIC support with Pillow once at import time
register_heif_opener()

# Pillow save format identifiers keyed by extension
_PILLOW_FORMATS: dict[str, str] = {
    "jpg":  "JPEG",
    "jpeg": "JPEG",
    "png":  "PNG",
    "webp": "WEBP",
    "gif":  "GIF",
    "bmp":  "BMP",
    "tiff": "TIFF",
}


class ImageConverter(BaseConverter):
    """Converts image files between common formats."""

    def convert(self, source: Path, target_format: str) -> Path:
        """Convert an image file to the target format.

        Args:
            source: Path to the source image.
            target_format: Target extension without dot (e.g. "jpg").

        Returns:
            Path to the converted image.

        Raises:
            ValueError: If the target format is unsupported.
            OSError: If reading or writing fails.
        """
        fmt = target_format.lower()

        if fmt not in _PILLOW_FORMATS:
            raise ValueError(
                f"Unsupported target image format: '{target_format}'. "
                f"Supported: {sorted(_PILLOW_FORMATS)}"
            )

        output_path = self.get_output_path(source, fmt)
        pillow_format = _PILLOW_FORMATS[fmt]

        with Image.open(source) as img:
            # JPEG does not support an alpha channel — convert to RGB first
            if pillow_format == "JPEG" and img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")

            img.save(output_path, pillow_format)

        return output_path
