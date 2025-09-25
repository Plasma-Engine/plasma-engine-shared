# Plasma Engine Shared

This repository centralizes shared assets for the Plasma Engine program:

- `.github` templates (issues, PRs, CODEOWNERS) consumed by all service repositories.
- Documentation (`docs/`) including the [Development Handbook](docs/development-handbook.md).
- Utility scripts (`scripts/`) for template synchronization and developer ergonomics.

## Getting Started

```bash
git clone https://github.com/xkonjin/plasma-engine-shared.git
cd plasma-engine-shared
```

Ensure sibling repositories are checked out in the same parent directory (see handbook). After cloning:

```bash
chmod +x scripts/sync-templates.sh
./scripts/sync-templates.sh ../plasma-engine-*
```

## Contribution Workflow

1. Create an issue using the appropriate template.
2. Branch from `main` using `<repo>/<PE-XX>-summary` naming.
3. Run lint/tests locally before opening a PR.
4. Submit a PR (CodeRabbit + human review required).

Refer to [CONTRIBUTING.md](CONTRIBUTING.md) for the full process.

## Documentation

- [Development Handbook](docs/development-handbook.md)
- DevOps process overview lives in the program documentation repository (`plasma-engine/docs/devops-process.md`).

## License

Copyright © 2025 Plasma Engine. All rights reserved.
