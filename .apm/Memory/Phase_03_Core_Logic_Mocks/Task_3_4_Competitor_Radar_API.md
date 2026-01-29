# Task 3.4 - Competitor Tracking & Radar API

## Status
- [x] **Competitors CRUD**: Implemented full CRUD with quota enforcement.
- [x] **Radar API**: Implemented mock market discovery endpoint with scoring.
- [x] **Integration**: Routers mounted in `main.py`.

## Implementation Details
1.  **Schemas**: Created `backend/app/schemas/competitor.py` with Pydantic models.
2.  **API Routes**:
    -   `backend/app/api/v1/competitors.py`:
        -   `POST /`: Adds competitor, checks quota using `QuotaService`.
        -   `GET /`: Lists competitors for current user (filtered by project).
        -   `GET /radar`: Returns mock market scan results with `ScoringService` logic.
        -   `GET /{id}`, `PATCH /{id}`, `DELETE /{id}`: Standard CRUD.
3.  **Main**: Registered `competitors` router in `backend/app/main.py`.

## Key Decisions
-   **Quota Check**: Integrated `QuotaService.can_add_competitor` before insertion.
-   **Radar**: Returns `RadarResult` list with simulated threat scores and market presence.
-   **Project Scoping**: Competitors are linked to projects; API verifies project ownership.

## Next Steps
-   **Task 3.5**: Dashboard Stats API.