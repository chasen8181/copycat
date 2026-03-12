# Contributing to CopyCat

Thank you for contributing.

## Before you start

- Open an issue for bugs, regressions, or larger feature work.
- Keep pull requests focused. Small changes review faster and are safer to merge.
- Match the existing product direction: fast, simple, predictable, and easy to self-host.

## Development workflow

1. Fork the repository and create a branch from `main`.
2. Make the smallest change that solves the problem cleanly.
3. Run the relevant checks before opening a pull request.
4. Write a clear pull request description with the problem, approach, and verification steps.

## Local checks

- Build the frontend with `npm run build`.
- Validate backend changes by starting the app locally or in Docker.
- Update docs when behavior, configuration, or storage layout changes.

## Pull request guidelines

- Explain user-visible changes first.
- Include screenshots for UI changes when they help review.
- Avoid unrelated refactors in the same pull request.
- Keep naming, formatting, and API behavior consistent with the existing codebase.

## Reporting bugs

Please include:

- the version or commit
- deployment method
- exact reproduction steps
- expected behavior
- actual behavior
- logs or screenshots when relevant

## Security

Do not open a public issue for sensitive vulnerabilities. Report them privately to the maintainer instead.
