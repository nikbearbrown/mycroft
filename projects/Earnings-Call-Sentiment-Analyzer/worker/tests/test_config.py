import tempfile
import unittest
from pathlib import Path

from app.config import Settings


class SettingsTest(unittest.TestCase):
    def test_resolves_files_inside_upload_directory(self):
        with tempfile.TemporaryDirectory() as upload_dir:
            settings = Settings(upload_dir=upload_dir)
            expected = Path(upload_dir, "call.txt").resolve()

            self.assertEqual(expected, settings.resolve_upload_path("call.txt"))

    def test_rejects_files_outside_upload_directory(self):
        with tempfile.TemporaryDirectory() as upload_dir:
            settings = Settings(upload_dir=upload_dir)

            with self.assertRaises(ValueError):
                settings.resolve_upload_path("../outside.txt")


if __name__ == "__main__":
    unittest.main()
