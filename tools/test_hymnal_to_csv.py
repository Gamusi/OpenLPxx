import csv
import tempfile
import unittest
from pathlib import Path

from hymnal_to_csv import parse_hymn_file, export_hymnal_to_csv


class TestHymnalToCsv(unittest.TestCase):
    def test_parses_title_and_multiple_verses(self) -> None:
        raw = "TITLE LINE\r\nVerse 1 line 1\r\nVerse 1 line 2\r\n\r\nVerse 2 line 1\r\nVerse 2 line 2\r\n"
        title, sections = parse_hymn_file(raw, fallback_title="FALLBACK")
        self.assertEqual(title, "TITLE LINE")
        self.assertEqual(
            sections,
            [
                ("v1", "Verse 1 line 1\nVerse 1 line 2"),
                ("v2", "Verse 2 line 1\nVerse 2 line 2"),
            ],
        )

    def test_skips_empty_hymn_files_and_writes_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            src.mkdir()
            (src / "list.txt").write_text("1: FIRST HYMN\n", encoding="utf-8")
            (src / "hymn1.txt").write_text("FIRST HYMN\nLine A\n\nLine B\n", encoding="utf-8")
            (src / "hymn2.txt").write_text("   \n", encoding="utf-8")
            out_csv = Path(tmp) / "out.csv"

            exported, skipped = export_hymnal_to_csv(src, out_csv, collection="Anglican Hymnal (Luganda)")
            self.assertEqual(exported, 1)
            self.assertEqual(skipped, ["hymn2.txt"])
            with out_csv.open("r", encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["collection"], "Anglican Hymnal (Luganda)")
            self.assertEqual(rows[0]["number"], "1")
            self.assertEqual(rows[0]["section"], "v1")
            self.assertEqual(rows[1]["section"], "v2")


if __name__ == "__main__":
    unittest.main()
