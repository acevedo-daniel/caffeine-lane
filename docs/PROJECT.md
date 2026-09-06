# Caffeine Lane — Project

> Product scope, actors, domain concepts, and durable business rules.

## Product

Caffeine Lane is an editorial web application for cafe racer builds, practical guides, reviews, and community discussions. It gives motorcycle builders and enthusiasts a structured platform to discover long-form content, maintain reader accounts and profiles, and participate in moderated discussions.

The product is centered on editorial publishing and community participation rather than commerce or open self-publishing.

## Problem

Detailed motorcycle builds, practical guides, and reviews are often fragmented across social feeds and forum threads without durable organization or editorial quality. Caffeine Lane organizes that content into structured articles with categories, full-text search, reader profiles, and one-level discussions.

## Scope

### In scope

- **Editorial publishing:** Create and manage draft or published posts across structural categories (`builds`, `guides`, `reviews`), with validated image uploads and related content surfacing.
- **Content discovery:** Browse editorial surfaces and categories, search published content with relevance ranking, and preserve search/filter state across pagination.
- **Accounts and profiles:** Register and authenticate using email identity, manage reader profile details and avatars, with environment-controlled password-reset flows.
- **Discussion and moderation:** Comment on published posts, reply one level deep, edit or withdraw personal comments, and hide comments via dedicated moderation permissions.
- **Localization & themes:** Serve the interface in English or Spanish with persistent light and dark themes.

### Out of scope

- E-commerce, subscriptions, payments, or paywalls.
- Third-party social login providers (OAuth/OIDC).
- Unrestricted recursive multi-level comment trees.
- Public reader-authored article publishing (publishing is restricted to staff/editorial roles).
- Automated unreviewed content scraping or feed ingestion.
- A separate Single Page Application (SPA) or public REST/GraphQL API product surface.

## Core workflows

### Editorial publishing

```text
Editor drafts article -> Assigns taxonomy (category, tags) -> Uploads featured media
-> Validates preview -> Sets publication timestamp -> Published across discovery surfaces
```

### Reader discussion and moderation

```text
Reader authenticates -> Submits comment on published post
-> Optional: Reader or other user submits 1-level reply
-> Author may edit or withdraw own comment (marked WITHDRAWN)
-> Moderator may hide abusive comment (marked HIDDEN via permission)
```

## Actors and domain concepts

### Actors

| Actor | Capabilities |
| --- | --- |
| Visitor | Browse published content, search and filter articles, change interface language/theme, and use the public contact flow. |
| Registered reader | Authenticate, maintain a profile, comment on published articles, reply to top-level comments, and manage their own comments. |
| Moderator | Hide comments when granted the `posts.moderate_comment` permission. |
| Editor / administrator | Manage editorial content and categories through Django permissions and the Django Admin. |

### Domain concepts

- **User (`accounts.User`):** Application identity using unique email as the authentication identifier, with associated reader profile metadata.
- **Category (`posts.Category`):** Editorial taxonomy centered around three structural slugs: `builds`, `guides`, and `reviews`.
- **Post (`posts.Post`):** Editorial article with lifecycle `DRAFT <-> PUBLISHED`. A publication timestamp is required for public exposure.
- **Comment (`posts.Comment`):** Discussion record linked to a post and author, with explicit visibility states (`VISIBLE`, `WITHDRAWN`, `HIDDEN`) and maximum 1-level depth.

## Business rules

- Public post listings and article detail pages expose only posts in `PUBLISHED` state with a valid publication timestamp.
- The slugs `search` and `new` are reserved for application routes and cannot be used by posts.
- A post with a visible featured image requires alternative text.
- Uploaded images are validated before persistence (accepted formats: JPEG, PNG, WebP, with enforced dimension and file-size limits).
- A comment reply must belong to the same post as its parent.
- Comment nesting is strictly limited to one reply level (replies to replies are rejected).
- Replies are accepted only for visible parent comments.
- An author may withdraw their own comment; hiding requires the `posts.moderate_comment` permission.
- Repeated identical comments from the same author on the same post are temporarily rejected to prevent duplicate submissions.
- Email is globally unique and serves as the single authentication identifier.

## Current limitations

- Editorial article creation is permission-controlled rather than open reader self-publishing.
- Password reset is disabled by default and depends on environment configuration, a verified Resend sending domain, and a functioning external email provider.
- Contact delivery depends on Resend; when the provider rejects a message, the application must return a controlled error rather than report success.
- Production media persistence depends on the configured Cloudinary account.
- The custom `accounts.User` baseline is incompatible with legacy databases containing the former `accounts_profile` table; `check_fresh_baseline` aborts startup or migration if detected.

## Provenance

Caffeine Lane started as a final project for the Informatorio program and was later rebuilt and modernized as a personal application.

## Related documentation

- [README](../README.md)
- [Architecture](ARCHITECTURE.md)
- [Development](DEVELOPMENT.md)
- [Testing](TESTING.md)
- [Deployment](DEPLOYMENT.md)
