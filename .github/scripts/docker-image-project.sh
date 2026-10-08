#!/usr/bin/env bash
set -euo pipefail

case "${1:-}" in
  quality)
    version="$(cat version)"
    grep -Fxq "ARG N8N_VERSION=$version" Dockerfile
    alpine_image="$(sed -n 's/^ARG ALPINE_IMAGE_VERSION=//p' Dockerfile)"
    alpine_repository="$(sed -n 's/^ARG ALPINE_REPOSITORY_VERSION=//p' Dockerfile)"
    case "$alpine_image" in
      "$alpine_repository".*) ;;
      *) echo "Alpine image patch must match its repository branch." >&2; exit 1 ;;
    esac
    grep -Fxq "FROM alpine:\${ALPINE_IMAGE_VERSION} AS tools" Dockerfile
    shellcheck .github/scripts/*.sh
    docker buildx build --check --platform linux/amd64 --build-arg "N8N_VERSION=$version" .
    docker build --platform linux/amd64 --build-arg "N8N_VERSION=$version" \
      --tag n8n-extended:pr .
    docker run --rm --platform linux/amd64 --entrypoint sh n8n-extended:pr -eu -c \
      'docker --version && ffmpeg -version && n8n --version'
    ;;
  publish)
    [ "$2" = extended ] || { echo "Unknown image: $2" >&2; exit 2; }
    docker build --platform linux/amd64 --build-arg "N8N_VERSION=$(cat version)" \
      --tag "$3" .
    docker push "$3"
    ;;
  notes)
    image_tag="$(jq -r '.images[0].tag' "$DOCKER_RELEASE_PLAN")"
    printf '## Docker Image\n\nこの GitHub Release に対応する Extended Image です。\n\n'
    printf -- "- Extended Image: \`%s:%s\`\n\n" "$IMAGE_REPOSITORY" "$image_tag"
    printf 'Docker Hub: https://hub.docker.com/r/%s\n' "$IMAGE_REPOSITORY"
    ;;
  *)
    echo "Usage: $0 {quality|publish|notes}" >&2
    exit 2
    ;;
esac
