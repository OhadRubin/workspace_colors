#!/usr/bin/env python3
"""Check contrast of all themes by capturing screenshots."""

import json
import tempfile
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from color_picker.base import load_themes, write_theme
from .capture_top import capture_region
from .contrast_rows import estimate_bg_and_text, contrast_ratio

BATCH_SIZE = 5
DATA_DIR = Path(__file__).parent.parent / "data"
TABLE_PATH = DATA_DIR / "contrast_table.png"
SNAPSHOTS_DIR = DATA_DIR / "contrast_snapshots"
CLASSIFICATIONS_PATH = DATA_DIR / "classifications.json"


def get_status(ratio: float) -> str:
    """Get status label for contrast ratio."""
    if ratio >= 2.0:
        return "GOOD"
    elif ratio >= 1.5:
        return "MID"
    else:
        return "BAD"


def get_status_color(status: str) -> tuple[int, int, int]:
    """Get color for status label."""
    if status == "GOOD":
        return (0, 150, 0)
    elif status == "MID":
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


def check_all_themes(workspace: Path, delay: float = 0.2) -> list[dict]:
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

                # Save raw screenshot (no labels)
                colors_dir = SNAPSHOTS_DIR / "colors"
                colors_dir.mkdir(parents=True, exist_ok=True)
                img.save(colors_dir / f"{name}.png")

                # Extract bg/text colors from the captured bar (preserve alpha if present)
                img_arr = np.array(img, dtype=np.uint8)
                bg, text = estimate_bg_and_text(img_arr)
                ratio = contrast_ratio(bg, text)

                status = get_status(ratio)
                result = {
                    "category": category,
                    "name": name,
                    "hex": hex_color,
                    "contrast": float(ratio),
                    "status": status,
                    "bg_rgb": [int(x) for x in bg],
                    "text_rgb": [int(x) for x in text],
                }
                results.append(result)

                print(f"[{count}/{total}] {status:4} {ratio:5.2f} {name:20} {hex_color}")

                # Update every BATCH_SIZE
                if count % BATCH_SIZE == 0 or count == total:
                    # Save classifications
                    with open(CLASSIFICATIONS_PATH, "w") as f:
                        json.dump(results, f, indent=2)
                    # Save progress table
                    last_5_results = results[-BATCH_SIZE:]
                    last_5_images = images[-BATCH_SIZE:]
                    table = build_table_image(last_5_results, last_5_images)
                    table.save(TABLE_PATH)
                    # Save batch table
                    tables_dir = SNAPSHOTS_DIR / "tables"
                    tables_dir.mkdir(parents=True, exist_ok=True)
                    table.save(tables_dir / f"table_{count:03d}.png")
                    print(f"  -> Updated {TABLE_PATH}")

    return results


if __name__ == "__main__":
    import sys

    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    results = check_all_themes(workspace.resolve())

    # Summary
    print("\n--- SUMMARY ---")
    bad = [r for r in results if r["status"] == "BAD"]
    mid = [r for r in results if r["status"] == "MID"]
    good = [r for r in results if r["status"] == "GOOD"]

    print(f"\nGOOD (>=2.0): {len(good)} themes")
    print(f"MID (1.5-2.0): {len(mid)} themes")
    print(f"BAD (<1.5): {len(bad)} themes")

    if bad:
        print(f"\nBAD contrast (<1.5):")
        for r in sorted(bad, key=lambda x: x["contrast"]):
            print(f"  {r['contrast']:5.2f} {r['name']} ({r['hex']})")

    print(f"\nSaved to {CLASSIFICATIONS_PATH}")
    print(f"Final table saved to {TABLE_PATH}")
