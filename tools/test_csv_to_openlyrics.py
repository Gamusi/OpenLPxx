import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from csv_to_openlyrics import CsvConversionError, convert_csv_to_openlyrics

NS = {"ol": "http://openlyrics.info/namespace/2009/song"}


class TestCsvToOpenLyrics(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write_csv(self, name: str, content: str) -> Path:
        p = self.root / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_groups_verses_chorus_and_preserves_order_and_unicode(self) -> None:
        csv_path = self._write_csv(
            "songs.csv",
            'collection,number,title,section,text\n'
            'Luganda Hymnal,25,"Ekitiibwa, Mukama",v1,"Line 1 — ŋŋenda\nLine 2"\n'
            'Luganda Hymnal,25,"Ekitiibwa, Mukama",c1,"Chorus line 1\nChorus line 2"\n'
            'Luganda Hymnal,25,"Ekitiibwa, Mukama",v2,"Verse 2 line 1"\n'
            'Luganda Hymnal,25,"Ekitiibwa, Mukama",c1,"Chorus line 1\nChorus line 2"\n',
        )
        out_dir = self.root / "out"
        written = convert_csv_to_openlyrics(csv_path, out_dir)
        self.assertEqual(len(written), 1)
        tree = ET.parse(written[0])
        root = tree.getroot()
        self.assertEqual(root.attrib.get("version"), "0.8")
        title = root.find("ol:properties/ol:titles/ol:title", NS)
        self.assertEqual(title.text, "Ekitiibwa, Mukama")
        sb = root.find("ol:properties/ol:songbooks/ol:songbook", NS)
        self.assertEqual(sb.attrib["name"], "Luganda Hymnal")
        self.assertEqual(sb.attrib["entry"], "25")
        vo = root.find("ol:properties/ol:verseOrder", NS)
        self.assertEqual(vo.text, "v1 c1 v2 c1")
        verses = root.findall("ol:lyrics/ol:verse", NS)
        self.assertEqual([v.attrib["name"] for v in verses], ["v1", "c1", "v2"])
        lines_el = verses[0].find("ol:lines", NS)
        self.assertEqual(len(lines_el.findall("ol:br", NS)), 1)
        self.assertIn("ŋŋenda", "".join(lines_el.itertext()))

    def test_deterministic_collision_safe_filenames(self) -> None:
        csv_path = self._write_csv(
            "dup_titles.csv",
            "collection,number,title,section,text\n"
            "Book A,1,Same Title,v1,Text A\n"
            "Book B,1,Same Title,v1,Text B\n",
        )
        out1 = self.root / "out1"
        out2 = self.root / "out2"
        files1 = [p.name for p in convert_csv_to_openlyrics(csv_path, out1)]
        files2 = [p.name for p in convert_csv_to_openlyrics(csv_path, out2)]
        self.assertEqual(files1, files2)
        self.assertEqual(len(set(files1)), 2)

    def test_rejects_missing_required_fields(self) -> None:
        csv_path = self._write_csv(
            "bad.csv",
            "collection,number,title,section,text\n"
            "Book A,,Missing Number,v1,Hello\n",
        )
        with self.assertRaises(CsvConversionError) as ctx:
            convert_csv_to_openlyrics(csv_path, self.root / "out")
        self.assertIn("row 2", str(ctx.exception).lower())

    def test_rejects_inconsistent_title_within_same_hymn(self) -> None:
        csv_path = self._write_csv(
            "bad_title.csv",
            "collection,number,title,section,text\n"
            "Book A,1,Title One,v1,Line 1\n"
            "Book A,1,Title Two,v2,Line 2\n",
        )
        with self.assertRaises(CsvConversionError) as ctx:
            convert_csv_to_openlyrics(csv_path, self.root / "out")
        self.assertIn("title", str(ctx.exception).lower())

    def test_rejects_invalid_section_tag(self) -> None:
        csv_path = self._write_csv(
            "bad_sec.csv",
            "collection,number,title,section,text\n"
            "Book A,1,Title One,verse1,Line 1\n",
        )
        with self.assertRaises(CsvConversionError):
            convert_csv_to_openlyrics(csv_path, self.root / "out")


if __name__ == "__main__":
    unittest.main()
