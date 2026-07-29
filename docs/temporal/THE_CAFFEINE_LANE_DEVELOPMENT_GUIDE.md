# The Caffeine Lane — Guía completa de modernización y desarrollo

**Repositorio:** `acevedo-daniel/caffeine-lane`
**Objetivo:** transformar el proyecto final del Informatorio en una aplicación Django moderna, mantenible, segura y presentable, sin perder su identidad original.
**Fecha de referencia técnica:** 27 de julio de 2026.
**Versión objetivo:** `2.0.0`.

---

## 1. Propósito

The Caffeine Lane no será tratado como un ejercicio descartable ni como un proyecto que deba reescribirse por completo. La modernización tendrá tres objetivos simultáneos:

1. Conservar el valor sentimental, visual y narrativo del proyecto.
2. Corregir las decisiones frágiles o incompletas de la versión académica.
3. Aplicar el criterio técnico que usaríamos al iniciar hoy una aplicación Django real.

La versión moderna debe seguir siendo reconocible como The Caffeine Lane, pero su base técnica deberá ser reproducible y confiable.

### Resultado esperado

Al finalizar, el proyecto deberá tener:

- Django y dependencias compatibles y actualizadas.
- PostgreSQL como base de datos oficial.
- Entornos separados para desarrollo, pruebas y producción.
- Usuario personalizado y autenticación completa.
- Modelos y flujos editoriales corregidos.
- Comentarios funcionales y moderables.
- Tailwind compilado localmente, sin Play CDN.
- Pruebas automatizadas.
- CI en GitHub Actions.
- Despliegue reproducible.
- Documentación honesta.
- Datos de demostración seguros.
- Una versión pública estable y terminada.

---

## 2. Decisiones arquitectónicas

### 2.1 Monolito modular

El proyecto seguirá siendo un **monolito Django modular**.

No se introducirán:

- Microservicios.
- Django REST Framework sin una necesidad real.
- React, Next.js o una SPA.
- Una capa `repository` sobre el ORM.
- Clases base genéricas sin uso concreto.
- Celery, Redis o colas antes de existir una necesidad real.
- Separaciones de archivos que solo aumenten navegación.

Django Templates, el ORM, los formularios y el panel de administración son suficientes para este producto.

### 2.2 Sin carpeta `src/`

Aunque un layout `src/` es válido, para este proyecto no aporta una ventaja proporcional al costo del movimiento. The Caffeine Lane es una aplicación desplegable, no una librería Python reutilizable.

La estructura moderna conservará `manage.py`, `apps/` y `config/` en la raíz. Esto reduce complejidad y evita una migración puramente estética.

### 2.3 Capas internas con criterio

Cada aplicación podrá tener:

- `models.py`: estado y reglas estructurales.
- `querysets.py`: consultas reutilizables y encadenables.
- `selectors.py`: consultas de lectura complejas.
- `services.py`: operaciones con efectos, transacciones o varios pasos.
- `forms.py`: validación de entradas HTML.
- `views.py`: coordinación HTTP.
- `tests/`: pruebas separadas por responsabilidad.

No es obligatorio crear todos esos archivos desde el comienzo. Solo deben existir cuando contengan una responsabilidad real.

### 2.4 Sin lógica principal en signals

Los signals se reservarán para tareas realmente desacopladas. No se usarán para crear perfiles, publicar posts, modificar permisos o ejecutar procesos esenciales.

---

## 3. Stack técnico objetivo

| Área                | Elección                                                   |
| ------------------- | ---------------------------------------------------------- |
| Lenguaje            | Python 3.13 como entorno principal                         |
| Compatibilidad CI   | Python 3.13 y 3.14                                         |
| Framework           | Django 6.0.7 o parche posterior dentro de 6.0              |
| Base de datos       | PostgreSQL 18                                              |
| Driver              | Psycopg 3                                                  |
| Dependencias        | `pyproject.toml` + `uv.lock`                               |
| Gestor Python       | uv                                                         |
| Lint y formato      | Ruff                                                       |
| Pruebas             | pytest + pytest-django                                     |
| Cobertura           | pytest-cov                                                 |
| Datos de prueba     | factory-boy                                                |
| Templates           | Django Templates                                           |
| CSS                 | Tailwind CSS 4 CLI                                         |
| Gestor frontend     | pnpm                                                       |
| JavaScript          | JavaScript modular, sin framework                          |
| Servidor producción | Gunicorn mediante WSGI                                     |
| Estáticos           | WhiteNoise                                                 |
| Media               | local en desarrollo; Cloudinary inicialmente en producción |
| Contenedores        | Docker Compose para PostgreSQL                             |
| CI                  | GitHub Actions                                             |
| Seguridad navegador | CSP nativo de Django 6                                     |
| Logging             | logging estándar de Django hacia stdout                    |

### Límites de versiones

```toml
requires-python = ">=3.13,<3.15"

dependencies = [
  "Django>=6.0.7,<6.1",
]
```

