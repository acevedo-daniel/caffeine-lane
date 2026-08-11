# The Rider character assets

`masters/` contains the source PNG artwork. It is intentionally outside
`static/` and must never be referenced from templates.

Public derivatives are optimized WebP files in
`static/images/brand/character/`:

- one 1024 × 1024 WebP per pose;
- `character-signature-512.webp` and `character-signature-256.webp` for compact use.

Use `components/character_badge.html` for circular presentation. The circle is
created in CSS; source and derivative assets remain uncropped square images.
