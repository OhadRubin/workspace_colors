#!/usr/bin/env python3
"""
Textual app to pick VSCode color themes from color_variations/ and apply them.
"""

import json
import json5
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Static, Label
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from rich.text import Text


class ColorThemeItem(ListItem):
    """A list item representing a color theme."""

    def __init__(self, theme_name: str, theme_path: Path, theme_colors: dict) -> None:
        super().__init__()
        self.theme_name = theme_name
        self.theme_path = theme_path
        self.theme_colors = theme_colors
        # Extract primary colors for preview
        customizations = theme_colors.get("workbench.colorCustomizations", {})
        self.active_bg = customizations.get("titleBar.activeBackground", "#333333")
        self.inactive_bg = customizations.get("titleBar.inactiveBackground", "#555555")

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
        self.current_colors: dict = {}

    def update_preview(self, theme_name: str, colors: dict) -> None:
        self.current_colors = colors
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

    def __init__(self) -> None:
        super().__init__()
        self.base_path = Path(__file__).parent
        self.vscode_settings_path = self.base_path / ".vscode" / "settings.json"
        self.themes: dict[str, tuple[Path, dict]] = {}
        self._load_themes()

    def _load_themes(self) -> None:
        """Load all color themes from color_variations/."""
        variations_path = self.base_path / "color_variations"
        if not variations_path.exists():
            raise FileNotFoundError(f"color_variations directory not found at {variations_path}")

        for theme_dir in sorted(variations_path.iterdir()):
            if not theme_dir.is_dir():
                continue
            settings_file = theme_dir / "settings.json"
            if settings_file.exists():
                with open(settings_file) as f:
                    colors = json5.load(f)
                self.themes[theme_dir.name] = (settings_file, colors)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with ListView(id="theme-list"):
                for theme_name, (theme_path, colors) in self.themes.items():
                    yield ColorThemeItem(theme_name, theme_path, colors)
            with Vertical(id="preview-panel"):
                yield ColorPreview()
                yield Static("", id="status")
        yield Footer()

    def on_mount(self) -> None:
        """Focus the list and show first theme preview."""
        list_view = self.query_one("#theme-list", ListView)
        list_view.focus()
        if self.themes:
            first_theme = next(iter(self.themes.keys()))
            _, colors = self.themes[first_theme]
            self.query_one(ColorPreview).update_preview(first_theme, colors)
            self._update_status(f"Use ↑↓ to browse, Enter to apply")

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Update preview and apply theme live when navigating."""
        if event.item is None:
            return
        if isinstance(event.item, ColorThemeItem):
            theme_name = event.item.theme_name
            _, colors = self.themes[theme_name]
            self.query_one(ColorPreview).update_preview(theme_name, colors)
            # Apply immediately as user navigates
            self._write_theme(theme_name, colors)

    def action_apply_theme(self) -> None:
        """Apply the currently selected theme to .vscode/settings.json."""
        list_view = self.query_one("#theme-list", ListView)
        if list_view.highlighted_child is None:
            self._update_status("[red]No theme selected![/red]")
            return

        item = list_view.highlighted_child
        if not isinstance(item, ColorThemeItem):
            raise TypeError(f"Expected ColorThemeItem, got {type(item)}")

        theme_name = item.theme_name
        _, colors = self.themes[theme_name]
        self._write_theme(theme_name, colors)
        self._update_status(f"[green]Applied {theme_name.upper()} theme![/green]")

    def _write_theme(self, theme_name: str, colors: dict) -> None:
        """Write theme to .vscode/settings.json."""
        self.vscode_settings_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.vscode_settings_path, "w") as f:
            json.dump(colors, f, indent=4)

    def _update_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)


if __name__ == "__main__":
    app = ColorPickerApp()
    app.run()
