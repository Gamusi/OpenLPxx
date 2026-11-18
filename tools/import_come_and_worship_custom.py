#!/usr/bin/env python3
"""Repeatable batch importer for Come and Worship liturgical resources into OpenLP Custom Slides."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from liturgy_slides import build_searchable_title, select_eligible_entries, split_into_slides


def _ensure_openlp_on_path(openlp_source: Path) -> None:
    if str(openlp_source) not in sys.path:
        sys.path.insert(0, str(openlp_source))


def import_liturgy_collection(
    source_dir: Path,
    custom_db_path: Path,
    openlp_source: Path = Path(r"D:\OpenLPxx\openlp-source"),
) -> dict[str, Any]:
    """Import eligible Come and Worship resources into an OpenLP custom.sqlite database."""
    _ensure_openlp_on_path(openlp_source)
    from openlp.core.db.manager import DBManager
    from openlp.plugins.custom.lib.customxmlhandler import CustomXML
    from openlp.plugins.custom.lib.db import CustomSlide, init_schema

    src = Path(source_dir)
    index_data = json.loads((src / "index.json").read_text(encoding="utf-8"))
    eligible, excluded = select_eligible_entries(index_data["entries"])

    manager = DBManager("custom", init_schema, db_file_path=Path(custom_db_path))
    try:
        existing_slides = manager.get_all_objects(CustomSlide)
        existing_credits = [s.credits or "" for s in existing_slides]
        existing_titles = {s.title for s in existing_slides}

        imported: list[str] = []
        existing: list[str] = []

        for entry in eligible:
            key = entry["resource_key"]
            res_id = entry["resource_id"]
            raw_text = (src / entry["extracted_path"]).read_text(encoding="utf-8")
            title = build_searchable_title(entry, raw_text)
            credits = f"Come and Worship — {key} ({res_id})"

            already_present = (
                title in existing_titles
                or any(res_id in c or f"— {key} " in c for c in existing_credits)
            )
            if already_present:
                existing.append(key)
                continue

            slides = split_into_slides(raw_text)
            if not slides:
                continue
            cxml = CustomXML()
            for idx, slide_text in enumerate(slides, start=1):
                cxml.add_verse_to_lyrics("custom", idx, slide_text)

            cs = CustomSlide(
                title=title,
                text=str(cxml.extract_xml(), "utf-8"),
                credits=credits,
            )
            manager.save_object(cs)
            existing_titles.add(title)
            existing_credits.append(credits)
            imported.append(key)

        return {
            "imported": imported,
            "existing": existing,
            "excluded": [e["resource_key"] for e in excluded],
            "total_in_db": len(manager.get_all_objects(CustomSlide)),
        }
    finally:
        bind = manager.session.bind
        manager.session.close()
        if bind is not None:
            bind.dispose()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import Come and Worship resources into OpenLP Custom Slides.")
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("portable_path", type=Path)
    args = parser.parse_args(argv)

    openlp_source = Path(r"D:\OpenLPxx\openlp-source")
    _ensure_openlp_on_path(openlp_source)
    from openlp.core.common.registry import Registry
    from openlp.core.common.settings import Settings

    Registry.create()
    Settings.setDefaultFormat(Settings.IniFormat)
    Settings.set_filename(args.portable_path / "Data" / "OpenLP.ini")
    Registry().register("settings", Settings())

    db_path = args.portable_path / "Data" / "custom" / "custom.sqlite"
    result = import_liturgy_collection(args.source_dir, db_path, openlp_source)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
