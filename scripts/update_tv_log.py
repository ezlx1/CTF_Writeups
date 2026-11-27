#!/usr/bin/env python3
"""
Rewrites the TV screen inside assets/header.svg, between the
<!-- TVLOG:START --> / <!-- TVLOG:END --> markers.

On page load the TV shows your latest commit once, then loops through
your writeups, grouped by top-level folder. A writeup is a tracked
<Category>/<Name>/README.md file.

Run from the repo root (same convention as update_writeups_table.py).
"""

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SVG_PATH = REPO_ROOT / "assets" / "header.svg"
START_MARKER = "<!-- TVLOG:START -->"
END_MARKER = "<!-- TVLOG:END -->"

COMMIT_SECONDS = 6      # how long the commit screen shows
PAGE_SECONDS = 4        # how long each writeups page shows
PER_PAGE = 4            # writeups per page
MAX_CHARS = 32
LINE_HEIGHT = 18
FIRST_LINE_Y = 118
PROMPT_Y = 214
SCREEN_LEFT_X = 364
SKIP_FOLDERS = {"assets", "scripts", "Temp"}


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True,
        encoding="utf-8", check=True,
    ).stdout


def latest_commit() -> str:
    """Newest commit subject that wasn't made by a bot."""
    for line in git("log", "-n50", "--pretty=format:%an%x09%s").splitlines():
        author, subject = line.split("\t", 1)
        if not author.endswith("[bot]"):
            return subject
    return "—"


def writeups() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for path in git("ls-files", "-z").split("\0"):
        parts = path.split("/")
        if (len(parts) == 3 and parts[2].lower() == "readme.md"
                and parts[0] not in SKIP_FOLDERS and not parts[0].startswith(".")):
            found.setdefault(parts[0], []).append(parts[1])
    return {k: sorted(found[k], key=str.lower) for k in sorted(found, key=str.lower)}


def fit(text: str) -> str:
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS - 1] + "…"
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def screen_text(lines: list[str], prompt: str) -> list[str]:
    rows = [
        f'        <text x="{SCREEN_LEFT_X}" y="{FIRST_LINE_Y + i * LINE_HEIGHT}">{fit(line)}</text>'
        for i, line in enumerate(lines)
    ]
    rows.append(f'        <text x="{SCREEN_LEFT_X}" y="{PROMPT_Y}" fill="#eafff0">{fit(prompt)}</text>')
    return rows


def build_block() -> str:
    pages = []
    for category, names in writeups().items():
        total = (len(names) + PER_PAGE - 1) // PER_PAGE
        for n in range(total):
            title = f"{category}/" + (f" ({n + 1}/{total})" if total > 1 else "")
            chunk = names[n * PER_PAGE:(n + 1) * PER_PAGE]
            pages.append(([title] + [f"  {name}" for name in chunk], "$ ls writeups/"))
    if not pages:
        pages.append((["No writeups yet"], "$ ls writeups/"))

    out = ["    <g font-family=\"Consolas, 'Courier New', monospace\" font-size=\"13\" fill=\"#39ff14\">"]

    # commit screen: shown once, then hidden for good
    out.append("      <g>")
    out.append(f'        <set attributeName="opacity" to="0" begin="{COMMIT_SECONDS}s" fill="freeze"/>')
    out += screen_text(["Latest commit:", latest_commit()], "$ git log -1")
    out.append("      </g>")

    # writeup pages: loop forever after the commit screen
    count = len(pages)
    for i, (lines, prompt) in enumerate(pages):
        out.append('      <g opacity="0">')
        if count == 1:
            out.append(f'        <set attributeName="opacity" to="1" begin="{COMMIT_SECONDS}s" fill="freeze"/>')
        else:
            values = ";".join("1" if j == i else "0" for j in range(count))
            times = ";".join(f"{j / count:.6f}" for j in range(count))
            out.append(
                f'        <animate attributeName="opacity" values="{values}" keyTimes="{times}" '
                f'calcMode="discrete" begin="{COMMIT_SECONDS}s" dur="{count * PAGE_SECONDS}s" '
                'repeatCount="indefinite"/>'
            )
        out += screen_text(lines, prompt)
        out.append("      </g>")

    out.append(
        f'      <rect x="{SCREEN_LEFT_X + 160}" y="{PROMPT_Y - 11}" width="8" height="14" fill="#eafff0">\n'
        f'        <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>\n'
        f"      </rect>"
    )
    out.append("    </g>")
    return "\n".join(out)


def main():
    svg = SVG_PATH.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL)

    if not pattern.search(svg):
        raise SystemExit("Could not find TVLOG markers in header.svg — nothing updated.")

    replacement = f"{START_MARKER}\n{build_block()}\n    {END_MARKER}"
    new_svg = pattern.sub(lambda _: replacement, svg)

    if new_svg != svg:
        SVG_PATH.write_text(new_svg, encoding="utf-8")
        print("header.svg TV readout updated.")
    else:
        print("header.svg TV readout already up to date.")


if __name__ == "__main__":
    main()
