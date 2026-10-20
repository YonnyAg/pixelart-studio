"""Prueba del programa empaquetado, con datos temporales y cierre automático."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import traceback

from PIL import Image
from .converter import export_image, load_image
from .history import History
from .presets import Settings
from .ui import PixelArtApp


def run_smoke_test(report_path):
    report = {"ok": False}
    app = None
    try:
        with TemporaryDirectory() as directory:
            try:
                app = PixelArtApp(history=History(Path(directory) / "data"))
                app.update()
                app.withdraw()
                app.source = Image.new("RGBA", (120, 80), (80, 180, 250, 160))
                app.show_preview("Original", app.source)
                app.presets.save("Prueba", Settings(48, 32, 4, 16, True))
                app.refresh_presets("Prueba")
                app.apply_preset("Prueba")
                assert app.current_settings() == Settings(48, 32, 4, 16, True)
                app.convert()
                deadline = time.monotonic() + 15
                while app.busy and time.monotonic() < deadline:
                    app.update()
                    time.sleep(0.02)
                assert not app.busy and app.result is not None
                assert app.result.size == (192, 128)
                app.tabs.set("Comparar")
                app.deiconify()
                app.update()
                left, right = app.comparison.viewers
                left.set_zoom(8)
                app.update()
                assert abs(left.normalized_view()[0] - right.normalized_view()[0]) < 0.02
                left.scroll_x("moveto", 0.3)
                left.scroll_y("moveto", 0.2)
                app.update()
                for a, b in zip(left.normalized_view(), right.normalized_view()):
                    assert abs(a - b) < 0.025, (left.normalized_view(), right.normalized_view())
                left.fit()
                app.update()
                assert left.fit_mode and right.fit_mode
                output = Path(directory) / "export.png"
                export_image(app.result, output)
                assert load_image(output).size == (192, 128)
                app.history.clear()
                assert app.history.entries() == []
                assert app.presets.names() == ["Prueba"]
                report = {"ok": True, "checks": ["window_icon", "presets", "conversion", "comparison",
                                                    "synchronized_zoom_and_pan", "export", "history"]}
            finally:
                if app is not None:
                    app.close()
    except Exception:
        report["error"] = traceback.format_exc()
    Path(report_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0 if report["ok"] else 1
