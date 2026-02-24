# Git Flow

## WHY
Adopt a simple branching strategy to balance parallel development and quality assurance in team collaboration.
Minimize impact on production while enabling independent feature development.

## WHAT
- main: Production (production-ready code)
- develop: Development (integration branch for features)
- feature/*: Features (branch from develop, merge to develop)
- release/*: Not used
- hotfix/*: Not used

## HOW
```bash
# Start feature development
git checkout develop && git pull
git checkout -b feature/<feature-name>

# Create pull request
gh pr create --base develop
```
