"""Interfaz oscura adaptable; el procesamiento ocurre fuera del hilo gráfico."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .converter import export_image, load_image, pixelate
from .history import History
from .viewer import ImageViewer
from .desktop import configure_app_identity, apply_window_icon
from .presets import Presets, Settings
from .comparison import Comparison


class PixelArtApp(ctk.CTk):
    def __init__(self, history=None):
        configure_app_identity()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        super().__init__()
        apply_window_icon(self)
        self.title("PixelArt Studio")
        self.geometry("1200x820")
        self.minsize(1020, 740)
        self.configure(fg_color="#0c1020")
        self.source = None
        self.result = None
        self.source_name = "imagen"
        self.result_name = "imagen"
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.busy = False
        self.history = history if history is not None else History()
        self.presets = Presets(self.history)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build()
        self.refresh_history()
        self.refresh_presets()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=28, pady=(24, 18))
        ctk.CTkLabel(header, text="▦  PixelArt Studio", font=("Segoe UI", 27, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="TU IMAGEN. CADA PÍXEL.", text_color="#8b98b9",
                     font=("Segoe UI", 11, "bold")).pack(side="right")

        controls = ctk.CTkScrollableFrame(self, width=250, corner_radius=18, fg_color="#151c30")
        controls.grid(row=1, column=0, sticky="ns", padx=(24, 14), pady=(0, 20))
        controls.grid_columnconfigure(0, weight=1)
        self.open_button = ctk.CTkButton(controls, text="＋  Abrir imagen", height=44,
                                        command=self.open_image)
        self.open_button.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(controls, text="01 / CUADRÍCULA", text_color="#8b98b9",
                     anchor="w").grid(row=1, column=0, sticky="ew", padx=20, pady=(8, 8))
        dimensions = ctk.CTkFrame(controls, fg_color="transparent")
        dimensions.grid(row=2, column=0, padx=20)
        self.width_input = self._dimension(dimensions, "Ancho", 0)
        self.height_input = self._dimension(dimensions, "Alto", 1)
        self.keep_ratio = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(controls, text="Mantener proporción", variable=self.keep_ratio).grid(
            row=3, column=0, padx=20, pady=18, sticky="w")
        ctk.CTkLabel(controls, text="02 / ACABADO", text_color="#8b98b9",
                     anchor="w").grid(row=4, column=0, padx=20, sticky="ew", pady=(10, 8))
        ctk.CTkLabel(controls, text="Escala de exportación", anchor="w").grid(
            row=5, column=0, padx=20, sticky="ew")
        self.scale = ctk.CTkOptionMenu(controls, values=[str(n) for n in range(1, 17)])
        self.scale.set("8")
        self.scale.grid(row=6, column=0, padx=20, pady=(4, 14), sticky="ew")
        ctk.CTkLabel(controls, text="Paleta de colores", anchor="w").grid(
            row=7, column=0, padx=20, sticky="ew")
        self.colors = ctk.CTkOptionMenu(controls, values=["Sin límite", "8", "16", "32", "64", "128", "256"])
        self.colors.set("32")
        self.colors.grid(row=8, column=0, padx=20, pady=(4, 20), sticky="ew")
        self.convert_button = ctk.CTkButton(controls, text="Crear PixelArt  →", height=44,
                                           fg_color="#7559ed", hover_color="#6145d3",
                                           command=self.convert, state="disabled")
        self.convert_button.grid(row=9, column=0, padx=20, pady=10, sticky="ew")
        self.save_button = ctk.CTkButton(controls, text="↓  Guardar imagen", height=40,
                                        fg_color="#273451", hover_color="#354669",
                                        command=self.save_image, state="disabled")
        self.save_button.grid(row=10, column=0, padx=20, pady=(0, 12), sticky="ew")
        ctk.CTkLabel(controls, text="Cuadrícula × escala = tamaño final\nPNG conserva la transparencia.",
                     text_color="#8b98b9", font=("Segoe UI", 11)).grid(
            row=11, column=0, padx=20, pady=12)

        ctk.CTkLabel(controls, text="03 / PRESETS", text_color="#8b98b9", anchor="w").grid(
            row=12, column=0, sticky="ew", padx=20, pady=(12, 4))
        self.preset_menu = ctk.CTkOptionMenu(controls, values=["Sin presets"], command=self.apply_preset)
        self.preset_menu.grid(row=13, column=0, padx=20, pady=6, sticky="ew")
        ctk.CTkButton(controls, text="Guardar configuración", command=self.save_preset).grid(
            row=14, column=0, padx=20, pady=6, sticky="ew")
        self.delete_preset_button = ctk.CTkButton(controls, text="Eliminar preset", command=self.delete_preset,
            fg_color="#493047", hover_color="#633d54")
        self.delete_preset_button.grid(row=15, column=0, padx=20, pady=(6, 20), sticky="ew")

        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.grid(row=1, column=1, sticky="nsew", padx=(0, 24), pady=(0, 20))
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_rowconfigure(0, weight=1)
        self.tabs = ctk.CTkTabview(workspace, fg_color="#151c30", corner_radius=18)
        self.tabs.grid(row=0, column=0, sticky="nsew")
        self.previews = {}
        for title in ("Original", "PixelArt"):
            tab = self.tabs.add(title)
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)
            viewer = ImageViewer(tab, "Abre una imagen para empezar" if title == "Original"
                                 else "Tu próxima creación aparecerá aquí", pixel_art=title == "PixelArt")
            viewer.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
            self.previews[title] = viewer
        comparison_tab = self.tabs.add("Comparar")
        comparison_tab.grid_rowconfigure(0, weight=1)
        comparison_tab.grid_columnconfigure(0, weight=1)
        self.comparison = Comparison(comparison_tab)
        self.comparison.grid(row=0, column=0, sticky="nsew")
        self.status = ctk.StringVar(value="Listo · procesamiento 100% local")
        ctk.CTkLabel(workspace, textvariable=self.status, anchor="w", text_color="#aab8d6").grid(
            row=1, column=0, sticky="ew", pady=8)
        self.history_frame = ctk.CTkScrollableFrame(workspace, height=125,
                                                  label_text="Creaciones recientes · últimas 20",
                                                  fg_color="#151c30")
        self.history_frame.grid(row=2, column=0, sticky="ew")
        self.history_frame.grid_columnconfigure(0, weight=1)
        self.clear_history_button = ctk.CTkButton(workspace, text="Vaciar historial", width=150,
            fg_color="#493047", hover_color="#633d54", command=self.clear_history)
        self.clear_history_button.grid(row=3, column=0, sticky="e", pady=(8, 0))

    @staticmethod
    def _dimension(parent, title, column):
        ctk.CTkLabel(parent, text=title, text_color="#aab8d6").grid(row=0, column=column, sticky="w", padx=4)
        entry = ctk.CTkEntry(parent, width=105)
        entry.insert(0, "64")
        entry.grid(row=1, column=column, padx=4)
        return entry

    def run_task(self, function, on_success):
        """Sondea un Future desde Tk: el trabajador nunca modifica widgets."""
        if self.busy:
            return
        self.busy = True
        for button in (self.open_button, self.convert_button, self.save_button, self.clear_history_button):
            button.configure(state="disabled")
        future = self.executor.submit(function)

        def poll():
            if not future.done():
                self.after(60, poll)
                return
            self.busy = False
            self.open_button.configure(state="normal")
            self.clear_history_button.configure(state="normal" if self.history.entries() else "disabled")
            try:
                on_success(future.result())
            except Exception as error:
                self.status.set("No se pudo completar la operación")
                messagebox.showerror("PixelArt Studio", str(error), parent=self)
            finally:
                self.convert_button.configure(state="normal" if self.source is not None else "disabled")
                self.save_button.configure(state="normal" if self.result is not None else "disabled")
        self.after(60, poll)

    def show_preview(self, title, image):
        self.previews[title].set_image(image)

    def open_image(self):
        path = filedialog.askopenfilename(parent=self, title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tif *.tiff *.ico"),
                       ("Todos los archivos", "*.*")])
        if not path:
            return
        self.status.set("Cargando imagen…")
        def loaded(image):
            self.source = image
            self.source_name = Path(path).stem
            self.result = None
            self.previews["PixelArt"].clear("Pulsa Crear PixelArt")
            self.show_preview("Original", image)
            self.comparison.set_images(None, None)
            self.tabs.set("Original")
            self.status.set(f"{Path(path).name} · {image.width} × {image.height} px")
        self.run_task(lambda: load_image(path), loaded)

    def convert(self):
        if self.source is None or self.busy:
            return
        try:
            settings = self.current_settings()
            width, height, scale, colors, keep = (settings.width, settings.height, settings.scale, settings.colors, settings.keep_ratio)
        except ValueError as error:
            messagebox.showerror("Configuración inválida", str(error), parent=self)
            return
        self.status.set("Creando tu PixelArt…")
        source, name = self.source, self.source_name
        def work():
            result = pixelate(source, width, height, scale, colors, keep)
            # Un fallo de disco no debe impedir guardar manualmente el resultado.
            warning = None
            try:
                self.history.add(result, name)
            except (OSError, sqlite3.Error) as error:
                warning = str(error)
            return result, warning
        def completed(payload):
            self.result, warning = payload
            self.result_name = name
            self.show_preview("PixelArt", self.result)
            self.comparison.set_images(source, self.result)
            self.tabs.set("PixelArt")
            self.status.set(f"PixelArt listo · {self.result.width} × {self.result.height} px")
            self.refresh_history()
            if warning:
                messagebox.showwarning("Historial", f"La imagen está lista, pero no se archivó: {warning}", parent=self)
        self.run_task(work, completed)

    def save_image(self):
        if self.result is None or self.busy:
            return
        path = filedialog.asksaveasfilename(parent=self, title="Guardar PixelArt",
            initialfile=f"{self.result_name}_pixelart.png", defaultextension=".png",
            filetypes=[("PNG · transparencia", "*.png"), ("WebP sin pérdida", "*.webp"),
                       ("JPEG · fondo blanco", "*.jpg")])
        if path:
            image = self.result
            self.status.set("Guardando imagen…")
            self.run_task(lambda: export_image(image, path),
                          lambda _: self.status.set(f"Guardado: {path}"))

    def refresh_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        entries = self.history.entries()
        self.clear_history_button.configure(state="normal" if entries and not self.busy else "disabled")
        if not entries:
            ctk.CTkLabel(self.history_frame, text="Tus conversiones se guardarán aquí automáticamente.",
                         text_color="#8b98b9").grid(row=0, column=0)
        for index, (identifier, name, created, width, height) in enumerate(entries):
            ctk.CTkButton(self.history_frame,
                text=f"▦  {name[:32]}   ·   {width} × {height}   ·   {created.replace('T', ' ')}",
                anchor="w", height=32, fg_color="#202b44", hover_color="#354669",
                command=lambda key=identifier, title=name: self.restore(key, title),
            ).grid(row=index, column=0, sticky="ew", pady=3, padx=4)
            ctk.CTkButton(self.history_frame, text="Eliminar", width=76,
                fg_color="#493047", hover_color="#633d54",
                command=lambda key=identifier: self.delete_history_entry(key),
            ).grid(row=index, column=1, padx=4, pady=3)

    def delete_history_entry(self, identifier):
        if self.busy:
            return
        if messagebox.askyesno("Eliminar creación", "¿Eliminar esta creación del historial?\n"
                               "Los archivos exportados se conservarán.", parent=self):
            self.run_task(lambda: self.history.delete(identifier),
                          lambda _: self.history_changed("Creación eliminada del historial"))

    def clear_history(self):
        if self.busy:
            return
        if messagebox.askyesno("Vaciar historial", "¿Eliminar todas las creaciones del historial?\n"
                               "Los archivos exportados se conservarán.", parent=self):
            self.run_task(self.history.clear,
                          lambda _: self.history_changed("Historial vacío"))

    def history_changed(self, message):
        self.refresh_history()
        self.status.set(message)

    def restore(self, identifier, name):
        if self.busy:
            return
        def restored(image):
            self.result = image
            self.result_name = name
            self.show_preview("PixelArt", image)
            self.comparison.set_images(None, image)
            self.tabs.set("PixelArt")
            self.status.set(f"Historial · {image.width} × {image.height} px · listo para guardar")
        self.run_task(lambda: load_image(self.history.path_for(identifier)), restored)

    def current_settings(self):
        try:
            return Settings(int(self.width_input.get()), int(self.height_input.get()),
                int(self.scale.get()), 0 if self.colors.get() == "Sin límite" else int(self.colors.get()),
                self.keep_ratio.get())
        except ValueError as error:
            raise ValueError(f"Revisa la configuración: {error}") from error

    def refresh_presets(self, selected=None):
        names = self.presets.names()
        self.preset_menu.configure(values=names or ["Sin presets"], state="normal" if names else "disabled")
        self.preset_menu.set(selected if selected in names else names[0] if names else "Sin presets")
        self.delete_preset_button.configure(state="normal" if names else "disabled")

    def apply_preset(self, name):
        try:
            settings = self.presets.load(name)
            for entry, value in ((self.width_input, settings.width), (self.height_input, settings.height)):
                entry.delete(0, "end")
                entry.insert(0, str(value))
            self.scale.set(str(settings.scale))
            self.colors.set(str(settings.colors) if settings.colors else "Sin límite")
            self.keep_ratio.set(settings.keep_ratio)
            self.status.set(f"Preset aplicado: {name} · pulsa Crear PixelArt")
        except (ValueError, TypeError, sqlite3.Error) as error:
            messagebox.showerror("Preset", str(error), parent=self)

    def save_preset(self):
        try:
            settings = self.current_settings()
            dialog = ctk.CTkInputDialog(text="Nombre del preset (máximo 60 caracteres):", title="Guardar preset")
            name = dialog.get_input()
            if name is None:
                return
            name = name.strip()
            if name in self.presets.names() and not messagebox.askyesno(
                    "Reemplazar preset", f"¿Reemplazar el preset «{name}»?", parent=self):
                return
            self.presets.save(name, settings)
            self.refresh_presets(name)
            self.status.set(f"Preset guardado: {name}")
        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror("Preset", str(error), parent=self)

    def delete_preset(self):
        name = self.preset_menu.get()
        if name not in self.presets.names():
            return
        if messagebox.askyesno("Eliminar preset", f"¿Eliminar el preset «{name}»?", parent=self):
            try:
                self.presets.delete(name)
                self.refresh_presets()
                self.status.set("Preset eliminado")
            except sqlite3.Error as error:
                messagebox.showerror("Preset", str(error), parent=self)

    def close(self):
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.destroy()
