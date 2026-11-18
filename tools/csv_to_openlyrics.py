#!/usr/bin/env python3
"""Convert a structured hymn CSV file into OpenLyrics 0.8 XML files for OpenLP."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

OPENLYRICS_NS = "http://openlyrics.info/namespace/2009/song"
REQUIRED_COLUMNS = ("collection", "number", "title", "section", "text")
SECTION_PATTERN = re.compile(r"^[vcbpeio]\d+[a-z]?$")


class CsvConversionError(ValueError):
    """Raised when the input CSV structure or row content is invalid."""


@dataclass
class HymnRecord:
    """In-memory representation of a single grouped hymn."""

    collection: str
    number: str
    title: str
    sections: dict[str, str] = field(default_factory=dict)
    verse_order: list[str] = field(default_factory=list)


def _slugify(value: str, max_len: int = 48) -> str:
    """Return a filesystem-safe ASCII slug for deterministic filenames."""
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").lower()
    return (slug[:max_len].strip("_") or "item")


def build_output_filename(collection: str, number: str, title: str, used: set[str]) -> str:
    """Build a deterministic, collision-safe filename for a hymn."""
    col_slug = _slugify(collection, 24)
    num_slug = _slugify(number, 16)
    title_slug = _slugify(title, 36)
    base = f"{col_slug}_{num_slug}_{title_slug}"
    candidate = f"{base}.xml"
    if candidate not in used:
        used.add(candidate)
        return candidate
    digest = hashlib.sha1(f"{collection}\x00{number}\x00{title}".encode("utf-8")).hexdigest()[:8]
    candidate = f"{base}_{digest}.xml"
    suffix = 2
    while candidate in used:
        candidate = f"{base}_{digest}_{suffix}.xml"
        suffix += 1
    used.add(candidate)
    return candidate


def _parse_and_group_csv(csv_path: Path) -> list[HymnRecord]:
    """Read and validate the CSV, grouping rows by (collection, number)."""
    if not csv_path.exists():
        raise CsvConversionError(f"Input CSV not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise CsvConversionError("CSV file is empty or missing a header row.")
        missing_cols = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing_cols:
            raise CsvConversionError(f"CSV missing required columns: {', '.join(missing_cols)}")

        grouped: dict[tuple[str, str], HymnRecord] = {}
        for row_idx, row in enumerate(reader, start=2):
            if None in row:
                raise CsvConversionError(f"Malformed CSV at row {row_idx}: unexpected extra columns.")
            values = {k: (row[k] or "").strip() if k != "text" else (row[k] or "") for k in REQUIRED_COLUMNS}
            for col in REQUIRED_COLUMNS:
                if not values[col].strip():
                    raise CsvConversionError(f"Missing required field '{col}' at row {row_idx}.")

            section = values["section"].lower()
            if not SECTION_PATTERN.fullmatch(section):
                raise CsvConversionError(
                    f"Invalid section tag '{values['section']}' at row {row_idx}. "
                    "Expected OpenLyrics tag like v1, v2, c1, b1."
                )

            key = (values["collection"], values["number"])
            text_norm = values["text"].replace("\r\n", "\n").replace("\r", "\n").strip("\n")
            if key not in grouped:
                grouped[key] = HymnRecord(
                    collection=values["collection"],
                    number=values["number"],
                    title=values["title"],
                )
            hymn = grouped[key]
            if hymn.title != values["title"]:
                raise CsvConversionError(
                    f"Inconsistent title for ({values['collection']}, {values['number']}) at row {row_idx}: "
                    f"expected '{hymn.title}', got '{values['title']}'."
                )
            if section in hymn.sections and hymn.sections[section] != text_norm:
                raise CsvConversionError(
                    f"Conflicting text for duplicate section '{section}' of "
                    f"({values['collection']}, {values['number']}) at row {row_idx}."
                )
            hymn.sections[section] = text_norm
            hymn.verse_order.append(section)

    if not grouped:
        raise CsvConversionError("CSV contains no hymn data rows.")
    return list(grouped.values())


def build_openlyrics_element(hymn: HymnRecord) -> ET.Element:
    """Construct an OpenLyrics 0.8 <song> XML element compatible with OpenLP 3.1.7."""
    ET.register_namespace("", OPENLYRICS_NS)
    song_el = ET.Element(f"{{{OPENLYRICS_NS}}}song", {"version": "0.8"})

    props = ET.SubElement(song_el, f"{{{OPENLYRICS_NS}}}properties")
    titles = ET.SubElement(props, f"{{{OPENLYRICS_NS}}}titles")
    title_el = ET.SubElement(titles, f"{{{OPENLYRICS_NS}}}title")
    title_el.text = hymn.title

    songbooks = ET.SubElement(props, f"{{{OPENLYRICS_NS}}}songbooks")
    ET.SubElement(
        songbooks,
        f"{{{OPENLYRICS_NS}}}songbook",
        {"name": hymn.collection, "entry": hymn.number},
    )

    verse_order_el = ET.SubElement(props, f"{{{OPENLYRICS_NS}}}verseOrder")
    verse_order_el.text = " ".join(hymn.verse_order)

    lyrics_el = ET.SubElement(song_el, f"{{{OPENLYRICS_NS}}}lyrics")
    for section_name, section_text in hymn.sections.items():
        verse_el = ET.SubElement(lyrics_el, f"{{{OPENLYRICS_NS}}}verse", {"name": section_name})
        lines_el = ET.SubElement(verse_el, f"{{{OPENLYRICS_NS}}}lines")
        text_lines = section_text.split("\n")
        lines_el.text = text_lines[0]
        for line in text_lines[1:]:
            br_el = ET.SubElement(lines_el, f"{{{OPENLYRICS_NS}}}br")
            br_el.tail = line

    return song_el


def convert_csv_to_openlyrics(csv_path: Path, output_dir: Path) -> list[Path]:
    """Convert all hymns in csv_path into OpenLyrics XML files in output_dir."""
    hymns = _parse_and_group_csv(Path(csv_path))
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    used_names: set[str] = set()
    written: list[Path] = []
    for hymn in hymns:
        filename = build_output_filename(hymn.collection, hymn.number, hymn.title, used_names)
        target = out_dir / filename
        root = build_openlyrics_element(hymn)
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(target, encoding="utf-8", xml_declaration=True)
        written.append(target)
    return written


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for CSV-to-OpenLyrics conversion."""
    parser = argparse.ArgumentParser(description="Convert a hymn CSV file into OpenLyrics 0.8 XML files.")
    parser.add_argument("csv_path", type=Path, help="Path to the input UTF-8 CSV file.")
    parser.add_argument("output_dir", type=Path, help="Directory where OpenLyrics .xml files will be written.")
    args = parser.parse_args(argv)

    try:
        written = convert_csv_to_openlyrics(args.csv_path, args.output_dir)
    except CsvConversionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Converted {len(written)} hymn(s) to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
