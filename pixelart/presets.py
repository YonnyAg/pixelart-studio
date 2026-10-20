"""Configuraciones reutilizables, independientes del historial de imágenes."""

from dataclasses import asdict, dataclass
import json


@dataclass(frozen=True)
class Settings:
    width: int = 64
    height: int = 64
    scale: int = 8
    colors: int = 32
    keep_ratio: bool = True

    def __post_init__(self):
        if any(type(value) is not int for value in (self.width, self.height, self.scale, self.colors)):
            raise ValueError("Tamaño, escala y colores deben ser números enteros.")
        if not 1 <= self.width <= 512 or not 1 <= self.height <= 512:
            raise ValueError("La cuadrícula debe estar entre 1 y 512 por eje.")
        if not 1 <= self.scale <= 16 or self.colors not in (0, 8, 16, 32, 64, 128, 256):
            raise ValueError("Escala o paleta no válidas.")
        if type(self.keep_ratio) is not bool:
            raise ValueError("La opción de proporción debe ser booleana.")
        if self.width * self.height * self.scale ** 2 > 24_000_000:
            raise ValueError("La configuración supera el límite de 24 megapíxeles.")


class Presets:
    def __init__(self, history):
        self.history = history
        with history.connect() as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS presets (name TEXT PRIMARY KEY, settings TEXT NOT NULL)")

    def names(self):
        with self.history.connect() as connection:
            return [row[0] for row in connection.execute("SELECT name FROM presets ORDER BY name COLLATE NOCASE")]

    def save(self, name: str, settings: Settings):
        name = name.strip()
        if not name or len(name) > 60:
            raise ValueError("El nombre debe tener entre 1 y 60 caracteres.")
        with self.history.connect() as connection:
            connection.execute("INSERT INTO presets VALUES (?, ?) ON CONFLICT(name) "
                               "DO UPDATE SET settings = excluded.settings", (name, json.dumps(asdict(settings))))

    def load(self, name: str):
        with self.history.connect() as connection:
            row = connection.execute("SELECT settings FROM presets WHERE name = ?", (name,)).fetchone()
        if row is None:
            raise ValueError("Ese preset ya no existe.")
        return Settings(**json.loads(row[0]))

    def delete(self, name: str):
        with self.history.connect() as connection:
            connection.execute("DELETE FROM presets WHERE name = ?", (name,))
