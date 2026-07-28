# PostgreSQL local con Docker Compose

El desarrollo usa PostgreSQL 18 en Docker y Django se ejecuta en el host con `uv`. No se incluye pgAdmin. Docker Desktop debe estar iniciado antes de ejecutar los comandos de Compose.

## Inicio

1. Copia `.env.example` a `.env` si aún no existe y conserva `DATABASE_URL=postgresql://caffeine:caffeine@localhost:5432/caffeine`.
2. Inicia la base y espera su healthcheck:

   ```powershell
   docker compose up -d db
   docker compose ps
   ```

3. Sincroniza y ejecuta Django desde el host:

   ```powershell
   uv sync
   uv run python manage.py migrate
   uv run python manage.py runserver
   ```

La aplicación estará disponible en `http://127.0.0.1:8000/`.

## Datos de demostración

La migración crea el esquema vacío. Para cargar los datos académicos incluidos en el repositorio, ejecuta:

```powershell
uv run python manage.py loaddata initial_data.json
```

## Detener y reiniciar

Para detener el contenedor sin borrar datos:

```powershell
docker compose stop db
```

Para reiniciarlo:

```powershell
docker compose up -d db
```

## Reset destructivo de la base

El siguiente comando elimina el contenedor y el volumen `postgres_data`, incluyendo todos sus datos locales. Úsalo sólo si quieres empezar desde cero:

```powershell
docker compose down --volumes
docker compose up -d db
uv run python manage.py migrate
```
