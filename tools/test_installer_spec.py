import unittest
from pathlib import Path

ISS_PATH = Path(r"D:\OpenLPxx\distribution\build-scripts\OpenLP-Anglican.iss")


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

    def test_iss_protects_existing_user_data_from_overwrite(self) -> None:
        text = ISS_PATH.read_text(encoding="utf-8")
        self.assertIn("onlyifdoesntexist", text)
        self.assertIn("uninsneveruninstall", text)
        self.assertIn("ShouldInitializeUserData", text)
        self.assertIn("--portable --portable-path", text)


if __name__ == "__main__":
    unittest.main()
