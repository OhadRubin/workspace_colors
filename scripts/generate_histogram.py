#!/usr/bin/env python3
"""Generate histogram of contrast ratios from classifications.json."""

import json
from pathlib import Path

import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).parent.parent / "data"
CLASSIFICATIONS_PATH = DATA_DIR / "classifications.json"
OUTPUT_PATH = DATA_DIR / "contrast_histogram.png"


def main():
    data = json.loads(CLASSIFICATIONS_PATH.read_text())
    contrasts = [d["contrast"] for d in data]

    plt.figure(figsize=(10, 6))
    plt.hist(contrasts, bins=30, edgecolor='black', alpha=0.7)
    plt.axvline(x=1.5, color='orange', linestyle='--', label='MID threshold (1.5)')
    plt.axvline(x=2.0, color='green', linestyle='--', label='GOOD threshold (2.0)')
    plt.xlabel('Contrast Ratio')
    plt.ylabel('Count')
    plt.title('Distribution of Color Contrast Ratios')
    plt.legend()
    plt.savefig(OUTPUT_PATH, dpi=150)
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
