"""Comparación con el mismo encuadre relativo, aunque cambie la resolución."""

import customtkinter as ctk
from .viewer import ImageViewer


class Comparison(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.syncing = False
        self.grid_columnconfigure((0, 1), weight=1, uniform="comparison")
        self.grid_rowconfigure(1, weight=1)
        self.viewers = []
        for column, title in enumerate(("Original", "PixelArt")):
            ctk.CTkLabel(self, text=title, font=("Segoe UI", 14, "bold")).grid(row=0, column=column)
            viewer = ImageViewer(self, "Convierte una imagen para comparar", pixel_art=column == 1)
            viewer.grid(row=1, column=column, sticky="nsew", padx=4)
            viewer.on_view_change = self.synchronize
            self.viewers.append(viewer)

    def set_images(self, original, result):
        self.syncing = True
        try:
            self.viewers[0].set_image(original)
            self.viewers[1].set_image(result)
            if original is None and result is not None:
                self.viewers[0].clear("El historial conserva solo el resultado.\nAbre y convierte una imagen para comparar.")
        finally:
            self.syncing = False

    def synchronize(self, source):
        if self.syncing:
            return
        target = self.viewers[1] if source is self.viewers[0] else self.viewers[0]
        if source.image is None or target.image is None:
            return
        self.syncing = True
        try:
            if source.fit_mode:
                target.fit()
            else:
                target.apply_normalized_view(source.normalized_view())
        finally:
            self.syncing = False