`uv.lock` fijará las versiones exactas. No se usará Django 6.1 mientras siga siendo prerelease.

### Dependencias iniciales de producción

```text
Django
django-environ
psycopg[binary]
Pillow
gunicorn
whitenoise
cloudinary
django-cloudinary-storage
argon2-cffi
```

No se usarán simultáneamente `django-environ` y `dj-database-url`. `django-environ` será la única capa para leer y convertir variables de entorno.

### Dependencias de desarrollo

```text
ruff
pytest
pytest-django
pytest-cov
factory-boy
pre-commit
djlint
django-debug-toolbar
```

`django-stubs` y mypy quedarán como mejora opcional posterior.

---

## 4. Estructura final

```text
the-caffeine-lane-blog/
├── apps/
│   ├── accounts/
│   │   ├── migrations/
│   │   ├── tests/
│   │   │   ├── factories.py
│   │   │   ├── test_admin.py
│   │   │   ├── test_forms.py
│   │   │   ├── test_models.py
│   │   │   ├── test_services.py
│   │   │   └── test_views.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── managers.py
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── core/
│   │   ├── tests/
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── views.py
│   └── posts/
│       ├── migrations/
│       ├── tests/
│       │   ├── factories.py
│       │   ├── test_admin.py
│       │   ├── test_forms.py
│       │   ├── test_models.py
│       │   ├── test_queries.py
│       │   ├── test_services.py
│       │   └── test_views.py
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── models.py
│       ├── querysets.py
│       ├── selectors.py
│       ├── services.py
│       ├── urls.py
│       └── views.py
├── config/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── production.py
│   │   └── test.py
│   ├── asgi.py
│   ├── urls.py
│   └── wsgi.py
├── templates/
│   ├── layouts/base.html
│   ├── components/
│   ├── registration/
│   ├── 400.html
│   ├── 403.html
│   ├── 404.html
│   └── 500.html
├── static/
│   ├── src/css/app.css
│   ├── src/js/
│   ├── src/images/
│   └── dist/
├── docs/
│   ├── architecture.md
│   ├── audit-initial.md
│   ├── development.md
│   ├── deployment.md
│   └── decisions/
├── scripts/
│   ├── check.ps1
│   ├── check.sh
│   └── entrypoint.sh
├── .github/workflows/ci.yml
├── .env.example
├── .pre-commit-config.yaml
├── compose.yaml
├── Dockerfile
├── manage.py
├── package.json
├── pnpm-lock.yaml
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## 5. Reglas de trabajo

### Una fase por rama y pull request

```text
modernize/00-baseline
modernize/01-tooling
modernize/02-django-52
modernize/03-django-60
modernize/04-settings
modernize/05-accounts
```

Cada PR debe:

- Resolver una sola fase.
- No mezclar cambios visuales y de infraestructura.
- Incluir pruebas o explicar por qué todavía no corresponden.
- Enumerar los comandos ejecutados.
- Mantener el proyecto ejecutable.
- No modificar datos reales sin una copia previa.

### Convención de commits

```text
chore: preserve legacy baseline
build: migrate dependencies to uv
test: add characterization tests for posts
refactor: split Django settings by environment
feat: introduce custom user model
fix: preserve post slugs during updates
security: harden production settings
docs: document local development workflow
```

### Prohibiciones para la IA

Codex o ChatGPT no deben:

- Reescribir todo el proyecto en una sola tarea.
- Cambiar arquitectura y comportamiento simultáneamente.
- Eliminar migraciones sin una decisión expresa.
- Crear o publicar secretos.
- Ejecutar `git push`, mergear o desplegar sin autorización.
- Introducir una dependencia sin justificarla.
- Silenciar errores para conseguir una ejecución verde.
- Cambiar el diseño visual durante fases de backend.
- Añadir funcionalidades no solicitadas.
- Usar `ALLOWED_HOSTS = ["*"]`.
- Volver a crear un superusuario dentro de fixtures.

---

## 6. Comprobación estándar

```bash
uv lock --check
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run pytest
pnpm run build
```

En producción:

```bash
uv run python manage.py check --deploy --settings=config.settings.production
```

Se crearán `scripts/check.ps1` y `scripts/check.sh` para ejecutar estas comprobaciones y detenerse ante el primer error.

---

# 7. Plan por fases

## Fase 0 — Congelar y preservar la versión original

### Objetivo

Garantizar que la modernización no destruya el proyecto académico ni sus datos.

### Acciones

1. Confirmar que `main` está limpia.
2. Crear la etiqueta `legacy-informatorio-v1`.
3. Crear la rama `modernize/00-baseline`.
4. Guardar fuera del repositorio:
   - exportación privada de la base;
   - copia de media;
   - variables actuales;
   - capturas de las páginas principales.
5. Documentar rutas y comportamiento.
6. Crear `docs/audit-initial.md`.
7. No corregir código todavía.

### Criterio de salida

- Existe una etiqueta recuperable.
- Hay una copia privada de datos y media.
- El comportamiento visible está documentado.
- No se publicaron secretos nuevos.

### Prompt

```text
Audita el estado actual de acevedo-daniel/the-caffeine-lane-blog antes de modificarlo.

