"""Logging system for conversion operations."""

import logging
from pathlib import Path
from datetime import datetime
from enum import Enum


class ConversionStatus(Enum):
    """Status of a conversion operation."""
    SUCCESS = "SUCCESS"
    SKIPPED = "SKIPPED"
    DELETED = "DELETED"
    ERROR   = "ERROR"


class ConversionLogger:
    """Logger for file conversion operations."""

    def __init__(self, log_dir: Path):
        """Initialize logger.

        Args:
            log_dir: Directory to store log files.
        """
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = log_dir / f"converter_{timestamp}.log"

        self.logger = logging.getLogger("file_converter")
        self.logger.setLevel(logging.INFO)

        # Avoid duplicate handlers across sessions
        self.logger.handlers.clear()

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self._log_session_start()

    def _log_session_start(self) -> None:
        self.logger.info("=" * 80)
        self.logger.info("File Conversion Session Started")
        self.logger.info("=" * 80)

    def log_conversion(
        self,
        source: Path,
        destination: Path,
        original_kept: bool,
    ) -> None:
        """Log a successful conversion.

        Args:
            source: Source file path.
            destination: Output file path.
            original_kept: Whether the source file was kept.
        """
        self.logger.info(
            f"{ConversionStatus.SUCCESS.value} | "
            f"{source.name} -> {destination.name} | "
            f"original {'kept' if original_kept else 'deleted'}"
        )

    def log_skip(self, source: Path, reason: str) -> None:
        """Log a skipped file.

        Args:
            source: File that was skipped.
            reason: Reason for skipping.
        """
        self.logger.info(
            f"{ConversionStatus.SKIPPED.value} | {source.name} | {reason}"
        )

    def log_delete(self, source: Path) -> None:
        """Log deletion of original file.

        Args:
            source: File that was deleted.
        """
        self.logger.warning(
            f"{ConversionStatus.DELETED.value} | {source.name}"
        )

    def log_error(self, source: Path, error: Exception) -> None:
        """Log a conversion error.

        Args:
            source: File that caused the error.
            error: Exception that occurred.
        """
        self.logger.error(
            f"{ConversionStatus.ERROR.value} | "
            f"{source.name} | {type(error).__name__}: {error}"
        )

    def log_summary(self, stats: dict) -> None:
        """Log session summary.

        Args:
            stats: Dictionary with operation statistics.
        """
        self.logger.info("=" * 80)
        self.logger.info("Session Summary:")
        for key, value in stats.items():
            self.logger.info(f"  {key.capitalize()}: {value}")
        self.logger.info("=" * 80)

    def get_log_path(self) -> Path:
        """Return path to the current log file."""
        return self.log_file
