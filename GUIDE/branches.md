# Branching Guide

## Main branch
- `main` is the protected, stable branch.
- Direct commits to `main` are not allowed.
- All changes must come through pull requests.

## Feature branches
- Create feature branches for new work or experiments.
- Use short, descriptive names, for example:
  - `feature/add-offset-cache`
  - `feature/update-parser`
- Merge via pull request after review and checks.

## Branch workflow
1. Create a feature branch from `main`.
2. Commit changes to the feature branch.
3. Open a pull request into `main`.
4. Require review and passing checks.
5. Merge and delete the feature branch after release.
