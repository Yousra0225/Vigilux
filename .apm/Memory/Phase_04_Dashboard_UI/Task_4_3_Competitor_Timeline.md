# Task 4.3 - Competitor List & Timeline View

## Status
- [x] Complete

## Changes
- **Backend**:
    - Created `backend/app/api/v1/projects.py` to allow fetching user projects (required for `project_id`).
    - Registered `projects` router in `backend/app/main.py`.
    - Added `GET /api/v1/competitors/{competitor_id}/events` to `backend/app/api/v1/competitors.py` to fetch events for a specific competitor.
- **Frontend**:
    - Created `frontend/src/app/dashboard/competitors/page.tsx` as the main container.
    - Created `frontend/src/components/competitors/CompetitorList.tsx` for the list view.
    - Created `frontend/src/components/competitors/EventTimeline.tsx` for the vertical timeline.
    - Integrated logic to fetch Projects -> Competitors -> Events.
    - Implemented "Breakthrough Signal" highlighting (Score > 7) with red styling and icons.

## Technical Details
- Added `GET /api/v1/projects/` endpoint to bridge the gap between User and Competitors (since `read_competitors` requires `project_id`).
- Used `lucide-react` for icons (Globe, AlertTriangle, Zap, etc.).
- Implemented responsive grid layout (List on left, Timeline on right on large screens).
- Handled loading states and empty states for all async operations.

## Verification
- `npm run build` passed.
- Components are correctly typed and integrated.
- Backend API extensions facilitate the required data flow.
