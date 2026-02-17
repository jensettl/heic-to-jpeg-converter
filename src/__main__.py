"""Entry point for the file converter application."""

from .tui.app import FileConverterApp


def main() -> None:
    """Launch the File Converter TUI."""
    app = FileConverterApp()
    app.run()


if __name__ == "__main__":
    main()
