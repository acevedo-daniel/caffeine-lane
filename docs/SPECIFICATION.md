# Specification

## Actors

| Actor | Description |
|---|---|
| Visitor | An unauthenticated reader of public pages and published posts. |
| Registered reader | An authenticated user who can manage a profile and participate in comments. |
| Editor | A user with post permissions. |
| Moderator | A user with the `posts.moderate_comment` permission. |

## Functional requirements

### FR-001 - Browse editorial content

The system must show only published posts on public listings and post-detail pages.

**Acceptance criteria**

- **AC-001.1:** Given a visitor opens Home, when published posts exist, then the page shows editorial content and up to five banner posts.
- **AC-001.2:** Given a visitor opens a structural category, when posts belong to it, then the category lists published matching posts with pagination.
- **AC-001.3:** Given a visitor requests an unknown category or unpublished post, then the response is not a public post page.

### FR-002 - Find editorial content

The system must let visitors search published posts and optionally filter by category and sort order.

**Acceptance criteria**

- **AC-002.1:** Given a query, when a matching published post exists, then it appears in search results.
- **AC-002.2:** Given a selected category or sort option, when results are shown, then the result set honors that selection.
- **AC-002.3:** Given pagination, when a visitor changes page, then the active search and filter parameters are retained.

### FR-003 - Accounts and participation

The system must support email-based registration, sign-in, profile editing, password changes, and sign-out.

**Acceptance criteria**

- **AC-003.1:** Given a visitor completes both registration steps with valid unique data, then an account is created and the visitor is signed in.
- **AC-003.2:** Given an authenticated user updates a valid profile form, then the profile change is retained.
- **AC-003.3:** Given a signed-in user signs out, then the session ends through a POST request.

### FR-004 - Comments and moderation

The system must allow authenticated readers to comment on published posts and to add one level of replies.

**Acceptance criteria**

- **AC-004.1:** Given an authenticated reader submits a valid comment, then it appears on the related post.
- **AC-004.2:** Given a reply targets another reply, when it is submitted, then it is rejected because replies are limited to one level.
- **AC-004.3:** Given a comment author withdraws a comment or a moderator hides it, then its visible state changes according to the action.

### FR-005 - Contact and recovery availability

The system must provide a contact form and clearly communicate whether public password recovery is available.

**Acceptance criteria**

- **AC-005.1:** Given a valid contact form and an available email provider, when it is submitted, then the configured recipient receives a message whose reply address is the visitor's email.
- **AC-005.2:** Given contact email delivery fails, when the form is submitted, then the visitor receives feedback instead of an unhandled server error.
- **AC-005.3:** Given `PASSWORD_RESET_ENABLED=false`, when a visitor requests password recovery, then an explanatory unavailable page is shown and no recovery email is sent.

### FR-006 - Interface language

The system must present English by default and allow a visitor to choose Spanish for translated interface strings.

**Acceptance criteria**

- **AC-006.1:** Given no language preference, when a visitor opens the site, then the interface defaults to English.
- **AC-006.2:** Given a visitor changes language, when the next page renders, then available interface strings use the selected language.

## Business rules

| ID | Rule |
|---|---|
| BR-001 | `builds`, `guides`, and `reviews` are structural categories and must exist after migrations. |
| BR-002 | A public post must be published and have a publication date. |
| BR-003 | `search` and `new` are reserved post slugs. |
| BR-004 | A visible uploaded post image requires meaningful alternative text. |
| BR-005 | Comments belong to one post and can have at most one parent level. |
| BR-006 | Seeded authors are non-privileged and have unusable passwords. |

## Non-functional requirements

| Area | Requirement |
|---|---|
| Accessibility | Interactive navigation, carousel controls, forms, language selection, and enhanced selects remain usable by keyboard; motion respects reduced-motion preferences. |
| Responsive behavior | Public views support narrow mobile through large desktop layouts. |
| Security | Production uses HTTPS proxy settings, secure cookies, CSP configuration, validation for uploads, and no committed secrets. |
| Asset delivery | Authored frontend files are built into generated static assets before delivery. |
| Availability | `/healthz/` returns `{"status": "ok"}` for service health checks. |

## Permissions

| Action | Permission |
|---|---|
| Read public posts and categories | Visitor or registered reader |
| Create comments and replies | Registered reader |
| Edit or withdraw own comment | Comment author |
| Hide a comment | Moderator |
| Create, update, or delete posts | User with the matching Django post permission |

## Edge cases / errors

- A database containing `accounts_profile` is rejected before migrations because it is not compatible with the current user schema.
- Empty categories and search results render intentional empty states.
- Provider failures during contact delivery return feedback without exposing provider details.
- When only one banner post is available, Home hides unnecessary carousel controls.
- Error responses use dedicated 400, 403, 404, and 500 templates when `DEBUG=False`.

## External interfaces

The application has no public API contract. Its operational integrations are documented in [Architecture](ARCHITECTURE.md) and [Deployment](DEPLOYMENT.md).
