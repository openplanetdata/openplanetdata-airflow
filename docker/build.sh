#!/usr/bin/env bash
#
# Build and optionally publish the OpenPlanetData Airflow worker image
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

# Extract versions from Dockerfile
AIRFLOW_VERSION=$(grep -E '^ARG AIRFLOW_VERSION=' "$SCRIPT_DIR/Dockerfile" | cut -d= -f2)
GOL_VERSION=$(grep -E '^ARG GOL_VERSION=' "$SCRIPT_DIR/Dockerfile" | cut -d= -f2)
PYTHON_VERSION=$(grep -E '^ARG PYTHON_VERSION=' "$SCRIPT_DIR/Dockerfile" | cut -d= -f2)

echo "Building image with:"
echo "  AIRFLOW_VERSION: $AIRFLOW_VERSION"
echo "  GOL_VERSION: $GOL_VERSION"
echo "  PYTHON_VERSION: $PYTHON_VERSION"
echo ""

# Build the image
docker build \
    --build-arg AIRFLOW_VERSION="$AIRFLOW_VERSION" \
    --build-arg GOL_VERSION="$GOL_VERSION" \
    --build-arg PYTHON_VERSION="$PYTHON_VERSION" \
    -t "$IMAGE_NAME:latest" \
    -t "$IMAGE_NAME:$AIRFLOW_VERSION" \
    "$SCRIPT_DIR"

echo ""
echo "Built: $IMAGE_NAME:latest"
echo "Built: $IMAGE_NAME:$AIRFLOW_VERSION"

# Push if requested
if [[ "$PUSH" == "true" ]]; then
    echo ""
    echo "Pushing to Docker Hub..."
    docker push "$IMAGE_NAME:latest"
    docker push "$IMAGE_NAME:$AIRFLOW_VERSION"
    echo ""
    echo "Pushed: $IMAGE_NAME:latest"
    echo "Pushed: $IMAGE_NAME:$AIRFLOW_VERSION"
fi
