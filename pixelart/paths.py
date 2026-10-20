"""Separa los recursos empaquetados de los datos persistentes del usuario."""

import os
from pathlib import Path
import sys


def data_directory():
    # Un EXE escribe fuera de su paquete, también si se instala en Program Files.
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "PixelArtStudio"
    return Path(__file__).resolve().parent.parent / "data"
