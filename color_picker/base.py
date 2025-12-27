#!/usr/bin/env python3
"""
Core color utilities and theme generation.
No TUI dependencies - can be used by CLI or TUI.
"""

import colorsys
import json
from pathlib import Path


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


def get_colors_json_path(base_path: Path | None = None) -> Path:
    """Get path to colors.json. Checks package dir first, then repo layout."""
    if base_path is not None:
        return base_path / "vscode-workspace-colors" / "src" / "colors.json"

    # Check package-bundled colors.json first
    pkg_colors = Path(__file__).parent / "colors.json"
    if pkg_colors.exists():
        return pkg_colors

    # Fall back to repo layout
    return Path(__file__).parent.parent / "vscode-workspace-colors" / "src" / "colors.json"


def load_themes(base_path: Path | None = None) -> dict[str, dict[str, str]]:
    """Load all color themes from colors.json."""
    colors_path = get_colors_json_path(base_path)
    if not colors_path.exists():
        raise FileNotFoundError(f"colors.json not found at {colors_path}")
    with open(colors_path) as f:
        return json.load(f)


def write_theme(base_color: str, workspace_path: Path) -> None:
    """Write theme to workspace's .vscode/settings.json."""
    bright_color = generate_bright_version(base_color)
    colors = generate_color_customizations(base_color, bright_color)
    settings_path = workspace_path / ".vscode" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump(colors, f, indent=4)
