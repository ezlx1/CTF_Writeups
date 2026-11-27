#!/usr/bin/env python3
"""Compress assets/clips/*.gif and embed them into assets/header.svg.

Run from the repo root. Safe to re-run after swapping a clip.
Original GIFs are not modified. Needs ffmpeg.
"""
import base64
import re
import subprocess
import tempfile
from pathlib import Path

SVG = Path("assets/header.svg")
CLIPS = Path("assets/clips")
FPS = 10        # lower = smaller file
SECONDS = 4     # max length of each clip
SCALE = 1.25    # resolution relative to the slot size
COLORS = 96     # GIF palette size

svg = SVG.read_text(encoding="utf-8")
count = 0


def attr(tag, name):
    return re.search(rf'\s{name}="([^"]*)"', tag).group(1)


def embed(match):
    global count
    tag = match.group(0)
    found = re.search(r'(?:data-clip="|href="clips/)(shelf-[\w-]+\.gif)"', tag)
    if not found:
        return tag
    name = found.group(1)
    x, y, w, h = (attr(tag, k) for k in ("x", "y", "width", "height"))
    vf = (
        f"fps={FPS},scale={int(int(w) * SCALE)}:{int(int(h) * SCALE)}"
        ":force_original_aspect_ratio=decrease:flags=lanczos,"
        f"split[a][b];[a]palettegen=max_colors={COLORS}[p];"
        "[b][p]paletteuse=dither=bayer:bayer_scale=4"
    )
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / name
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-t", str(SECONDS),
             "-i", str(CLIPS / name), "-vf", vf, "-loop", "0", str(out)],
            check=True,
        )
        data = out.read_bytes()
    print(f"{name}: {len(data) / 1e6:.2f} MB")
    count += 1
    uri = "data:image/gif;base64," + base64.b64encode(data).decode()
    return (f'<image data-clip="{name}" href="{uri}" x="{x}" y="{y}" '
            f'width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet"/>')


svg = re.sub(r"<image\b[^>]*/>", embed, svg)
# remove the filename placeholder labels
svg = re.sub(r"\s*<text\b[^>]*>clips/shelf-[\w-]+\.gif</text>", "", svg)
SVG.write_text(svg, encoding="utf-8")
print(f"Embedded {count} clips. header.svg is {SVG.stat().st_size / 1e6:.2f} MB")