Trabaja solo en preservación:
- documenta estructura, rutas, variables y despliegue;
- crea docs/audit-initial.md;
- identifica qué datos deben respaldarse fuera del repositorio;
- no refactorices ni corrijas código;
- no elimines archivos;
- no hagas commit ni push.

Al terminar informa archivos creados, riesgos y pasos manuales pendientes.
```

## Fase 1 — Reproducir el legado localmente

### Objetivo

Levantar la versión original y registrar sus fallos reales antes de modernizarla.

### Acciones

- Crear un `.env` local privado.
- Ejecutar instalación, check, migraciones y servidor.
- Probar landing, home, categorías, búsqueda, registro, autenticación, perfil, posts, comentarios, contacto y password reset.
- Registrar errores confirmados.
- Añadir pruebas de caracterización.
- Reproducir el error de `Post.save()` mediante una prueba.

### Criterio de salida

- El proyecto puede ejecutarse o sus bloqueos están documentados.
- Existe un inventario de comportamiento.
- Los errores críticos son reproducibles.

### Prompt

```text
Levanta y caracteriza la versión actual del repositorio.

Objetivos:
- conseguir una ejecución local sin modernizar todavía;
- probar manualmente las rutas principales;
- agregar pruebas mínimas del comportamiento actual;
- reproducir con una prueba el error de Post.save() al editar sin cambiar el título.

No actualices Django, no cambies estructura y no corrijas el error todavía.
```

## Fase 2 — Migrar dependencias a uv

### Objetivo

Crear un entorno reproducible antes de actualizar el framework.

### Acciones

- Crear `pyproject.toml`.
- Migrar únicamente dependencias utilizadas.
- Separar runtime y desarrollo.
- Generar `uv.lock`.
- Crear `.python-version` con Python 3.13.
- Mantener temporalmente la versión de Django.
- Retirar `requirements.txt` cuando uv reproduzca el proyecto.

### Criterio de salida

- `uv sync` crea el entorno.
- `uv run python manage.py check` funciona.
- Producción no instala herramientas de desarrollo.

### Prompt

```text
Migra este proyecto de requirements.txt a pyproject.toml y uv.

Reglas:
- conserva por ahora las versiones funcionales;
- incluye solo dependencias realmente usadas;
- separa runtime y desarrollo;
- genera uv.lock;
- actualiza los comandos de desarrollo;
- no refactorices aplicaciones ni templates.

Valida con uv sync y manage.py check.
```

## Fase 3 — Ruff, pytest y pre-commit

### Objetivo

Establecer controles automáticos antes de cambios grandes.

### Acciones

- Configurar Ruff como linter y formatter.
- Configurar pytest-django y cobertura.
- Mover `tests.py` a carpetas `tests/`.
- Añadir factory-boy.
- Configurar pre-commit.
- Crear scripts de comprobación.
- Realizar el formateo mecánico en un commit separado.

### Prompt

```text
Configura la base de calidad del proyecto.

Agrega Ruff, pytest, pytest-django, pytest-cov, factory-boy y pre-commit.
Mueve las pruebas existentes a carpetas tests sin cambiar su comportamiento.
Crea scripts/check.ps1 y scripts/check.sh.
No corrijas todavía lógica de negocio.
```

## Fase 4 — Actualizar a Django 5.2 LTS corregido

### Objetivo

Actualizar desde 5.2.5 al último parche 5.2 antes del salto mayor.

### Acciones

- Usar `Django>=5.2.16,<5.3`.
- Reemplazar `psycopg2-binary` por `psycopg[binary]`.
- Ejecutar Django con warnings visibles.
- Corregir incompatibilidades sin refactorizar arquitectura.

### Prompt

```text
Actualiza el proyecto desde Django 5.2.5 al último parche estable de Django 5.2.

Además:
- reemplaza psycopg2-binary por Psycopg 3;
- actualiza únicamente dependencias necesarias;
- ejecuta Django con warnings habilitados;
- conserva el comportamiento visible.

No saltes todavía a Django 6.
```

## Fase 5 — Actualizar a Django 6.0

### Objetivo

Llevar la aplicación a Django 6.0 estable sin mezclar otros refactors.

### Acciones

- Usar `Django>=6.0.7,<6.1`.
- Revisar incompatibilidades.
- Corregir APIs eliminadas o deprecadas.
- Mantener WSGI y Gunicorn.
- No activar CSP todavía si existen scripts inline.

### Prompt

```text
Actualiza el proyecto estabilizado en Django 5.2 al último parche estable de Django 6.0.

