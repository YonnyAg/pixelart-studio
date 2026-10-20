"""Verifica widgets y conversión asíncrona sin dejar ventanas abiertas."""

from pathlib import Path
from tempfile import TemporaryDirectory
import time
from unittest.mock import patch
from types import SimpleNamespace

from PIL import Image

from pixelart.history import History
from pixelart.ui import PixelArtApp


with TemporaryDirectory() as directory:
    with patch("pixelart.ui.History", lambda: History(Path(directory))):
        app = PixelArtApp()
    app.update()
    try:
        app.source = Image.new("RGBA", (120, 80), (80, 180, 250, 160))
        app.show_preview("Original", app.source)
        app.convert()
        deadline = time.monotonic() + 10
        while app.busy and time.monotonic() < deadline:
            app.update()
            time.sleep(0.02)
        assert not app.busy, "La tarea no terminó a tiempo"
        assert app.result is not None
        assert app.result.size == (512, 344)
        assert len(app.history.entries()) == 1
        identifier = app.history.entries()[0][0]
        app.restore(identifier, "restaurada")
        deadline = time.monotonic() + 10
        while app.busy and time.monotonic() < deadline:
            app.update()
            time.sleep(0.02)
        assert not app.busy
        assert app.result_name == "restaurada"
        assert app.source_name == "imagen"
        viewer = app.previews["PixelArt"]
        app.update()
        original_bytes = app.result.tobytes()
        viewer.set_zoom(1.0)
        app.update()
        assert viewer.zoom == 1.0
        viewer.on_wheel(SimpleNamespace(delta=120))
        app.update()
        assert viewer.zoom == 1.25
        viewer.set_zoom(16)
        app.update()
        # La memoria del bitmap de vista previa depende del panel, no del zoom.
        assert viewer.photo.width() == viewer.canvas.winfo_width()
        assert viewer.photo.height() == viewer.canvas.winfo_height()
        viewer.scroll_x("moveto", 0.5)
        viewer.scroll_y("moveto", 0.5)
        app.update()
        assert viewer.canvas.xview()[0] > 0
        assert viewer.canvas.yview()[0] > 0
        viewer.fit()
        app.update()
        assert viewer.fit_mode
        assert app.result.tobytes() == original_bytes
        # Cancelar no elimina datos. Aceptar elimina registro y PNG.
        with patch("pixelart.ui.messagebox.askyesno", return_value=False):
            app.clear_history()
        assert len(app.history.entries()) == 1
        with patch("pixelart.ui.messagebox.askyesno", return_value=True):
            app.delete_history_entry(identifier)
        deadline = time.monotonic() + 10
        while app.busy and time.monotonic() < deadline:
            app.update()
            time.sleep(0.02)
        assert not app.busy
        assert app.history.entries() == []
        assert not app.history.path_for(identifier).exists()
        assert app.result is not None  # La vista sigue disponible para exportar.
        app.history.add(app.result, "to clear")
        app.refresh_history()
        with patch("pixelart.ui.messagebox.askyesno", return_value=True):
            app.clear_history()
        deadline = time.monotonic() + 10
        while app.busy and time.monotonic() < deadline:
            app.update()
            time.sleep(0.02)
        assert not app.busy
        assert app.history.entries() == []
        assert app.clear_history_button.cget("state") == "disabled"
        print("Interfaz, conversión, zoom, desplazamiento y eliminación del historial: OK")
    finally:
        app.close()
