# Publicación en Microsoft Store

Estado: preparación técnica. Todavía no existe un paquete con identidad de Store
confirmada ni una publicación aprobada. Este flujo usa **MSIX**, no la opción
de enviar una URL de un instalador EXE/MSI sin firma.

## 1. Registro que completa el propietario

1. Abre https://storedeveloper.microsoft.com y pulsa **Get started for free**.
2. Para este proyecto personal gratuito, elige desarrollador **Individual**.
3. Inicia sesión con tu cuenta Microsoft. Completa personalmente la verificación
   de identidad, documentos y selfie que solicite Microsoft y revisa sus acuerdos.
4. Accede a Partner Center y crea un producto **MSIX o PWA**.
5. Comprueba la disponibilidad y reserva **PixelArt Studio**, o un nombre alternativo
   si no está disponible. No podemos garantizar la disponibilidad de ese nombre.
6. Abre **Administración del producto → Identidad del producto** y copia exactamente:
   - `Package/Identity/Name`
   - `Package/Identity/Publisher`
   - `Package/Properties/PublisherDisplayName`

Estos identificadores del paquete no son contraseñas ni claves privadas. No
compartas documentos, contraseñas, tokens ni códigos de recuperación en el chat.

## 2. Preparación local

Ya están disponibles el borrador de ficha `LISTING.es-ES.md`, la política de
privacidad, el icono y el script de empaquetado. Para revisar una carpeta de ejemplo:

```powershell
.\.env\Scripts\python.exe prepare_store.py --preview
```

La vista previa usa una identidad ficticia y no genera un MSIX. Primero debe
existir `dist/PixelArtStudio/`, generado con `build_windows.py`.

Cuando tengas los identificadores reales:

```powershell
Copy-Item store/identity.example.json store/identity.local.json
# Completa el JSON con los tres valores reales y el nombre reservado.
.\.env\Scripts\python.exe prepare_store.py --identity store/identity.local.json
```

Se necesita `MakeAppx.exe` del [Windows SDK](https://developer.microsoft.com/windows/downloads/windows-sdk/).
Si no está en la ruta habitual, pasa `--makeappx C:\ruta\makeappx.exe`.
La identidad local está excluida de Git para evitar subir configuraciones en curso.
El manifiesto declara x64, Windows 10 2004 o superior, interfaz es-ES y runFullTrust.

## 3. Validación antes del envío

El script ejecuta la validación de MakeAppx, pero esto no sustituye una prueba
real del paquete instalado ni la certificación de Microsoft. Una vez obtenida
la identidad real, debemos probar instalación, apertura de archivos, exportación,
presets, historial y la integración del icono con la identidad MSIX.

El MSIX para enviar a la Store no se firma aquí con un certificado autofirmado.
Microsoft lo vuelve a firmar después de aprobar su certificación. No se debe
distribuir este paquete sin firmar como si fuera una instalación pública lista.

## 4. Ficha y envío

En Partner Center crea el envío, carga el MSIX y completa la ficha con el borrador.
Añade capturas reales, selecciona gratuito, mercados, clasificación por edades,
URL de soporte y privacidad. Revisa el resumen y envía a certificación.
Podemos preparar y rellenar los campos técnicos; la identidad, los acuerdos y
las declaraciones del propietario los completa o revisa el propietario.

La publicación no es inmediata ni está garantizada: queda sujeta a revisión.
El enlace de Microsoft Store se añade al README cuando exista una ficha publicada.
La aprobación de Store no elimina por sí sola los avisos del EXE externo de GitHub.

## Referencias oficiales

- [Registro de desarrolladores](https://learn.microsoft.com/windows/apps/publish/partner-center/open-a-developer-account)
- [Identidad del producto](https://learn.microsoft.com/windows/apps/publish/view-app-identity-details)
- [Manifiesto de escritorio](https://learn.microsoft.com/windows/msix/desktop/desktop-to-uwp-manual-conversion)
- [MakeAppx](https://learn.microsoft.com/windows/msix/package/create-app-package-with-makeappx-tool)
