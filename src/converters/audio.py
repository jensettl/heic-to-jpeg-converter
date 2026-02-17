"""Audio file converter using ffmpeg-python."""

from pathlib import Path

import ffmpeg

from .base import BaseConverter

_SUPPORTED_FORMATS: frozenset[str] = frozenset({
    "mp3", "wav", "flac", "aac", "ogg", "m4a",
})


class AudioConverter(BaseConverter):
    """Converts audio files between common formats via ffmpeg."""

    def convert(self, source: Path, target_format: str) -> Path:
        """Convert an audio file to the target format.

        Args:
            source: Path to the source audio file.
            target_format: Target extension without dot (e.g. "mp3").

        Returns:
            Path to the converted audio file.

        Raises:
            ValueError: If the target format is unsupported.
            ffmpeg.Error: If ffmpeg encounters an error during conversion.
        """
        fmt = target_format.lower()

        if fmt not in _SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported target audio format: '{target_format}'. "
                f"Supported: {sorted(_SUPPORTED_FORMATS)}"
            )

        output_path = self.get_output_path(source, fmt)

        (
            ffmpeg
            .input(str(source))
            .output(str(output_path))
            .overwrite_output()
            .run(quiet=True)
        )

        return output_path
