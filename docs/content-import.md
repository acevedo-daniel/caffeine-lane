# Contenido demo e importación seleccionada

`initial_data.json` fue retirado: contenía un superusuario y contenido repetido. No debe restaurarse ni usarse en despliegues.

Para crear datos locales mínimos sin contraseñas utilizables ni permisos elevados:

```powershell
uv run python manage.py seed_portfolio
```

El comando es idempotente y crea el autor no privilegiado `demo-author@example.invalid`, las categorías `builds` y `guides`, y dos publicaciones limpias.

La importación de contenido real es deliberadamente separada y requiere que exista un autor no privilegiado:

```powershell
uv run python manage.py import_selected_content .\selected-content.json --author-email editor@example.com --dry-run
uv run python manage.py import_selected_content .\selected-content.json --author-email editor@example.com
```

El archivo JSON debe contener `categories` y `posts`. Cada post requiere `slug`, `title`, `excerpt`, `content`, `categories` y `published_at` en ISO 8601. El importador rechaza usuarios privilegiados, slugs duplicados, encoding inválido, texto provisional y campos de usuario, contraseñas o imágenes. Las imágenes se revisan y cargan aparte con texto alternativo antes de hacerse visibles.
