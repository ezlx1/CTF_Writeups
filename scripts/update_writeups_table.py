#!/usr/bin/env python3
"""
Rebuilds the "Latest Writeups" table in README.md between the
<!-- WRITEUPS:START --> / <!-- WRITEUPS:END --> markers.

Treats every top-level directory (other than the ones in EXCLUDE) as a
platform (e.g. "Tryhackme", "HackTheBox", "pwn.college"), and every
immediate subdirectory of a platform as one writeup/room. It reads the
first .md file in each room folder and pulls out:
  - Title       -> first line starting with "# "
  - Difficulty  -> a line containing "**Difficulty:**"
  - OS          -> a line containing "**OS:**"

Rows are sorted by each file's last git-commit date (newest first),
falling back to filesystem mtime if git history isn't available
(e.g. a brand-new file in the same commit that triggered this run).

Run from the repo root. Exits 0 whether or not README.md changed;
the calling workflow checks `git status` itself to decide whether to commit.
"""

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"
START_MARKER = "<!-- WRITEUPS:START -->"
END_MARKER = "<!-- WRITEUPS:END -->"
EXCLUDE_DIRS = {"assets", "scripts", ".github", ".git", ".obsidian"}
MAX_ROWS = 12


def git_last_modified(path: Path) -> str:
    """Return ISO commit date of the last commit touching `path`, or '' if unknown."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(path.relative_to(REPO_ROOT))],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        date = result.stdout.strip()
        if date:
            return date
    except subprocess.CalledProcessError:
        pass
    # Fall back to filesystem mtime (e.g. file just added, not committed yet)
    try:
        import datetime

        return datetime.datetime.fromtimestamp(path.stat().st_mtime).isoformat()
    except OSError:
        return ""


def extract_field(text: str, label: str) -> str:
    match = re.search(rf"\*\*{re.escape(label)}:\*\*\s*`?([^`\n]+?)`?\s*$", text, re.MULTILINE)
    return match.group(1).strip() if match else "—"


def extract_title(text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def find_writeup_file(room_dir: Path) -> Path | None:
    md_files = sorted(room_dir.glob("*.md"))
    return md_files[0] if md_files else None


def collect_rows():
    rows = []
    for platform_dir in sorted(REPO_ROOT.iterdir()):
        if not platform_dir.is_dir() or platform_dir.name in EXCLUDE_DIRS or platform_dir.name.startswith("."):
            continue
        for room_dir in sorted(platform_dir.iterdir()):
            if not room_dir.is_dir():
                continue
            md_file = find_writeup_file(room_dir)
            if md_file is None:
                continue
            text = md_file.read_text(encoding="utf-8", errors="ignore")
            title = extract_title(text, room_dir.name)
            difficulty = extract_field(text, "Difficulty")
            os_name = extract_field(text, "OS")
            date = git_last_modified(md_file)
            rel_path = md_file.relative_to(REPO_ROOT).as_posix()
            rows.append(
                {
                    "title": title,
                    "platform": platform_dir.name,
                    "difficulty": difficulty,
                    "os": os_name,
                    "date": date,
                    "path": rel_path,
                }
            )
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows[:MAX_ROWS]


def build_table(rows) -> str:
    if not rows:
        return "_No writeups found yet._"
    lines = [
        "| Writeup | Platform | Difficulty | OS |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| [{r['title']}]({r['path']}) | {r['platform']} | {r['difficulty']} | {r['os']} |")
    return "\n".join(lines)


def main():
    rows = collect_rows()
    table = build_table(rows)

    readme = README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )
    replacement = f"{START_MARKER}\n{table}\n{END_MARKER}"

    if not pattern.search(readme):
        raise SystemExit(
            f"Could not find {START_MARKER} / {END_MARKER} markers in README.md — nothing updated."
        )

    new_readme = pattern.sub(replacement, readme)
    if new_readme != readme:
        README_PATH.write_text(new_readme, encoding="utf-8")
        print("README.md updated.")
    else:
        print("README.md already up to date.")


if __name__ == "__main__":
    main()
