import json
import tempfile
import unittest
from pathlib import Path

from extract_come_and_worship import classify_resource, extract_title, write_extracted_resources


class TestExtractComeAndWorship(unittest.TestCase):
    def test_extract_title_uses_first_non_empty_line(self) -> None:
        self.assertEqual(extract_title("\n\n  THE NICENE CREED \nWe believe..."), "THE NICENE CREED")
        self.assertIsNone(extract_title("   \n  "))

    def test_classify_resource_categories(self) -> None:
        self.assertEqual(classify_resource("THE APOSTLES’ CREED", "story10"), "creed_and_confession")
        self.assertEqual(classify_resource("CONFESSION", "story17"), "creed_and_confession")
        self.assertEqual(classify_resource("ORDER OF SERVICE FOR HOLY COMMUNION", "story16"), "order_of_service")
        self.assertEqual(classify_resource("PRAYER OF CONSECRATION", "story27"), "communion_liturgy")
        self.assertEqual(classify_resource("APPENDIX 1", "story39"), "appendix")

    def test_write_extracted_resources_preserves_exact_text_and_index(self) -> None:
        sample = {
            "story1": {
                "id": "0x7f1100ef",
                "key": "story1",
                "locale": "default",
                "value": "\nTHE LORD’S PRAYER\n\nOur Father in heaven,\nhallowed be your name.",
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            index = write_extracted_resources(sample, out_dir, source_label="base.apk:resources.arsc")
            self.assertEqual(len(index["entries"]), 1)
            entry = index["entries"][0]
            self.assertEqual(entry["resource_id"], "0x7f1100ef")
            self.assertEqual(entry["resource_key"], "story1")
            self.assertEqual(entry["title"], "THE LORD’S PRAYER")
            self.assertEqual(entry["source_resource_file"], "base.apk:resources.arsc")
            extracted_file = out_dir / entry["extracted_path"]
            self.assertTrue(extracted_file.exists())
            self.assertEqual(extracted_file.read_text(encoding="utf-8"), sample["story1"]["value"])
            self.assertTrue((out_dir / "index.json").exists())
            loaded = json.loads((out_dir / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(loaded["total_entries"], 1)


if __name__ == "__main__":
    unittest.main()
