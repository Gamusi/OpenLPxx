import csv
import tempfile
import unittest
import zipfile
from pathlib import Path

from vpl_to_openlp_csv import USFM_BOOKS, convert_vpl_zip_to_csv


class TestVplToOpenLpCsv(unittest.TestCase):
    def test_66_canonical_books_mapped(self) -> None:
        self.assertEqual(len(USFM_BOOKS), 66)
        self.assertEqual(USFM_BOOKS["GEN"][:3], (1, 1, "Genesis"))
        self.assertEqual(USFM_BOOKS["PSA"][:3], (19, 1, "Psalms"))
        self.assertEqual(USFM_BOOKS["SNG"][:3], (22, 1, "Song of Solomon"))
        self.assertEqual(USFM_BOOKS["MAT"][:3], (40, 2, "Matthew"))
        self.assertEqual(USFM_BOOKS["REV"][:3], (66, 2, "Revelation"))

    def test_converts_vpl_xml_in_zip_to_books_and_verses_csv(self) -> None:
        xml_sample = (
            '<?xml version="1.0" encoding="utf-8"?><verseFile>\n'
            '<v b="GEN" c="1" v="1">In the beginning, God created the heavens and the earth. </v>\n'
            '<v b="JHN" c="3" v="16">For God so loved the world, “test” </v>\n'
            '</verseFile>\n'
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            zpath = tmp_p / "sample_vpl.zip"
            with zipfile.ZipFile(zpath, "w") as z:
                z.writestr("sample_vpl.xml", xml_sample.encode("utf-8"))
            out_dir = tmp_p / "out"
            stats = convert_vpl_zip_to_csv(zpath, out_dir, xml_member="sample_vpl.xml")
            self.assertEqual(stats["books_count"], 2)
            self.assertEqual(stats["verses_count"], 2)

            with (out_dir / "books.csv").open("r", encoding="utf-8", newline="") as f:
                books = list(csv.reader(f))
            self.assertEqual(books[0], ["book_id", "testament_id", "book_name", "book_abbreviation"])
            self.assertEqual(books[1], ["1", "1", "Genesis", "Gen"])
            self.assertEqual(books[2], ["43", "2", "John", "John"])

            with (out_dir / "verses.csv").open("r", encoding="utf-8", newline="") as f:
                verses = list(csv.reader(f))
            self.assertEqual(verses[0], ["book_id", "chapter_number", "verse_number", "verse_text"])
            self.assertEqual(verses[1], ["1", "1", "1", "In the beginning, God created the heavens and the earth."])
            self.assertEqual(verses[2][3], "For God so loved the world, “test”")

    def test_rejects_unknown_book_code(self) -> None:
        xml_bad = '<?xml version="1.0" encoding="utf-8"?><verseFile><v b="XXX" c="1" v="1">Hi</v></verseFile>'
        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            zpath = tmp_p / "bad.zip"
            with zipfile.ZipFile(zpath, "w") as z:
                z.writestr("bad_vpl.xml", xml_bad.encode("utf-8"))
            with self.assertRaises(ValueError):
                convert_vpl_zip_to_csv(zpath, tmp_p / "out", xml_member="bad_vpl.xml")


if __name__ == "__main__":
    unittest.main()
