# Despliegue con Docker

La imagen se construye de forma multi-etapa: compila los assets de Tailwind, instala
solamente las dependencias runtime de Python y ejecuta Gunicorn como el usuario `app`.
No copia `.env`, `media/`, `node_modules` ni `staticfiles`.

```bash
docker build -t caffeine-lane .
docker run --rm -p 8000:8000 --env-file .env caffeine-lane
```

El contenedor usa `config.settings.production`, recoge estáticos al iniciar y expone
`GET /health/`. La media se almacena en Cloudinary, por lo que el contenedor no depende
de un volumen de media local.

## Release de migraciones

Las migraciones no se ejecutan al iniciar el contenedor. Ejecútalas como una operación
de release única del proveedor, usando la misma imagen y las variables de producción:

```bash
docker run --rm --env-file .env caffeine-lane python manage.py migrate --noinput
```

Después inicia los procesos web normalmente. No se ejecutan fixtures ni se crean
superusuarios durante el build, release o arranque.
