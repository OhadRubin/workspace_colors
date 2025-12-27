#!/usr/bin/env python3
"""Capture portion of a display."""

import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image


def capture_region(
    display: int = 3,
    top_percent: int = 0,
    bottom_percent: int = 10,
    left_percent: int = 0,
    right_percent: int = 100,
    output: str = "capture.png",
) -> None:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    # Capture full display
    subprocess.run(["screencapture", f"-D{display}", tmp_path], check=True)

    # Crop to region
    img = Image.open(tmp_path)
    left = int(img.width * left_percent / 100)
    right = int(img.width * right_percent / 100)
    top = int(img.height * top_percent / 100)
    bottom = int(img.height * bottom_percent / 100)

    cropped = img.crop((left, top, right, bottom))

    # Remove top 1/3
    final = cropped.crop((0, cropped.height // 3, cropped.width, cropped.height))
    final.save(output)

    Path(tmp_path).unlink()
    print(f"Captured region to {output} ({cropped.width}x{cropped.height})")


if __name__ == "__main__":
    # Example: capture just the tab bar area (middle 60% horizontally, top 5%)
    output = sys.argv[1] if len(sys.argv) > 1 else "capture.png"
    capture_region(
        display=3,
        top_percent=0,
        bottom_percent=5,
        left_percent=46,
        right_percent=54,
        output=output,
    )
