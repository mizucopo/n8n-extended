# Extended Image release automation

Extended Image Releases run from `main` only when a release input changes, derive one immutable tag from `version` and the optional `revision`, and refuse to overwrite an existing git tag or Docker Hub tag. Open, unmerged Pull Requests report the release check but skip duplicate-tag inspection when they do not change a release input, avoiding unnecessary revision allocation for documentation or unrelated repository changes.

The pre-release check ignores title/body-only edits, while base edits still require validation. Closed or merged event snapshots skip the job. Before checkout, the check also reads the current PR state to skip runs merged or closed while queued. The [Get a pull request API](https://docs.github.com/en/rest/pulls/pulls#get-a-pull-request) accepts the existing `contents: read` permission; no additional token permission is required.

Validation checks out the event head SHA explicitly and compares the event base/head commits, preserving the original comparison on reruns. Missing commits are fetched by SHA and both commit objects and their merge base must exist before diffing. Acquisition, API, and comparison failures fail validation instead of reporting no release changes. This prevents a post-squash-merge run from trying to compare a deleted PR head or rejecting tags that were already published by that merge.