Trabaja solo en compatibilidad:
- corrige APIs eliminadas o deprecadas;
- conserva WSGI y Gunicorn;
- no cambies estructura, modelos ni diseño;
- no uses Django 6.1 prerelease.

Valida con checks, migraciones y pytest.
```

## Fase 6 — Reorganizar settings y configuración

### Objetivo

Separar correctamente desarrollo, pruebas y producción.

### Estructura

```text
config/settings/
├── __init__.py
├── base.py
├── local.py
├── production.py
└── test.py
```

### Responsabilidades

**`base.py`:** apps, middleware, templates, internacionalización, validadores y configuración común.
**`local.py`:** debug, hosts locales, email por consola, media local y Debug Toolbar.
**`test.py`:** email en memoria, storage temporal, hasher rápido y cero servicios externos.
**`production.py`:** secretos obligatorios, hosts explícitos, HTTPS, WhiteNoise, storage remoto y logging.

### Variables mínimas

```dotenv
DJANGO_SETTINGS_MODULE=config.settings.local
SECRET_KEY=change-me-locally
DEBUG=true
DATABASE_URL=postgresql://caffeine:caffeine@localhost:5432/caffeine
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000
CLOUDINARY_URL=
DEFAULT_FROM_EMAIL=noreply@example.com
CONTACT_RECIPIENT_EMAIL=owner@example.com
```

### Reglas

- No usar una clave insegura de respaldo en producción.
- No usar `ALLOWED_HOSTS = ["*"]`.
- Cloudinary no debe ser obligatorio para tests.
- Local no debe necesitar credenciales externas.

### Prompt

```text
Divide la configuración Django en base, local, production y test.

Usa django-environ como única capa de variables.
Local y tests no deben depender de Cloudinary ni SMTP.
Producción debe exigir SECRET_KEY, DATABASE_URL y hosts explícitos.
Crea .env.example sin secretos.
No cambies todavía modelos ni templates.
```

## Fase 7 — PostgreSQL local con Docker Compose

### Objetivo

Usar la misma familia de base de datos en desarrollo y producción.

### Acciones

- Crear `compose.yaml` con PostgreSQL 18.
- Añadir volumen y healthcheck con `pg_isready`.
- Ejecutar Django en el host mediante uv.
- Documentar el reset de la base.
- No agregar pgAdmin por defecto.

### Flujo esperado

```bash
docker compose up -d db
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

### Prompt

```text
Agrega un compose.yaml sencillo para PostgreSQL 18.

Debe incluir volumen, healthcheck y variables documentadas.
Django seguirá ejecutándose en el host mediante uv.
Actualiza .env.example y la guía de desarrollo.
No agregues pgAdmin ni contenedores innecesarios.
```

## Fase 8 — Seguridad base de producción

### Objetivo

Eliminar la configuración peligrosa de la versión académica.

### Acciones

- Configurar redirección HTTPS y cookies seguras.
- Configurar HSTS de forma progresiva.
- Configurar proxy SSL cuando el proveedor lo requiera.
- Definir referrer policy y hosts explícitos.
- Usar Argon2 como primer password hasher.
- Añadir logging a stdout.
- Crear páginas 400, 403, 404 y 500.
- Ejecutar `check --deploy`.
- Dejar CSP para después de retirar inline scripts.

### Prompt

```text
Endurece config.settings.production siguiendo los checks de despliegue de Django 6.

Elimina valores inseguros y configura HTTPS, cookies, HSTS, hosts, CSRF y logging.
Usa Argon2 como hasher principal.
No actives CSP estricta todavía.
Ejecuta check --deploy y documenta cada decisión.
```

## Fase 9 — Reset controlado y usuario personalizado

### Decisión

La base actual contiene datos demostrativos, contenido repetido y un superusuario dentro de un fixture público. Se recomienda un **reset controlado del esquema** en la rama de modernización.

Esto solo es válido porque no se pretende preservar usuarios reales. Si aparecen datos valiosos, deberá hacerse una migración explícita.

### Modelo recomendado

```text
accounts.User(AbstractUser)
- email único
- username como handle público
- display_name opcional
- bio
- avatar
- personal_url
- has_motorcycle
- created_at
- updated_at
```

El inicio de sesión será mediante email. `username` seguirá existiendo como nombre público.

Se eliminarán:

- El modelo `Profile`.
- El signal que crea perfiles.
- Campos personales sin uso funcional.
- Imports directos de `django.contrib.auth.models.User`.

### Acciones

1. Confirmar respaldo privado.
2. Crear usuario personalizado y manager.
3. Definir `AUTH_USER_MODEL`.
4. Adaptar formularios y admin.
5. Recrear migraciones iniciales propias.
6. Crear una base nueva.
7. Completar registro, login, logout por POST, perfil, cambio y recuperación de contraseña.
8. Añadir pruebas.

### Prompt

