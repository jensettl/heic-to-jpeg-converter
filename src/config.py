"""Application configuration and settings."""

from pathlib import Path
from dataclasses import dataclass


LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

APP_NAME = "File Converter"
APP_VERSION = "0.1.0"


@dataclass(frozen=True)
class AppConfig:
    """Global application configuration."""

    log_dir: Path = LOG_DIR
    app_name: str = APP_NAME
    app_version: str = APP_VERSION
