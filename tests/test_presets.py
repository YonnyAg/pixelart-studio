from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from pixelart.history import History
from pixelart.presets import Presets, Settings
from pixelart.paths import data_directory


class PresetTests(unittest.TestCase):
    def test_packaged_data_is_outside_application(self):
        with TemporaryDirectory() as directory:
            with patch("sys.frozen", True, create=True), patch.dict("os.environ", {"LOCALAPPDATA": directory}):
                self.assertEqual(data_directory(), Path(directory) / "PixelArtStudio")

    def test_persist_replace_delete_and_independent_history(self):
        with TemporaryDirectory() as directory:
            history = History(Path(directory))
            presets = Presets(history)
            settings = Settings(32, 48, 4, 16, False)
            presets.save("  Mi preset  ", settings)
            reopened = Presets(History(Path(directory)))
            self.assertEqual(reopened.load("Mi preset"), settings)
            presets.save("Mi preset", Settings())
            self.assertEqual(reopened.load("Mi preset"), Settings())
            history.clear()
            self.assertEqual(reopened.names(), ["Mi preset"])
            presets.delete("Mi preset")
            self.assertEqual(reopened.names(), [])
            with self.assertRaises(ValueError):
                reopened.load("Mi preset")

    def test_reject_invalid_configuration_and_names(self):
        for settings in ({"width": 0}, {"scale": 17}, {"colors": 3}, {"keep_ratio": 1},
                         {"width": True}, {"width": 512, "height": 512, "scale": 16}):
            with self.assertRaises(ValueError):
                Settings(**settings)
        with TemporaryDirectory() as directory:
            presets = Presets(History(Path(directory)))
            for name in (" ", "a" * 61):
                with self.assertRaises(ValueError):
                    presets.save(name, Settings())
