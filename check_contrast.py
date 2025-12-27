#!/usr/bin/env python3
"""Check contrast of all themes by capturing screenshots."""

import tempfile
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import numpy as np

from color_picker.base import load_themes, write_theme
from capture_top import capture_region

BATCH_SIZE = 5
TABLE_PATH = Path("contrast_table.png")
SNAPSHOTS_DIR = Path("contrast_snapshots")


def get_dominant_color(img: Image.Image) -> tuple[int, int, int]:
    """Get the most common color (background)."""
    arr = np.array(img)
    pixels = arr.reshape(-1, 3)
    rounded = (pixels // 10) * 10
    unique, counts = np.unique(rounded, axis=0, return_counts=True)
    dominant = unique[counts.argmax()]
    return tuple(dominant)


TEXT_COLOR = (255, 255, 255)  # Fixed white text


def relative_luminance(r: int, g: int, b: int) -> float:
    """Calculate relative luminance per WCAG."""
    def channel(c: int) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(color1: tuple[int, int, int], color2: tuple[int, int, int]) -> float:
    """Calculate WCAG contrast ratio between two colors."""
    l1 = relative_luminance(*color1)
    l2 = relative_luminance(*color2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def get_status(ratio: float) -> str:
    """Get status label for contrast ratio."""
    if ratio >= 4.5:
        return "OK"
    elif ratio >= 3:
        return "LOW"
    else:
        return "BAD"


def get_status_color(status: str) -> tuple[int, int, int]:
    """Get color for status label."""
    if status == "OK":
        return (0, 150, 0)
    elif status == "LOW":
        return (200, 150, 0)
    else:
        return (200, 0, 0)


def build_table_image(results: list[dict], images: list[Image.Image]) -> Image.Image:
    """Build a table image with all results so far."""
    if not results:
        raise ValueError("No results to build table from")

    # Layout constants
    label_width = 180
    img_width = images[0].width if images else 275
    img_height = images[0].height if images else 24
    row_height = img_height
    padding = 4

    total_width = label_width + img_width + padding * 3
    total_height = len(results) * row_height + padding * (len(results) + 1)

    # Create table
    table = Image.new("RGB", (total_width, total_height), (40, 40, 40))
    draw = ImageDraw.Draw(table)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 12)
    except Exception:
        font = ImageFont.load_default()

    for i, (result, img) in enumerate(zip(results, images)):
        y = padding + i * (row_height + padding)

        # Status + name + ratio
        status = get_status(result["contrast"])
        status_color = get_status_color(status)
        label = f"{status:3} {result['contrast']:4.1f} {result['name'][:15]}"
        draw.text((padding, y + 4), label, fill=status_color, font=font)

        # Paste captured image
        table.paste(img, (label_width + padding * 2, y))

    return table


def check_all_themes(workspace: Path, delay: float = 0.5) -> list[dict]:
    """Check contrast for all themes."""
    themes = load_themes()
    results = []
    images = []

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        total = sum(len(colors) for colors in themes.values())
        count = 0

        for category, colors in themes.items():
            for name, hex_color in colors.items():
                count += 1

                # Apply theme
                write_theme(hex_color, workspace)
                time.sleep(delay)

                # Capture (using finetuned params from capture_top.py)
                capture_path = tmp_path / "capture.png"
                capture_region(
                    display=3,
                    top_percent=0,
                    bottom_percent=5,
                    left_percent=46,
                    right_percent=54,
                    output=str(capture_path),
                )

                # Load and keep image
                img = Image.open(capture_path).copy()
                images.append(img)

                # Analyze
                try:
                    bg = get_dominant_color(img)
                    ratio = contrast_ratio(bg, TEXT_COLOR)
                except Exception:
                    ratio = -1
                    bg = (0, 0, 0)

                result = {
                    "category": category,
                    "name": name,
                    "hex": hex_color,
                    "contrast": ratio,
                    "bg_rgb": bg,
                }
                results.append(result)

                status = get_status(ratio)
                print(f"[{count}/{total}] {status:4} {ratio:5.2f} {name:20} {hex_color}")

                # Update table every BATCH_SIZE
                if count % BATCH_SIZE == 0 or count == total:
                    # Both tables: only last 5
                    last_5_results = results[-BATCH_SIZE:]
                    last_5_images = images[-BATCH_SIZE:]
                    table = build_table_image(last_5_results, last_5_images)
                    table.save(TABLE_PATH)
                    # Intermediate snapshot
                    SNAPSHOTS_DIR.mkdir(exist_ok=True)
                    intermediate_path = SNAPSHOTS_DIR / f"table_{count:03d}.png"
                    table.save(intermediate_path)
                    print(f"  -> Updated {TABLE_PATH} + {intermediate_path}")

    return results


if __name__ == "__main__":
    import sys

    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    results = check_all_themes(workspace.resolve())

    # Summary
    print("\n--- SUMMARY ---")
    bad = [r for r in results if r["contrast"] < 3]
    low = [r for r in results if 3 <= r["contrast"] < 4.5]
    ok = [r for r in results if r["contrast"] >= 4.5]

    print(f"\nOK:  {len(ok)} themes")
    print(f"LOW: {len(low)} themes")
    print(f"BAD: {len(bad)} themes")

    if bad:
        print(f"\nBAD contrast (<3:1):")
        for r in sorted(bad, key=lambda x: x["contrast"]):
            print(f"  {r['contrast']:5.2f} {r['name']} ({r['hex']})")

    if low:
        print(f"\nLOW contrast (3-4.5:1):")
        for r in sorted(low, key=lambda x: x["contrast"]):
            print(f"  {r['contrast']:5.2f} {r['name']} ({r['hex']})")

    print(f"\nFinal table saved to {TABLE_PATH}")
