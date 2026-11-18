#!/usr/bin/env python3
"""Prepare extracted Anglican Hymnal .txt files into the standard CSV template."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


def _load_index(list_path: Path) -> dict[int, str]:
    """Load hymn number -> title mapping from list.txt if present."""
    index: dict[int, str] = {}
    if not list_path.exists():
        return index
    for line in list_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*(\d+)\s*:\s*(.+?)\s*$", line)
        if m:
            index[int(m.group(1))] = m.group(2)
    return index


def parse_hymn_file(raw_text: str, fallback_title: str = "") -> tuple[str, list[tuple[str, str]]]:
    """Extract (title, [(section_tag, text), ...]) from a single hymnN.txt file."""
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return "", []

    blocks = [b.strip() for b in re.split(r"\n\s*\n", normalized) if b.strip()]
    first_lines = [ln.strip() for ln in blocks[0].split("\n") if ln.strip()]
    title = first_lines[0] if first_lines else fallback_title
    first_verse_lines = first_lines[1:]
    if first_verse_lines:
        verse_blocks = ["\n".join(first_verse_lines)] + blocks[1:]
    elif len(blocks) > 1:
        verse_blocks = blocks[1:]
    else:
        # Single-line hymn fallback: keep title as v1 text so it is not lost
        verse_blocks = [title]

    sections = [(f"v{idx}", blk) for idx, blk in enumerate(verse_blocks, start=1)]
    return title or fallback_title, sections


def export_hymnal_to_csv(
    source_dir: Path,
    output_csv: Path,
    collection: str = "Anglican Hymnal (Luganda)",
) -> tuple[int, list[str]]:
    """Convert numbered hymn*.txt files in source_dir into a CSV template file."""
    src = Path(source_dir)
    index = _load_index(src / "list.txt")
    hymn_paths = sorted(
        (p for p in src.glob("hymn*.txt") if re.fullmatch(r"hymn(\d+)\.txt", p.name)),
        key=lambda p: int(re.fullmatch(r"hymn(\d+)\.txt", p.name).group(1)),
    )

    exported = 0
    skipped: list[str] = []
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["collection", "number", "title", "section", "text"])
        for path in hymn_paths:
            num = int(re.fullmatch(r"hymn(\d+)\.txt", path.name).group(1))
            raw = path.read_text(encoding="utf-8")
            title, sections = parse_hymn_file(raw, fallback_title=index.get(num, f"Hymn {num}"))
            if not sections:
                skipped.append(path.name)
                continue
            for sec_tag, sec_text in sections:
                writer.writerow([collection, str(num), title, sec_tag, sec_text])
            exported += 1

    return exported, skipped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export extracted Anglican Hymnal .txt files to CSV.")
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--collection", default="Anglican Hymnal (Luganda)")
    args = parser.parse_args(argv)
    exported, skipped = export_hymnal_to_csv(args.source_dir, args.output_csv, args.collection)
    print(f"Exported {exported} hymns to {args.output_csv}; skipped empty: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
