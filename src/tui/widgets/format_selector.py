"""Format selector widget — updates valid targets based on selected files."""

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Select

from ...registry import registry


class FormatSelector(Widget):
    """Dropdown that shows only valid target formats for the current source format."""

    DEFAULT_CSS = """
    FormatSelector {
        height: auto;
        padding: 0 1;
    }
    FormatSelector Label {
        margin-bottom: 1;
        color: $text-muted;
    }
    """

    source_format: reactive[str | None] = reactive(None)

    def compose(self) -> ComposeResult:
        yield Label("Convert to:")
        yield Select(
            options=[],
            prompt="Select source files first",
            id="format-select",
        )

    def watch_source_format(self, source_format: str | None) -> None:
        """React to source format changes and rebuild the options list.

        Args:
            source_format: New source format extension, or None.
        """
        select = self.query_one("#format-select", Select)

        if source_format is None:
            select.set_options([])
            select.prompt = "Select source files first"
            return

        targets = registry.get_valid_targets(source_format)

        if not targets:
            select.set_options([])
            select.prompt = f"No conversions available for .{source_format}"
            return

        options = [(f".{fmt.upper()}", fmt) for fmt in targets]
        select.set_options(options)
        select.prompt = "Choose target format"

    @property
    def selected_format(self) -> str | None:
        """Return the currently selected target format, or None."""
        select = self.query_one("#format-select", Select)
        value = select.value
        return value if value is not Select.BLANK else None