```text
Implementa un usuario personalizado para la versión 2.

Usa AbstractUser, email único como login y username como handle público.
Integra los campos útiles del antiguo Profile dentro del usuario.
Elimina el signal de perfil.
Completa registro, login, logout, perfil, cambio y recuperación de contraseña.
Asume una base nueva y crea migraciones iniciales limpias.

Agrega pruebas completas y no toques todavía la app posts.
```

## Fase 10 — Modernizar categorías y publicaciones

### Objetivo

Convertir `posts` en un dominio editorial confiable.

### Campos recomendados

**Category:** `name`, `slug`, `description`, `image`, timestamps.
**Post:** `title`, `slug`, `excerpt`, `content`, `featured_image`, `featured_image_alt`, `author`, `categories`, `status`, `published_at`, timestamps.

### Reglas

- `Status` usa `models.TextChoices`.
- El slug se genera al crear y permanece estable después de publicar.
- La publicación exige `published_at`.
- Toda imagen visible tiene alt text.
- El autor usa `settings.AUTH_USER_MODEL`.
- Las relaciones tienen `related_name`.
- Los visitantes solo ven posts publicados.
- Los drafts no son accesibles por URL pública.

### QuerySet recomendado

```text
PostQuerySet.published()
PostQuerySet.with_author()
PostQuerySet.with_categories()
PostQuerySet.for_listing()
```

### Servicios posibles

```text
publish_post()
unpublish_post()
```

No crear servicios para envolver un simple `form.save()`.

### Prompt

```text
Moderniza los modelos Category y Post.

Corrige slugs, agrega estado con TextChoices, published_at, excerpt y alt text.
Usa un QuerySet para publicaciones públicas y optimiza relaciones.
Mantén URLs estables después de publicar.
Adapta formularios, vistas, admin y templates solo lo necesario.
Agrega pruebas de modelos, permisos y vistas.
```

## Fase 11 — Importación segura de contenido legado

### Objetivo

Preservar únicamente el contenido valioso sin reutilizar el fixture peligroso.

### Acciones

- Eliminar `initial_data.json` del despliegue.
- Crear `python manage.py seed_demo`.
- Hacer el comando idempotente.
- Crear categorías por slug.
- Crear pocos posts limpios y sin usuarios privilegiados.
- No incluir contraseñas.
- Crear un importador separado para contenido seleccionado.
- Revisar duplicados, encoding, imágenes y texto provisional.

### Prompt

```text
Reemplaza initial_data.json por un comando idempotente seed_demo.

No debe crear superusuarios ni incluir contraseñas.
Debe crear categorías y unos pocos posts de demostración limpios.
Crea una estrategia separada para importar contenido legado seleccionado.
Retira loaddata del build y agrega pruebas del comando.
```

## Fase 12 — Comentarios completos y moderación

### Objetivo

Terminar la funcionalidad parcialmente implementada.

### Alcance

- Comentarios principales.
- Respuestas de un solo nivel.
- Edición por autor.
- Indicador de edición.
- Retiro por autor.
- Ocultamiento por moderador.
- Conservación de la conversación.
- Protección básica contra spam.

### Reglas

- Una respuesta pertenece al mismo post que su padre.
- No hay niveles infinitos.
- Solo autor o moderador pueden editar.
- Acciones destructivas usan POST.
- Las plantillas no muestran controles sin permiso.

### Prompt

```text
Completa el sistema de comentarios.

Implementa respuestas de un solo nivel, edición marcada y moderación.
Valida que una respuesta pertenezca al mismo post.
Usa POST para acciones destructivas.
Conserva la conversación cuando un comentario se retira.
Agrega pruebas de permisos y casos maliciosos.
```

## Fase 13 — Búsqueda, relacionados y rendimiento

### Objetivo

Reemplazar consultas incompletas y eliminar N+1.

### Acciones obligatorias

- Implementar posts relacionados por categorías.
- Añadir paginación.
- Usar `select_related` para autor.
- Usar `prefetch_related` para categorías.
- Evitar consultas desde templates.
- Probar el número de consultas de listados importantes.
- Corregir el formulario de búsqueda.

### Mejora recomendada

Implementar búsqueda de texto completo de PostgreSQL con:

- `SearchVector`.
- `SearchQuery`.
- `SearchRank`.
- Título, excerpt y contenido.
- Filtro por categoría.
- Orden por relevancia o fecha.
- Índice GIN cuando la consulta esté validada.

### Prompt

```text
Optimiza lectura y búsqueda de posts.

Implementa related_posts, paginación y QuerySets con select_related/prefetch_related.
Corrige el formulario de búsqueda.
Después agrega búsqueda de texto completo de PostgreSQL con ranking sin romper filtros.
Incluye pruebas y evita consultas N+1.
```

## Fase 14 — Tailwind CSS 4 compilado

### Objetivo

Conservar la identidad visual eliminando Play CDN e inline assets.

### Acciones

