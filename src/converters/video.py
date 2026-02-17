"""Video file converter using ffmpeg-python."""

from pathlib import Path

import ffmpeg

from .base import BaseConverter


class VideoConverter(BaseConverter):
    """Converts video files between common formats via ffmpeg."""

    def convert(self, source: Path, target_format: str) -> Path:
        """Convert a video file to the target format.

        Args:
            source: Path to the source video.
            target_format: Target extension without dot (e.g. "mp4").

        Returns:
            Path to the converted video.

        Raises:
            ffmpeg.Error: If ffmpeg encounters an error during conversion.
        """
        output_path = self.get_output_path(source, target_format.lower())

        (
            ffmpeg
            .input(str(source))
            .output(str(output_path))
            .overwrite_output()
            .run(quiet=True)
        )

        return output_path
