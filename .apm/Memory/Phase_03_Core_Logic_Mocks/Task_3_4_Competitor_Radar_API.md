# Task 3.4 - Competitor Tracking & Radar API

## Status
- [x] **Competitors CRUD**: Implemented full CRUD with quota enforcement.
- [x] **Radar API**: Implemented mock market discovery endpoint with scoring.
- [x] **Integration**: Routers mounted, Auth patched.

## Implementation Details
1.  **Models**: Updated `backend/app/models/competitor.py` with Pydantic schemas (`Create`, `Read`, `Update`).
2.  **API Routes**:
    -   `backend/app/api/v1/competitors.py`:
        -   `POST /`: Adds competitor, checks quota using `check_competitor_quota`.
        -   `GET /`: Lists competitors for a project.
        -   `PATCH /`, `DELETE /`: Standard operations.
    -   `backend/app/api/v1/radar.py`:
        -   `GET /`: Returns list of mock opportunities with "threat scores" and insights.
3.  **Auth Fix**:
    -   Patched `backend/app/api/deps.py`:
        -   Removed non-existent `is_active` check.
        -   Added UUID casting for `token_data.sub` to fix SQLite compatibility issues.
4.  **Main**: Registered new routers in `backend/app/main.py`.
5.  **Testing**: Verified via `backend/tests/api/test_competitors_radar.py`.

## Key Decisions
-   **Quota Check**: Enforced at the service level before DB insert.
-   **Radar Simulation**: Used deterministic random seed in scoring service, but added random selection in API for variety.
-   **UUID Handling**: Explicitly cast string tokens to UUIDs in `deps.py` to prevent SQLAlchemy/SQLite type mismatch errors.

## Next Steps
-   **Task 3.5**: Dashboard Stats API.
-   **Future**: Replace mock Radar data with real scraping/search integration.
