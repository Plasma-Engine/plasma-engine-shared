# Contributing to Plasma Engine

Thanks for investing in Plasma Engine! This repository houses shared libraries, documentation, and tooling consumed by the domain services. Please follow these guidelines when contributing:

## Process

1. **Open an Issue** – Use the appropriate template (bug, feature, task, ADR change) and link it to the Program Project board.
2. **Create a Branch** – Format: `<repo>/<PE-XX>-short-description` (example: `shared/PE-04-dev-handbook`).
3. **Write Tests & Docs** – Validate your change with automated tests and update documentation.
4. **Open a PR** – Reference the issue ID in the title and fill out the pull request template. CodeRabbit is auto-added as a reviewer.
5. **Merge Strategy** – Squash merge unless otherwise noted. Ensure CI passes and at least one human approver signs off in addition to CodeRabbit.

## Development Environment

- Install required runtimes (Python 3.11+, Node.js 20+, Docker).
- Use the local Docker Compose stack defined in the development handbook.
- Configure your `.env` based on `docs/development-handbook.md`.

## Coding Standards

- Python: `ruff`, `black`, and type hints (mypy) where applicable.
- TypeScript: `eslint`, `prettier`, strict TS config.
- Commit messages: Conventional Commits (e.g., `feat(shared): add template sync script`).

## Testing Expectations

- Unit tests required for all logic changes.
- Integration tests when touching service boundaries or shared tooling.
- Snapshot or visual tests for documentation site updates if applicable.

## Documentation

- Update README files and the development handbook when behavior changes.
- Add or update ADRs for architectural decisions via the ADR change template.

## Release Notes

- Service repos manage their own release notes. Shared packages should update CHANGELOG.md (if present) and bump versions via Release Please or semantic-release workflows once configured.

Questions? Reach out in the `#plasma-engine-devops` Slack channel or mention @xkonjin in your issue.

