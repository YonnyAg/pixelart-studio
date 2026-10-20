"""Pruebas de dimensiones, alfa, exportación y persistencia real."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

from pixelart.converter import export_image, load_image, pixelate
from pixelart.history import History


class ConversionTests(unittest.TestCase):
    def test_ratio_and_integer_blocks(self):
        source = Image.new("RGBA", (100, 50), (80, 100, 200, 128))
        result = pixelate(source, 20, 20, scale=4, colors=8)
        self.assertEqual(result.size, (80, 40))
        self.assertEqual(result.getpixel((0, 0))[3], 128)
        self.assertEqual(result.getpixel((0, 0)), result.getpixel((3, 3)))

    def test_exact_dimensions(self):
        result = pixelate(Image.new("RGBA", (100, 50)), 7, 9, 3, 0, False)
        self.assertEqual(result.size, (21, 27))

    def test_reject_invalid_size_and_large_output(self):
        for width, height, scale in [(0, 10, 1), (513, 10, 1), (512, 512, 16)]:
            with self.assertRaises(ValueError):
                pixelate(Image.new("RGBA", (32, 32)), width, height, scale)

    def test_exports(self):
        source = Image.new("RGBA", (8, 8), (255, 0, 0, 0))
        with TemporaryDirectory() as directory:
            for suffix in ("png", "webp", "jpg"):
                path = Path(directory) / f"result.{suffix}"
                export_image(source, path)
                loaded = load_image(path)
                self.assertEqual(loaded.size, (8, 8))
                if suffix == "jpg":
                    self.assertEqual(loaded.getpixel((0, 0)), (255, 255, 255, 255))
                else:
                    self.assertEqual(loaded.getpixel((0, 0))[3], 0)

    def test_history_persists_and_prunes(self):
        with TemporaryDirectory() as directory:
            history = History(Path(directory), limit=2)
            for name in ("one", "two", "three"):
                history.add(Image.new("RGBA", (8, 8)), name)
            reopened = History(Path(directory), limit=2)
            self.assertEqual([row[1] for row in reopened.entries()], ["three", "two"])
            self.assertEqual(len(list(Path(directory).glob("*.png"))), 2)
            for row in reopened.entries():
                self.assertEqual(load_image(reopened.path_for(row[0])).size, (8, 8))

    def test_delete_and_clear_preserve_exports(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            history = History(root / "history")
            image = Image.new("RGBA", (8, 8), "red")
            exported = root / "manual_export.png"
            export_image(image, exported)
            history.add(image, "one")
            history.add(image, "two")
            identifier = history.entries()[0][0]
            history.delete(identifier)
            self.assertFalse(history.path_for(identifier).exists())
            self.assertEqual([row[1] for row in history.entries()], ["one"])
            history.delete(identifier)  # Repetir una eliminación es inocuo.
            history.clear()
            self.assertEqual(History(root / "history").entries(), [])
            self.assertEqual(list((root / "history").glob("*.png")), [])
            self.assertTrue(exported.exists())

    def test_delete_rejects_paths_and_handles_missing_png(self):
        with TemporaryDirectory() as directory:
            history = History(Path(directory))
            with self.assertRaises(ValueError):
                history.delete("../manual_export")
            history.add(Image.new("RGBA", (4, 4)), "missing")
            identifier = history.entries()[0][0]
            history.path_for(identifier).unlink()
            history.clear()
            self.assertEqual(history.entries(), [])


if __name__ == "__main__":
    unittest.main()