- Crear `package.json` y usar pnpm.
- Instalar Tailwind CSS 4 y su CLI.
- Crear `static/src/css/app.css` y `static/dist/css/app.css`.
- Agregar scripts `dev:css`, `build:css` y `build`.
- Eliminar Play CDN.
- Extraer JavaScript y CSS inline.
- Dividir `base.html` en layout y componentes.
- Usar template partials donde aporten claridad.
- Corregir idioma, copyright, enlaces `#`, navegación móvil, focus y formularios.
- Mantener paridad visual antes de rediseñar.

### Prompt

```text
Migra el frontend desde Tailwind Play CDN a Tailwind CSS 4 compilado con pnpm y CLI.

Extrae CSS y JavaScript inline a static/src.
Divide base.html en layout y componentes reutilizables.
Conserva primero la apariencia actual.
Corrige accesibilidad, enlaces falsos y navegación responsive sin rediseño completo.
Valida con pnpm run build.
```

## Fase 15 — CSP

### Objetivo

Aprovechar el soporte CSP nativo de Django 6 después de limpiar inline assets.

### Acciones

- Agregar `ContentSecurityPolicyMiddleware`.
- Comenzar con `SECURE_CSP_REPORT_ONLY`.
- Permitir recursos propios y el proveedor de imágenes.
- Revisar violaciones.
- Evitar `unsafe-inline` como solución general.
- Activar `SECURE_CSP` cuando todas las páginas funcionen.

### Prompt

```text
Configura CSP nativa de Django 6.

Empieza en report-only, revisa violaciones y crea una política mínima para recursos propios y el proveedor de imágenes.
No uses unsafe-inline como solución general.
Cuando todas las páginas funcionen, activa la política y documenta las fuentes permitidas.
```

## Fase 16 — Media e imágenes

### Objetivo

Separar correctamente assets del proyecto y archivos subidos.

### Reglas

- Logos, fondos y recursos del diseño van a `static/`.
- Avatares y portadas subidas van al storage de media.
- `media/` no se versiona.
- Desarrollo usa filesystem local.
- Producción usa Cloudinary inicialmente.
- El avatar por defecto es estático.
- Las imágenes se validan por tamaño, formato y peso.
- Las plantillas soportan imágenes faltantes.

### Prompt

```text
Ordena el manejo de imágenes.

Separa assets estáticos de uploads.
Desactiva el versionado de media.
Usa filesystem local en desarrollo/tests y Cloudinary en producción.
Agrega validación de tamaño, peso y formato, además de placeholders seguros.
No cambies proveedor todavía.
```

## Fase 17 — Email, contacto y password reset

### Objetivo

Completar los flujos de correo y evitar formularios falsamente funcionales.

### Acciones

- Consola en local.
- Backend en memoria para tests.
- SMTP o proveedor real en producción.
- Configurar remitentes, destinatario y timeout.
- Completar todas las rutas y templates de password reset.
- Crear emails en texto y HTML.
- Usar `reply_to` para contacto.
- Añadir honeypot, límites de longitud y protección de frecuencia.
- Probar mediante `mail.outbox`.

### Prompt

```text
Completa email y formularios de contacto.

Configura consola local, locmem en tests y variables de producción.
Implementa todas las vistas y templates de password reset.
Usa EmailMessage con reply_to para contacto.
Agrega validación, honeypot y protección básica contra abuso.
Incluye pruebas con mail.outbox.
```

## Fase 18 — Admin editorial

### Objetivo

Convertir Django Admin en una herramienta agradable para mantener el blog.

### Acciones

- Mejorar listados, filtros y búsquedas.
- Añadir autocompletado y campos readonly.
- Crear acciones de publicar y despublicar.
- Mostrar miniaturas cuando aporten valor.
- Facilitar moderación de comentarios.
- Reutilizar servicios y reglas existentes.
- Probar permisos de staff.

### Prompt

```text
Mejora el Django Admin como panel editorial.

Optimiza listados, filtros, búsquedas, autocompletado y acciones de publicar/despublicar.
Agrega moderación clara de comentarios.
Reutiliza las reglas de dominio existentes y no dupliques lógica en admin.
Incluye pruebas de permisos principales.
```

## Fase 19 — CI con GitHub Actions

### Objetivo

Impedir que `main` vuelva a aceptar cambios rotos.

### Pipeline mínimo

1. Checkout.
2. Instalar uv y Python.
3. `uv sync --locked`.
4. PostgreSQL como service.
5. Ruff check y format check.
6. `makemigrations --check --dry-run`.
7. pytest con cobertura.
8. Instalar pnpm con lockfile.
9. Build de Tailwind.
10. `check --deploy` con variables seguras.

### Matriz

- Python 3.13 como principal.
- Python 3.14 como comprobación de compatibilidad.

La cobertura debe crecer de forma progresiva. El objetivo será al menos 80% en autenticación, publicaciones y comentarios, no 100% artificial.

### Prompt

