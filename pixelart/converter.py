"""Conversión local con Pillow, sin servicios externos."""

from pathlib import Path
import warnings

from PIL import Image, ImageOps

MAX_PIXELS = 24_000_000


def load_image(path: str | Path) -> Image.Image:
    """Carga el primer fotograma, aplica orientación EXIF y conserva alfa."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(path) as source:
            if source.width * source.height > MAX_PIXELS:
                raise ValueError("La imagen supera el límite de 24 megapíxeles.")
            return ImageOps.exif_transpose(source).convert("RGBA")


def pixelate(image: Image.Image, width: int, height: int,
             scale: int = 8, colors: int = 32,
             keep_ratio: bool = True) -> Image.Image:
    """Reduce a una cuadrícula y amplía con vecino más cercano.

    width/height son límites de la cuadrícula cuando keep_ratio está activo.
    scale es un factor entero: cada celda se transforma en un bloque nítido.
    colors=0 conserva todos los colores y el canal alfa original.
    """
    if not 1 <= width <= 512 or not 1 <= height <= 512:
        raise ValueError("La cuadrícula debe estar entre 1 y 512 píxeles por eje.")
    if not 1 <= scale <= 16:
        raise ValueError("La escala debe estar entre 1 y 16.")
    if colors != 0 and not 2 <= colors <= 256:
        raise ValueError("Selecciona entre 2 y 256 colores, o sin límite.")
    size = (width, height)
    if keep_ratio:
        ratio = min(width / image.width, height / image.height)
        size = (max(1, round(image.width * ratio)),
                max(1, round(image.height * ratio)))
    output_size = (size[0] * scale, size[1] * scale)
    if output_size[0] * output_size[1] > MAX_PIXELS:
        raise ValueError("La salida supera 24 megapíxeles. Reduce tamaño o escala.")
    small = image.convert("RGBA").resize(size, Image.Resampling.BOX)
    if colors:
        # Cuantizamos RGB por separado para conservar exactamente la transparencia.
        alpha = small.getchannel("A")
        small = small.convert("RGB").quantize(
            colors=colors, method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.NONE,
        ).convert("RGBA")
        small.putalpha(alpha)
    return small.resize(output_size, Image.Resampling.NEAREST)


def export_image(image: Image.Image, path: str | Path) -> None:
    """Exporta PNG/WebP sin pérdida; JPEG compone transparencia sobre blanco."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        background = Image.new("RGB", image.size, "white")
        background.paste(image, mask=image.getchannel("A"))
        background.save(path, format="JPEG", quality=95, subsampling=0)
    elif suffix == ".webp":
        image.save(path, format="WEBP", lossless=True)
    elif suffix == ".png":
        image.save(path, format="PNG")
    else:
        raise ValueError("Utiliza una extensión .png, .jpg, .jpeg o .webp.")
