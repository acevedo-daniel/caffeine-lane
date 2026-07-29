# Despliegue de portfolio: Render, Neon, Cloudinary y Resend

Esta guía prepara un único entorno público de portfolio. No crea servicios ni
despliega nada por sí misma. Para un proyecto personal, no se recomienda pagar
por un staging permanente: la CI, Docker local y un despliegue de prueba antes
de conectar un dominio propio ofrecen una validación suficiente.

## Arquitectura propuesta

```text
GitHub Actions ──> Render Web Service (Django + Gunicorn)
                              │
                              ├──> Neon PostgreSQL
                              ├──> Cloudinary (media)
                              └──> Resend SMTP (email transaccional)
```

Render ejecuta el `Dockerfile` existente. Neon conserva los datos, Cloudinary
conserva la media y Resend entrega los emails; por tanto, el filesystem efímero
de Render no contiene información persistente.

## Antes de crear recursos

1. Mantener la CI verde en GitHub.
2. Elegir la rama que Render puede desplegar. Para el primer despliegue de
   portfolio puede ser `modernize/00-baseline`; cuando se integre, `main`.
3. Confirmar la URL temporal deseada, por ejemplo
   `caffeine-lane.onrender.com`. Un dominio propio es opcional y puede añadirse
   después.
4. Preparar un contenido demo pequeño mediante `seed_demo`; no importar el
   fixture legado ni usuarios reales.

## 1. Crear Neon PostgreSQL

1. Crear un proyecto Neon y una base para este portfolio.
2. Copiar la cadena de conexión TLS que proporciona Neon, incluyendo
   `sslmode=require` si Neon la incluye.
3. Guardarla como `DATABASE_URL` sólo en Render y en la sesión local temporal
   usada para la migración. No guardarla en `.env.example`, GitHub ni este
   documento.
4. En el plan gratuito, configurar un recordatorio para exportar un backup
   antes de cambios de esquema importantes:

   ```bash
   pg_dump --format=custom "$DATABASE_URL" > caffeine-lane-backup.dump
   ```

   El backup es privado y no se sube al repositorio. El restore de Neon en el
   plan gratuito tiene una ventana limitada, por lo que no sustituye un backup
   propio si se quiere conservar contenido.

## 2. Configurar Cloudinary

1. Crear o reutilizar una cuenta de Cloudinary para el portfolio.
2. Copiar `CLOUDINARY_URL` al gestor de variables de Render.
3. Para evitar mezclar archivos con otro proyecto, usar una cuenta separada o
   acordar un aislamiento de media antes de subir contenido real.
4. Verificar en la aplicación una portada y un avatar de prueba; después se
   pueden borrar desde Cloudinary.

## 3. Configurar Resend

1. Crear una cuenta de Resend y verificar un dominio o remitente permitido.
2. Crear una API key para SMTP. No la compartas en chat ni la subas a Git.
3. Configurar estas variables en Render:

   ```dotenv
   EMAIL_HOST=smtp.resend.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=resend
   EMAIL_HOST_PASSWORD=<RESEND_API_KEY>
   EMAIL_USE_TLS=true
   EMAIL_TIMEOUT=10
   DEFAULT_FROM_EMAIL=noreply@<tu-dominio-verificado>
   CONTACT_RECIPIENT_EMAIL=<tu-buzon-personal>
   ```

4. Enviar desde staging/portfolio una prueba de contacto y una recuperación de
   contraseña a un buzón propio. No probar contra direcciones de terceros.

## 4. Crear el Web Service en Render

1. Conectar Render al repositorio de GitHub y seleccionar la rama elegida.
2. Crear un **Web Service** con runtime **Docker** y el `Dockerfile` de la raíz.
3. Elegir la región más cercana a las personas que visitarán el portfolio y,
   si es posible, a la región de Neon.
4. Configurar el health check como `/health/`.
5. Empezar con el subdominio `onrender.com`; conectar el dominio propio sólo
   después de validar la aplicación.
6. Desactivar el auto-deploy hasta completar la primera migración y smoke test.

### Variables de Render

Crear las siguientes variables en el panel de Render. Los valores entre
corchetes son secretos o decisiones locales y no deben incluirse en Git:

```dotenv
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=[clave aleatoria larga y única]
DATABASE_URL=[cadena TLS de Neon]
ALLOWED_HOSTS=[tu-servicio.onrender.com]
CSRF_TRUSTED_ORIGINS=https://[tu-servicio.onrender.com]
CLOUDINARY_URL=[credencial de Cloudinary]
DEFAULT_FROM_EMAIL=noreply@[dominio-verificado-en-resend]
CONTACT_RECIPIENT_EMAIL=[tu-buzon]
EMAIL_HOST=smtp.resend.com
EMAIL_PORT=587
EMAIL_HOST_USER=resend
EMAIL_HOST_PASSWORD=[API key de Resend]
EMAIL_USE_TLS=true
EMAIL_TIMEOUT=10
USE_X_FORWARDED_PROTO=true
CSP_ENFORCE=false
SECURE_HSTS_SECONDS=3600
SECURE_HSTS_INCLUDE_SUBDOMAINS=false
SECURE_HSTS_PRELOAD=false
```

Cuando se conecte un dominio propio, añadir ambos hosts y orígenes mientras se
mantiene el subdominio de Render:

```dotenv
ALLOWED_HOSTS=tu-servicio.onrender.com,www.tu-dominio.com
CSRF_TRUSTED_ORIGINS=https://tu-servicio.onrender.com,https://www.tu-dominio.com
```

## 5. Ajuste necesario antes del primer despliegue

El `Dockerfile` actual fija Gunicorn al puerto `8000`. Render permite configurar
el puerto, pero es preferible adaptar la imagen para que use la variable
`PORT` que entrega la plataforma y mantenga `8000` como valor local. Ese cambio
se implementará antes de crear el servicio para evitar depender de un ajuste
manual de plataforma.

El `ENTRYPOINT` ya ejecuta `collectstatic`; no se deben añadir `migrate`,
`loaddata` ni `createsuperuser` al comando de inicio.

## 6. Migración explícita de release

En un servicio gratuito, no asumir acceso a tareas one-off o shell remoto. La
primera migración puede ejecutarse desde una máquina local confiable usando las
mismas variables de producción, antes de activar el deploy web:

```bash
uv run python manage.py check --deploy
uv run python manage.py migrate --noinput
uv run python manage.py seed_demo
```

`seed_demo` es opcional e idempotente. Para no depender de una estación local a
largo plazo, el siguiente paso sería añadir un workflow manual de GitHub Actions
que ejecute sólo `migrate` con secretos de entorno; no debe ejecutarse con cada
push automáticamente.

## 7. Primer deploy y smoke test

1. Autorizar manualmente el primer deploy desde Render.
2. Verificar logs: `collectstatic` completa y Gunicorn inicia sin traceback.
3. Comprobar:

   - `GET /health/` devuelve `200` y `{"status": "ok"}`.
   - `/home/`, búsqueda, una categoría y un post publicado cargan.
   - Un draft devuelve `404` por URL pública.
   - Registro, login, logout por POST y perfil funcionan.
   - Contacto y password reset llegan a un buzón propio mediante Resend.
   - Una imagen subida llega a Cloudinary.
   - Django Admin permite publicar y moderar con una cuenta staff.

4. Mantener `CSP_ENFORCE=false` inicialmente y revisar los reportes CSP en logs.
5. Tras varios accesos sin errores, activar el auto-deploy para la rama elegida
   si se desea.

## Rollback y operación

- Registrar el commit y el deploy anterior de Render antes de cada cambio.
- Si falla la aplicación sin migración incompatible, usar el rollback de Render
  al deploy anterior.
- Antes de migraciones relevantes, crear un `pg_dump` de Neon.
- No restaurar ni borrar datos por una prueba de portfolio; confirmar primero el
  diagnóstico y el backup disponible.
- Dejar CSP en modo reporte hasta revisar sus violaciones; no resolverlas con
  `unsafe-inline`.

## Datos que deben confirmarse antes de implementar

No envíes secretos por chat. Basta con confirmar valores no sensibles y cargar
los secretos directamente en los paneles de cada proveedor.

| Dato | Ejemplo de decisión |
| --- | --- |
| Rama de primer deploy | `modernize/00-baseline` o `main` |
| Nombre de servicio Render | `caffeine-lane-portfolio` |
| Región Render y Neon | La misma región o la más cercana posible |
| URL inicial | Subdominio de Render o dominio propio |
| Dominio de correo verificado | `example.com` |
| Remitente y destinatario de contacto | Direcciones controladas por ti |
| Cloudinary aislado | Cuenta propia o cuenta/proyecto acordado |
| Contenido inicial | Sólo `seed_demo` o importación seleccionada |
| Estrategia de migración | Manual local al inicio; workflow manual después |

La implementación posterior sólo requiere acceso autorizado al panel de Render
y que las variables secretas estén cargadas allí; no requiere publicar ninguna
clave en el repositorio.