```text
Crea un workflow de GitHub Actions para este proyecto.

Debe validar uv.lock, Ruff, formato, migraciones, pytest con PostgreSQL, cobertura, pnpm y build de Tailwind.
Agrega check --deploy con variables seguras de CI.
Usa Python 3.13 como principal y comprueba 3.14.
No despliegues desde este workflow todavía.
```

## Fase 20 — Dockerfile y despliegue reproducible

### Objetivo

Eliminar scripts de build inseguros y crear una imagen repetible.

### El contenedor debe

- Usar varias etapas.
- Compilar Tailwind.
- Instalar solo dependencias runtime.
- Ejecutar como usuario no root.
- Ejecutar `collectstatic`.
- Lanzar Gunicorn.
- Exponer un endpoint `/health/`.
- No ejecutar `loaddata`.
- No crear superusuarios.
- No depender de media local persistente.

Las migraciones deben ser una operación explícita de release cuando el proveedor lo permita.

### Prompt

```text
Crea un Dockerfile multi-stage para producción.

Compila Tailwind, instala dependencias bloqueadas con uv, ejecuta como usuario no root y lanza Gunicorn.
No cargues fixtures ni crees superusuarios.
Agrega un endpoint de healthcheck.
Documenta cómo ejecutar migraciones como paso separado de release.
```

## Fase 21 — Staging, despliegue y observabilidad

### Objetivo

Publicar la versión 2 con capacidad de diagnóstico y rollback.

### Acciones

- Crear staging.
- Configurar dominio, HTTPS, base, storage, email, hosts y CSRF.
- Ejecutar migraciones, collectstatic, check deploy y smoke tests.
- Configurar backups de PostgreSQL.
- Confirmar logs.
- Probar rollback.
- No eliminar el despliegue legado antes de validar el nuevo.

### Prompt

```text
Prepara el despliegue de la versión 2 sin modificar todavía producción.

Crea una checklist de staging, variables, migraciones, media, backups, smoke tests y rollback.
Audita el proveedor actual y adapta la configuración sin introducir otro proveedor innecesariamente.
No despliegues ni borres el servicio anterior sin mi autorización.
```

## Fase 22 — Documentación y lanzamiento 2.0

### Objetivo

Cerrar el proyecto como un producto terminado y mantenible.

### README final

Debe explicar:

- Historia del proyecto y del Informatorio.
- Motivación de la modernización.
- Capturas.
- Funcionalidades reales.
- Stack.
- Instalación local.
- Variables.
- Pruebas y frontend.
- Arquitectura.
- Despliegue.
- Licencia y estado.

### Release

- Crear `CHANGELOG.md`.
- Marcar `2.0.0`.
- Publicar una release de GitHub.
- Conservar la etiqueta legacy.
- Actualizar descripción y topics.
- Añadir enlace al sitio.

### Prompt

```text
Prepara la documentación de lanzamiento 2.0.

Reescribe el README con la historia del Informatorio y la modernización.
Documenta desarrollo, arquitectura, despliegue, variables y pruebas.
Crea CHANGELOG y una checklist de release.
No exageres características ni afirmes que algo está implementado si no lo está.
```

---

# 8. Carril opcional: mejoras por diversión

Estas mejoras solo comienzan después de que la versión 2.0 sea estable. Cada una debe ser un epic independiente.

## Preview editorial

Vista previa de drafts para autores autorizados, con la misma presentación que el post publicado.

## Publicación programada

Usar `published_at` futuro y un cron o tarea sencilla. No introducir Celery si un proceso programado del proveedor es suficiente.

## HTMX para comentarios

Crear, editar y retirar comentarios sin recargar, conservando las rutas HTML normales como fallback.

## Editor Markdown

Guardar Markdown como fuente, renderizar con allowlist segura y ofrecer preview. No aceptar HTML arbitrario.

## Favoritos

Relación única usuario-post y una página personal de guardados.

## Búsqueda destacada

Fragmentos resaltados, sugerencias y ranking mejorado sin seguimiento invasivo.

## Newsletter

Suscripción confirmada, baja sencilla, consentimiento explícito y proveedor externo.

## Modo oscuro

Respetar `prefers-color-scheme`, conservar identidad y persistir una preferencia mínima.

---

# 9. Prompts maestros reutilizables

## Implementación

```text
Trabaja en acevedo-daniel/the-caffeine-lane-blog.

Fase actual: [NOMBRE].
Objetivo: [OBJETIVO CONCRETO].

Reglas:
- inspecciona primero el estado real;
- modifica solo lo necesario para esta fase;
- no agregues funcionalidades fuera de alcance;
- conserva el comportamiento no relacionado;
- agrega o actualiza pruebas;
- no ocultes errores;
- no hagas commit, push, merge ni despliegue sin autorización.

Validaciones obligatorias:
- [COMANDOS].

Al terminar entrega:
1. resumen de cambios;
2. archivos modificados;
3. decisiones tomadas;
4. comandos ejecutados y resultados;
5. riesgos o trabajo pendiente.
```

## Auditoría posterior

