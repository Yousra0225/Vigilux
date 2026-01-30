# Task 4.3: Competitor List & Timeline View

## Status: Completed

## Implementation Details
- Implemented `frontend/src/app/dashboard/competitors/page.tsx`.
- Created `frontend/src/components/competitors/EventTimeline.tsx` compatible with backend `Event` model.
- Created `frontend/src/components/competitors/CompetitorList.tsx` (verified).
- Added `GET /api/v1/competitors/{id}/events` endpoint to backend.
- Added `GET /api/v1/projects/` endpoint to backend and integrated into `main.py`.
- Fixed `vitest` dependency issue in frontend.

## Artifacts
- `frontend/src/app/dashboard/competitors/page.tsx`
- `backend/app/api/v1/competitors.py` (updated)
- `backend/app/api/v1/projects.py` (created)
- `backend/app/main.py` (updated)
