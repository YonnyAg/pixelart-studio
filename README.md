# PixelArt Studio

<p align="center"><img src="assets/app-icon.png" width="128" alt="PixelArt Studio"></p>

Editor de escritorio para convertir imágenes en PixelArt, construido con Python,
CustomTkinter y Pillow. Procesamiento local, sin cuentas ni servicios externos.

## Funciones

- Cuadrícula de 1–512 píxeles por eje, con proporción opcional.
- Escala de exportación de 1–16 y paletas de 8–256 colores o sin límite.
- Vista original, resultado y comparación lado a lado.
- Zoom manual de 10%–1600%, tamaño real, ajuste al panel y desplazamiento.
- Comparación con zoom y centro sincronizados en coordenadas relativas: original
  y resultado muestran la misma zona aunque sus resoluciones sean distintas.
- Presets con nombre: guardar, aplicar, reemplazar y eliminar tamaño, escala,
  paleta y proporción. Permanecen disponibles al reiniciar y al vaciar el historial.
- Historial persistente de las últimas 20 creaciones, con eliminación individual
  y vaciado completo mediante confirmación.
- Exportación PNG, WebP sin pérdida y JPEG sobre fondo blanco.
- Icono propio para la ventana y el ejecutable de Windows.

## Descargar para Windows