```text
Audita únicamente los cambios de la fase [NOMBRE].

Comprueba:
- criterios de salida;
- errores funcionales;
- seguridad;
- migraciones;
- pruebas faltantes;
- dependencias innecesarias;
- cambios fuera de alcance;
- documentación desactualizada.

No modifiques código.
Ordena hallazgos por severidad y cita archivo y línea.
```

## Corrección de hallazgos

```text
Corrige solo los hallazgos aprobados de la auditoría de la fase [NOMBRE].

No amplíes alcance ni refactorices otras áreas.
Agrega pruebas que fallen antes de cada corrección cuando sea posible.
Ejecuta las validaciones completas y entrega un resumen verificable.
No hagas commit ni push.
```

## Preparación de PR

```text
Prepara el resumen del pull request de la fase [NOMBRE].

Incluye:
- problema;
- solución;
- decisiones técnicas;
- cambios visibles;
- migraciones;
- pruebas ejecutadas;
- riesgos;
- pasos manuales;
- checklist de revisión.

No publiques el PR todavía.
```

---

# 10. Orden recomendado de pull requests

```text
PR 01 — Preserve legacy baseline
PR 02 — Introduce uv and pyproject
PR 03 — Add Ruff, pytest and pre-commit
PR 04 — Upgrade Django 5.2 patch and Psycopg 3
PR 05 — Upgrade to Django 6.0
PR 06 — Split settings and environment configuration
PR 07 — Add PostgreSQL Compose development service
PR 08 — Harden production settings
PR 09 — Introduce custom user and clean schema
PR 10 — Modernize posts domain
PR 11 — Replace fixture with seed command
PR 12 — Complete comments and moderation
PR 13 — Improve search, related posts and queries
PR 14 — Compile Tailwind and refactor templates
PR 15 — Enable CSP
PR 16 — Normalize media storage
PR 17 — Complete email and password reset
PR 18 — Improve editorial admin
PR 19 — Add CI
PR 20 — Add production container
PR 21 — Prepare staging and deployment
PR 22 — Documentation and 2.0 release
```

No deben combinarse el salto de Django, el usuario personalizado y el refactor de modelos en un mismo PR.

---

# 11. Definición de terminado para 2.0

## Código

- [ ] Python 3.13 y Django 6.0 estable.
- [ ] Dependencias administradas por uv.
- [ ] Lockfile comprobado.
- [ ] Ruff sin errores.
- [ ] Sin migraciones pendientes.
- [ ] Tests verdes.
- [ ] Cobertura útil en autenticación, posts y comentarios.

## Seguridad

- [ ] Sin secretos en Git.
- [ ] Sin superusuario en fixtures.
- [ ] Hosts y CSRF explícitos.
- [ ] HTTPS y cookies seguras.
- [ ] `check --deploy` revisado.
- [ ] CSP activa.
- [ ] Uploads validados.
- [ ] Acciones destructivas por POST.

## Funcionalidad

- [ ] Registro, login y perfil.
- [ ] Cambio y recuperación de contraseña.
- [ ] Crear, editar, publicar y eliminar posts con permisos.
- [ ] Categorías, búsqueda y relacionados.
- [ ] Comentarios, respuestas y moderación.
- [ ] Contacto.
- [ ] Admin editorial.

## Frontend

- [ ] Tailwind compilado.
- [ ] Sin Play CDN.
- [ ] Sin enlaces falsos principales.
- [ ] Responsive y navegable con teclado.
- [ ] Páginas de error.
- [ ] Imágenes con fallback y alt text.

## Operaciones

- [ ] PostgreSQL.
- [ ] CI.
- [ ] Staging.
- [ ] Backups.
- [ ] Logs.
- [ ] Healthcheck.
- [ ] Despliegue reproducible.
- [ ] Rollback documentado.

## Documentación

- [ ] README real.
- [ ] Guía de desarrollo.
- [ ] Arquitectura.
- [ ] Despliegue.
- [ ] Variables.
- [ ] Changelog.
- [ ] Release 2.0.0.
- [ ] Historia del Informatorio preservada.

---

# 12. Primera tarea recomendada

No comenzar actualizando todas las dependencias. La primera tarea correcta es preservar el legado y después reproducirlo.

```text
Trabaja en acevedo-daniel/the-caffeine-lane-blog.

Quiero iniciar la modernización 2.0, pero esta primera tarea es solo de preservación y diagnóstico.

Haz lo siguiente:
- inspecciona la rama main;
- documenta estructura, rutas, configuración, dependencias y despliegue;
- crea docs/audit-initial.md;
- identifica datos, media y variables que debo respaldar fuera del repositorio;
- propone pruebas de caracterización para el comportamiento actual;
- no actualices dependencias;
- no refactorices;
- no borres migraciones, fixtures ni media;
- no hagas commit, push ni despliegue.

Al terminar entrega un resumen, los archivos creados y los pasos manuales que debo realizar.
```
