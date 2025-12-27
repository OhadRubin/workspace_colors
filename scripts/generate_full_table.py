#!/usr/bin/env python3
"""Generate a single table with all colors sorted by contrast ratio."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DATA_DIR = Path(__file__).parent.parent / "data"
CLASSIFICATIONS_PATH = DATA_DIR / "classifications.json"
COLORS_DIR = DATA_DIR / "contrast_snapshots" / "colors"
OUTPUT_PATH = DATA_DIR / "contrast_full_table.png"


def get_status_color(status: str) -> tuple[int, int, int]:
    if status == "GOOD":
        return (0, 150, 0)
    elif status == "MID":
        return (200, 150, 0)
    else:
        return (200, 0, 0)


def main():
    data = json.loads(CLASSIFICATIONS_PATH.read_text())
    # Sort by contrast ratio
    data = sorted(data, key=lambda x: x["contrast"])

    # Load first image to get dimensions
    first_img_path = COLORS_DIR / f"{data[0]['name']}.png"
    first_img = Image.open(first_img_path)
    img_width, img_height = first_img.size

    # Layout
    label_width = 200
    padding = 2
    row_height = img_height

    total_width = label_width + img_width + padding * 3
    total_height = len(data) * row_height + padding * (len(data) + 1)

    # Create table
    table = Image.new("RGB", (total_width, total_height), (40, 40, 40))
    draw = ImageDraw.Draw(table)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 11)
    except Exception:
        font = ImageFont.load_default()

    for i, entry in enumerate(data):
        y = padding + i * (row_height + padding)

        # Load screenshot
        img_path = COLORS_DIR / f"{entry['name']}.png"
        if img_path.exists():
            img = Image.open(img_path)
            table.paste(img, (label_width + padding * 2, y))

        # Draw label
        status_color = get_status_color(entry["status"])
        label = f"{entry['status']:4} {entry['contrast']:4.2f} {entry['name'][:18]}"
        draw.text((padding, y + 4), label, fill=status_color, font=font)

    table.save(OUTPUT_PATH)
    print(f"Saved {len(data)} colors to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
