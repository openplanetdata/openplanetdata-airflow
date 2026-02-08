#!/usr/bin/env bash
#
# Update versions, build and publish the OpenPlanetData Airflow worker image
# Usage: ./build.sh [--push]
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="openplanetdata/openplanetdata-airflow"

# Parse arguments
PUSH=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --push)
            PUSH=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--push]"
            exit 1
            ;;
    esac
done

# Update Dockerfile versions to latest releases
"$SCRIPT_DIR/update-versions.sh" --apply

# Extract versions from Dockerfile
AIRFLOW_VERSION=$(grep -E '^ARG AIRFLOW_VERSION=' "$SCRIPT_DIR/Dockerfile" | cut -d= -f2)
GOL_VERSION=$(grep -E '^ARG GOL_VERSION=' "$SCRIPT_DIR/Dockerfile" | cut -d= -f2)
OSMCOASTLINE_VERSION=$(grep -E '^ARG OSMCOASTLINE_VERSION=' "$SCRIPT_DIR/Dockerfile" | cut -d= -f2)
PYTHON_VERSION=$(grep -E '^ARG PYTHON_VERSION=' "$SCRIPT_DIR/Dockerfile" | cut -d= -f2)
GIT_SHA=$(git -C "$SCRIPT_DIR" rev-parse --short HEAD)

VERSION_TAG="${AIRFLOW_VERSION}-${GIT_SHA}"

echo ""
echo "Building image with:"
echo "  AIRFLOW_VERSION: $AIRFLOW_VERSION"
echo "  GOL_VERSION: $GOL_VERSION"
echo "  OSMCOASTLINE_VERSION: $OSMCOASTLINE_VERSION"
echo "  PYTHON_VERSION: $PYTHON_VERSION"
echo ""
echo "Tags:"
echo "  $IMAGE_NAME:$VERSION_TAG"
echo "  $IMAGE_NAME:latest"
echo ""

# Build the image
docker build \
    --build-arg AIRFLOW_VERSION="$AIRFLOW_VERSION" \
    --build-arg GOL_VERSION="$GOL_VERSION" \
    --build-arg OSMCOASTLINE_VERSION="$OSMCOASTLINE_VERSION" \
    --build-arg PYTHON_VERSION="$PYTHON_VERSION" \
    -t "$IMAGE_NAME:$VERSION_TAG" \
    -t "$IMAGE_NAME:latest" \
    "$SCRIPT_DIR"

echo ""
echo "Built: $IMAGE_NAME:$VERSION_TAG"
echo "Built: $IMAGE_NAME:latest"

# Push if requested
if [[ "$PUSH" == "true" ]]; then
    echo ""
    echo "Pushing to Docker Hub..."
    docker push "$IMAGE_NAME:$VERSION_TAG"
    docker push "$IMAGE_NAME:latest"
    echo ""
    echo "Pushed: $IMAGE_NAME:$VERSION_TAG"
    echo "Pushed: $IMAGE_NAME:latest"
fi
