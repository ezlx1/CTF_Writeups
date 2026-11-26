#!/usr/bin/env python3
"""
Rewrites the terminal-readout lines inside assets/header.svg, between the
<!-- TVLOG:START --> / <!-- TVLOG:END --> markers, with this repo's most
recent commit subjects — so the in-scene "TV" reflects real activity
instead of placeholder text.

Run from the repo root (same convention as update_writeups_table.py).
"""

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SVG_PATH = REPO_ROOT / "assets" / "header.svg"
START_MARKER = "<!-- TVLOG:START -->"
END_MARKER = "<!-- TVLOG:END -->"
MAX_LINES = 5
MAX_CHARS = 32
LINE_HEIGHT = 18
FIRST_LINE_Y = 118
SCREEN_LEFT_X = 364


def recent_commit_subjects() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "log", f"-n{MAX_LINES}", "--pretty=format:%s"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        lines = []
    while len(lines) < MAX_LINES:
        lines.append("—")
    return lines[:MAX_LINES]


def escape_xml(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_block(lines: list[str]) -> str:
    rows = []
    y = FIRST_LINE_Y
    for line in lines:
        trimmed = escape_xml(line[:MAX_CHARS])
        rows.append(f'      <text x="{SCREEN_LEFT_X}" y="{y}">{trimmed}</text>')
        y += LINE_HEIGHT

    prompt_y = y + 6
    rows.append(f'      <text x="{SCREEN_LEFT_X}" y="{prompt_y}" fill="#eafff0">$ git log --oneline</text>')
    rows.append(
        f'      <rect x="{SCREEN_LEFT_X + 160}" y="{prompt_y - 11}" width="8" height="14" fill="#eafff0">\n'
        f'        <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>\n'
        f"      </rect>"
    )

    inner = "\n".join(rows)
    return (
        "    <g font-family=\"Consolas, 'Courier New', monospace\" font-size=\"13\" fill=\"#39ff14\">\n"
        f"{inner}\n"
        "    </g>"
    )


def main():
    svg = SVG_PATH.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL)

    if not pattern.search(svg):
        raise SystemExit("Could not find TVLOG markers in header.svg — nothing updated.")

    replacement = f"{START_MARKER}\n{build_block(recent_commit_subjects())}\n    {END_MARKER}"
    new_svg = pattern.sub(replacement, svg)

    if new_svg != svg:
        SVG_PATH.write_text(new_svg, encoding="utf-8")
        print("header.svg TV readout updated.")
    else:
        print("header.svg TV readout already up to date.")


if __name__ == "__main__":
    main()
