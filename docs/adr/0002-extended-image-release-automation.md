# Extended Image release automation

Extended Image Releases use repo-template's shared Docker project pipeline. A squash-merged PR on `main` with exactly one release-classification label enables numbering and publication; an unlabelled latest merged PR skips both. This supersedes the previous file-change trigger and project-local duplicate-tag check.

The fixed declaration uses the upstream-revision scheme: `version` remains the Upstream n8n Version, while Actions allocates an Extended Image Revision and advances past occupied Git, GitHub Release and Docker Hub tags. Revision zero has no suffix; corrected images use `-rN`. No classification label independently bumps the upstream version.

Only the Dockerfile and project quality/publish/notes hook retain n8n-specific behavior. Shared helpers own numbering commits, immutable tags, persistent image ownership, same-run recovery, Release names and latest promotion. Recovery reruns the original workflow run; old runs cannot roll back latest. The migration removes the old workflows, and does not recover releases made by the old protocol.
