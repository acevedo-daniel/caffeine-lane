# Runbook de staging y rollout de v2

Este documento prepara el despliegue de v2 sin ejecutar ningún despliegue ni
modificar el servicio legado. La imagen, la migración y el tráfico se gestionan
como operaciones separadas.

## Auditoría disponible

- El único remoto configurado es GitHub (`acevedo-daniel/caffeine-lane`).
- El repositorio usa el `Dockerfile` como única vía de arranque del web process;
  no contiene manifiestos ni configuración de Heroku, Render, Railway, Fly.io u
  otro proveedor.
- La aplicación necesita PostgreSQL, Cloudinary, Resend mediante Anymail y Gunicorn; sus logs van
  a stdout. Cloudinary ya es el storage de media de producción.

No es posible identificar ni cambiar el proveedor actual sin acceso a su panel,
al dominio o a sus credenciales. Conserva el proveedor existente para staging
si ofrece un servicio web, PostgreSQL administrado, variables de entorno, HTTPS
y logs. No se debe introducir otro proveedor sólo para este rollout.

## Crear staging

- [ ] Crear un servicio o entorno **staging** aislado del servicio legado y sin
  apuntar tráfico público de producción.
- [ ] Asignar un subdominio, por ejemplo `staging.example.com`, y verificar su
  certificado HTTPS antes de habilitar tráfico.
- [ ] Crear una base PostgreSQL de staging independiente y restringir su red al
  servicio de staging.
- [ ] Usar credenciales de Cloudinary distintas de producción, o confirmar con
  el equipo un aislamiento equivalente antes de subir media de prueba.
- [ ] Configurar una API key de Resend y un destinatario de staging controlado; nunca
  reutilizar listas reales de destinatarios para pruebas.
- [ ] Configurar un healthcheck HTTP contra `GET /health/`.
- [ ] Retener logs de aplicación, acceso y base durante un periodo acordado; al
  menos deben poder consultarse durante la ventana de validación y rollback.

## Variables de staging

Las variables se cargan en el proveedor, no en Git ni en la imagen:

```dotenv
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<clave-aleatoria-distinta-de-produccion>
DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<staging_db>
ALLOWED_HOSTS=staging.example.com
CSRF_TRUSTED_ORIGINS=https://staging.example.com
CLOUDINARY_URL=<credencial-aislada-de-staging>
DEFAULT_FROM_EMAIL=noreply@staging.example.com
CONTACT_RECIPIENT_EMAIL=<buzon-controlado>
RESEND_API_KEY=<api-key-de-resend>
USE_X_FORWARDED_PROTO=true
CSP_ENFORCE=false
SECURE_HSTS_SECONDS=3600
SECURE_HSTS_INCLUDE_SUBDOMAINS=false
SECURE_HSTS_PRELOAD=false
```

`CSP_ENFORCE=false` mantiene CSP en modo reporte durante la validación. Activarlo
requiere revisar primero los reportes de violación registrados en stdout.

## Checklist de release

- [ ] El commit está en `main`, la CI de ambas versiones de Python está verde y
  la imagen se construye desde ese commit.
- [ ] Registrar el digest inmutable de la imagen candidata y el commit asociado.
- [ ] Ejecutar con las variables de staging:

  ```bash
  docker run --rm --env-file <staging-env> <image> python manage.py check --deploy
  docker run --rm --env-file <staging-env> <image> python manage.py migrate --noinput
  ```

- [ ] Ejecutar las migraciones una sola vez como tarea de release; el proceso
  web no ejecuta migraciones ni carga fixtures ni crea superusuarios.
- [ ] Iniciar la imagen web y confirmar que `collectstatic` termina antes de
  Gunicorn. La imagen usa Cloudinary para media, no un volumen de media local.
- [ ] Confirmar en los logs el inicio de Gunicorn, la salida de Django y los
  reportes CSP.

## Backups de PostgreSQL

- [ ] Antes de las migraciones, solicitar o ejecutar un backup consistente de
  la base de staging y registrar su fecha, tamaño y ubicación privada.
- [ ] Verificar la política de backups automáticos, cifrado, retención y el
  procedimiento de restauración del proveedor.
- [ ] Probar una restauración en una base de prueba independiente; no restaurar
  sobre staging ni producción como parte de una prueba.
- [ ] Repetir el backup inmediatamente antes de cualquier futura migración de
  producción.

Ejemplo genérico para un PostgreSQL accesible desde una tarea de release:

```bash
pg_dump --format=custom --no-owner "$DATABASE_URL" > staging-before-v2.dump
pg_restore --list staging-before-v2.dump
```

El fichero resultante es privado: no se sube al repositorio ni se adjunta a logs.

## Smoke tests de staging

- [ ] `GET /health/` devuelve `200` y `{"status": "ok"}`.
- [ ] El dominio redirige HTTP a HTTPS y las cookies de sesión/CSRF son seguras.
- [ ] `GET /`, `/home/`, una categoría, búsqueda, un post publicado y una URL
  de draft muestran el comportamiento esperado; el draft devuelve `404`.
- [ ] Registro, login por email, logout por POST, perfil y avatar se prueban con
  una cuenta de staging.
- [ ] Contacto llega al buzón controlado con `reply_to`; password reset genera
  texto y HTML sin enviar a usuarios reales.
- [ ] Una imagen de prueba se almacena en el storage aislado y la interfaz sigue
  funcionando cuando una portada o avatar falta.
- [ ] Admin, publicación, comentarios y moderación se prueban con usuarios de
  staging y permisos explícitos.
- [ ] No hay errores 5xx en logs; revisar reportes CSP antes de activar
  `CSP_ENFORCE=true`.

## Observabilidad y rollback

- [ ] Configurar alertas para healthcheck fallido, reinicios del proceso, 5xx y
  capacidad/conexiones de PostgreSQL según el proveedor disponible.
- [ ] Registrar el digest de v2, el digest de la versión anterior y la hora de
  cada migración.
- [ ] Mantener el despliegue legado y su ruta de tráfico intactos hasta que el
  responsable valide staging y autorice un cambio de producción.
- [ ] Probar rollback en staging: desplegar la imagen anterior **sin** deshacer
  migraciones, confirmar `/health/` y los flujos públicos, y volver a v2.
- [ ] Si una migración no es compatible hacia atrás, el rollback de aplicación
  requiere un plan específico; restaurar una base sólo desde el backup validado
  y con autorización explícita.

No se elimina el servicio legado, su base ni su media durante esta fase.
