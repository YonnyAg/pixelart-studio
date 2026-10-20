"""Visor con zoom y desplazamiento, sin ampliar la imagen completa en memoria."""

import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk


class ImageViewer(ctk.CTkFrame):
    def __init__(self, master, empty_text, pixel_art=False):
        super().__init__(master, fg_color="transparent")
        self.image = None
        self.pixel_art = pixel_art
        self.empty_text = empty_text
        self.zoom = 1.0
        self.fit_mode = True
        self.pending_render = None
        self.photo = None
        self.on_view_change = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.buttons = []
        for text, command in (("−", lambda: self.change_zoom(1 / 1.25)),
                              ("＋", lambda: self.change_zoom(1.25)),
                              ("100%", lambda: self.set_zoom(1.0)),
                              ("Ajustar", self.fit)):
            button = ctk.CTkButton(toolbar, text=text, width=48, command=command, state="disabled")
            button.pack(side="left", padx=(0, 6))
            self.buttons.append(button)
        self.zoom_text = ctk.StringVar(value="—")
        ctk.CTkLabel(toolbar, textvariable=self.zoom_text, text_color="#aab8d6").pack(side="left", padx=8)
        self.canvas = tk.Canvas(self, bg="#111827", highlightthickness=0, borderwidth=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.vertical = ctk.CTkScrollbar(self, command=self.scroll_y)
        self.vertical.grid(row=1, column=1, sticky="ns")
        self.horizontal = ctk.CTkScrollbar(self, orientation="horizontal", command=self.scroll_x)
        self.horizontal.grid(row=2, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=self.horizontal.set, yscrollcommand=self.vertical.set)
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<MouseWheel>", self.on_wheel)
        self.canvas.bind("<Button-4>", lambda event: self.change_zoom(1.25))
        self.canvas.bind("<Button-5>", lambda event: self.change_zoom(1 / 1.25))
        self.canvas.bind("<ButtonPress-1>", lambda event: self.canvas.scan_mark(event.x, event.y))
        self.canvas.bind("<B1-Motion>", self.on_drag)
        ctk.CTkLabel(self, text="Rueda: zoom · Arrastra para desplazarte · 100%: tamaño real",
                     wraplength=280, text_color="#8b98b9", font=("Segoe UI", 11)).grid(
            row=3, column=0, columnspan=2, sticky="w")

    def set_image(self, image):
        self.image = image
        for button in self.buttons:
            button.configure(state="normal" if image is not None else "disabled")
        self.fit_mode = True
        self.fit()

    def clear(self, text):
        self.empty_text = text
        self.set_image(None)

    def fit(self):
        self.fit_mode = True
        if self.image is not None:
            self.zoom = min(max(1, self.canvas.winfo_width()) / self.image.width,
                            max(1, self.canvas.winfo_height()) / self.image.height, 16)
        self.update_region()
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.schedule_render()
        self.notify_view_change()

    def set_zoom(self, zoom, *, clamp=True):
        if self.image is None:
            return
        # Conserva el punto central al cambiar el nivel de zoom.
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        old_width = max(width, round(self.image.width * self.zoom))
        old_height = max(height, round(self.image.height * self.zoom))
        offset_x = (old_width - self.image.width * self.zoom) / 2
        offset_y = (old_height - self.image.height * self.zoom) / 2
        center_x = (self.canvas.canvasx(width / 2) - offset_x) / self.zoom
        center_y = (self.canvas.canvasy(height / 2) - offset_y) / self.zoom
        self.zoom = max(0.1, min(16.0, zoom)) if clamp else zoom
        self.fit_mode = False
        self.update_region()
        total_width = max(width, round(self.image.width * self.zoom))
        total_height = max(height, round(self.image.height * self.zoom))
        self.canvas.xview_moveto((center_x * self.zoom + (total_width - self.image.width * self.zoom) / 2 - width / 2) / total_width)
        self.canvas.yview_moveto((center_y * self.zoom + (total_height - self.image.height * self.zoom) / 2 - height / 2) / total_height)
        self.schedule_render()
        self.notify_view_change()

    def change_zoom(self, factor):
        self.set_zoom(self.zoom * factor)

    def update_region(self):
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        size = (max(width, round(self.image.width * self.zoom)),
                max(height, round(self.image.height * self.zoom))) if self.image else (width, height)
        self.canvas.configure(scrollregion=(0, 0, *size))

    def on_resize(self, event):
        if self.fit_mode:
            self.fit()
        else:
            self.update_region()
            self.schedule_render()

    def on_wheel(self, event):
        if event.delta:
            self.change_zoom(1.25 if event.delta > 0 else 1 / 1.25)
        return "break"

    def on_drag(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.schedule_render()
        self.notify_view_change()

    def scroll_x(self, *args):
        self.canvas.xview(*args)
        self.schedule_render()
        self.notify_view_change()

    def scroll_y(self, *args):
        self.canvas.yview(*args)
        self.schedule_render()
        self.notify_view_change()

    def notify_view_change(self):
        if self.image is not None and self.on_view_change is not None:
            self.on_view_change(self)

    def normalized_view(self):
        """Zoom relativo al panel y centro relativo a la imagen (0..1)."""
        width, height = max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height())
        scaled_width, scaled_height = self.image.width * self.zoom, self.image.height * self.zoom
        center_x = (self.canvas.canvasx(width / 2) - max(0, (width - scaled_width) / 2)) / scaled_width
        center_y = (self.canvas.canvasy(height / 2) - max(0, (height - scaled_height) / 2)) / scaled_height
        return scaled_width / width, center_x, center_y

    def apply_normalized_view(self, state):
        coverage, center_x, center_y = state
        width, height = max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height())
        self.set_zoom(coverage * width / self.image.width, clamp=False)
        scaled_width, scaled_height = self.image.width * self.zoom, self.image.height * self.zoom
        total_width, total_height = max(width, round(scaled_width)), max(height, round(scaled_height))
        self.canvas.xview_moveto((center_x * scaled_width + max(0, (width - scaled_width) / 2) - width / 2) / total_width)
        self.canvas.yview_moveto((center_y * scaled_height + max(0, (height - scaled_height) / 2) - height / 2) / total_height)
        self.schedule_render()

    def schedule_render(self):
        if self.pending_render is None:
            self.pending_render = self.after_idle(self.render)

    def render(self):
        self.pending_render = None
        self.canvas.delete("all")
        if self.image is None:
            self.photo = None
            self.zoom_text.set("—")
            self.canvas.create_text(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2,
                                    text=self.empty_text, fill="#8b98b9")
            return
        width, height = max(1, self.canvas.winfo_width()), max(1, self.canvas.winfo_height())
        x, y = self.canvas.canvasx(0), self.canvas.canvasy(0)
        offset_x = max(0, (width - self.image.width * self.zoom) / 2)
        offset_y = max(0, (height - self.image.height * self.zoom) / 2)
        # Renderiza únicamente la región visible: un zoom de 1600% sigue usando
        # un bitmap del tamaño del panel, incluso con imágenes grandes.
        box = ((x - offset_x) / self.zoom, (y - offset_y) / self.zoom,
               (x + width - offset_x) / self.zoom, (y + height - offset_y) / self.zoom)
        preview = self.image.transform((width, height), Image.Transform.EXTENT, box,
            resample=Image.Resampling.NEAREST if self.pixel_art else Image.Resampling.BICUBIC)
        background = Image.new("RGBA", (width, height), "#202a40")
        draw = ImageDraw.Draw(background)
        for top in range(0, height, 12):
            for left in range(0, width, 12):
                if (left // 12 + top // 12) % 2:
                    draw.rectangle((left, top, left + 11, top + 11), fill="#2b3650")
        background.alpha_composite(preview)
        self.photo = ImageTk.PhotoImage(background, master=self.canvas)
        self.canvas.create_image(x, y, image=self.photo, anchor="nw")
        self.zoom_text.set(f"{self.zoom * 100:.0f}%")

    def destroy(self):
        if self.pending_render is not None:
            self.after_cancel(self.pending_render)
        super().destroy()
