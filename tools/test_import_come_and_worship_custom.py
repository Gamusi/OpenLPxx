import sys
import tempfile
import unittest
from pathlib import Path

from liturgy_slides import (
    EXCLUDED_KEYS,
    build_searchable_title,
    select_eligible_entries,
    split_into_slides,
)


class TestLiturgySlides(unittest.TestCase):
    def test_excludes_front_matter_and_commentary(self) -> None:
        entries = [
            {"resource_key": "story1", "resource_id": "0x1", "category": "front_matter", "title": "Pub"},
            {"resource_key": "story2", "resource_id": "0x2", "category": "front_matter", "title": "Faith"},
            {"resource_key": "story3", "resource_id": "0x3", "category": "communion_liturgy", "title": "COMMENTARY ON THE HOLY COMMUNION"},
            {"resource_key": "story10", "resource_id": "0x4", "category": "creed_and_confession", "title": "THE APOSTLES’ CREED"},
        ]
        eligible, excluded = select_eligible_entries(entries)
        self.assertEqual([e["resource_key"] for e in eligible], ["story10"])
        self.assertEqual([e["resource_key"] for e in excluded], ["story1", "story2", "story3"])
        self.assertTrue(EXCLUDED_KEYS.issuperset({"story1", "story2", "story3"}))

    def test_preserves_text_speaker_labels_and_is_deterministic(self) -> None:
        sample = (
            "CONFESSION\n"
            "[All kneel]\n\n"
            "Leader: Almighty God, our heavenly Father,\n"
            "we have sinned against you.\n\n"
            "People: Lord, have mercy.\n"
            "Christ, have mercy.\n"
        )
        slides_a = split_into_slides(sample, max_lines=4, max_chars=120)
        slides_b = split_into_slides(sample, max_lines=4, max_chars=120)
        self.assertEqual(slides_a, slides_b)
        joined = "\n".join(slides_a)
        self.assertIn("Leader: Almighty God, our heavenly Father,", joined)
        self.assertIn("People: Lord, have mercy.", joined)
        self.assertIn("[All kneel]", joined)

    def test_searchable_title_handles_generic_titles(self) -> None:
        t1 = build_searchable_title(
            {"resource_key": "story30", "title": "ORDER OF SERVICE FOR"},
            "ORDER OF SERVICE FOR\nBAPTISM\n[All stand]",
        )
        self.assertIn("BAPTISM", t1)
        self.assertIn("Come and Worship", t1)


class TestBatchImportIdempotency(unittest.TestCase):
    def test_idempotent_and_preserves_locally_edited_items(self) -> None:
        openlp_root = Path(r"D:\OpenLPxx\openlp-source")
        if str(openlp_root) not in sys.path:
            sys.path.insert(0, str(openlp_root))
        from openlp.core.common.registry import Registry
        from openlp.core.common.settings import Settings
        from openlp.plugins.custom.lib.db import CustomSlide
        from import_come_and_worship_custom import import_liturgy_collection

        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            Registry.create()
            Settings.setDefaultFormat(Settings.IniFormat)
            Settings.set_filename(tmp_p / "test.ini")
            Registry().register("settings", Settings())

            src_dir = tmp_p / "src"
            (src_dir / "resources").mkdir(parents=True)
            (src_dir / "resources" / "story01.txt").write_text("Pub info", encoding="utf-8")
            (src_dir / "resources" / "story17.txt").write_text("CONFESSION\nLeader: Pray\nPeople: Amen.", encoding="utf-8")
            index_data = {
                "entries": [
                    {
                        "resource_key": "story1",
                        "resource_id": "0x7f1100ef",
                        "category": "front_matter",
                        "title": "Pub info",
                        "extracted_path": "resources/story01.txt",
                    },
                    {
                        "resource_key": "story17",
                        "resource_id": "0x7f1100f7",
                        "category": "creed_and_confession",
                        "title": "CONFESSION",
                        "extracted_path": "resources/story17.txt",
                    },
                ]
            }
            import json
            (src_dir / "index.json").write_text(json.dumps(index_data), encoding="utf-8")
            db_path = tmp_p / "custom.sqlite"

            r1 = import_liturgy_collection(src_dir, db_path)
            self.assertEqual(len(r1["imported"]), 1)
            self.assertEqual(len(r1["excluded"]), 1)
            self.assertEqual(len(r1["existing"]), 0)

            # Simulate local operator edit of title & text
            from openlp.core.db.manager import DBManager
            from openlp.plugins.custom.lib.db import init_schema
            mgr = DBManager("custom", init_schema, db_file_path=db_path)
            slide = mgr.get_all_objects(CustomSlide)[0]
            slide.title = "My Locally Edited Confession"
            slide.text = "<song version=\"1.0\"><lyrics language=\"en\"><verse type=\"custom\" label=\"1\"><![CDATA[Local edit]]></verse></lyrics></song>"
            mgr.save_object(slide)
            bind = mgr.session.bind
            mgr.session.close()
            if bind is not None:
                bind.dispose()

            # Second run must NOT duplicate or overwrite local edit
            r2 = import_liturgy_collection(src_dir, db_path)
            self.assertEqual(len(r2["imported"]), 0)
            self.assertEqual(len(r2["existing"]), 1)

            mgr2 = DBManager("custom", init_schema, db_file_path=db_path)
            slides_after = mgr2.get_all_objects(CustomSlide)
            self.assertEqual(len(slides_after), 1)
            self.assertEqual(slides_after[0].title, "My Locally Edited Confession")
            self.assertIn("Local edit", slides_after[0].text)
            bind2 = mgr2.session.bind
            mgr2.session.close()
            if bind2 is not None:
                bind2.dispose()


if __name__ == "__main__":
    unittest.main()
