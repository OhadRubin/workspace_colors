#!/usr/bin/env python3
"""
Textual app to pick VSCode color themes and apply them.
Uses colors from vscode-workspace-colors/src/colors.json.
"""

import colorsys
import json
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Static, Label
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from rich.text import Text


def hex_to_hsl(hex_color: str) -> tuple[float, float, float]:
    """Convert hex color to HSL (hue 0-360, sat 0-100, light 0-100)."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s * 100, l * 100


def hsl_to_hex(h: float, s: float, l: float) -> str:
    """Convert HSL (hue 0-360, sat 0-100, light 0-100) to hex color."""
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def generate_bright_version(hex_color: str, lightness_boost: float = 25) -> str:
    """Generate a brighter version of the given color."""
    h, s, l = hex_to_hsl(hex_color)
    new_l = min(100, l + lightness_boost)
    return hsl_to_hex(h, s, new_l)


def generate_color_customizations(base_color: str, bright_color: str) -> dict:
    """Generate VS Code settings dict."""
    return {
        "workbench.colorCustomizations": {
            "titleBar.activeBackground": base_color,
            "titleBar.inactiveBackground": bright_color,
            "titleBar.border": bright_color,
            "statusBar.background": bright_color,
            "statusBar.debuggingBackground": bright_color,
            "tab.activeBorder": bright_color,
        }
    }


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

    def __init__(self) -> None:
        super().__init__()
        self.base_path = Path(__file__).parent
        self.vscode_settings_path = self.base_path / ".vscode" / "settings.json"
        self.colors_by_category: dict[str, dict[str, str]] = {}
        self._load_themes()

    def _load_themes(self) -> None:
        """Load all color themes from vscode-workspace-colors/src/colors.json."""
        colors_path = self.base_path / "vscode-workspace-colors" / "src" / "colors.json"
        if not colors_path.exists():
            raise FileNotFoundError(f"colors.json not found at {colors_path}")

        with open(colors_path) as f:
            self.colors_by_category = json.load(f)

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
        bright_color = generate_bright_version(base_color)
        colors = generate_color_customizations(base_color, bright_color)
        self.vscode_settings_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.vscode_settings_path, "w") as f:
            json.dump(colors, f, indent=4)

    def _update_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)


if __name__ == "__main__":
    app = ColorPickerApp()
    app.run()
