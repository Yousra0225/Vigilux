# Task 3.3 - Mock IA Scoring Engine

## Status
- [x] **Completed** (2026-01-30)

## Implementation Details
1.  **Service (`backend/app/services/scoring.py`)**:
    - `ScoringService` class created.
    - `calculate_score`: Generates mock score (1-100) based on event type and keywords.
    - `analyze_event`: Categorizes events with score > 70 as "Breakthrough Signals".

## Usage
- To be used in `Event` creation API or background tasks.