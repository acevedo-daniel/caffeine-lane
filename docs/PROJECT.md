# Caffeine Lane — Project

> Product scope, actors, domain concepts, and durable business rules for Caffeine Lane.

## Product

Caffeine Lane is an editorial web application for cafe racer builds, guides, and reviews. It gives motorcycle enthusiasts a structured place to discover long-form content, maintain reader accounts, and participate in moderated discussions.

The product is centered on editorial publishing and community participation rather than commerce or open self-publishing.

## Problem

Detailed motorcycle builds, practical guides, and reviews are often fragmented across social feeds and forum threads. Caffeine Lane organizes that content into durable articles with categories, search, reader profiles, and discussions.

## Actors

| Actor | Capabilities |
| --- | --- |
| Visitor | Browse published content, search and filter articles, change interface language, and use the public contact flow. |
| Registered reader | Authenticate, maintain a profile, comment on published articles, reply to top-level comments, and manage their own comments. |
| Moderator | Hide comments when granted the `posts.moderate_comment` permission. |
| Editor / administrator | Manage editorial content and categories through Django permissions and the Django Admin. |

## Scope

### Editorial publishing

- Create and manage draft or published posts.
- Associate posts with editorial categories.
- Add featured images and alternative text.
- Publish or return posts to draft state.
- Surface related published content.

### Content discovery

- Browse the home/editorial surfaces.
- Browse posts by category.
- Search published content.
- Sort and paginate search results.
- Preserve search/filter state across pagination.

### Accounts and profiles

- Register and authenticate with email-based accounts.
- Maintain profile information and an avatar.
- Change passwords.
- Expose password-reset flows only when the feature is enabled for the environment.

### Discussion and moderation

- Add comments to published posts.
- Reply one level deep to top-level comments.
- Edit or withdraw an author's own visible comments.
- Hide comments through a dedicated moderation permission.
- Preserve visible, withdrawn, and moderator-hidden comment states.

### Localization

- Serve the interface in English or Spanish using Django internationalization.

## Out of scope

Caffeine Lane does not currently include:

- e-commerce, subscriptions, payments, or paywalls;
- social-login providers;
- unrestricted multi-level comment trees;
- public reader-authored article publishing;
- automated unreviewed content scraping or ingestion;
- a separate SPA or public API product surface.

## Domain model

### User

`accounts.User` is the application identity. Email is unique and is used as the authentication identifier.

A user can also hold profile information such as display name, biography, avatar, personal URL, and motorcycle ownership metadata.

Django permissions determine editorial and moderation capabilities.

### Category

`posts.Category` organizes published content. The application defines three structural category slugs:

```text
builds
guides
reviews
```

Additional category records may exist, but these three form the primary editorial taxonomy used by the application.

### Post

`posts.Post` represents an editorial article.

Its lifecycle is intentionally small:

```text
DRAFT <-> PUBLISHED
```

A published post requires a non-null publication timestamp. Public listing/detail queries use the published queryset rather than exposing drafts.

Posts may have multiple categories and an optional featured image.

### Comment

`posts.Comment` belongs to one post and one author.

Comment visibility is explicit:

```text
VISIBLE
WITHDRAWN
HIDDEN
```

A comment may reply to a top-level comment, but replies to replies are rejected.

## Business rules

- Public post listings and article detail pages expose only posts in `PUBLISHED` state with a publication timestamp.
- The slugs `search` and `new` are reserved for application routes and cannot be used by posts.
- A post with a visible featured image requires alternative text.
- Uploaded images are validated before use; accepted formats are JPEG, PNG, and WebP, with configured file-size and dimension limits.
- A comment reply must belong to the same post as its parent.
- Comment nesting is limited to one reply level.
- Replies are accepted only for visible parent comments.
- An author may withdraw their own comment; hiding requires the `posts.moderate_comment` permission.
- Repeated identical comments from the same author on the same post are temporarily rejected to reduce accidental duplicate submission.
- Email is unique for application users and is the login identifier.

## Current limitations

- Editorial article creation is permission-controlled rather than open reader self-publishing.
- Password reset depends on environment configuration and a working email provider.
- Production media persistence depends on the configured Cloudinary account.
- The custom `accounts.User` baseline is incompatible with legacy databases that still contain the former `accounts_profile` table; `check_fresh_baseline` stops startup/migration work when that legacy table is detected.

## Provenance

Caffeine Lane started as a final project for the Informatorio program and was later rebuilt and modernized as a personal application.

## Related documentation

- [README](../README.md)
- [Architecture](ARCHITECTURE.md)
- [Development](DEVELOPMENT.md)
- [Testing](TESTING.md)
- [Deployment](DEPLOYMENT.md)
