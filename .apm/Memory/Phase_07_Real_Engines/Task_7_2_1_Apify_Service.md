# Task 7.2.1 - Apify Service Client

## Status
Completed

## Implementation Details
- **Service Created**: `backend/app/services/apify_client.py`
- **Class**: `ApifyService`
- **Key Methods**:
  - `__init__`: Initializes `ApifyClient` with `APIFY_API_TOKEN` from `app.core.config.settings`.
  - `run_actor`: generic method to start an actor, wait for completion (`call()`), check status ('SUCCEEDED'), and retrieve items from the default dataset.
- **Dependencies**: Verified `apify-client>=1.6.0` exists in `backend/requirements.txt`.
- **Configuration**: Uses `APIFY_API_TOKEN` from `backend/app/core/config.py`.

## Technical Decisions
- Used `apify_client.ApifyClient.call()` for a synchronous-like wrapper around the async/polling nature of actor runs, simplifying the initial implementation.
- Added basic error handling for non-SUCCEEDED statuses.
- Instantiated a singleton `apify_service` at the end of the module for easy import.

## Next Steps
- Implement **Task 7.2.2 - Google Maps Connector** utilizing this service.
