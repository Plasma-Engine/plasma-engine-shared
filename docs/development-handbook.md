# Plasma Engine Development Handbook

This handbook describes the standard local development environment for all Plasma Engine repositories.

## Prerequisites

- **Git** ≥ 2.45 with credential helper configured for GitHub.
- **Python** ≥ 3.11 (use `pyenv` or asdf for version management).
- **Node.js** ≥ 20.10 (via `fnm`, `nvm`, or asdf).
- **Docker Desktop** (Kubernetes optional but recommended).
- **Make** or **Task** for convenience scripts.
- **Poetry** (for Python packaging) and **pnpm** (for Node monorepos) will be introduced as scaffolding lands.

## Repository Layout

```
plasma-engine-repos/
  plasma-engine-gateway/
  plasma-engine-research/
  plasma-engine-brand/
  plasma-engine-content/
  plasma-engine-agent/
  plasma-engine-shared/
  plasma-engine-infra/
```

Clone all repositories into the same parent directory to simplify template syncing and local Compose setups.

## Environment Variables

1. Copy `.env.example` (when available) to `.env` in each repo.
2. Store secrets using a password manager (1Password, Bitwarden). Never commit secrets.
3. For local testing, use the following naming convention:

```
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GITHUB_TOKEN=
NEO4J_URI=bolt://localhost:7687
REDIS_URL=redis://localhost:6379/0
POSTGRES_URL=postgresql://plasma:plasma@localhost:5432/plasma
```

## Docker Compose Stack

`plasma-engine-infra` will provide a shared Compose file. Until then, run the provisional stack:

```bash
docker compose -f compose.deps.yml up -d
```

Services:
- `postgres`: main relational database
- `redis`: cache and queue backend
- `neo4j`: knowledge graph store
- `minio`: artifact/object storage

## Tooling Standards

| Language | Formatter | Linter | Tests |
| --- | --- | --- | --- |
| Python | black | ruff, mypy | pytest |
| TypeScript | prettier | eslint (strict) | vitest / jest |
| Terraform | terraform fmt | tfsec, checkov | terraform validate |

Before committing, run `make lint` / `make test` where available. CI will enforce these checks.

## Git Workflow

- Branch naming: `<repo>/<PE-XX>-description`
- Commits: Conventional Commits.
- Rebase on `main` before opening a PR.
- Use Draft PRs for early feedback.

## Code Review

- CodeRabbit provides automated review notes.
- At least one human approver required.
- Respond to all review comments before merge.

## Project Management

- Issues must be linked to the Program board.
- Update issue statuses daily or when work state changes.
- Close issues only after code is merged and deployed (if applicable).

## Troubleshooting

- **Docker not starting**: Ensure no port conflicts (5432, 6379, 7687, 9000).
- **Python deps**: Run `poetry lock --no-update` to sync lockfiles.
- **Node deps**: Use `corepack pnpm install` for deterministic installs.
- **Neo4j auth errors**: Reset using `neo4j-admin set-initial-password`.

## Support

- Slack channel: `#plasma-engine-devops`
- Incident reports: open an issue with label `incident`
- Weekly sync notes stored in `plasma-engine-shared/docs/meetings/`

