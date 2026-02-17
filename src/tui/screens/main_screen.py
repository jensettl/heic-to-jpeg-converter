"""Main screen: file selection and conversion setup."""

from pathlib import Path
from typing import Iterable

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    DirectoryTree,
    Select,
)
from textual.reactive import reactive

from ...registry import registry, MediaType
from ..widgets.format_selector import FormatSelector


class FilteredDirectoryTree(DirectoryTree):
    """DirectoryTree that hides hidden files and folders (dotfiles)."""

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """Exclude any path whose name starts with a dot.

        Args:
            paths: Candidate paths from the parent implementation.

        Returns:
            Filtered iterable with hidden paths removed.
        """
        return [p for p in paths if not p.name.startswith(".")]


class MainScreen(Screen):
    """File browser and conversion configuration screen."""

    BINDINGS = [
        ("ctrl+c", "app.quit", "Quit"),
    ]

    DEFAULT_CSS = """
    MainScreen {
        layout: vertical;
    }

    #browser-panel {
        width: 40%;
        border-right: solid $primary;
    }

    #right-panel {
        width: 60%;
        padding: 1 2;
    }

    #file-table {
        height: 1fr;
        margin-bottom: 1;
    }

    #status-label {
        color: $warning;
        margin-bottom: 1;
        height: auto;
    }

    #convert-btn {
        margin-top: 1;
        width: 100%;
    }
    """

    _selected_files: reactive[list[Path]] = reactive(list)
    _detected_media_type: reactive[MediaType | None] = reactive(None)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="browser-panel"):
                yield Label("📂 Browse Files", markup=True)
                yield FilteredDirectoryTree(
                    str(Path.home() / "Downloads"), id="dir-tree"
                )

            with Vertical(id="right-panel"):
                yield Label("Selected Files", id="files-label")
                yield DataTable(id="file-table")
                yield Label("", id="status-label")
                yield FormatSelector(id="format-selector")
                yield Button(
                    "Convert →",
                    variant="success",
                    id="convert-btn",
                    disabled=True,
                )
        yield Footer()

    def on_mount(self) -> None:
        """Set up the file table columns on mount."""
        table = self.query_one("#file-table", DataTable)
        table.add_columns("File", "Type", "Size")
        table.cursor_type = "row"

    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Stage the clicked file, replacing any existing selection.

        Args:
            event: FileSelected event carrying the path.
        """
        self._replace_selection(event.path)

    @on(Button.Pressed, "#convert-btn")
    def on_convert_pressed(self) -> None:
        """Validate selection and push the progress screen."""
        selector = self.query_one("#format-selector", FormatSelector)
        target_format = selector.selected_format

        if not target_format or not self._selected_files:
            return

        from .progress_screen import ProgressScreen
        self.app.push_screen(
            ProgressScreen(
                files=list(self._selected_files),
                target_format=target_format,
            )
        )

    def _replace_selection(self, path: Path) -> None:
        """Replace the current file selection with a new file.

        Clicking a file replaces the previous selection so only one
        media-type-consistent batch is ever staged at a time.

        Args:
            path: Path to the newly selected file.
        """
        extension = path.suffix.lstrip(".").lower()
        media_type = registry.get_media_type(extension)

        if media_type is None:
            self._set_status(f"Unsupported file type: .{extension}")
            return

        # If the new file is a different media type, clear the old selection
        if self._detected_media_type and media_type != self._detected_media_type:
            self._clear_selection()

        if path in self._selected_files:
            self._set_status(f"Already added: {path.name}")
            return

        self._detected_media_type = media_type
        self._selected_files = [*self._selected_files, path]

        table = self.query_one("#file-table", DataTable)
        size = self._format_size(path.stat().st_size)
        table.add_row(path.name, f".{extension}", size)

        self._refresh_state()
        self._set_status("")

    def _clear_selection(self) -> None:
        """Clear all staged files and reset state."""
        self._selected_files = []
        self._detected_media_type = None
        table = self.query_one("#file-table", DataTable)
        table.clear()

    def _refresh_state(self) -> None:
        """Update format selector and convert button based on current files."""
        selector = self.query_one("#format-selector", FormatSelector)
        convert_btn = self.query_one("#convert-btn", Button)

        if not self._selected_files:
            selector.source_format = None
            self._detected_media_type = None
            convert_btn.disabled = True
            return

        ext = self._selected_files[0].suffix.lstrip(".").lower()
        selector.source_format = ext

    @on(Select.Changed, "#format-select")
    def on_format_changed(self) -> None:
        """Enable convert button when both files and a format are selected."""
        selector = self.query_one("#format-selector", FormatSelector)
        convert_btn = self.query_one("#convert-btn", Button)
        convert_btn.disabled = (
            not self._selected_files or selector.selected_format is None
        )

    def _set_status(self, message: str) -> None:
        """Update the status label.

        Args:
            message: Status message to display.
        """
        self.query_one("#status-label", Label).update(message)

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size as a human-readable string."""
        for unit in ("B", "KB", "MB", "GB"):
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes //= 1024
        return f"{size_bytes:.1f} TB"
