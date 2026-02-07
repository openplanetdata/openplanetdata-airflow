#!/usr/bin/env bash
#
# Update Dockerfile versions to latest stable releases
# Usage: ./update-versions.sh [--apply]
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKERFILE="$SCRIPT_DIR/Dockerfile"

# Parse arguments
APPLY=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --apply)
            APPLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--apply]"
            exit 1
            ;;
    esac
done

# Get current versions
CURRENT_AIRFLOW=$(grep -E '^ARG AIRFLOW_VERSION=' "$DOCKERFILE" | cut -d= -f2)
CURRENT_GOL=$(grep -E '^ARG GOL_VERSION=' "$DOCKERFILE" | cut -d= -f2)
CURRENT_PYTHON=$(grep -E '^ARG PYTHON_VERSION=' "$DOCKERFILE" | cut -d= -f2)

echo "Current versions:"
echo "  AIRFLOW_VERSION: $CURRENT_AIRFLOW"
echo "  GOL_VERSION: $CURRENT_GOL"
echo "  PYTHON_VERSION: $CURRENT_PYTHON"
echo ""

# Fetch latest versions
echo "Fetching latest versions..."
LATEST_AIRFLOW=$(curl -s https://api.github.com/repos/apache/airflow/releases \
    | jq -r '[.[] | select(.prerelease == false and (.tag_name | test("^[0-9]+\\.[0-9]+\\.[0-9]+$")))] | first | .tag_name')

LATEST_GOL=$(curl -s https://api.github.com/repos/clarisma/geodesk-gol/releases/latest \
    | jq -r '.tag_name | ltrimstr("v")')

echo ""
echo "Latest versions:"
echo "  AIRFLOW_VERSION: $LATEST_AIRFLOW"
echo "  GOL_VERSION: $LATEST_GOL"
echo "  PYTHON_VERSION: $CURRENT_PYTHON (not auto-updated)"
echo ""

# Check for updates
UPDATES=false
if [[ "$CURRENT_AIRFLOW" != "$LATEST_AIRFLOW" ]]; then
    echo "Airflow: $CURRENT_AIRFLOW -> $LATEST_AIRFLOW"
    UPDATES=true
fi
if [[ "$CURRENT_GOL" != "$LATEST_GOL" ]]; then
    echo "GOL: $CURRENT_GOL -> $LATEST_GOL"
    UPDATES=true
fi

if [[ "$UPDATES" == "false" ]]; then
    echo "All versions are up to date."
    exit 0
fi

# Apply updates if requested
if [[ "$APPLY" == "true" ]]; then
    echo ""
    echo "Applying updates..."
    sed -i "s/^ARG AIRFLOW_VERSION=.*/ARG AIRFLOW_VERSION=$LATEST_AIRFLOW/" "$DOCKERFILE"
    sed -i "s/^ARG GOL_VERSION=.*/ARG GOL_VERSION=$LATEST_GOL/" "$DOCKERFILE"
    echo "Updated $DOCKERFILE"
else
    echo ""
    echo "Run with --apply to update Dockerfile"
fi
