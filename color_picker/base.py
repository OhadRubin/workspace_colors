#!/usr/bin/env python3
"""
Core color utilities and theme generation.
No TUI dependencies - can be used by CLI or TUI.
"""

import colorsys
import json
from pathlib import Path

# Cache for classifications data
_classifications_cache: dict[str, dict] | None = None


def _srgb_to_linear(u: float) -> float:
    """Convert sRGB component to linear RGB."""
    return u / 12.92 if u <= 0.03928 else ((u + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """Calculate relative luminance per WCAG 2.1."""
    hex_color = hex_color.lstrip('#')
    r, g, b = (int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))
    r_lin, g_lin, b_lin = _srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(color1: str, color2: str) -> float:
    """Calculate WCAG contrast ratio between two hex colors."""
    l1 = relative_luminance(color1)
    l2 = relative_luminance(color2)
    lighter, darker = (l1, l2) if l1 >= l2 else (l2, l1)
    return (lighter + 0.05) / (darker + 0.05)


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


def generate_bright_version(hex_color: str, lightness_boost: float | None = None) -> str:
    """Generate a brighter version of the given color.

    Uses adaptive lightness boost: more for dark colors, less for light colors.
    Caps at 75% lightness to maintain visibility against white text.
    """
    h, s, l = hex_to_hsl(hex_color)

    if lightness_boost is None:
        # Adaptive: dark colors get more boost, light colors less
        # Range roughly: 35 for l=0, 15 for l=60
        lightness_boost = max(15, 35 - l * 0.33)

    # Cap at 75% to avoid washing out (keeps contrast with text)
    new_l = min(75, l + lightness_boost)
    return hsl_to_hex(h, s, new_l)


def choose_foreground(bg_hex: str) -> str:
    """Choose black or white foreground based on background luminance."""
    lum = relative_luminance(bg_hex)
    # WCAG recommends 4.5:1 for normal text; we use luminance threshold
    # Dark bg (lum < 0.4) -> white text, Light bg -> black text
    return "#ffffff" if lum < 0.4 else "#000000"


def generate_color_customizations(base_color: str, bright_color: str) -> dict:
    """Generate VS Code settings dict with proper foreground colors."""
    # Choose foreground colors based on background luminance
    base_fg = choose_foreground(base_color)
    bright_fg = choose_foreground(bright_color)

    # Generate a darker version for activity bar (more muted)
    h, s, l = hex_to_hsl(base_color)
    activity_bar_bg = hsl_to_hex(h, s, max(10, l - 10))
    activity_bar_fg = choose_foreground(activity_bar_bg)

    return {
        "workbench.colorCustomizations": {
            # Title bar
            "titleBar.activeBackground": base_color,
            "titleBar.activeForeground": base_fg,
            "titleBar.inactiveBackground": bright_color,
            "titleBar.inactiveForeground": bright_fg,
            "titleBar.border": bright_color,
            # Status bar
            "statusBar.background": bright_color,
            "statusBar.foreground": bright_fg,
            "statusBar.debuggingBackground": bright_color,
            "statusBar.debuggingForeground": bright_fg,
            # Activity bar
            "activityBar.background": activity_bar_bg,
            "activityBar.foreground": activity_bar_fg,
            # Tabs
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


def get_classifications_path(base_path: Path | None = None) -> Path:
    """Get path to classifications.json."""
    if base_path is not None:
        return base_path / "data" / "classifications.json"
    # Check package-bundled first
    pkg_path = Path(__file__).parent / "classifications.json"
    if pkg_path.exists():
        return pkg_path
    # Fall back to repo layout
    return Path(__file__).parent.parent / "data" / "classifications.json"


def load_classifications(base_path: Path | None = None) -> dict[str, dict]:
    """Load classifications.json and return dict keyed by color name."""
    global _classifications_cache
    if _classifications_cache is not None:
        return _classifications_cache

    path = get_classifications_path(base_path)
    if not path.exists():
        return {}

    with open(path) as f:
        data = json.load(f)

    # Index by name for fast lookup
    _classifications_cache = {entry["name"]: entry for entry in data}
    return _classifications_cache


def get_color_status(name: str, base_path: Path | None = None) -> str:
    """Get contrast status (GOOD/MID/BAD) for a named color."""
    classifications = load_classifications(base_path)
    entry = classifications.get(name)
    if entry:
        return entry.get("status", "UNKNOWN")
    return "UNKNOWN"


def load_themes(base_path: Path | None = None) -> dict[str, dict[str, str]]:
    """Load all color themes from colors.json."""
    colors_path = get_colors_json_path(base_path)
    if not colors_path.exists():
        raise FileNotFoundError(f"colors.json not found at {colors_path}")
    with open(colors_path) as f:
        return json.load(f)


def load_themes_with_status(base_path: Path | None = None) -> dict[str, dict[str, dict]]:
    """Load themes with contrast status from classifications.json.

    Returns: {category: {name: {"hex": str, "status": str, "contrast": float}}}
    """
    themes = load_themes(base_path)
    classifications = load_classifications(base_path)

    result = {}
    for category, colors in themes.items():
        result[category] = {}
        for name, hex_color in colors.items():
            entry = classifications.get(name, {})
            result[category][name] = {
                "hex": hex_color,
                "status": entry.get("status", "UNKNOWN"),
                "contrast": entry.get("contrast", 0.0),
            }
    return result


def write_theme(base_color: str, workspace_path: Path) -> None:
    """Write theme to workspace's .vscode/settings.json."""
    bright_color = generate_bright_version(base_color)
    colors = generate_color_customizations(base_color, bright_color)
    settings_path = workspace_path / ".vscode" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump(colors, f, indent=4)
