"""Main Textual application."""

from textual.app import App

from .screens.main_screen import MainScreen
from ..config import APP_NAME, APP_VERSION


class FileConverterApp(App):
    """Root Textual application for the file converter."""

    TITLE = f"{APP_NAME} v{APP_VERSION}"
    SUB_TITLE = "Local file conversion — no uploads"

    CSS = """
    Screen {
        background: $surface;
    }
    """

    def on_mount(self) -> None:
        """Push the main screen on startup."""
        self.push_screen(MainScreen())
