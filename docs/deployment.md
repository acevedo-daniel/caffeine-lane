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

Las migraciones no se ejecutan durante el arranque del servidor. Ejecutalas una
vez desde una máquina de confianza o un workflow manual de release, con las
mismas variables de producción y ambas conexiones de Neon:

```bash
./scripts/release.sh
```

En PowerShell:

```powershell
bash ./scripts/release.sh
```

El script usa temporalmente `DIRECT_DATABASE_URL`, ejecuta `migrate --noinput`
y verifica que `posts.0007_create_structural_categories` y las categorías
`builds`, `guides` y `reviews` estén presentes. Luego, si corresponde, ejecutá
manualmente `uv run python manage.py seed_portfolio` una única vez para cargar
el contenido público y sus imágenes en Cloudinary.

El Web Service de Render siempre requiere la URL pooled en `DATABASE_URL`; no
puede iniciar sin ella ni recurrir a SQLite. `DIRECT_DATABASE_URL` solo se usa
en la tarea manual de release. No se cargan fixtures ni se crean superusuarios
durante el build o el arranque.
