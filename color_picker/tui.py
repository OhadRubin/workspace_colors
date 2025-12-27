"""Textual TUI for color picker."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Static, Label
from textual.containers import Horizontal, Vertical

from .base import (
    generate_bright_version,
    generate_color_customizations,
    load_themes,
    write_theme,
)

class ColorThemeItem(ListItem):
    """A list item representing a color theme."""

    def __init__(self, theme_name: str, base_color: str) -> None:
        super().__init__()
        self.theme_name = theme_name
        self.base_color = base_color
        self.bright_color = generate_bright_version(base_color)
        self.active_bg = base_color
        self.inactive_bg = self.bright_color

    def compose(self) -> ComposeResult:
        with Horizontal(classes="theme-row"):
            # Color preview boxes
            yield Static(" ", classes="color-box", id=f"box1-{self.theme_name}")
            yield Static(" ", classes="color-box", id=f"box2-{self.theme_name}")
            # Theme name
            yield Label(f"  {self.theme_name.upper()}", classes="theme-label")

    def on_mount(self) -> None:
        """Apply colors after mounting."""
        box1 = self.query_one(f"#box1-{self.theme_name}")
        box2 = self.query_one(f"#box2-{self.theme_name}")
        box1.styles.background = self.active_bg
        box2.styles.background = self.inactive_bg


class ColorPreview(Static):
    """Shows a preview of the currently selected/hovered theme."""

    def __init__(self) -> None:
        super().__init__()
        self.current_base_color: str = ""

    def update_preview(self, theme_name: str, base_color: str) -> None:
        self.current_base_color = base_color
        bright_color = generate_bright_version(base_color)
        colors = generate_color_customizations(base_color, bright_color)
        customizations = colors.get("workbench.colorCustomizations", {})

        lines = [f"[bold]{theme_name.upper()}[/bold]\n"]
        for key, value in customizations.items():
            short_key = key.split(".")[-1]
            lines.append(f"  [{value}]██[/] {short_key}: {value}")

        self.update("\n".join(lines))


class ColorPickerApp(App):
    """Pick and apply VSCode color themes."""

    CSS = """
    Screen {
        layout: horizontal;
    }

    #theme-list {
        width: 40%;
        border: solid green;
        height: 100%;
    }

    #preview-panel {
        width: 60%;
        border: solid blue;
        padding: 1 2;
    }

    .theme-row {
        height: 3;
        padding: 0 1;
    }

    .color-box {
        width: 4;
        height: 1;
        margin: 0 1 0 0;
    }

    .theme-label {
        width: 1fr;
    }

    #status {
        dock: bottom;
        height: 3;
        background: $surface;
        padding: 1;
        border-top: solid $primary;
    }

    ListView > ListItem.--highlight {
        background: $accent 30%;
    }

    ListView > ListItem:focus {
        background: $accent 50%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("enter", "apply_theme", "Apply Theme"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(self, workspace_path: Path | None = None) -> None:
        super().__init__()
        # Default to package parent dir (the repo root)
        self.workspace_path = workspace_path or Path(__file__).parent.parent
        self.colors_by_category = load_themes(self.workspace_path)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with ListView(id="theme-list"):
                for category, colors in self.colors_by_category.items():
                    for theme_name, base_color in colors.items():
                        yield ColorThemeItem(theme_name, base_color)
            with Vertical(id="preview-panel"):
                yield ColorPreview()
                yield Static("", id="status")
        yield Footer()

    def on_mount(self) -> None:
        """Focus the list and show first theme preview."""
        list_view = self.query_one("#theme-list", ListView)
        list_view.focus()
        if self.colors_by_category:
            first_category = next(iter(self.colors_by_category.values()))
            first_name, first_color = next(iter(first_category.items()))
            self.query_one(ColorPreview).update_preview(first_name, first_color)
            self._update_status("Use ↑↓ to browse, Enter to apply")

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Update preview and apply theme live when navigating."""
        if event.item is None:
            return
        if isinstance(event.item, ColorThemeItem):
            item = event.item
            self.query_one(ColorPreview).update_preview(item.theme_name, item.base_color)
            # Apply immediately as user navigates
            self._write_theme(item.base_color)

    def action_apply_theme(self) -> None:
        """Apply the currently selected theme to .vscode/settings.json."""
        list_view = self.query_one("#theme-list", ListView)
        if list_view.highlighted_child is None:
            self._update_status("[red]No theme selected![/red]")
            return

        item = list_view.highlighted_child
        if not isinstance(item, ColorThemeItem):
            raise TypeError(f"Expected ColorThemeItem, got {type(item)}")

        self._write_theme(item.base_color)
        self._update_status(f"[green]Applied {item.theme_name.upper()} theme![/green]")

    def _write_theme(self, base_color: str) -> None:
        """Write theme to .vscode/settings.json."""
        write_theme(base_color, self.workspace_path)

    def _update_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)


