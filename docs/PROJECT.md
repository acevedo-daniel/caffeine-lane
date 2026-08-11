# Project

## Summary

Caffeine Lane is a personal editorial web application for people interested in cafe racer motorcycles. It publishes builds, guides, and reviews, then gives readers a way to find content, create an account, and participate in moderated discussion.

## Problem

Motorcycle build notes, practical riding advice, and gear opinions are often scattered across disconnected sources. Caffeine Lane provides one focused, readable space where that content can be organized, discovered, and discussed.

## Users and stakeholders

| Role | Need / responsibility |
|---|---|
| Visitor | Read published stories, browse categories, search, and contact the site owner. |
| Registered reader | Maintain a profile and write or reply to comments. |
| Editor | Create, update, publish, and remove posts through Django Admin or authorized editorial views. |
| Moderator | Hide comments that require moderation. |
| Site owner | Maintains content, provider configuration, and deployment. |

## Objectives

- Make practical cafe racer content easy to read, search, and browse by category.
- Provide a safe, lightweight participation path through accounts and moderated comments.
- Keep local development and the hosted deployment reproducible with documented tooling.

## Out of scope

- Payments, subscriptions, newsletters, and social-login integrations.
- Native mobile clients.
- Automatic import of unreviewed content, images, users, or passwords.
- Public password-reset email while the configured sender cannot deliver to arbitrary recipients.

## Scope

### Includes

- A public landing page, home page, static pages, post detail, categories, and search.
- Editorial posts with draft/published status, categories, featured images, and alternative text.
- Accounts, profiles, password changes, comments, one-level replies, and moderation.
- English and Spanish interface selection.
- Docker-based hosting with managed database, media, static assets, and transactional email providers.

### Does not include

- Any functionality listed in **Out of scope**.
- Preservation or conversion of databases that contain the incompatible `accounts_profile` schema.

## Success criteria

- A fresh local installation can migrate, seed the portfolio, build assets, and serve the site using the documented commands.
- Visitors can reach published content and each structural category without an unexpected server error or missing route.
- Authorized users can complete the documented account, editorial, and comment actions.
- The hosted service exposes `/healthz/` and keeps uploaded media outside the Render filesystem.

## Relevant constraints

- The public taxonomy always includes `builds`, `guides`, and `reviews`.
- Production runtime uses Neon pooled connections; schema migrations require a direct Neon connection.
- Production media is stored by Cloudinary and static files are served by WhiteNoise.
- The current Resend onboarding sender limits password-reset delivery; the public reset flow is disabled by default.

## Background

Caffeine Lane started as a final project for the Informatorio program in Resistencia, Chaco. It was later rebuilt and modernized as a personal project, adopting current Django practices, a custom frontend pipeline, managed cloud providers, and structured testing.

## Category context

Personal project. Caffeine Lane is maintained by a single developer and documented for reproducible development, operation, and future personal work without introducing unnecessary organizational process.
