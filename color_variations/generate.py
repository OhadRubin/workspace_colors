#!/usr/bin/env python3
"""Generate VS Code color theme variations from base colors."""

import colorsys
import json
import os


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


def generate_settings(base_color: str, bright_color: str) -> dict:
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


def save_variation(output_dir: str, name: str, settings: dict) -> None:
    """Save settings to a JSON file."""
    path = os.path.join(output_dir, name)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "settings.json"), "w") as f:
        json.dump(settings, f, indent=4)
    print(f"Created: {path}/settings.json")


def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))

    # Base colors to generate variations from
    base_colors = {
        "green": "#008200",
        "blue": "#0055aa",
        "purple": "#6b2d8b",
        "red": "#aa2200",
        "orange": "#cc6600",
        "teal": "#008080",
        "pink": "#aa3366",
    }

    for name, base in base_colors.items():
        bright = generate_bright_version(base, lightness_boost=25)
        h, s, l = hex_to_hsl(base)
        print(f"{name}: base={base} (HSL: {h:.0f}, {s:.0f}%, {l:.0f}%) -> bright={bright}")

        settings = generate_settings(base, bright)
        save_variation(output_dir, name, settings)


if __name__ == "__main__":
    main()
