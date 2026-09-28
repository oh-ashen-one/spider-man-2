#!/usr/bin/env python3
"""Split a 4-view character turnaround sheet (front, left, back, right) into four
separate full-height images for Tripo multiview. Finds the figures by
comparing each pixel with its row's median colour (the background), then groups
figure columns into four runs."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

VIEWS = ["front", "left", "back", "right"]

def split(path, out_dir):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    h, w, _ = a.shape
    m = max(8, w // 50)                              # per-row background from the left and right borders, which
    bg_row = np.median(np.concatenate([a[:, :m], a[:, -m:]], axis=1), axis=1, keepdims=True)  # are always empty
    fg = np.abs(a - bg_row).sum(axis=2) > 45         # pixels that differ from their row's background
    bg = np.median(a[:40].reshape(-1, 3), axis=0)     # canvas fill colour for the output
    col = fg.sum(axis=0) > h * 0.03                  # columns that contain figure (3% filters noise)
    runs, start = [], None
    for x, on in enumerate(col):
        if on and start is None: start = x
        if not on and start is not None: runs.append([start, x]); start = None
    if start is not None: runs.append([start, w])
    runs = [r for r in runs if r[1] - r[0] > w * 0.01]
    edge = w * 0.03                                  # drop vignette strips hugging the left/right border
    runs = [r for r in runs if not ((r[0] < edge or r[1] > w - edge) and r[1] - r[0] < w * 0.05)]
    if len(runs) < 4:
        sys.exit(f"{path}: found {len(runs)} figure columns, expected at least 4")
    # the three widest empty gaps separate the four figures; smaller gaps are inside a figure (arm vs torso)
    gaps = sorted(range(len(runs) - 1), key=lambda i: runs[i + 1][0] - runs[i][1], reverse=True)[:3]
    cuts = sorted(gaps)
    groups, s = [], 0
    for c in cuts + [len(runs) - 1]:
        groups.append([runs[s][0], runs[c][1]]); s = c + 1
    runs = groups
    # cut straight from the sheet between the midpoints of neighbouring figures, full height: the real
    # background is kept (no flat fill), so gradients and vignettes never show a pasted box
    name = Path(path).stem.replace("sheet_", "")
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, (view, (x0, x1)) in enumerate(zip(VIEWS, runs)):
        left = 0 if i == 0 else (runs[i - 1][1] + x0) // 2
        right = w if i == 3 else (x1 + runs[i + 1][0]) // 2
        crop = im.crop((left, 0, right, h))
        dst = out_dir / f"{name}_{view}.png"
        crop.save(dst); print(dst, crop.size, f"figure {x1 - x0}px wide")


if __name__ == "__main__":
    failed = []
    for p in sys.argv[1:]:
        try:
            split(p, Path(p).parent / "views")
        except SystemExit as e:
            print(e, file=sys.stderr); failed.append(p)
    sys.exit(1 if failed else 0)
