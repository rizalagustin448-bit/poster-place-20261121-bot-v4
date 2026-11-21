"""AURMARA - The Harbour of Golden Stairs (poster v4).

Writes one vintage travel-poster image to /output/entry.png: a golden-hour
coastal town with a golden clock tower, grand staircase, harbour sailboats,
a balcony couple, and two people at a cafe table on the terrace.

Stdlib only: the poster is a pre-rendered asset (poster.png, drawn at build
time with Pillow - see draw_poster.py); this program just copies it to the
output directory, so it runs in the sandbox with no network and no installs.
"""

import os
import shutil
from pathlib import Path


MAX_BYTES = 1_048_576  # competition limit for /output/entry.png


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    src = Path(__file__).resolve().parent / "poster.png"
    if not src.is_file():
        raise SystemExit(f"missing asset: {src}")
    size = src.stat().st_size
    if size > MAX_BYTES:
        raise SystemExit(f"asset too large: {size} bytes > {MAX_BYTES}")
    dst = out_dir / "entry.png"
    shutil.copyfile(src, dst)
    # sanity: the copied file must still be a PNG (magic bytes intact)
    with open(dst, "rb") as fh:
        if fh.read(8) != b"\x89PNG\r\n\x1a\n":
            raise SystemExit(f"copied file is not a PNG: {dst}")
    print(f"wrote {dst} ({dst.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
