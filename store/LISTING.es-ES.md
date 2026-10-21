# Textos de referencia para la ficha de Microsoft Store

Estado: aplicación publicada el 21 de octubre de 2026.
Ficha pública: https://apps.microsoft.com/detail/9N18J6HDCHTS
Estos textos son una referencia para mantener y actualizar la ficha.

## Nombre propuesto

PixelArt Studio

## Descripción breve

Convierte tus imágenes en PixelArt, guarda tus estilos y compara el resultado.

## Descripción

Transforma tus imágenes en PixelArt con una aplicación de escritorio sencilla,
gratuita y de código abierto. Controla la cuadrícula, el tamaño de exportación
y la cantidad de colores para conseguir el nivel de detalle que buscas.

Revisa el resultado antes de guardarlo: amplía la imagen, desplázate por sus
detalles o compárala con la original en dos paneles sincronizados. Guarda tus
ajustes favoritos como presets para volver a utilizarlos con otras imágenes.

Todo el procesamiento de imágenes se realiza en tu equipo. La aplicación no
requiere crear una cuenta ni enviar tus imágenes a un servidor.

## Características

- Tamaño de cuadrícula, escala y paleta ajustables.
- Comparación lado a lado con zoom y desplazamiento sincronizados.
- Presets persistentes con nombre.
- Historial de hasta 20 creaciones con opciones de eliminación.
- Exportación en PNG, WebP y JPEG.
- Soporte de transparencia en PNG y WebP.
- Interfaz en español y procesamiento local.

## Categoría sugerida

Fotografía y vídeo / edición de fotos, según las categorías disponibles en el portal.

## Sitio web y soporte

https://github.com/YonnyAg/pixelart-studio
https://github.com/YonnyAg/pixelart-studio/issues

## Política de privacidad

https://github.com/YonnyAg/pixelart-studio/blob/main/PRIVACY.md

## Notas para certificación

Aplicación de escritorio Python/Tkinter empaquetada con PyInstaller. No requiere
Python instalado, inicio de sesión ni privilegios de administrador.

La capacidad runFullTrust es necesaria para ejecutar la interfaz de escritorio,
abrir imágenes seleccionadas por el usuario, procesarlas con Pillow y exportar
archivos mediante los diálogos estándar. No se instalan servicios, controladores
ni tareas de inicio automático.

Para probar: abrir una imagen de ejemplo, elegir cuadrícula 64 × 64 y escala 8,
crear PixelArt, revisar Comparar y exportar a PNG. También se pueden guardar
presets y eliminar creaciones del historial. No hay credenciales de prueba.

## Elementos que revisar en futuras actualizaciones de Partner Center

- Nombre reservado y valores de identidad reales.
- Capturas reales de la aplicación según las medidas exigidas por el portal.
- Precio gratuito y mercados de distribución elegidos por el propietario.
- Cuestionario de clasificación por edades contestado por el propietario.
- Validación del MSIX instalado y resultado de certificación de Microsoft.
