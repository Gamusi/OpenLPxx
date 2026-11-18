#!/usr/bin/env python3
"""Extract liturgical resources from Come+and+Worship_23.0_APKPure.xapk."""

from __future__ import annotations

import argparse
import io
import json
import re
import zipfile
from pathlib import Path
from typing import Any

from arsc_decoder import decode_arsc


def extract_title(text: str) -> str | None:
    """Return the first non-empty line as title, or None if blank."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return None


def classify_resource(title: str | None, key: str) -> str:
    """Classify a recovered liturgical resource into a conservative category."""
    upper = (title or "").upper()
    if "CREED" in upper or "CONFESSION" in upper:
        return "creed_and_confession"
    if "ORDER OF SERVICE" in upper or "ORDER OF COMMISSIONING" in upper:
        return "order_of_service"
    if any(w in upper for w in ("COMMUNION", "CONSECRATION", "HUMBLE ACCESS", "OFFERTORY", "DISMISSAL")):
        return "communion_liturgy"
    if "APPENDIX" in upper:
        return "appendix"
    if any(w in upper for w in ("PRAYER", "INTERCESSION", "THANKSGIVING", "FORGIVENESS", "RESPONSES")):
        return "prayer_and_liturgy"
    if any(w in upper for w in ("BAPTISM", "PARENTS", "DECISION", "WELCOME", "PRESENTATION", "EXAMINATION", "ADMISSION", "SEASON", "SUNDAY", "LESSON", "SERMON", "CONCLUSION", "NOTICES", "PREPARATION", "ENCOURAGEMENT", "LEADER")):
        return "liturgical_section"
    if key == "story1" or "PUBLISHED" in upper or "FAITH" in upper:
        return "front_matter"
    return "other"


def write_extracted_resources(
    story_strings: dict[str, dict[str, Any]],
    output_dir: Path,
    source_label: str = "muhoozi.afritech.comeandworship.apk:resources.arsc",
) -> dict[str, Any]:
    """Write extracted resource text files and machine-readable index.json."""
    out_dir = Path(output_dir)
    res_dir = out_dir / "resources"
    res_dir.mkdir(parents=True, exist_ok=True)

    sorted_keys = sorted(
        story_strings.keys(),
        key=lambda k: int(re.fullmatch(r"story(\d+)", k).group(1)) if re.fullmatch(r"story(\d+)", k) else 999999,
    )

    entries: list[dict[str, Any]] = []
    category_counts: dict[str, int] = {}

    for seq_idx, key in enumerate(sorted_keys, start=1):
        item = story_strings[key]
        raw_text = item["value"]
        title = extract_title(raw_text)
        category = classify_resource(title, key)
        category_counts[category] = category_counts.get(category, 0) + 1

        match = re.fullmatch(r"story(\d+)", key)
        filename = f"story{int(match.group(1)):02d}.txt" if match else f"{key}.txt"
        rel_path = f"resources/{filename}"
        (out_dir / rel_path).write_text(raw_text, encoding="utf-8")

        entries.append(
            {
                "resource_id": item["id"],
                "resource_key": key,
                "resource_type": "string",
                "category": category,
                "title": title,
                "source_resource_file": source_label,
                "extracted_path": rel_path,
                "sequence_relationship": {
                    "resource_key_index": seq_idx,
                    "service_order_verified": False,
                    "note": "Ordered by resource key (story1..story42); exact UI/service assembly order is unknown from resources.arsc alone.",
                },
            }
        )

    index_data = {
        "source_package": "Come+and+Worship_23.0_APKPure.xapk",
        "base_apk": "muhoozi.afritech.comeandworship.apk",
        "total_entries": len(entries),
        "category_counts": category_counts,
        "entries": entries,
    }
    (out_dir / "index.json").write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")
    return index_data


def extract_from_xapk(xapk_path: Path, output_dir: Path) -> dict[str, Any]:
    """Decode resources.arsc from Come+and+Worship XAPK and extract story1..story42."""
    with zipfile.ZipFile(xapk_path, "r") as z:
        base_bytes = z.read("muhoozi.afritech.comeandworship.apk")
    with zipfile.ZipFile(io.BytesIO(base_bytes), "r") as base_apk:
        decoded = decode_arsc(base_apk.read("resources.arsc"))

    story_strings = {
        k: v for k, v in decoded["strings"].items() if re.fullmatch(r"story\d+", k)
    }
    return write_extracted_resources(story_strings, output_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract Come and Worship liturgical resources from XAPK.")
    parser.add_argument("xapk_path", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args(argv)
    index = extract_from_xapk(args.xapk_path, args.output_dir)
    print(f"Extracted {index['total_entries']} entries to {args.output_dir}; categories={index['category_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
