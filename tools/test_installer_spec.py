import configparser
import json
import unittest
from pathlib import Path

ISS_PATH = Path(r"D:\OpenLPxx\distribution\build-scripts\OpenLP-Anglican.iss")
STAGING_DATA = Path(r"D:\OpenLPxx\distribution\content-staging\Data")
STAGING_THEMES = STAGING_DATA / "themes"
STAGING_INI = STAGING_DATA / "OpenLP.ini"

OFFICIAL_THEMES = (
    "Blue Burst",
    "Clouds",
    "Geo Purple",
    "Moss on tree",
    "Sea with trees",
    "Wheat",
)


class TestInnoSetupScript(unittest.TestCase):
    def test_iss_exists_and_declares_core_sections(self) -> None:
        self.assertTrue(ISS_PATH.exists(), f"Missing {ISS_PATH}")
        text = ISS_PATH.read_text(encoding="utf-8")
        for section in ("[Setup]", "[Tasks]", "[Files]", "[Icons]", "[Code]"):
            self.assertIn(section, text)
        self.assertIn("OutputBaseFilename=OpenLP-3.1.7-Anglican-Setup", text)
        self.assertIn("AppName=OpenLP", text)
        self.assertIn("AppVersion=3.1.7", text)
        self.assertIn(r"DefaultDirName={autopf}\OpenLP Anglican", text)
        self.assertIn("AppId={{8F9E2B61-5D4C-4A31-9B7E-3170A6E1C062}", text)

    def test_iss_protects_existing_user_data_from_overwrite(self) -> None:
        text = ISS_PATH.read_text(encoding="utf-8")
        self.assertIn("onlyifdoesntexist", text)
        self.assertIn("uninsneveruninstall", text)
        self.assertIn("ShouldInitializeUserData", text)
        self.assertIn("--portable --portable-path", text)

    def test_iss_bundles_themes_and_preserves_customizations(self) -> None:
        text = ISS_PATH.read_text(encoding="utf-8")
        expected_line = (
            r'Source: "{#StagingRoot}\Data\themes\*"; '
            r'DestDir: "{code:GetProfileDir}\Data\themes"; '
            r'Flags: onlyifdoesntexist uninsneveruninstall recursesubdirs createallsubdirs'
        )
        self.assertIn(expected_line, text)
        # Ensure themes copy is not blocked on upgrade by ShouldInitializeUserData
        for line in text.splitlines():
            if r"{#StagingRoot}\Data\themes\*" in line:
                self.assertNotIn("ShouldInitializeUserData", line)
                self.assertIn("onlyifdoesntexist", line)
                self.assertIn("uninsneveruninstall", line)


class TestStagedThemes(unittest.TestCase):
    def test_six_official_themes_staged_with_assets_and_previews(self) -> None:
        self.assertTrue(STAGING_THEMES.is_dir(), f"Missing {STAGING_THEMES}")
        for name in OFFICIAL_THEMES:
            theme_dir = STAGING_THEMES / name
            self.assertTrue(theme_dir.is_dir(), f"Missing theme directory: {theme_dir}")

            json_file = theme_dir / f"{name}.json"
            self.assertTrue(json_file.is_file(), f"Missing theme JSON: {json_file}")
            data = json.loads(json_file.read_text(encoding="utf-8"))
            self.assertEqual(data.get("theme_name"), name)

            bg_info = data.get("background_filename")
            self.assertIsInstance(bg_info, dict, f"Missing background_filename in {json_file}")
            parts = bg_info.get("parts", [])
            self.assertTrue(parts, f"Empty background_filename parts in {json_file}")
            bg_path = STAGING_THEMES.joinpath(*parts)
            self.assertTrue(bg_path.is_file(), f"Missing background image {bg_path} for {name}")

            preview_png = STAGING_THEMES / f"{name}.png"
            thumb_png = STAGING_THEMES / "thumbnails" / f"{name}.png"
            self.assertTrue(preview_png.is_file(), f"Missing preview PNG: {preview_png}")
            self.assertTrue(thumb_png.is_file(), f"Missing thumbnail PNG: {thumb_png}")

    def test_staged_ini_sets_blue_burst_as_default_global_theme(self) -> None:
        self.assertTrue(STAGING_INI.is_file(), f"Missing {STAGING_INI}")
        parser = configparser.RawConfigParser()
        parser.read(STAGING_INI, encoding="utf-8")
        self.assertTrue(parser.has_section("themes"))
        self.assertEqual(parser.get("themes", "global%20theme"), "Blue Burst")
        self.assertEqual(parser.get("core", "has%20run%20wizard"), "true")


if __name__ == "__main__":
    unittest.main()
