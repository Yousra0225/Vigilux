# Vigilux – APM Implementation Plan
**Memory Strategy:** Dynamic-MD
**Last Modification:** Plan creation by the Setup Agent.
**Project Overview:** Vigilux is a competitive intelligence SaaS. Backend Phase 7 (Real Engines) is partially implemented (Apify/Celery files exist). **Current Priority:** Debugging existing backend logic and **Implementing the Frontend Integration** which is currently missing (UI is still static/mock).

## Phase 1: Foundation & Infrastructure (Completed/Maintenance)
*Reference Only - See existing codebase*

## Phase 2: Database Schema & Authentication (Completed/Maintenance)
*Reference Only - See existing codebase*

## Phase 3: Core Logic & Mocks (Completed/Maintenance)
*Reference Only - See existing codebase*

## Phase 4: Dashboard & UI Implementation (Completed/Maintenance)
*Reference Only - See existing codebase*

## Phase 5: Notifications & Integrations (Pending Future)
*Deferred until Real Engines are active*

## Phase 6: QA & Finalization (Continuous)
*Ongoing/Deferred*

## Phase 7: Real Engines & Frontend Integration (REVISED)

### Phase 7A: Backend Review & Fixes (Async/Scraping/AI)
*Note: Files for Apify/Celery exist. Manager must review and fix bugs.*

#### Task 7.1.1 – Backend Integrity Check - Agent_Backend_Async
**Objective:** Verify existing Celery/Redis/Apify implementation is bug-free.
**Output:** Bug fixes in `apify_client.py`, `celery_app.py`, and tasks.
**Guidance:**
- Verify `celery_app.py` loads config correctly.
- Test `ApifyService.scrape_google_maps` with real credentials.
- Ensure Rate Limit/Retry logic is actually active in `tasks`.

#### Task 7.1.2 – Scheduler & Quota Debugging - Agent_Backend_Async
**Objective:** Ensure the tiered scheduling logic (Starter vs Ultimate) works.
**Output:** Fixes to `tasks/scheduler.py` (if exists) or create it.
**Guidance:**
- Verify "Growth" users only get weekly updates.
- Verify "Starter" users are blocked from auto-updates.

### Phase 7E: Real-time User Feedback (Backend Side)
*Note: Ensure WebSockets are ready.*

#### Task 7.5.1 – WebSocket Backend Verification - Agent_Backend_Async
**Objective:** Confirm `ws` endpoints and Redis PubSub are working.
**Output:** Working `/ws/notifications/{user_id}` endpoint.
**Guidance:**
- Test connection.
- Ensure Celery tasks actually emit `SCRAPING_STARTED` events.

### Phase 7F: Frontend Integration & UX Polish (CRITICAL NEW PHASE)

#### Task 7.6.1 – Onboarding Niche Selection Modal - Agent_Frontend_App
**Objective:** Force users to select a domain/niche upon first login (like a paywall/setup screen).
**Output:** `NicheSelectionModal` component and `UserContext` update.
**Guidance:**
- Check if `user.niche` is set. If not, show **Blocking Modal**.
- List predefined niches from DB/Config.
- Prevent dashboard access until selection is saved.

#### Task 7.6.2 – Radar Chart & Spider Visualization - Agent_Frontend_App
**Objective:** Re-implement the Radar/Spider Chart using **Real Data** from the backend.
**Output:** `CompetitorRadarChart` component using Recharts.
**Guidance:**
- Fetch data from `/api/v1/competitors/{id}/radar`.
- Map `Competitor.attributes` (e.g., Price, Innovation, Reach) to Radar axes.
- Replace the static placeholder in `RadarPage`.

#### Task 7.6.3 – Async UX Integration (Progress Bars) - Agent_Frontend_Realtime
**Objective:** Connect the Dashboard to the WebSockets to show "Scanning...".
**Output:** Integrated `TaskProgress` component in `DashboardPage`.
**Guidance:**
- Replace the static "Refresh" button logic.
- When `SCRAPING_STARTED` event is received via WebSocket, replace Stats/Cards with a **Progress Bar / Loading State**.
- Prevent user interaction with the specific competitor card during scan.
- Toast notification on completion: "Scan Finished. New Insights Available."
