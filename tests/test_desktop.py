from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from pixelart.desktop import configure_app_identity


class DesktopIdentityTests(unittest.TestCase):
    def test_msix_keeps_windows_package_identity(self):
        set_identity = Mock(return_value=0)
        api = SimpleNamespace(shell32=SimpleNamespace(SetCurrentProcessExplicitAppUserModelID=set_identity))
        with patch("pixelart.desktop.sys.platform", "win32"), \
             patch("pixelart.desktop.has_package_identity", return_value=True), \
             patch("pixelart.desktop.ctypes.windll", api, create=True):
            configure_app_identity()
        set_identity.assert_not_called()

    def test_portable_keeps_custom_taskbar_identity(self):
        set_identity = Mock(return_value=0)
        api = SimpleNamespace(shell32=SimpleNamespace(SetCurrentProcessExplicitAppUserModelID=set_identity))
        with patch("pixelart.desktop.sys.platform", "win32"), \
             patch("pixelart.desktop.has_package_identity", return_value=False), \
             patch("pixelart.desktop.ctypes.windll", api, create=True):
            configure_app_identity()
        set_identity.assert_called_once_with("PixelArtStudio.Desktop.1")
