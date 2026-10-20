"""Construye y verifica la distribución portable de Windows y genera su ZIP."""

import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
VERSION = "1.0.0"


def main():
    if sys.platform != "win32" or sys.maxsize <= 2 ** 32:
        raise SystemExit("El ejecutable debe construirse en Windows con Python de 64 bits.")
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
        "--windowed", "--name", "PixelArtStudio", "--icon", str(ROOT / "assets/app-icon.ico"),
        "--add-data", f"{ROOT / 'assets/app-icon.ico'}:assets", "--add-data", f"{ROOT / 'assets/app-icon.png'}:assets",
        "--collect-data", "customtkinter", "--distpath", "dist", "--workpath", "build/pyinstaller",
        "--specpath", "build", str(ROOT / "main.py")], check=True, cwd=ROOT)
    package_release()
    build_standalone()


def package_release():
    """Verifica y empaqueta la carpeta ya compilada con avisos de terceros."""
    package = ROOT / "dist" / "PixelArtStudio"
    shutil.copy2(ROOT / "README.md", package / "README.md")
    shutil.copy2(ROOT / "NOTICE.md", package / "NOTICE.md")
    shutil.copy2(ROOT / "LICENSE", package / "LICENSE")
    licenses = package / "THIRD_PARTY_LICENSES"
    licenses.mkdir(exist_ok=True)
    # Distribuye los avisos originales de las bibliotecas incluidas.
    for name in ("customtkinter", "pillow", "darkdetect", "packaging", "pyinstaller"):
        distribution = metadata.distribution(name)
        destination = licenses / name
        destination.mkdir(exist_ok=True)
        for index, file in enumerate(distribution.files or []):
            if file.name.lower().startswith(("license", "copying", "notice")) and file.suffix not in (".py", ".pyc"):
                path = Path(distribution.locate_file(file))
                if path.is_file():
                    shutil.copy2(path, destination / f"{index}-{path.name}")
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if not python_license.is_file():
        raise SystemExit(f"No se encontró la licencia de Python: {python_license}")
    shutil.copy2(python_license, licenses / "PYTHON-LICENSE.txt")
    report = ROOT / "build" / "executable-smoke.json"
    subprocess.run([str(package / "PixelArtStudio.exe"), "--smoke-test", str(report)],
                   check=True, timeout=60, cwd=ROOT)
    if not json.loads(report.read_text(encoding="utf-8"))["ok"]:
        raise SystemExit(f"La verificación del ejecutable falló: {report}")
    release = ROOT / "release"
    release.mkdir(exist_ok=True)
    archive = Path(shutil.make_archive(str(release / f"PixelArtStudio-{VERSION}-windows-x64"),
                                       "zip", root_dir=ROOT / "dist", base_dir="PixelArtStudio"))
    write_checksums()
    print(f"Distribución verificada: {archive}")


def build_standalone():
    """Genera un EXE único para la descarga directa desde GitHub Releases."""
    license_dir = ROOT / "dist/PixelArtStudio/THIRD_PARTY_LICENSES"
    if not license_dir.is_dir():
        raise SystemExit("Construye primero la distribución portable y sus avisos de terceros.")
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--onefile", "--windowed",
        "--name", "PixelArtStudio", "--icon", str(ROOT / "assets/app-icon.ico"),
        "--collect-data", "customtkinter", "--distpath", "dist/standalone",
        "--workpath", "build/standalone", "--specpath", "build/standalone-spec"]
    for source, destination in ((ROOT / "assets/app-icon.ico", "assets"),
                                (ROOT / "assets/app-icon.png", "assets"),
                                (ROOT / "LICENSE", "."), (ROOT / "NOTICE.md", "."),
                                (ROOT / "README.md", "."), (license_dir, "THIRD_PARTY_LICENSES")):
        command.extend(["--add-data", f"{source}:{destination}"])
    subprocess.run([*command, str(ROOT / "main.py")], check=True, cwd=ROOT)
    executable = ROOT / "dist/standalone/PixelArtStudio.exe"
    report = ROOT / "build/standalone-smoke.json"
    subprocess.run([str(executable), "--smoke-test", str(report)], check=True, timeout=90, cwd=ROOT)
    if not json.loads(report.read_text(encoding="utf-8"))["ok"]:
        raise SystemExit(f"La verificación del EXE independiente falló: {report}")
    destination = ROOT / "release" / f"PixelArtStudio-{VERSION}-windows-x64.exe"
    shutil.copy2(executable, destination)
    write_checksums()
    print(f"EXE independiente verificado: {destination}")


def write_checksums():
    release = ROOT / "release"
    lines = []
    for suffix in ("exe", "zip"):
        path = release / f"PixelArtStudio-{VERSION}-windows-x64.{suffix}"
        if path.is_file():
            with path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            lines.append(f"{digest}  {path.name}\n")
    (release / "SHA256SUMS.txt").write_text("".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
