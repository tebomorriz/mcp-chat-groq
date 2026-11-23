# Continuous Integration with GitHub Actions

## 1. Overview

This project uses GitHub Actions to automatically run its Python test suite whenever code is pushed to the `main` branch or a pull request targets `main`.

This practice is called **Continuous Integration (CI)**.

The objective is to identify errors early and ensure that code changes do not break existing functionality.

## 2. What is GitHub Actions?

GitHub Actions is an automation platform integrated into GitHub.

It allows developers to define workflows that automatically perform tasks such as:

- Running automated tests.
- Checking code quality.
- Building applications.
- Publishing packages.
- Deploying applications.

A workflow is defined in a YAML file stored inside `.github/workflows/`.

Our workflow is located at:

`.github/workflows/tests.yml`

## 3. How our CI pipeline works

The workflow follows these steps:

1. A developer pushes code to GitHub or opens a pull request.
2. GitHub Actions detects the event.
3. GitHub creates a temporary Ubuntu runner.
4. The repository is checked out.
5. Python and uv are installed.
6. Project dependencies are installed using the lockfile.
7. Pytest executes the automated tests.
8. GitHub reports whether the workflow passed or failed.

## 4. Understanding the workflow configuration

### Workflow name

`name: MCP Chat Tests`

Defines the name displayed in the GitHub Actions interface.

### Trigger events

The `on` section specifies when the workflow should run.

- `push`: Runs when changes are pushed to the `main` branch.
- `pull_request`: Runs when a pull request targets `main`.

### Permissions

`permissions: contents: read`

Gives the workflow read-only access to repository contents. This follows the principle of least privilege.

### Job configuration

`jobs:` defines the automated tasks.

Our job is called `test`.

`runs-on: ubuntu-latest` tells GitHub to execute it on an Ubuntu-hosted runner.

### Checking out the repository

`actions/checkout@v4` downloads the repository contents into the runner so subsequent steps can access the source code.

### Setting up Python

`actions/setup-python@v5` installs Python 3.12 for the workflow.

### Installing uv

`astral-sh/setup-uv@v6` installs uv, our Python package and project management tool.

### Installing dependencies

`uv sync --locked` installs the dependencies defined in `pyproject.toml` and verifies that `uv.lock` is consistent.

The lockfile helps ensure reproducible dependency installation.

### Running tests

`uv run pytest -v` executes our automated test suite.

The `-v` option enables verbose output, showing individual test results.

## 5. Why do we use automated testing?

Our MCP Chat application has several components that must work together.

Automated tests help verify:

- Document reading and editing.
- MCP resource and prompt functionality.
- Groq API adapter behaviour.
- MCP tool discovery.
- MCP tool execution and error handling.

Our current test suite contains 18 tests.

## 6. Understanding CI versus CD

**Continuous Integration (CI)** focuses on automatically checking code changes through activities such as testing and validation.

**Continuous Delivery (CD)** ensures that validated software is ready for release.

**Continuous Deployment** goes further by automatically deploying validated changes to production.

Our current GitHub Actions workflow implements Continuous Integration. It does not deploy the application.

## 7. Security considerations

- Never commit `.env` files or API keys.
- Use GitHub Secrets if future workflows require credentials.
- Give workflow permissions only when necessary.
- Avoid exposing secrets in logs.
- Keep dependencies and GitHub Actions updated.

Our current automated tests use mocks and dummy credentials, so the CI workflow does not need a real Groq API key.

## 8. Current status

- [x] GitHub Actions workflow created.
- [x] Python environment configured.
- [x] uv dependency installation configured.
- [x] Automated test execution configured.
- [x] Local validation completed successfully.
- [ ] Workflow pushed to GitHub.
- [ ] First remote GitHub Actions run verified.

## 10. Key learning points

- CI automates software validation.
- GitHub Actions workflows are written in YAML.
- A runner is the machine that executes workflow jobs.
- A trigger determines when a workflow runs.
- A job contains one or more steps.
- A lockfile helps maintain consistent dependencies.
- Automated tests help prevent regressions.
