# Git Flow

- main: Production
- develop: Development
- feature/*: Features (branch from develop, merge to develop)
- release/*: Not used
- hotfix/*: Not used

## Workflow
git checkout develop && git pull
git checkout -b feature/*
gh pr create --base develop
