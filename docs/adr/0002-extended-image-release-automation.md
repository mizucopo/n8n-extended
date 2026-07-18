# Extended Image release automation

Extended Image Releases run from `main` only when a release input changes, derive one immutable tag from `version` and the optional `revision`, and refuse to overwrite an existing git tag or Docker Hub tag. Pull Requests always report the release check but skip duplicate-tag inspection when they do not change a release input, avoiding unnecessary revision allocation for documentation or unrelated repository changes.
