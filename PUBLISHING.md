# Publicar nuevas versiones

Repositorio: https://github.com/YonnyAg/pixelart-studio

El proyecto se publica bajo licencia MIT. No se incluyen entornos virtuales,
datos personales ni binarios generados en el historial de Git.

## Validar y compilar

Desde un entorno Python 3.11 x64 en Windows:

```powershell
python -m venv .env
.\.env\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.env\Scripts\python.exe -m unittest discover -s tests -v
.\.env\Scripts\python.exe -m tests.smoke_ui
.\.env\Scripts\python.exe build_windows.py
```

Antes de una versión nueva, actualiza `VERSION` en `build_windows.py`, el changelog,
las notas de publicación y los nombres de archivo de los enlaces del README.
El script comprueba ambos ejecutables con datos temporales y genera hashes SHA256.

## Publicar con GitHub CLI

Autentícate con `gh auth login` si hace falta. Revisa `git status` antes del commit:
`.env/`, `data/`, `build/`, `dist/` y `release/` deben permanecer excluidos.

```powershell
git add .
git diff --cached --check
git commit -m "release: PixelArt Studio 1.0.0"
git push origin main
git tag v1.0.0
git push origin v1.0.0
gh release create v1.0.0 release/PixelArtStudio-1.0.0-windows-x64.exe release/PixelArtStudio-1.0.0-windows-x64.zip release/SHA256SUMS.txt --verify-tag --title "PixelArt Studio 1.0.0" --notes-file .github/RELEASE_NOTES.md
```

Usa el número nuevo en lugar de `1.0.0` para publicaciones posteriores. No reemplaces
silenciosamente archivos de versiones anteriores; crea una versión nueva.

El EXE independiente se puede distribuir solo. El ejecutable que está dentro del
ZIP necesita su carpeta `_internal`, por lo que se distribuye el ZIP completo.
Ambas variantes conservan los datos en `%LOCALAPPDATA%/PixelArtStudio/`.

GitHub Actions valida y compila; la publicación en Releases es un paso explícito
del mantenedor. Los binarios se adjuntan a Releases, no se añaden a Git.
