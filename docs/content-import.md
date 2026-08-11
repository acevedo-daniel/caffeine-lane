# Demo content and selected imports

`initial_data.json` was removed because it contained a superuser and duplicate content.
Do not restore it or use it in deployments.

Create the safe, idempotent portfolio dataset:

```powershell
uv run python manage.py seed_portfolio
```

It creates the non-privileged `demo-author@example.invalid` author, the `builds`,
`guides`, and `reviews` categories, and ten posts with documented WebP covers.

Import reviewed real content separately with an existing non-privileged author:

```powershell
uv run python manage.py import_selected_content .\selected-content.json --author-email editor@example.com --dry-run
uv run python manage.py import_selected_content .\selected-content.json --author-email editor@example.com
```

The JSON must contain `categories` and `posts`. Every post needs `slug`, `title`,
`excerpt`, `content`, `categories`, and ISO 8601 `published_at`. The importer
rejects privileged users, duplicate slugs, invalid encoding, placeholder text,
and user, password, or image fields. Upload reviewed images separately with
meaningful alternative text before publishing.
