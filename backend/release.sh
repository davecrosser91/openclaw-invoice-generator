#!/bin/bash
# filepath: scripts/update_version_and_tag.sh

# Usage: ./update_version_and_tag.sh <neue_version>
# Beispiel: ./update_version_and_tag.sh 1.2.3

set -e

TOML_FILE="pyproject.toml"
VESION=$(grep -E '^version[[:space:]]*=' pyproject.toml | head -1 | sed -E 's/^version[[:space:]]*=[[:space:]]*"([^"]+)".*/\1/')

if [[ -z "$NEW_VERSION" ]]; then
  echo "Usage: $0 <neue_version>"
  exit 1
fi

# Version in pyproject.toml ersetzen
sed -i '' -E "s/^version[[:space:]]*=[[:space:]]\^*\".*\"/version = \"$NEW_VERSION\"/" pyproject.toml

# # Git commit und Tag setzen
git add .
git commit -m "chore: bump version to v$NEW_VERSION"
git tag "@ascend/python-backend@$NEW_VERSION"
# git push
# git push --tags