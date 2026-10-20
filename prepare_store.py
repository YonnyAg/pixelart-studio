"""Prepara un paquete MSIX para la Store usando su identidad real.

--preview genera solo una carpeta de revisión con identidad de ejemplo.
No firma certificados, instala paquetes ni envía nada a Microsoft.
"""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parent
FOUNDATION = "http://schemas.microsoft.com/appx/manifest/foundation/windows10"
UAP = "http://schemas.microsoft.com/appx/manifest/uap/windows10"
RESCAP = "http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
ET.register_namespace("", FOUNDATION)
ET.register_namespace("uap", UAP)
ET.register_namespace("rescap", RESCAP)


def validate_identity(identity):
    for key in ("name", "publisher", "publisher_display_name", "display_name", "version"):
        value = identity.get(key)
        if not isinstance(value, str) or not value.strip() or "COPIAR" in value:
            raise ValueError(f"Falta el valor real de Microsoft Store: {key}")
    if not re.fullmatch(r"[A-Za-z0-9.-]{3,50}", identity["name"]):
        raise ValueError("Package/Identity/Name no tiene un formato válido.")
    if not identity["publisher"].startswith("CN="):
        raise ValueError("Publisher debe copiarse completo, incluyendo CN=.")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+\.0", identity["version"]):
        raise ValueError("La versión para Store debe tener cuatro números y terminar en .0.")
    parts = [int(part) for part in identity["version"].split(".")]
    if parts[0] == 0 or any(part > 65535 for part in parts):
        raise ValueError("La versión debe empezar en 1 o más; cada componente admite hasta 65535.")


def create_manifest(identity):
    validate_identity(identity)
    tag = lambda name: f"{{{FOUNDATION}}}{name}"
    package = ET.Element(tag("Package"), {"IgnorableNamespaces": "uap rescap"})
    ET.SubElement(package, tag("Identity"), Name=identity["name"], Publisher=identity["publisher"],
                  Version=identity["version"], ProcessorArchitecture="x64")
    properties = ET.SubElement(package, tag("Properties"))
    for name, value in (("DisplayName", identity["display_name"]),
                        ("PublisherDisplayName", identity["publisher_display_name"]),
                        ("Description", "Convierte imágenes en PixelArt con presets y comparación."),
                        ("Logo", "Assets\\StoreLogo.png")):
        ET.SubElement(properties, tag(name)).text = value
    resources = ET.SubElement(package, tag("Resources"))
    ET.SubElement(resources, tag("Resource"), Language="es-ES")
    dependencies = ET.SubElement(package, tag("Dependencies"))
    ET.SubElement(dependencies, tag("TargetDeviceFamily"), Name="Windows.Desktop",
                  MinVersion="10.0.19041.0", MaxVersionTested="10.0.26100.0")
    applications = ET.SubElement(package, tag("Applications"))
    application = ET.SubElement(applications, tag("Application"), Id="PixelArtStudio",
                                Executable="App\\PixelArtStudio.exe", EntryPoint="Windows.FullTrustApplication")
    ET.SubElement(application, f"{{{UAP}}}VisualElements", DisplayName=identity["display_name"],
                  Description="Convierte imágenes en PixelArt.", BackgroundColor="transparent",
                  Square150x150Logo="Assets\\Square150x150Logo.png",
                  Square44x44Logo="Assets\\Square44x44Logo.png")
    capabilities = ET.SubElement(package, tag("Capabilities"))
    ET.SubElement(capabilities, f"{{{RESCAP}}}Capability", Name="runFullTrust")
    tree = ET.ElementTree(package)
    ET.indent(tree, space="  ")
    return tree


def stage_package(identity, source):
    if not (source / "PixelArtStudio.exe").is_file() or not (source / "_internal").is_dir():
        raise ValueError("Falta la distribución onedir. Ejecuta primero build_windows.py.")
    (ROOT / "build").mkdir(exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="msix-stage-", dir=ROOT / "build"))
    shutil.copytree(source, staging / "App")
    assets = staging / "Assets"
    assets.mkdir()
    with Image.open(ROOT / "assets/icon-source.png") as image:
        for name, size in (("Square44x44Logo", 44), ("Square150x150Logo", 150), ("StoreLogo", 50)):
            image.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS).save(assets / f"{name}.png")
    create_manifest(identity).write(staging / "AppxManifest.xml", encoding="utf-8", xml_declaration=True)
    return staging


def find_makeappx():
    executable = shutil.which("makeappx.exe")
    if executable:
        return Path(executable)
    for variable in ("ProgramFiles(x86)", "ProgramFiles"):
        base = Path(os.environ.get(variable, "C:/Program Files (x86)")) / "Windows Kits/10/bin"
        candidates = sorted(base.glob("*/x64/makeappx.exe"), reverse=True)
        if candidates:
            return candidates[0]
    raise ValueError("No se encontró MakeAppx.exe. Instala Windows SDK o usa --makeappx con su ruta.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true", help="Solo prepara una revisión; no genera un MSIX.")
    mode.add_argument("--identity", type=Path, help="JSON con los valores reales de Partner Center.")
    parser.add_argument("--source", type=Path, default=ROOT / "dist/PixelArtStudio")
    parser.add_argument("--makeappx", type=Path, help="Ruta a MakeAppx.exe del Windows SDK.")
    args = parser.parse_args()
    identity = {"name": "LocalPreview.PixelArtStudio", "publisher": "CN=LocalPreview",
                "publisher_display_name": "Solo vista previa", "display_name": "PixelArt Studio",
                "version": "1.0.0.0"} if args.preview else json.loads(args.identity.read_text(encoding="utf-8"))
    validate_identity(identity)
    makeappx = None if args.preview else args.makeappx or find_makeappx()
    staging = stage_package(identity, args.source.resolve())
    print(f"Carpeta preparada: {staging}")
    if args.preview:
        print("Vista previa solamente: identidad ficticia, sin MSIX y sin envío a Microsoft.")
        return
    output = ROOT / "release/store" / f"PixelArtStudio-{identity['version']}-x64.msix"
    output.parent.mkdir(parents=True, exist_ok=True)
    # MakeAppx valida el manifiesto. No usamos /nv para saltar comprobaciones.
    subprocess.run([str(makeappx), "pack", "/d", str(staging), "/p", str(output), "/o"], check=True)
    print(f"MSIX generado para revisión y certificación: {output}")
    print("No está firmado para instalación directa; Microsoft firma tras aprobar la publicación.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, json.JSONDecodeError) as error:
        raise SystemExit(str(error))
