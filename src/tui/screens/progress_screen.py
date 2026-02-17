"""Progress screen: live conversion progress and keep/delete prompt."""

from pathlib import Path

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    Log,
    ProgressBar,
)

from ...registry import registry
from ...logger import ConversionLogger
from ...config import AppConfig


class ProgressScreen(Screen):
    """Shows live conversion progress and prompts for keep/delete per file."""

    BINDINGS = [("escape", "app.pop_screen", "Back")]

    DEFAULT_CSS = """
    ProgressScreen {
        layout: vertical;
        padding: 1 2;
    }

    #title-label {
        height: auto;
    }

    #progress-bar {
        height: auto;
        margin: 1 0;
    }

    #log-panel {
        height: 1fr;
        min-height: 10;
        border: solid $primary;
    }

    #prompt-panel {
        height: auto;
        border: solid $warning;
        padding: 1 2;
        margin-top: 1;
        display: none;
    }

    #prompt-panel.visible {
        display: block;
    }

    #prompt-label {
        height: auto;
        margin-bottom: 1;
    }

    Button {
        margin-right: 1;
    }
    """

    def __init__(self, files: list[Path], target_format: str) -> None:
        """Initialise the progress screen.

        Args:
            files: Files to convert.
            target_format: Target format extension without dot.
        """
        super().__init__()
        self._files = files
        self._target_format = target_format
        self._current_file: Path | None = None
        self._converted_output: Path | None = None
        self._stats = {"success": 0, "skipped": 0, "errors": 0}
        config = AppConfig()
        self._logger = ConversionLogger(config.log_dir)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Label(
            f"Converting {len(self._files)} file(s) "
            f"→ .{self._target_format.upper()}",
            id="title-label",
        )
        yield ProgressBar(total=len(self._files), id="progress-bar")
        yield Log(id="log-panel", auto_scroll=True)
        with Vertical(id="prompt-panel"):
            yield Label("", id="prompt-label")
            with Horizontal():
                yield Button("Keep original", variant="primary", id="keep-btn")
                yield Button("Delete original", variant="error", id="delete-btn")
        yield Footer()

    def on_mount(self) -> None:
        """Start conversion when the screen mounts."""
        self._run_conversions()

    @work(thread=True)
    def _run_conversions(self) -> None:
        """Convert all files in a background thread."""
        log = self.query_one("#log-panel", Log)
        progress = self.query_one("#progress-bar", ProgressBar)

        for file in self._files:
            self._current_file = file
            ext = file.suffix.lstrip(".").lower()

            try:
                route = registry.get_route(ext, self._target_format)
                converter = route.converter_class()

                if route.lossy:
                    self.app.call_from_thread(
                        log.write_line,
                        f"⚠  {file.name} — lossy conversion, quality may be reduced",
                    )

                output = converter.convert(file, self._target_format)
                self._converted_output = output
                self._stats["success"] += 1

                self.app.call_from_thread(
                    log.write_line,
                    f"✓  {file.name}  →  {output.name}",
                )

                self.app.call_from_thread(self._show_keep_prompt, file)
                self._wait_for_prompt()

            except Exception as exc:
                self._stats["errors"] += 1
                self._logger.log_error(file, exc)
                self.app.call_from_thread(
                    log.write_line,
                    f"✗  {file.name}  —  {exc}",
                )

            self.app.call_from_thread(progress.advance, 1)

        self._logger.log_summary(self._stats)
        self.app.call_from_thread(self._show_done)

    def _show_keep_prompt(self, file: Path) -> None:
        """Show the keep/delete prompt for a converted file.

        Args:
            file: The original source file.
        """
        self.query_one("#prompt-label", Label).update(
            f"Keep original file?  [bold]{file.name}[/bold]"
        )
        self.query_one("#prompt-panel").add_class("visible")

    def _wait_for_prompt(self) -> None:
        """Block the worker thread until the user dismisses the prompt."""
        import time
        prompt_panel = self.query_one("#prompt-panel")
        while "visible" in prompt_panel.classes:
            time.sleep(0.05)

    @on(Button.Pressed, "#keep-btn")
    def on_keep(self) -> None:
        """User chose to keep the original file."""
        if self._current_file and self._converted_output:
            self._logger.log_conversion(
                self._current_file, self._converted_output, original_kept=True
            )
        self._dismiss_prompt()

    @on(Button.Pressed, "#delete-btn")
    def on_delete(self) -> None:
        """User chose to delete the original file."""
        if self._current_file:
            try:
                self._current_file.unlink()
                self._logger.log_delete(self._current_file)
            except OSError as exc:
                self._logger.log_error(self._current_file, exc)

        if self._current_file and self._converted_output:
            self._logger.log_conversion(
                self._current_file, self._converted_output, original_kept=False
            )
        self._dismiss_prompt()

    def _dismiss_prompt(self) -> None:
        """Hide the keep/delete prompt to unblock the worker thread."""
        self.query_one("#prompt-panel").remove_class("visible")

    def _show_done(self) -> None:
        """Update the UI when all conversions are complete."""
        log = self.query_one("#log-panel", Log)
        log.write_line("")
        log.write_line(
            f"Done — ✓ {self._stats['success']} converted  "
            f"✗ {self._stats['errors']} errors"
        )
        log.write_line(f"Log saved to: {self._logger.get_log_path()}")
