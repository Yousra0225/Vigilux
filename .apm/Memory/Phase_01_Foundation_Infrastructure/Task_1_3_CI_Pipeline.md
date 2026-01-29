# Memory Log - Task 1.3: CI Pipeline Setup

## Status
- [x] Completed

## Decisions
- Created `.github/workflows/ci.yml`.
- Triggers on push/PR to `main` and `develop`.
- Separate jobs for `backend-test` and `frontend-test` for parallelism.
- Uses `ruff` for Python linting and `pytest` for testing.
- Uses `npm run lint` for Frontend validation.

## Verification
- Syntax checked against GitHub Actions schema standards.
