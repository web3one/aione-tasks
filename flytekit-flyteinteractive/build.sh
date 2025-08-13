#!/bin/bash

# Shell script to build aione.flyteinteractive Docker image
# Usage: ./build.sh [version]
# If no version is provided, defaults to v1.0.0

# Set default version
DEFAULT_VERSION="v1.3.0"
VERSION=${1:-$DEFAULT_VERSION}

# Remove 'v' prefix if present for Docker build arg
BUILD_VERSION=${VERSION#v}

# Image name
IMAGE_NAME="push.fzyun.io/founder/aione.flyteinteractive"

echo "Building Docker image: ${IMAGE_NAME}:${VERSION}"
echo "Using build version: ${BUILD_VERSION}"

# Build the Docker image
docker build \
    --build-arg TARGETARCH=amd64 \
    -t ${IMAGE_NAME}:${VERSION} \
    -t ${IMAGE_NAME}:latest \
    .

if [ $? -eq 0 ]; then
    echo "Successfully built ${IMAGE_NAME}:${VERSION}"
    echo "Also tagged as ${IMAGE_NAME}:latest"
else
    echo "Failed to build Docker image"
    exit 1
fi