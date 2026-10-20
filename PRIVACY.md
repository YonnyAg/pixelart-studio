# Política de privacidad de PixelArt Studio

Última actualización: 20 de octubre de 2026.

PixelArt Studio procesa imágenes localmente. La aplicación no requiere cuentas,
no incorpora publicidad ni telemetría y no envía imágenes, presets o historial
a servidores del desarrollador ni a servicios de inteligencia artificial.

## Datos guardados en el equipo

La aplicación abre los archivos elegidos por el usuario. Conserva hasta 20
resultados en PNG, junto con el nombre de la imagen, fecha y dimensiones en
una base SQLite. Los presets guardan el nombre elegido y los parámetros de
conversión. Estos datos se utilizan para ofrecer el historial y reutilizar ajustes.

En la versión portable para Windows, se guardan en
`%LOCALAPPDATA%/PixelArtStudio/`. En una instalación MSIX, Windows puede
redirigir el almacenamiento a la ubicación privada del paquete. Al ejecutar
el código fuente, se utiliza la carpeta `data/` del proyecto.

## Control de los datos

Puedes eliminar entradas o vaciar el historial desde la aplicación y eliminar
presets individualmente. Los archivos que exportes manualmente permanecen en
la ubicación que elegiste. Para una copia de seguridad, cierra la aplicación
y copia su carpeta de datos. El comportamiento de eliminación al desinstalar
un paquete MSIX depende del almacenamiento administrado por Windows.

## Servicios externos

La distribución se realiza a través de GitHub y, si se aprueba su publicación,
Microsoft Store. Estos servicios aplican sus propias políticas a las descargas,
cuentas y transacciones realizadas en sus plataformas. La aplicación de escritorio
no añade seguimiento propio ni comparte tus imágenes con ellos.

Si decides reportar un problema públicamente en GitHub, comparte únicamente
información e imágenes que quieras hacer públicas.

## Contacto

Consultas sobre privacidad: https://github.com/YonnyAg/pixelart-studio/issues

No adjuntes datos personales ni imágenes privadas a un reporte público.
