````markdown
<!--
README.md — Universal Solo Developer Template

INSTRUCCIONES
1. Reemplaza todos los valores {{PLACEHOLDER}}.
2. Elimina las secciones opcionales que no aporten información.
3. No dejes títulos vacíos ni datos ficticios.
4. Verifica que todos los comandos puedan copiarse y ejecutarse.
5. Nunca publiques secretos, credenciales ni información confidencial.
-->

<!-- OPTIONAL: elimina este bloque si el proyecto no tiene logo. -->
<p align="center">
  <img
    src="./docs/assets/logo.svg"
    alt="{{PROJECT_NAME}} logo"
    width="96"
  />
</p>

<h1 align="center">{{PROJECT_NAME}}</h1>

<p align="center">
  {{ONE_SENTENCE_PROJECT_DESCRIPTION}}
</p>

<!-- OPTIONAL: conserva solamente los enlaces existentes. -->
<p align="center">
  <a href="{{LIVE_DEMO_URL}}">Live Demo</a>
  ·
  <a href="{{DOCUMENTATION_URL}}">Documentation</a>
  ·
  <a href="{{ISSUES_URL}}">Report an Issue</a>
</p>

> [!NOTE]
> **Project status:** {{ACTIVE_DEVELOPMENT | MAINTENANCE | COMPLETED | ARCHIVED}}
> {{SHORT_STATUS_EXPLANATION}}

## Overview

{{Explain in two or three paragraphs what the project is, which problem it
solves, who it is intended for, and what makes its approach relevant.}}

{{Avoid repeating the project title or listing technologies without explaining
their purpose.}}

## Project Context

| Field               | Details                             |
| ------------------- | ----------------------------------- |
| **Type**            | {{Personal / Freelance / Academic}} |
| **Purpose**         | {{MAIN_PROJECT_GOAL}}               |
| **Role**            | Solo developer                      |
| **Started**         | {{YYYY-MM}}                         |
| **Current version** | {{VERSION_OR_NOT_APPLICABLE}}       |

<!--
For academic projects, Purpose may include:
Course, institution, assignment, learning objective or evaluation context.

For freelance projects, avoid publishing client information unless authorized.
-->

## Key Features

- **{{FEATURE_NAME}}:** {{SHORT_DESCRIPTION}}.
- **{{FEATURE_NAME}}:** {{SHORT_DESCRIPTION}}.
- **{{FEATURE_NAME}}:** {{SHORT_DESCRIPTION}}.
- **{{FEATURE_NAME}}:** {{SHORT_DESCRIPTION}}.

<!-- OPTIONAL: use this section only when the project has something visual. -->

## Preview

<p align="center">
  <img
    src="./docs/assets/preview.png"
    alt="{{PROJECT_NAME}} application preview"
    width="900"
  />
</p>

<!-- OPTIONAL: add more screenshots only when they explain different features. -->

## Tech Stack

| Area               | Technology                         |
| ------------------ | ---------------------------------- |
| **Language**       | {{LANGUAGE_AND_VERSION}}           |
| **Runtime**        | {{RUNTIME_AND_VERSION}}            |
| **Framework**      | {{FRAMEWORK}}                      |
| **Database**       | {{DATABASE}}                       |
| **Testing**        | {{TESTING_TOOLS}}                  |
| **Infrastructure** | {{DOCKER_CLOUD_OR_NOT_APPLICABLE}} |

<!-- Remove rows that do not apply. -->

## Scope

### Included

- {{IN_SCOPE_ITEM}}
- {{IN_SCOPE_ITEM}}
- {{IN_SCOPE_ITEM}}

### Not Included

- {{OUT_OF_SCOPE_ITEM}}
- {{OUT_OF_SCOPE_ITEM}}

<!--
This section is especially useful for freelance and academic projects.
Remove it when the project scope is already obvious.
-->

## Getting Started

### Prerequisites

Before installing the project, make sure you have:

- {{RUNTIME}} {{MINIMUM_VERSION}} or newer.
- {{PACKAGE_MANAGER}} {{MINIMUM_VERSION}} or newer.
- {{DATABASE_OR_EXTERNAL_SERVICE}}, when applicable.
- Git.

### Installation

Clone the repository:

```bash
git clone {{REPOSITORY_URL}}
cd {{REPOSITORY_DIRECTORY}}
```

Install the dependencies:

```bash
{{INSTALL_COMMAND}}
```

### Environment Variables

Create a local environment file from the provided example:

```bash
cp .env.example .env
```

Configure the required variables:

| Variable            | Required | Description     | Example            |
| ------------------- | :------: | --------------- | ------------------ |
| `{{VARIABLE_NAME}}` |   Yes    | {{DESCRIPTION}} | `{{SAFE_EXAMPLE}}` |
| `{{VARIABLE_NAME}}` |   Yes    | {{DESCRIPTION}} | `{{SAFE_EXAMPLE}}` |
| `{{VARIABLE_NAME}}` |    No    | {{DESCRIPTION}} | `{{SAFE_EXAMPLE}}` |

> [!IMPORTANT]
> Never commit `.env` files or real credentials. Keep `.env.example` limited to
> variable names and safe example values.

### Database Setup

<!-- OPTIONAL: remove when the project does not use a database. -->

Run the migrations:

```bash
{{MIGRATION_COMMAND}}
```

Load development data, when needed:

```bash
{{SEED_COMMAND}}
```

### Run Locally

Start the development environment:

```bash
{{DEVELOPMENT_COMMAND}}
```

The application will be available at:

```text
http://localhost:{{PORT}}
```

## Usage

{{Explain the shortest path a user should follow to use the main functionality.}}

