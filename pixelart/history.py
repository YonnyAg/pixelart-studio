"""Historial persistente con SQLite y archivos PNG propios."""

from datetime import datetime
from contextlib import contextmanager
from pathlib import Path
import sqlite3
from uuid import uuid4

from PIL import Image
from .paths import data_directory

DATA_DIR = data_directory()


class History:
    """Conserva las últimas 20 conversiones, incluso después de reiniciar."""

    def __init__(self, directory: Path = DATA_DIR, limit: int = 20):
        self.directory = directory
        self.limit = limit
        self.directory.mkdir(parents=True, exist_ok=True)
        self.db = self.directory / "history.sqlite3"
        with self.connect() as connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS images (
                id TEXT PRIMARY KEY, name TEXT NOT NULL,
                created TEXT NOT NULL, width INTEGER, height INTEGER
            )""")

    @contextmanager
    def connect(self):
        """Confirma transacciones y cierra el archivo también en Windows."""
        connection = sqlite3.connect(self.db)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def entries(self) -> list[tuple]:
        with self.connect() as connection:
            return connection.execute(
                "SELECT id, name, created, width, height FROM images "
                "ORDER BY rowid DESC LIMIT ?", (self.limit,),
            ).fetchall()

    def path_for(self, identifier: str) -> Path:
        # Solo UUID generados internamente pueden convertirse en rutas.
        if len(identifier) != 32 or any(c not in "0123456789abcdef" for c in identifier):
            raise ValueError("Identificador de historial inválido.")
        return self.directory / f"{identifier}.png"

    def add(self, image: Image.Image, name: str) -> None:
        identifier = uuid4().hex
        path = self.path_for(identifier)
        image.save(path, format="PNG")
        try:
            with self.connect() as connection:
                connection.execute("INSERT INTO images VALUES (?, ?, ?, ?, ?)", (
                    identifier, name, datetime.now().isoformat(timespec="seconds"),
                    image.width, image.height,
                ))
        except Exception:
            path.unlink(missing_ok=True)
            raise
        with self.connect() as connection:
            expired = connection.execute(
                "SELECT id FROM images ORDER BY rowid DESC LIMIT -1 OFFSET ?",
                (self.limit,),
            ).fetchall()
            for (old_id,) in expired:
                self.path_for(old_id).unlink(missing_ok=True)
                connection.execute("DELETE FROM images WHERE id = ?", (old_id,))

    def delete(self, identifier: str) -> None:
        """Elimina únicamente el PNG y el registro de una creación archivada."""
        path = self.path_for(identifier)
        with self.connect() as connection:
            exists = connection.execute("SELECT 1 FROM images WHERE id = ?", (identifier,)).fetchone()
            if exists:
                path.unlink(missing_ok=True)
                connection.execute("DELETE FROM images WHERE id = ?", (identifier,))

    def clear(self) -> None:
        """Vacía los registros y sus PNG; nunca borra exportaciones del usuario."""
        with self.connect() as connection:
            identifiers = connection.execute("SELECT id FROM images").fetchall()
        # Cada eliminación confirma su propia transacción. Si un archivo está
        # bloqueado, los registros restantes siguen apuntando a archivos válidos.
        for (identifier,) in identifiers:
            self.delete(identifier)
