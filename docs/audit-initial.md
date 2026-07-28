# Auditoría inicial — baseline Informatorio

Fecha: 2026-07-28  
Rama de trabajo: `modernize/00-baseline`  
Referencia recuperable: etiqueta anotada `legacy-informatorio-v1` en `77c9c27100649e20a148834a381e5b89e91a2075`.

## Integridad del baseline

Al iniciar esta fase, `main` apuntaba al commit indicado pero **no estaba limpia**: Git informó el directorio `docs/` como no seguido. Contiene `THE_CAFFEINE_LANE_DEVELOPMENT_GUIDE.md`, que se considera contenido preexistente del usuario. No se agregó, modificó, movió ni eliminó durante esta fase.

La etiqueta preserva exactamente el `HEAD` de `main`; por tanto permite volver al código versionado de la entrega académica. Esta auditoría es el único archivo nuevo de la rama de baseline y no modifica el comportamiento de la aplicación.

## Datos, media y configuración

Se creó una copia privada de `media/` fuera del repositorio, en el directorio temporal local:

`C:\Users\mrdan\AppData\Local\Temp\caffeine-lane-private-backup-20260728\media`

La copia contiene 53 archivos. El directorio privado también contiene `backup-status.txt`; no debe añadirse a Git.

No hay `db.sqlite3` en el árbol. La configuración usa SQLite solo como valor local y una base externa cuando existe `DATABASE_URL`; en esta sesión `DATABASE_URL` no estaba disponible. Por ese motivo no fue posible generar una exportación de base de datos verificable. Debe realizarse desde el proveedor de la base en producción antes de cualquier cambio de datos.

Tampoco estaban disponibles en esta sesión las variables `SECRET_KEY`, `DATABASE_URL`, `CLOUD_NAME`, `CLOUD_API_KEY` ni `CLOUD_API_SECRET`, y no existe `.env` local. No se exportaron valores ni se publicó ningún secreto. Para completar el resguardo de entorno, copiar los valores vigentes a un gestor de secretos o archivo cifrado fuera del repositorio.

## Comportamiento y rutas observados

| Ruta | Comportamiento actual |
| --- | --- |
| `/` | Landing estática. |
| `/home/` | Inicio: posts publicados, categorías y secciones builds, guides y reviews. |
| `/about/` | Página institucional. |
| `/contact/` | Formulario de contacto; en POST válido intenta enviar correo a `DEFAULT_FROM_EMAIL`. |
| `/posts/search/` | Búsqueda de posts publicados por título/contenido, categoría y orden. |
| `/posts/new/` | Creación de post; requiere sesión y permiso `posts.add_post`. |
| `/posts/<slug>/` | Detalle de post publicado y comentarios; comentar requiere sesión. |
| `/posts/<slug>/edit/`, `/delete/` | Edición/borrado; requieren los permisos correspondientes. |
| `/posts/category/<slug>/` | Listado de posts publicados de una categoría. |
| `/accounts/register/step1/`, `/step2/` | Registro en dos pasos mediante sesión. |
| `/accounts/login/`, `/logout/` | Inicio de sesión y cierre mediante POST. |
| `/accounts/profile/` | Perfil autenticado y carga de avatar. |
| `/accounts/password_reset/`, `/password_change/` | Flujos de contraseña provistos por Django. |
| `/admin/` | Administración de Django. |

La configuración actual tiene `DEBUG = False`, y la configuración de Cloudinary exige variables que no estaban disponibles. Por ello no se iniciaron páginas para captura visual: producir capturas representativas requiere el entorno vigente y datos de la instancia original. La lista anterior documenta el comportamiento implementado por las rutas, no una validación visual de producción.

## Pendientes obligatorios antes de modernizar datos o interfaz

1. Exportar la base de producción desde la cuenta que tenga `DATABASE_URL`.
2. Guardar los valores de entorno vigentes en un almacén privado cifrado.
3. Capturar `/`, `/home/`, `/about/`, `/contact/`, una categoría, un post, login y perfil con el entorno original operativo.
4. Registrar fecha, responsable y checksum de cada respaldo en este documento, sin incluir secretos.
