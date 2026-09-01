## Issue-First Branch Workflow

### WHAT

- Never make changes directly on `main`.
- Before starting work, create a GitHub Issue that describes the work.
- Perform the work on a non-`main` branch associated with that Issue.
- Automated base image update PRs created by the `prefect-flows` workflow are exempt from the Issue requirement and use the fixed `automation/n8n-stable-update` branch.

## Documentation

### HOW

- Update related documentation when code changes affect users
- Document usage for new features in README
- Update relevant docs when interfaces change
- Split large docs into separate files in `docs/` folder
- Add links to split docs in README

## File Operations

### HOW

```bash
# File operations
git mv <old-path> <new-path>  # Move files
git rm <path>                  # Delete files
```

## Agent skills

### Issue tracker

Issues are tracked in GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

The default five-role vocabulary is used. See `docs/agents/triage-labels.md`.

### Domain docs

This repository uses a single-context layout. See `docs/agents/domain.md`.
