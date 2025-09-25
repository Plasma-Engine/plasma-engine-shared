#!/usr/bin/env bash

set -euo pipefail

# Sync shared .github templates into sibling repositories.
# Usage: ./scripts/sync-templates.sh ../plasma-engine-gateway ../plasma-engine-research ...

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
TEMPLATE_DIR="$ROOT_DIR/.github"

if [ ! -d "$TEMPLATE_DIR" ]; then
  echo "Template directory not found: $TEMPLATE_DIR" >&2
  exit 1
fi

if [ $# -eq 0 ]; then
  echo "Usage: $0 <target_repo_path>..." >&2
  exit 1
fi

for target in "$@"; do
  if [ ! -d "$target" ]; then
    echo "Skipping missing repo: $target" >&2
    continue
  fi

  echo "Syncing templates to $target/.github"
  mkdir -p "$target/.github"
  rsync -av --delete \
    --exclude 'workflows/' \
    "$TEMPLATE_DIR/" "$target/.github/"
done

echo "Template sync complete."

