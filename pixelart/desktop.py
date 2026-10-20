"""Identidad de escritorio y recursos de la aplicación."""

import ctypes
from pathlib import Path
import sys
import tkinter as tk


ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
APP_ID = "PixelArtStudio.Desktop.1"


def has_package_identity():
    """Windows asigna su propia identidad a una aplicación instalada por MSIX."""
    if sys.platform != "win32":
        return False
    get_package = ctypes.windll.kernel32.GetCurrentPackageFullName
    get_package.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_wchar_p]
    get_package.restype = ctypes.c_long
    length = ctypes.c_uint32(0)
    result = get_package(ctypes.byref(length), None)
    if result == 15700:  # APPMODEL_ERROR_NO_PACKAGE
        return False
    if result in (0, 122):  # ERROR_SUCCESS / ERROR_INSUFFICIENT_BUFFER
        return length.value > 0
    raise ctypes.WinError(result)


def configure_app_identity():
    """Se ejecuta antes de crear ventanas para identificar el proceso en Windows."""
    if sys.platform == "win32" and not has_package_identity():
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
