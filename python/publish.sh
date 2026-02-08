#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PYPROJECT="$PROJECT_DIR/pyproject.toml"

current_version=$(grep -Po '(?<=^version = ")[^"]+' "$PYPROJECT")
echo "Current version: $current_version"

read -rp "New version to publish: " new_version

if [[ -z "$new_version" ]]; then
    echo "Error: version cannot be empty"
    exit 1
fi

if [[ "$new_version" == "$current_version" ]]; then
    echo "Error: new version is the same as current version"
    exit 1
fi

sed -i "s/^version = \"$current_version\"/version = \"$new_version\"/" "$PYPROJECT"
echo "Updated $PYPROJECT to version $new_version"

git -C "$PROJECT_DIR" add "$PYPROJECT"
git -C "$PROJECT_DIR" commit -m "Bump version to $new_version"
git -C "$PROJECT_DIR" push

rm -rf "$PROJECT_DIR/dist"
python3 -m build "$PROJECT_DIR"
twine upload "$PROJECT_DIR/dist/"*

echo "Published openplanetdata-airflow $new_version to PyPI"
