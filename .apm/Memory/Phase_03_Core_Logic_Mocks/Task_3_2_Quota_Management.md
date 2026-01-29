# Task 3.2 - Quota Management Logic

## Status
- [x] **Completed** (2026-01-30)

## Implementation Details
1.  **Service (`backend/app/services/quota.py`)**:
    - `QuotaService` class created.
    - `get_effective_plan`: Downgrades Growth to Starter if 7-day trial expired.
    - `can_add_competitor`: Checks usage against limits (Starter: 3, Growth: 15, Ultimate: 50).

## Usage
- To be used in `Competitor` creation API (Phase 3 implementation).