"""Punto de entrada del código fuente y del ejecutable sin consola."""

import os
import sys

# PyInstaller --windowed deja estos streams en None. Algunas dependencias
# escriben diagnósticos en stderr al importar; necesitan un stream válido.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

from pixelart.ui import PixelArtApp


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--smoke-test":
        from pixelart.diagnostics import run_smoke_test
        raise SystemExit(run_smoke_test(sys.argv[2]))
    PixelArtApp().mainloop()
