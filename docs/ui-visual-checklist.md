# Visual release checklist

Use a freshly migrated database for empty states and run `python manage.py
seed_portfolio` for populated states.

## Viewports

- Mobile: 360 × 800 px
- Tablet: 768 × 1024 px
- Desktop: 1440 × 900 px

## Pages and states

- `/`, `/home/`, `/about/`, and `/contact/`: normal content, empty form, and form errors.
- `/posts/search/`: no query, no results, results, and pagination.
- Build, guide, and review categories: populated and empty states.
- Post detail: image, long excerpt, comments, anonymous and authenticated users.
- Login, registration, password reset, and profile: valid forms, field errors, and general errors.
- `400`, `403`, `404`, and `500` pages with `DEBUG=False`.

## Acceptance criteria

- Header, mobile navigation, and footer are keyboard accessible with visible focus.
- Internal links never return an unexpected 404 or 500.
- Typography, spacing, buttons, forms, cards, badges, messages, and pagination are consistent.
- Cards remain stable with long titles and excerpts; every image has useful alt text or a decorative placeholder.
- The carousel has accessible controls and does not cover text on mobile.
- No horizontal scrolling, clipped text, or mixed languages at 360 px.

## Final pass

Repeat the three viewports after fixes, then review alignment, spacing, shadows,
truncation, hover states, focus states, and image-loading shifts.
