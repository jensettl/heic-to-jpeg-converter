"""Abstract base class for all converters."""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseConverter(ABC):
    """Abstract base class that all converters must implement."""

    @abstractmethod
    def convert(self, source: Path, target_format: str) -> Path:
        """Convert a file to the target format.

        Saves the output file in the same directory as the source.

        Args:
            source: Path to the source file.
            target_format: Target file extension without dot (e.g. "jpg").

        Returns:
            Path to the converted output file.

        Raises:
            ValueError: If the conversion is not supported.
            OSError: If reading or writing fails.
        """

    def get_output_path(self, source: Path, target_format: str) -> Path:
        """Build the output file path next to the source file.

        Args:
            source: Path to the source file.
            target_format: Target extension without dot.

        Returns:
            Output path in the same directory as source.
        """
        return source.with_suffix(f".{target_format.lower()}")
