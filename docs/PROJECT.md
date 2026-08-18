# Project

## Summary

Caffeine Lane is an editorial web application for cafe racer builds, riding guides, and motorcycle reviews. It combines a public content platform with email-based authentication, user profiles, interactive comments with one-level replies, administrative moderation, search, and a responsive interface with English and Spanish language options.

## Problem

Motorcycle build logs, practical mechanical advice, and riding gear reviews are often scattered across ephemeral forums and social media. Caffeine Lane provides a dedicated, structured editorial space where detailed build stories and guides can be published, categorized, discovered, and discussed.

## Actors and Permissions

| Actor                 | Access & Capabilities                                                                                                                                                       |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Visitor**           | Unauthenticated reader. Discovers published posts, browses categories, searches content, filters by tag/category, changes interface language, and submits contact messages. |
| **Registered Reader** | Authenticated user. Manages profile details, changes passwords, posts comments on published articles, and submits single-level replies to other readers.                    |
| **Comment Author**    | The author of a specific comment. Can edit or withdraw their own active comments.                                                                                           |
| **Moderator**         | Staff member with `posts.moderate_comment` permission. Can review, hide, or moderate inappropriate comments.                                                                |
| **Editor / Admin**    | Staff member with Django post management permissions. Creates, edits, publishes, and organizes posts and categories via the Django Admin interface.                         |
| **Site Owner**        | Technical administrator. Manages infrastructure, database lifecycle, cloud integrations, and environment deployments.                                                       |

## Scope

### In Scope

- **Editorial Publishing:** Rich articles with featured images, structured categories, draft/published lifecycle, publication dates, and alternative text.
- **Content Discovery:** Home hero carousel, category-filtered catalog (`builds`, `guides`, `reviews`), text search with query persistence across pagination, and related post suggestions.
- **User Accounts & Profiles:** Email-based authentication, two-step registration, profile customization (bio, avatar), password change, and controlled password-reset capability.
- **Reader Participation:** Nested single-level comment threads, comment editing, self-service withdrawal, and administrative moderation.
- **Internationalization:** English as the primary default language with Spanish interface translations.
- **Cloud Infrastructure:** Multi-stage Dockerized delivery, Neon PostgreSQL, Cloudinary media storage, Resend transactional email, WhiteNoise static delivery, and `/healthz/` liveness monitoring.

### Out of Scope

- E-commerce transactions, paid subscriptions, or digital paywalls.
- Social OAuth / third-party identity providers (intentionally email-based auth).
- Multi-tier threaded discussions beyond one level of parent-child replies.
- Public automated unreviewed content scraping or user self-publishing without editorial review.

## Domain & Business Rules

| Rule ID    | Domain Rule                 | Description                                                                                                                                           |
| ---------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **BR-001** | **Structural Taxonomy**     | `builds`, `guides`, and `reviews` are permanent structural categories and must exist in the database after initial migrations.                        |
| **BR-002** | **Publication Visibility**  | Public post listings and detail views display only articles with `is_published=True` and a valid publication timestamp.                               |
| **BR-003** | **Reserved Slugs**          | The URL slugs `search` and `new` are strictly reserved for system routes and cannot be used by post entities.                                         |
| **BR-004** | **Accessible Media**        | Every visible uploaded post image requires meaningful descriptive alternative text (`alt_text`).                                                      |
| **BR-005** | **Single-Level Replies**    | Comments belong to exactly one post. A reply can target a top-level comment, but replies to replies are rejected to maintain clean, readable threads. |
| **BR-006** | **Author Seeding Security** | Seeded demo authors are non-privileged accounts created with unusable passwords.                                                                      |

## Relevant Constraints & Limitations

- **Email Delivery Constraints:** Public password reset requires an operational transactional email provider; demo configurations keep `PASSWORD_RESET_ENABLED=false` by default when using testing senders.
- **Database Schema Invariant:** The database requires the custom email-based `accounts.User` schema. Legacy databases containing the deprecated `accounts_profile` table from earlier iterations are rejected at startup by `check_fresh_baseline`.
- **Media Persistence:** Uploaded media files are stored in Cloudinary in production to ensure persistence outside ephemeral Docker container filesystems.

## Project Background

Caffeine Lane originated as a final project for the Informatorio program in Resistencia, Chaco, and was subsequently rebuilt and modernized as an independent personal application. It serves as a practical showcase of modern Python/Django architecture, structured database workflows, and multi-provider cloud delivery.

## Related Documentation

- [Architecture](ARCHITECTURE.md)
- [Development](DEVELOPMENT.md)
- [Testing](TESTING.md)
- [Deployment](DEPLOYMENT.md)
