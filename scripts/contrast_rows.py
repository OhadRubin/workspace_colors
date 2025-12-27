#!/usr/bin/env python3
"""
contrast_rows.py

usage:
  python contrast_rows.py path/to/image.png

deps:
  pillow, numpy
(optional faster cc labeling: scipy)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from PIL import Image


@dataclass
class Box:
    x0: int
    y0: int
    x1: int
    y1: int

    @property
    def w(self) -> int:
        return self.x1 - self.x0

    @property
    def h(self) -> int:
        return self.y1 - self.y0

    @property
    def area(self) -> int:
        return self.w * self.h


def srgb_to_linear(u: np.ndarray) -> np.ndarray:
    # u in [0,1]
    return np.where(u <= 0.03928, u / 12.92, ((u + 0.055) / 1.055) ** 2.4)


def relative_luminance(rgb255: np.ndarray) -> float:
    # rgb255 shape (3,) in [0,255]
    rgb = np.clip(rgb255 / 255.0, 0.0, 1.0)
    lin = srgb_to_linear(rgb)
    return float(0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2])


def contrast_ratio(rgb_a: np.ndarray, rgb_b: np.ndarray) -> float:
    la = relative_luminance(rgb_a)
    lb = relative_luminance(rgb_b)
    hi, lo = (la, lb) if la >= lb else (lb, la)
    return (hi + 0.05) / (lo + 0.05)


def _label_components(mask: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    returns (labels, nlabels), labels in 0..nlabels (0 = background)
    tries scipy first; falls back to a pure-numpy flood fill.
    """
    try:
        from scipy.ndimage import label  # type: ignore

        labels, n = label(mask.astype(np.uint8))
        return labels.astype(np.int32), int(n)
    except Exception:
        pass

    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int32)
    cur = 0

    # 4-neighborhood flood fill
    for y in range(h):
        for x in range(w):
            if not mask[y, x] or labels[y, x] != 0:
                continue
            cur += 1
            stack = [(y, x)]
            labels[y, x] = cur
            while stack:
                cy, cx = stack.pop()
                for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and labels[ny, nx] == 0:
                        labels[ny, nx] = cur
                        stack.append((ny, nx))

    return labels, cur


def find_bar_boxes(img_rgb: np.ndarray) -> List[Box]:
    """
    assumes dark outer background; bars are the big bright-ish connected components.
    """
    # luminance proxy
    y = (0.2126 * img_rgb[..., 0] + 0.7152 * img_rgb[..., 1] + 0.0722 * img_rgb[..., 2]).astype(np.float32)

    # mask out dark background; tune threshold if needed
    mask = y > 55.0

    labels, n = _label_components(mask)

    boxes: List[Box] = []
    for k in range(1, n + 1):
        ys, xs = np.where(labels == k)
        if ys.size == 0:
            continue
        x0, x1 = int(xs.min()), int(xs.max()) + 1
        y0, y1 = int(ys.min()), int(ys.max()) + 1
        b = Box(x0, y0, x1, y1)

        # filters to keep wide bars and drop small bits
        if b.area < 2000:
            continue
        if b.w / max(1, b.h) < 2.5:
            continue
        if b.h < 15:
            continue

        boxes.append(b)

    # sort top to bottom
    boxes.sort(key=lambda bb: bb.y0)
    return boxes


def estimate_bg_and_text(row_rgba: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    bg: median rgb from border pixels
    text: median rgb from inner pixels far from bg color (in rgb distance)

    Accepts RGB (H,W,3) or RGBA (H,W,4) input.
    """
    h, w, c = row_rgba.shape

    # Clip top/bottom edges (removes window border artifacts)
    clip_v = max(1, int(0.10 * h))
    row_rgba = row_rgba[clip_v:-clip_v, :, :]
    h = row_rgba.shape[0]

    # Handle both RGB and RGBA - just extract RGB for now
    if c == 4:
        row_rgb = row_rgba[:, :, :3]
    elif c == 3:
        row_rgb = row_rgba
    else:
        raise ValueError(f"Expected 3 or 4 channels, got {c}")

    # border sampling for bg
    bt = max(1, int(0.12 * h))
    bl = max(1, int(0.06 * w))
    border = np.concatenate(
        [
            row_rgb[:bt, :, :].reshape(-1, 3),
            row_rgb[-bt:, :, :].reshape(-1, 3),
            row_rgb[:, :bl, :].reshape(-1, 3),
            row_rgb[:, -bl:, :].reshape(-1, 3),
        ],
        axis=0,
    )
    bg = np.median(border.astype(np.float32), axis=0)

    # inner region for text detection
    iy0, iy1 = bt, h - bt
    ix0, ix1 = bl, w - bl
    inner = row_rgb[iy0:iy1, ix0:ix1, :].astype(np.float32).reshape(-1, 3)

    # pick pixels far from bg as "text"
    d = np.linalg.norm(inner - bg[None, :], axis=1)
    text_pixels = inner[d > 25.0]

    if text_pixels.shape[0] < 50:
        # fallback: take the farthest pixels if thresholding found too few
        idx = np.argsort(d)[-max(50, inner.shape[0] // 200) :]
        text_pixels = inner[idx]

    text = np.median(text_pixels, axis=0)
    return bg, text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("image_path", type=str)
    ap.add_argument("--topk", type=int, default=0, help="only evaluate first k rows (0 = all)")
    args = ap.parse_args()

    img = Image.open(args.image_path).convert("RGB")
    img_rgb = np.array(img, dtype=np.uint8)

    boxes = find_bar_boxes(img_rgb)
    if args.topk and args.topk > 0:
        boxes = boxes[: args.topk]

    if not boxes:
        raise SystemExit("no bar rows found. try adjusting the luminance threshold in find_bar_boxes().")

    ratios: List[float] = []
    for i, b in enumerate(boxes, start=1):
        row = img_rgb[b.y0:b.y1, b.x0:b.x1, :]
        bg, tx = estimate_bg_and_text(row)
        r = contrast_ratio(bg, tx)
        ratios.append(r)
        print(f"row {i}: contrast={r:.3f}  bg={bg.round(1)}  text={tx.round(1)}")

    worst_i = int(np.argmin(np.array(ratios))) + 1
    print(f"\nleast legible row: {worst_i} (contrast={min(ratios):.3f})")


if __name__ == "__main__":
    main()
