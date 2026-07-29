# Despliegue con Docker

La imagen multi-stage compila los assets de Tailwind, instala las dependencias
runtime de Python y ejecuta Gunicorn como el usuario no privilegiado `app`. No
copia `.env`, `media/`, `node_modules` ni `staticfiles`.

```bash
docker build -t caffeine-lane .
docker run --rm -p 8000:8000 --env-file .env caffeine-lane
```

El contenedor usa `config.settings.production`, expone `GET /healthz/`, sirve
estaticos con WhiteNoise y guarda la media en Cloudinary. Por eso no depende de
un volumen local para archivos subidos.

## Fresh baseline obligatorio

Esta rama no es compatible con una base creada desde `main`. La migracion
`accounts.0001_initial` evoluciono desde `auth.User` mas `accounts.Profile` a
un modelo `accounts.User` personalizado con el mismo identificador de
migracion. Crea una base de Neon nueva; no intentes reutilizar o convertir la
anterior en caliente.

El proceso web ejecuta `python manage.py check_fresh_baseline` y aborta si
detecta la tabla heredada `accounts_profile`. Esta comprobacion no borra datos.

## Migracion de release

Render Free no ofrece una shell de ejecución. Por eso la imagen de producción
ejecuta tareas idempotentes de release antes de iniciar Gunicorn: migra con
`DIRECT_DATABASE_URL`, vuelve a la conexión pooled y ejecuta
`seed_portfolio`. Esto ocurre en cada arranque; la semilla usa
`update_or_create` y solo sube una imagen si el post todavía no la tiene.

Para ejecutar la misma verificación desde una máquina de confianza, con ambas
conexiones de Neon:

```bash
./scripts/release.sh
```

En PowerShell:

```powershell
bash ./scripts/release.sh
```

El script usa temporalmente `DIRECT_DATABASE_URL`, ejecuta `migrate --noinput`
y verifica que `posts.0007_create_structural_categories` y las categorías
`builds`, `guides` y `reviews` estén presentes. En Render, el entrypoint carga
el portfolio público y sus imágenes en Cloudinary antes de iniciar Gunicorn.

El Web Service de Render requiere la URL pooled en `DATABASE_URL` y la conexión
directa en `DIRECT_DATABASE_URL`; no puede iniciar sin ambas ni recurrir a
SQLite. No se cargan fixtures ni se crean superusuarios durante el build o el
arranque.