**[⬇ Descargar PixelArt Studio (.exe)](https://github.com/YonnyAg/pixelart-studio/releases/latest/download/PixelArtStudio-1.0.0-windows-x64.exe)**

[ZIP portable](https://github.com/YonnyAg/pixelart-studio/releases/latest/download/PixelArtStudio-1.0.0-windows-x64.zip)
· [Todas las versiones](https://github.com/YonnyAg/pixelart-studio/releases)
· [Checksums SHA256](https://github.com/YonnyAg/pixelart-studio/releases/latest/download/SHA256SUMS.txt)
· [Licencia MIT](LICENSE)

Requiere **Windows 10/11 de 64 bits**. No requiere Python ni permisos de administrador.

### Opción recomendada: EXE independiente

Descarga `PixelArtStudio-1.0.0-windows-x64.exe` y ábrelo con doble clic. Es un
archivo autocontenido: no tienes que instalar dependencias ni descargar la carpeta
`_internal`. Al arrancar extrae sus recursos en una ubicación temporal, por lo que
puede tardar unos segundos. El historial y los presets se guardan de forma permanente
en tu perfil de usuario, fuera de esa carpeta temporal.

### Alternativa: ZIP portable

Descarga `PixelArtStudio-1.0.0-windows-x64.zip`, extrae **toda** la carpeta y abre
`PixelArtStudio/PixelArtStudio.exe`. En esta versión debes mantener `_internal`
junto al ejecutable. El ZIP también incluye documentación y avisos de licencias.

Ambas opciones son portables y no añaden un instalador. Los ejecutables no están
firmados digitalmente. Puedes verificar su integridad con `SHA256SUMS.txt`:

```powershell
Get-FileHash .\PixelArtStudio-1.0.0-windows-x64.exe -Algorithm SHA256
```

Compara el resultado con la línea del mismo archivo en el listado de checksums.

## Desarrollo

Requiere Windows y Python **3.11 de 64 bits** para compilar; el código fuente
puede ejecutarse en otros sistemas con Python 3.11+ y Tkinter disponible.

```powershell
git clone https://github.com/YonnyAg/pixelart-studio.git
cd pixelart-studio
python -m venv .env
.\.env\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.env\Scripts\python.exe main.py
```

`.env/` es el entorno virtual, no un archivo de variables de entorno.
Para ejecutar únicamente el código fuente, basta instalar `requirements.lock.txt`.
`requirements.txt` define dependencias directas; `requirements.lock.txt` fija las
versiones del programa y `requirements-build.lock.txt` las del entorno de compilación.
No necesitas activar el entorno ni cambiar la política de PowerShell.

En Linux/macOS utiliza `python3 -m venv .env` y `.env/bin/python`; Tkinter
puede requerir un paquete de sistema como `python3-tk` en Linux. El paquete
portable distribuido se construye y verifica exclusivamente para Windows x64.

## Uso

1. Abre una imagen.
2. Ajusta cuadrícula, escala, colores y proporción. Por ejemplo, 64 × 64 con
   escala 8 produce hasta 512 × 512 píxeles.
3. Opcionalmente guarda la configuración con un nombre en **Presets**. Selecciona
   un nombre del menú para aplicarlo; pulsa **Crear PixelArt** para generar la imagen.
4. Revisa las pestañas **Original**, **PixelArt** y **Comparar**. Usa la rueda o
   los botones de zoom y arrastra para desplazarte. **100%** muestra el tamaño
   real de la imagen en ese panel; en comparación el otro panel adopta un zoom
   equivalente para mostrar la misma zona. **Ajustar** encaja ambas imágenes.
5. Pulsa **Guardar imagen** y elige ubicación y formato. El zoom solo afecta
   a la vista previa; la exportación conserva las dimensiones del resultado.
6. Selecciona una creación del historial para exportarla de nuevo. Usa **Eliminar**
   o **Vaciar historial** para borrar sus copias internas, conservando exportaciones
   manuales, presets y el resultado abierto.

El historial conserva solo el resultado; al restaurarlo no se muestra un original
sin relación en **Comparar**. Para comparar, abre y convierte una imagen.

## Datos personales

- Desde el código fuente: `data/` en el proyecto, excluido de Git.
- Desde el ejecutable: `%LOCALAPPDATA%/PixelArtStudio/`, fuera del paquete.

La base SQLite contiene historial y presets; los resultados se conservan como PNG.
Los datos creados durante el desarrollo no se incluyen en el ZIP ni se trasladan
al ejecutable automáticamente. Actualizar la carpeta del programa conserva los
archivos de `%LOCALAPPDATA%/PixelArtStudio/`.

## Comprobaciones

```powershell
.\.env\Scripts\python.exe -m unittest discover -s tests -v
.\.env\Scripts\python.exe -m tests.smoke_ui
.\.env\Scripts\python.exe -m pip check
```

Para verificar además comparación y presets con datos temporales:

```powershell
New-Item -ItemType Directory -Force build
.\.env\Scripts\python.exe main.py --smoke-test build/source-smoke.json
```

## Compilar el ejecutable

```powershell
.\.env\Scripts\python.exe build_windows.py
```

El script incorpora los recursos de CustomTkinter y el icono, verifica el programa
empaquetado en ambos formatos con datos temporales y produce:

```text
dist/PixelArtStudio/PixelArtStudio.exe
release/PixelArtStudio-1.0.0-windows-x64.exe
release/PixelArtStudio-1.0.0-windows-x64.zip
release/SHA256SUMS.txt
build/executable-smoke.json
build/standalone-smoke.json
```

La compilación se apoya en [PyInstaller](https://pyinstaller.org/en/stable/usage.html)
y recoge los [recursos de CustomTkinter](https://github.com/TomSchimansky/CustomTkinter/wiki/Packaging).
El icono del archivo `.exe` y el de la ventana se configuran por separado.
Reinicia la aplicación para actualizarlo; un acceso directo fijado previamente
puede requerir volver a fijar la aplicación.

## Repositorio, versiones y contribuciones

El proyecto es **software libre y de código abierto bajo [licencia MIT](LICENSE)**.
Puedes utilizarlo, modificarlo y distribuirlo conservando los avisos de la licencia.

- [Código fuente](https://github.com/YonnyAg/pixelart-studio)
- [Descargas y versiones](https://github.com/YonnyAg/pixelart-studio/releases)
- [Reportar un problema](https://github.com/YonnyAg/pixelart-studio/issues)
- [Guía para contribuir](CONTRIBUTING.md)
- [Guía de publicación para mantenedores](PUBLISHING.md)

El flujo `.github/workflows/windows.yml` ejecuta pruebas, compila ambos formatos
para Windows y conserva los resultados como artefactos. Las versiones públicas se
adjuntan a GitHub Releases. Los datos personales y el entorno virtual quedan fuera
del repositorio. Los avisos de terceros figuran en [NOTICE.md](NOTICE.md).

## Estructura

```text
assets/             Icono, original y prompt del diseño
pixelart/           Interfaz, visor, comparación, presets, conversión e historial
tests/              Pruebas unitarias y de integración de la interfaz
.github/workflows/  Validación y compilación en Windows
main.py             Entrada del programa
build_windows.py    Empaquetado, verificación y ZIP
requirements*.txt   Dependencias y versiones fijadas
```

## Formatos y límites

PNG, JPEG, WebP, BMP, GIF, TIFF e ICO según los decodificadores de Pillow.
SVG, RAW y PDF requieren otras herramientas y no están incluidos. De archivos
animados o multipágina se usa únicamente el primer fotograma. Se aplica EXIF.
La entrada y la salida tienen un límite de 24 megapíxeles; los presets validan
ese límite sobre la cuadrícula máxima configurada. La paleta limita colores RGB
conservando los niveles alfa. PNG y WebP mantienen transparencia; JPEG usa blanco.
El efecto reduce resolución, cuantiza y amplía sin suavizar: no redibuja con IA.

El original del icono y el prompt están en [assets/DESIGN.md](assets/DESIGN.md).

## Preguntas frecuentes

**¿Qué significan cuadrícula y escala?** La cuadrícula define el detalle real del
PixelArt. Una cuadrícula 32 × 32 tiene menos detalle que 128 × 128. La escala
multiplica cada celda sin suavizar: 32 × 32 con escala 8 produce 256 × 256 píxeles.
Mantener proporción puede reducir uno de los ejes para respetar la imagen original.

**¿Por qué el PNG tiene zonas transparentes?** Se conserva el canal alfa de la
entrada. El tablero del visor representa transparencia y no se exporta. Selecciona
JPEG si quieres componer esas zonas sobre blanco.

**¿Cómo guardo un estilo para otra imagen?** Ajusta las opciones, pulsa **Guardar
configuración**, elige un nombre y después selecciónalo en el menú de presets.
Al aplicar un preset, pulsa **Crear PixelArt** para generar un nuevo resultado.

**¿Cómo hago una copia de seguridad?** Cierra la aplicación y copia toda la carpeta
`%LOCALAPPDATA%/PixelArtStudio/`. Guarda juntos la base SQLite y los PNG. Para
restaurar, cierra la aplicación y devuelve la copia a esa ubicación.

**¿Cómo actualizo?** Descarga el nuevo EXE, cierra la versión anterior y abre el
archivo nuevo. Si usas el ZIP, extrae la nueva versión en una carpeta aparte y
conserva todos sus archivos. Tus presets e historial siguen en tu perfil de usuario.

**¿Cómo desinstalo?** Cierra el programa y elimina el EXE o su carpeta portable.
Los datos de usuario permanecen en la ubicación indicada; puedes conservarlos como
respaldo o eliminarlos si ya no los necesitas.

**¿Se suben mis imágenes a Internet?** El procesamiento y el historial de la
aplicación son locales. No se envían imágenes a servidores ni se requieren cuentas.

**¿Qué adjunto a un reporte de error?** Indica versión, Windows, pasos para repetir
el problema y el mensaje exacto. Adjunta una imagen de ejemplo solo si puedes
compartirla públicamente. Los reportes se crean en la sección Issues del repositorio.
