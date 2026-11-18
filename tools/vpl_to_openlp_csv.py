#!/usr/bin/env python3
"""Convert an eBible.org VPL XML archive into OpenLP 3.1.7 CSV Bible files."""

from __future__ import annotations

import argparse
import csv
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

USFM_BOOKS: dict[str, tuple[int, int, str, str]] = {
    "GEN": (1, 1, "Genesis", "Gen"),
    "EXO": (2, 1, "Exodus", "Exod"),
    "LEV": (3, 1, "Leviticus", "Lev"),
    "NUM": (4, 1, "Numbers", "Num"),
    "DEU": (5, 1, "Deuteronomy", "Deut"),
    "JOS": (6, 1, "Joshua", "Josh"),
    "JDG": (7, 1, "Judges", "Judg"),
    "RUT": (8, 1, "Ruth", "Ruth"),
    "1SA": (9, 1, "1 Samuel", "1Sam"),
    "2SA": (10, 1, "2 Samuel", "2Sam"),
    "1KI": (11, 1, "1 Kings", "1Kgs"),
    "2KI": (12, 1, "2 Kings", "2Kgs"),
    "1CH": (13, 1, "1 Chronicles", "1Chr"),
    "2CH": (14, 1, "2 Chronicles", "2Chr"),
    "EZR": (15, 1, "Ezra", "Ezra"),
    "NEH": (16, 1, "Nehemiah", "Neh"),
    "EST": (17, 1, "Esther", "Esth"),
    "JOB": (18, 1, "Job", "Job"),
    "PSA": (19, 1, "Psalms", "Ps"),
    "PRO": (20, 1, "Proverbs", "Prov"),
    "ECC": (21, 1, "Ecclesiastes", "Eccl"),
    "SNG": (22, 1, "Song of Solomon", "Song"),
    "ISA": (23, 1, "Isaiah", "Isa"),
    "JER": (24, 1, "Jeremiah", "Jer"),
    "LAM": (25, 1, "Lamentations", "Lam"),
    "EZK": (26, 1, "Ezekiel", "Ezek"),
    "DAN": (27, 1, "Daniel", "Dan"),
    "HOS": (28, 1, "Hosea", "Hos"),
    "JOL": (29, 1, "Joel", "Joel"),
    "AMO": (30, 1, "Amos", "Amos"),
    "OBA": (31, 1, "Obadiah", "Obad"),
    "JON": (32, 1, "Jonah", "Jonah"),
    "MIC": (33, 1, "Micah", "Mic"),
    "NAM": (34, 1, "Nahum", "Nah"),
    "HAB": (35, 1, "Habakkuk", "Hab"),
    "ZEP": (36, 1, "Zephaniah", "Zeph"),
    "HAG": (37, 1, "Haggai", "Hag"),
    "ZEC": (38, 1, "Zechariah", "Zech"),
    "MAL": (39, 1, "Malachi", "Mal"),
    "MAT": (40, 2, "Matthew", "Matt"),
    "MRK": (41, 2, "Mark", "Mark"),
    "LUK": (42, 2, "Luke", "Luke"),
    "JHN": (43, 2, "John", "John"),
    "ACT": (44, 2, "Acts", "Acts"),
    "ROM": (45, 2, "Romans", "Rom"),
    "1CO": (46, 2, "1 Corinthians", "1Cor"),
    "2CO": (47, 2, "2 Corinthians", "2Cor"),
    "GAL": (48, 2, "Galatians", "Gal"),
    "EPH": (49, 2, "Ephesians", "Eph"),
    "PHP": (50, 2, "Philippians", "Phil"),
    "COL": (51, 2, "Colossians", "Col"),
    "1TH": (52, 2, "1 Thessalonians", "1Thess"),
    "2TH": (53, 2, "2 Thessalonians", "2Thess"),
    "1TI": (54, 2, "1 Timothy", "1Tim"),
    "2TI": (55, 2, "2 Timothy", "2Tim"),
    "TIT": (56, 2, "Titus", "Titus"),
    "PHM": (57, 2, "Philemon", "Phlm"),
    "HEB": (58, 2, "Hebrews", "Heb"),
    "JAS": (59, 2, "James", "Jas"),
    "1PE": (60, 2, "1 Peter", "1Pet"),
    "2PE": (61, 2, "2 Peter", "2Pet"),
    "1JN": (62, 2, "1 John", "1John"),
    "2JN": (63, 2, "2 John", "2John"),
    "3JN": (64, 2, "3 John", "3John"),
    "JUD": (65, 2, "Jude", "Jude"),
    "REV": (66, 2, "Revelation", "Rev"),
}


def convert_vpl_zip_to_csv(
    zip_path: Path,
    output_dir: Path,
    xml_member: str = "engwebp_vpl.xml",
) -> dict[str, int]:
    """Convert VPL XML inside zip_path into OpenLP-compatible books.csv and verses.csv."""
    with zipfile.ZipFile(zip_path, "r") as z:
        xml_bytes = z.read(xml_member)

    root = ET.fromstring(xml_bytes)
    seen_books: dict[str, tuple[int, int, str, str]] = {}
    verses_rows: list[tuple[int, int, int, str]] = []

    for el in root.findall("v"):
        code = el.attrib["b"]
        if code not in USFM_BOOKS:
            raise ValueError(f"Unsupported USFM book code: {code}")
        book_meta = USFM_BOOKS[code]
        seen_books[code] = book_meta
        chapter = int(el.attrib["c"])
        verse = int(el.attrib["v"])
        text = (el.text or "").strip()
        verses_rows.append((book_meta[0], chapter, verse, text))

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    ordered_books = sorted(seen_books.values(), key=lambda b: b[0])
    with (out / "books.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["book_id", "testament_id", "book_name", "book_abbreviation"])
        for b_id, test_id, name, abbr in ordered_books:
            w.writerow([b_id, test_id, name, abbr])

    with (out / "verses.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["book_id", "chapter_number", "verse_number", "verse_text"])
        w.writerows(verses_rows)

    return {"books_count": len(ordered_books), "verses_count": len(verses_rows)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert eBible VPL XML zip to OpenLP books.csv & verses.csv.")
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--xml-member", default="engwebp_vpl.xml")
    args = parser.parse_args(argv)
    stats = convert_vpl_zip_to_csv(args.zip_path, args.output_dir, args.xml_member)
    print(f"Converted {stats['books_count']} books, {stats['verses_count']} verses to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
