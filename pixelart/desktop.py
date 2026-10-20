"""Identidad de escritorio y recursos de la aplicación."""

import ctypes
from pathlib import Path
import sys
import tkinter as tk


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
APP_ID = "PixelArtStudio.Desktop.1"


def configure_app_identity():
    """Se ejecuta antes de crear ventanas para identificar el proceso en Windows."""
    if sys.platform == "win32":
        set_app_id = ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID
        set_app_id.argtypes = [ctypes.c_wchar_p]
        set_app_id.restype = ctypes.c_long
        result = set_app_id(APP_ID)
        if result < 0:
            raise OSError(f"Windows no pudo asignar la identidad de la aplicación: {result}")


def apply_window_icon(window):
    """El ICO contiene tamaños nativos para distintas escalas de Windows."""
    if sys.platform == "win32":
        # CustomTkinter respeta iconbitmap cuando ya se ha llamado al método;
        # no hace falta depender de una espera arbitraria al arrancar.
        icon_path = str(ASSETS_DIR / "app-icon.ico")
        window.iconbitmap(default=icon_path)
        window.iconbitmap(icon_path)
    else:
        window._app_icon = tk.PhotoImage(master=window, file=str(ASSETS_DIR / "app-icon.png"))
        window.iconphoto(True, window._app_icon)