1. {{FIRST_STEP}}
2. {{SECOND_STEP}}
3. {{THIRD_STEP}}

<!-- OPTIONAL: include a real request or code example when useful. -->

```bash
{{USAGE_EXAMPLE}}
```

Expected result:

```text
{{EXPECTED_RESULT}}
```

## Available Scripts

| Command                   | Description                         |
| ------------------------- | ----------------------------------- |
| `{{DEVELOPMENT_COMMAND}}` | Starts the development environment. |
| `{{BUILD_COMMAND}}`       | Creates a production build.         |
| `{{START_COMMAND}}`       | Starts the production application.  |
| `{{TEST_COMMAND}}`        | Runs the automated test suite.      |
| `{{LINT_COMMAND}}`        | Checks the code for linting issues. |
| `{{FORMAT_COMMAND}}`      | Formats the source code.            |
| `{{TYPECHECK_COMMAND}}`   | Runs static type checking.          |

<!-- Remove commands that do not exist. -->

## Project Structure

<details>
<summary><strong>View directory structure</strong></summary>

```text
{{REPOSITORY_DIRECTORY}}/
├── src/                 # Application source code
├── tests/               # Automated tests
├── docs/                # Additional documentation and assets
├── scripts/             # Development or maintenance scripts
├── .env.example         # Environment variable reference
├── {{CONFIG_FILE}}      # Main project configuration
├── LICENSE
└── README.md
```

</details>

<!-- Replace this example with the project's real structure. -->

## Architecture

<!--
OPTIONAL: keep this section only when architecture is relevant.
Describe responsibilities and data flow, not every individual file.
-->

{{SHORT_ARCHITECTURE_DESCRIPTION}}

### Main Components

- **{{COMPONENT}}:** {{RESPONSIBILITY}}.
- **{{COMPONENT}}:** {{RESPONSIBILITY}}.
- **{{COMPONENT}}:** {{RESPONSIBILITY}}.

Additional technical details are available in
[`docs/architecture.md`](./docs/architecture.md).

## Testing

Run the complete test suite:

```bash
{{TEST_COMMAND}}
```

Generate a coverage report:

```bash
{{COVERAGE_COMMAND}}
```

### Testing Strategy

- **Unit tests:** {{WHAT_IS_TESTED}}.
- **Integration tests:** {{WHAT_IS_TESTED}}.
- **End-to-end tests:** {{WHAT_IS_TESTED_OR_NOT_APPLICABLE}}.

<!--
Remove this section when the project does not yet have automated tests.
Do not claim coverage or testing practices that are not implemented.
-->

## Deployment

<!-- OPTIONAL: remove when the project is not deployed. -->

| Environment           | URL                | Provider     |
| --------------------- | ------------------ | ------------ |
| **Production**        | {{PRODUCTION_URL}} | {{PROVIDER}} |
| **Preview / Staging** | {{PREVIEW_URL}}    | {{PROVIDER}} |

Deployments are triggered by {{DEPLOYMENT_TRIGGER}} from the
`{{DEPLOYMENT_BRANCH}}` branch.

### Production Build

```bash
{{BUILD_COMMAND}}
```

## Known Limitations

<!-- OPTIONAL: useful for MVPs, prototypes and academic projects. -->

- {{KNOWN_LIMITATION}}
- {{KNOWN_LIMITATION}}
- {{KNOWN_LIMITATION}}

## Roadmap

- [x] {{COMPLETED_MILESTONE}}
- [x] {{COMPLETED_MILESTONE}}
- [ ] {{NEXT_MILESTONE}}
- [ ] {{FUTURE_MILESTONE}}

See the [open issues]({{ISSUES_URL}}) for planned improvements and known
problems.

## Documentation

<!-- Keep only documents that exist. -->

- [Architecture](./docs/architecture.md)
- [API Reference](./docs/api.md)
- [Development Guide](./docs/development.md)
- [Changelog](./CHANGELOG.md)
- [Security Policy](./SECURITY.md)

## Contributing

<!--
OPTIONAL: keep only if external contributions are accepted.
For larger contribution rules, create CONTRIBUTING.md.
-->

This project is maintained by a solo developer, but focused contributions are
welcome.

Before opening a pull request:

1. Open or reference an issue describing the proposed change.
2. Keep the change limited to a clear purpose.
3. Add or update tests when applicable.
4. Run the available quality checks.
5. Update the documentation when behavior changes.

For detailed instructions, see
[`CONTRIBUTING.md`](./CONTRIBUTING.md).

## Versioning

<!--
OPTIONAL: keep only if the project publishes identifiable releases.
-->

This project uses [Semantic Versioning](https://semver.org/).

Notable changes are documented in
[`CHANGELOG.md`](./CHANGELOG.md).

## License

{{LICENSE_STATEMENT}}

See [`LICENSE`](./LICENSE) for the complete terms.

<!--
Examples:

Open source:
Distributed under the MIT License.

Private or proprietary:
This project is proprietary software. All rights reserved.

Do not claim an open-source license unless the LICENSE file actually exists.
-->

## Author

**{{AUTHOR_NAME}}**

- GitHub: [@{{GITHUB_USERNAME}}](https://github.com/{{GITHUB_USERNAME}})
- LinkedIn: [{{LINKEDIN_LABEL}}]({{LINKEDIN_URL}})
- Portfolio: [{{PORTFOLIO_LABEL}}]({{PORTFOLIO_URL}})

<!-- OPTIONAL -->

## Acknowledgements

- {{LIBRARY_RESOURCE_OR_PERSON}}
- {{LIBRARY_RESOURCE_OR_PERSON}}
- {{INSPIRATION_OR_REFERENCE}}
````
