# n8n Extended Image

This context describes the Docker image managed and published by this repository.

## Language

**Extended Image**:
The Docker image managed by this repository that adds Docker CLI and ffmpeg to the official n8n image.
_Avoid_: custom n8n, Docker image

**Extended Image Repository**:
The Docker Hub repository `mizucopo/n8n-extended`, used to publish Extended Images.
_Avoid_: registry, image destination

**Upstream n8n Version**:
The n8n-provided version used by the parent n8n image and its matching External Task Runner Image.
_Avoid_: project version, release version

**Extended Image Tag**:
An immutable Docker tag for an Extended Image, formed from the Upstream n8n Version and an optional Extended Image Revision.
_Avoid_: version, latest tag

**Initial Extended Image Tag**:
An Extended Image Tag without an Extended Image Revision, used for the first publication for an Upstream n8n Version.
_Avoid_: unversioned tag, latest tag

**Extended Image Revision**:
An optional `rN` suffix used only when republishing an Extended Image for the same Upstream n8n Version.
_Avoid_: patch version, n8n version

**Extended Image Release**:
The publication of an immutable Extended Image Tag, its matching git tag and GitHub Release, and an update to the mutable Latest Image Tag.
_Avoid_: n8n release, version release

**Extended Image Release Tag**:
A git tag that marks the repository commit for an Extended Image Release and has the same value as its immutable Extended Image Tag.
_Avoid_: image tag, version tag

**Latest Image Tag**:
The mutable `latest` Docker tag that points to the most recently published Extended Image.
_Avoid_: release tag, initial tag

**External Task Runner Image**:
The official `n8nio/runners` image that matches the Upstream n8n Version and does not use an Extended Image Revision.
_Avoid_: Extended Image, runner revision
