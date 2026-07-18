#!/usr/bin/env bash
set -euo pipefail

: "${IMAGE_REPOSITORY:?IMAGE_REPOSITORY is required}"
: "${GITHUB_OUTPUT:?GITHUB_OUTPUT is required}"

n8n_version_raw="$(cat version)"
revision_raw="$(cat revision)"

case "${n8n_version_raw}" in
  *$'\n'*)
    echo "version must contain exactly one line." >&2
    exit 1
    ;;
esac

case "${revision_raw}" in
  *$'\n'*)
    echo "revision must contain at most one line." >&2
    exit 1
    ;;
esac

n8n_version="$(printf '%s' "${n8n_version_raw}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
revision="$(printf '%s' "${revision_raw}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"

if [ -z "${n8n_version}" ]; then
  echo "version must not be empty." >&2
  exit 1
fi

if [[ ! "${n8n_version}" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "version contains characters that are not valid for this release tag." >&2
  exit 1
fi

if [ -n "${revision}" ] && [[ ! "${revision}" =~ ^r[0-9]+$ ]]; then
  echo "revision must be empty or match r[0-9]+." >&2
  exit 1
fi

release_tag="${n8n_version}"

if [ -n "${revision}" ]; then
  release_tag="${release_tag}-${revision}"
fi

{
  echo "n8n_version=${n8n_version}"
  echo "revision=${revision}"
  echo "release_tag=${release_tag}"
  echo "image_tag=${release_tag}"
  echo "image=${IMAGE_REPOSITORY}:${release_tag}"
} >> "${GITHUB_OUTPUT}"
