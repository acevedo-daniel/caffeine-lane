# Caffeine Lane — Architecture

> System structure, component boundaries, persistence, external integrations, and technical trade-offs.

## Summary

Caffeine Lane is a server-rendered Django monolith.

Django owns routing, authentication, forms and validation, persistence, editorial and discussion behavior, internationalization, template rendering, and the administrative interface. A small Node.js/pnpm pipeline builds Tailwind CSS and JavaScript assets before Vercel serves them from its CDN.

Production runs the application as a Django WSGI function on Vercel.

```text
Browser -> Vercel CDN / Django function
                  -> Neon PostgreSQL
                  -> Cloudinary media storage
                  -> Resend email
```

## Component boundaries

| Component | Owns | Boundary |
| --- | --- | --- |
| `apps/core` | Landing/home surfaces, contact flow, image validation, CSP reporting, health endpoints | Does not own accounts or editorial domain models |
| `apps/accounts` | Custom user model, authentication, registration, profiles, password flows | Does not own post/comment behavior |
| `apps/posts` | Categories, posts, publishing behavior, search, comments, and moderation | Uses Django's user/permission boundary rather than owning authentication |
| `config/settings` | Base, local, test, and production configuration | Does not own application business behavior |
| `templates/` | Server-rendered layouts, forms, partials, and page templates | Does not own persistence or business logic |
| `static/src/` | Authored Tailwind CSS and JavaScript source | Generated output belongs in `static/dist/` |
| `static/dist/` | Compiled frontend assets | Must not be edited manually |
| `docker/` | Container startup, migration, and static-collection orchestration | Does not define local developer workflow |

### Request lifecycle

A typical server-rendered request follows Django's standard request lifecycle:

```text
HTTP request
-> middleware
-> URL dispatcher
-> view / form
-> queryset or domain service
-> template render / redirect
-> HTTP response
```

- **Views and forms** handle request input, permissions, form validation, messages, redirects, and rendering.
- **Models/querysets** define persistence shape and reusable query semantics such as published-content filtering.
- **Small services** hold lifecycle behavior where a named operation is clearer than embedding it directly in a view, such as publishing posts or moderating comments.
- **Templates and context processors** render the localized server-side interface.

The project does not impose an artificial repository layer where Django's ORM and application boundaries are already sufficient.

### Frontend and static asset pipeline

Authored frontend assets live under `static/src/`. The build pipeline compiles assets into distribution artifacts:

```text
static/src
-> Tailwind CSS / JavaScript build (pnpm)
-> static/dist
-> Vercel CDN in production
```

Uploaded media follows a distinct path:
- Local development: filesystem storage
- Tests: in-memory storage
- Production: Cloudinary storage

Keeping static build artifacts and user-uploaded media separate avoids depending on the ephemeral application container for persistent uploads.

### External integrations

| Integration | Platform | Responsibility | Application boundary |
| --- | --- | --- | --- |
| Neon | Hosted PostgreSQL | Production data persistence | Only Django connects to the database |
| Cloudinary | Media CDN | Production uploaded media storage | Configured through Django storage backend |
| Resend | Email API | Production transactional emails | Accessed via Django's email backend through Anymail |
| Vercel | Python runtime and CDN | Django web runtime and static asset delivery | Deployment and runtime environment |

### Security boundaries

Caffeine Lane relies on Django's session authentication and permission system:

- Secure session and CSRF cookies in production.
- HTTPS redirect and configurable HSTS.
- Content Security Policy (CSP) supporting report-only or enforced modes.
- Restricted production hosts and trusted CSRF origins.
- Argon2 as the prioritized password hasher in production.
- Provider credentials injected via environment variables rather than committed to source control.
- Server-side authorization checks for all editorial and moderation actions.

## Data and persistence

Production application data is stored in PostgreSQL on Neon. Local development normally uses PostgreSQL 18 through Docker Compose, with SQLite available as an intentional fallback when `DATABASE_URL` is omitted.

Tests use an isolated configuration: in-memory SQLite by default, or the explicit `TEST_DATABASE_URL` supplied in CI.

Core persistent entities:
- **`accounts.User`:** Custom user model with unique email authentication.
- **`posts.Category`:** Editorial taxonomy records.
- **`posts.Post`:** Draft/published editorial articles with categories and media metadata.
- **`posts.Comment`:** Discussion records with explicit visibility and optional one-level parent relations.

Django migrations are the single source of truth for the database schema.

### Search architecture

Search behavior adapts to the active database backend:
- **PostgreSQL:** Published content uses weighted full-text search (`SearchVector`, `SearchQuery`, `SearchRank`) across title (weight A), excerpt (weight B), and content (weight C).
- **SQLite fallback:** Falls back to case-insensitive substring matching (`icontains`) across title, excerpt, and content, keeping offline development functional without emulating full-text search.

## Hosted topology

```text
Browser
  -> Vercel CDN / Django function
      -> Neon PostgreSQL
      -> Cloudinary
      -> Resend
```

The repository retains a production-like `Dockerfile` and entrypoint for portable hosting and CI smoke tests. Vercel detects Django directly; provider-specific secrets and service settings are configured outside Git.

## Invariants

- **Published-content boundary:** Public editorial queries do not expose draft articles.
- **Identity boundary:** Email remains globally unique and serves as the single authentication identifier.
- **Comment-depth boundary:** Replies never exceed one level of nesting.
- **Permission boundary:** Moderation and editorial operations are enforced strictly server-side.
- **Media boundary:** Production uploads do not depend on container-local persistence.
- **Migration boundary:** Production migrations execute via a direct database connection separately from pooled web traffic.

## Trade-offs

### Server-rendered Django

Django templates keep routing, forms, authentication, localization, and rendering in one cohesive application boundary. The project gains a simpler deployment and avoids maintaining a separate frontend API contract, at the cost of tighter coupling between presentation and Django.

### PostgreSQL search with SQLite fallback

PostgreSQL provides the intended ranked full-text search behavior. The SQLite fallback keeps local and test scenarios lightweight, but its `icontains` behavior is deliberately less capable than full-text indexing.

### Pooled runtime with direct migrations

Production web traffic uses Neon's pooled connection, while explicit release scripts temporarily switch to `DIRECT_DATABASE_URL`. This preserves pooling efficiency for web requests while giving schema migrations an unpooled direct connection.

### Single-level discussions

One-level comment replies provide conversational context without requiring recursive tree rendering, deep nested navigation, or complex moderation rules.

## Related documentation

- [README](../README.md)
- [Project](PROJECT.md)
- [Development](DEVELOPMENT.md)
- [Testing](TESTING.md)
- [Deployment](DEPLOYMENT.md)
