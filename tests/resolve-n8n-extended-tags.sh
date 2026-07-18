#!/usr/bin/env sh
set -eu

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
script_path="$repo_root/scripts/resolve-n8n-extended-tags.sh"
image_repository="mizucopo/n8n-extended"
version_tag="2.25.2"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

run_case() {
  version_value="$1"
  revision_value="$2"

  printf '%s\n' "$version_value" > "$tmp_dir/version"
  printf '%s' "$revision_value" > "$tmp_dir/revision"

  (
    cd "$tmp_dir"
    IMAGE_REPOSITORY="$image_repository" \
      GITHUB_OUTPUT="$tmp_dir/output" \
      bash "$script_path"
  )
}

assert_output_contains() {
  expected="$1"

  if ! grep -Fqx "$expected" "$tmp_dir/output"; then
    echo "Expected output line not found: $expected" >&2
    echo "Actual output:" >&2
    cat "$tmp_dir/output" >&2
    exit 1
  fi
}

: > "$tmp_dir/output"
run_case "$version_tag" ""
assert_output_contains "n8n_version=$version_tag"
assert_output_contains "revision="
assert_output_contains "release_tag=$version_tag"
assert_output_contains "image_tag=$version_tag"
assert_output_contains "image=$image_repository:$version_tag"

: > "$tmp_dir/output"
run_case "$version_tag" "r1"
assert_output_contains "n8n_version=$version_tag"
assert_output_contains "revision=r1"
assert_output_contains "release_tag=$version_tag-r1"
assert_output_contains "image_tag=$version_tag-r1"
assert_output_contains "image=$image_repository:$version_tag-r1"

if run_case "$version_tag" "1" 2> "$tmp_dir/error"; then
  echo "Expected invalid revision to fail." >&2
  exit 1
fi

if ! grep -Fqx "revision must be empty or match r[0-9]+." "$tmp_dir/error"; then
  echo "Expected invalid revision error was not found." >&2
  cat "$tmp_dir/error" >&2
  exit 1
fi

printf '%s\n%s\n' "$version_tag" "2.25.3" > "$tmp_dir/version"
: > "$tmp_dir/revision"
if (
  cd "$tmp_dir"
  IMAGE_REPOSITORY="$image_repository" \
    GITHUB_OUTPUT="$tmp_dir/output" \
    bash "$script_path"
) 2> "$tmp_dir/error"; then
  echo "Expected multi-line version to fail." >&2
  exit 1
fi

if ! grep -Fqx "version must contain exactly one line." "$tmp_dir/error"; then
  echo "Expected multi-line version error was not found." >&2
  cat "$tmp_dir/error" >&2
  exit 1
fi
