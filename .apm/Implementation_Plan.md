# Vigilux – APM Implementation Plan
**Memory Strategy:** Dynamic-MD
**Last Modification:** Plan creation by the Setup Agent.
**Project Overview:** Vigilux is a competitive intelligence SaaS that transforms passive monitoring into actionable signals. Phase 1-4 are prototyped (Mock Data). The current focus is **Phase 7: Real Engines**, implementing the actual backend logic with Redis/Celery (Async), Apify (Scraping), Gemini (AI), and a tiered scheduling system (Starter/Growth/Ultimate).

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

## Phase 7A: Infrastructure & Async Backbone

### Task 7.1.1 – Redis Service Configuration - Agent_DevOps
**Objective:** Add Redis to the container stack to serve as the message broker for Celery.
**Output:** Updated `docker-compose.yml` and `.env.example`.
**Guidance:** Use standard redis:alpine image. Ensure persistence with a volume.
- Add `redis` service to `docker-compose.yml` mapping port 6379.
- Configure a named volume `redis_data` for data persistence.
- Add `REDIS_URL=redis://redis:6379/0` to environment variables.

### Task 7.1.2 – Celery Application Setup - Agent_Backend_Async
**Objective:** Initialize the Celery application instance in the backend codebase.
**Output:** `backend/app/core/celery_app.py`.
**Guidance:** **Depends on: Task 7.1.1 Output by Agent_DevOps**
- Create `celery_app.py` in core.
- Initialize `Celery('vigilux')` instance.
- Configure `broker_url` and `result_backend` using settings from `config.py`.
- Set `broker_connection_retry_on_startup = True`.

### Task 7.1.3 – Worker Container Configuration - Agent_DevOps
**Objective:** Create a dedicated Docker service to run the Celery worker process.
**Output:** Updated `docker-compose.yml`.
**Guidance:** **Depends on: Task 7.1.2 Output by Agent_Backend_Async**
- Add `worker` service to `docker-compose.yml`.
- Reuse the `backend` build context/image.
- Set command to `celery -A app.core.celery_app worker --loglevel=info`.
- Ensure it `depends_on` both `db` and `redis`.

### Task 7.1.4 – Base Task & Robust Retry Logic - Agent_Backend_Async
**Objective:** Implement a resilient base configuration for tasks to handle API failures (429s).
**Output:** Configuration update in `celery_app.py` or new `app/tasks/base.py`.
**Guidance:** **Depends on: Task 7.1.2 Output**
1. Define a default retry strategy: `default_retry_delay=60`, `max_retries=3`, `retry_backoff=True`.
2. Configure Celery to handle specific exceptions (e.g., RequestException) automatically if possible, or document how tasks should invoke `self.retry`.

## Phase 7B: Scraping & Data Acquisition

### Task 7.2.1 – Apify Service Client - Agent_Scraping
**Objective:** Implement the core service to interact with the Apify API.
**Output:** `backend/app/services/apify_client.py` and `requirements.txt` update.
**Guidance:**
- Add `apify-client` to requirements.
- Create `ApifyService` class initialized with `APIFY_API_TOKEN`.
- Implement a generic `run_actor(actor_id, run_input)` method that waits for completion and returns the dataset items.

### Task 7.2.2 – Google Maps Connector - Agent_Scraping
**Objective:** Implement specific logic to scrape Google Maps data (Reviews, Details).
**Output:** Method `scrape_google_maps` in `ApifyService`.
**Guidance:** **Depends on: Task 7.2.1 Output**
1. Use a standard actor (e.g., `compass/google-maps-scraper` or similar free tier compatible).
2. Construct input JSON: `searchStrings` based on Competitor Name + Location.
3. Fetch results including `reviews`, `totalScore`, `address`.

### Task 7.2.3 – Data Normalization Logic - Agent_Scraping
**Objective:** Transform raw Apify JSON into Vigilux internal schemas.
**Output:** `app/services/normalization.py`.
**Guidance:** **Depends on: Task 7.2.2 Output**
- Create functions to map external fields to `Competitor` model updates (e.g., address, rating).
- Extract reviews into a structure ready for AI analysis (List of text strings).
- Handle missing data gracefully.

### Task 7.2.4 – Async Scraping Task - Agent_Backend_Async
**Objective:** Create the Celery task that triggers the scraping process.
**Output:** `backend/app/tasks/scraping.py`.
**Guidance:** **Depends on: Task 7.1.4 Output, Task 7.2.1 Output by Agent_Scraping**
- Implement `scrape_competitor_task(competitor_id)`.
- Retrieve competitor from DB.
- Call `ApifyService`.
- On success, update Competitor status and trigger the AI Analysis task (chaining).
- Use the base task's retry logic for network errors.

## Phase 7C: AI Analysis & Insight Generation

### Task 7.3.1 – Gemini Service Wrapper - Agent_Intelligence
**Objective:** Implement the service to interact with Google's Generative AI.
**Output:** `backend/app/services/gemini.py`.
**Guidance:**
- Add `google-generativeai` to requirements.
- Initialize model (e.g., `gemini-pro`) with `GEMINI_API_KEY`.
- Implement `generate_insight(text_data)` method.

### Task 7.3.2 – Prompt Engineering & Parsing - Agent_Intelligence
**Objective:** Design the prompt to extract structured intelligence from raw text.
**Output:** Prompt templates and Pydantic parsers.
**Guidance:** **Depends on: Task 7.3.1 Output**
- Create a prompt that asks for: SWOT Analysis, Sentinel Score (0-100), and Key Events.
- Enforce JSON output format for machine parsing.
- Implement a validator to ensure the AI response matches the expected schema.

### Task 7.3.3 – Async Analysis Task - Agent_Backend_Async
**Objective:** Create the Celery task that processes scraping results with AI.
**Output:** `backend/app/tasks/analysis.py`.
**Guidance:** **Depends on: Task 7.3.1 Output by Agent_Intelligence, Task 7.1.4 Output**
- Implement `analyze_competitor_task(competitor_id, raw_data)`.
- Call `GeminiService.generate_insight`.
- Use the base task's retry logic for Rate Limit errors (429).

### Task 7.3.4 – Insight Persistence Logic - Agent_Backend_Async
**Objective:** Save the AI-generated insights into the database.
**Output:** DB persistence logic within the Analysis Task.
**Guidance:** **Depends on: Task 7.3.3 Output**
- Update `Competitor.score` and `Competitor.last_updated`.
- Create new `Event` records for each key event identified by Gemini.
- Trigger a notification dispatch (optional stub for now).

## Phase 7D: Scheduling & Tiered Logic Orchestration

### Task 7.4.1 – Manual Refresh API - Agent_Backend_Async
**Objective:** Allow users to trigger scans manually, respecting plan limits.
**Output:** Endpoint `POST /api/v1/competitors/{id}/refresh`.
**Guidance:** **Depends on: Task 7.2.4 Output, Task 3.2 (Quota Logic)**
- Implement endpoint to check if user has credits (Starter) or rate limit.
- If allowed, trigger `scrape_competitor_task.delay(id)`.
- Return `{"task_id": "...", "status": "pending"}`.

### Task 7.4.2 – Celery Beat Service - Agent_DevOps
**Objective:** Add the scheduler service to the Docker stack.
**Output:** Updated `docker-compose.yml`.
**Guidance:** **Depends on: Task 7.1.3 Output by Agent_DevOps**
- Add `beat` service using the same backend image.
- Command: `celery -A app.core.celery_app beat -l info`.
- Ensure it shares the `redis` network.

### Task 7.4.3 – Tiered Scheduler Implementation - Agent_Backend_Async
**Objective:** Implement the logic to automatically scan competitors based on User Plan.
**Output:** Scheduled task in `celery_app.py` or `tasks/scheduler.py`.
**Guidance:** **Depends on: Task 7.4.2 Output by Agent_DevOps**
1. Configure a periodic task running e.g., every hour or day.
2. Logic:
   - Find all **Ultimate** users -> Scan their competitors if last_update > 24h.
   - Find all **Growth** users -> Scan if last_update > 7 days.
   - **Starter** users -> Do not auto-scan.

## Phase 7E: Real-time User Feedback

### Task 7.5.1 – WebSocket Manager & Endpoint - Agent_Backend_Async
**Objective:** Enable real-time communication for task progress updates.
**Output:** `backend/app/api/v1/websockets.py`.
**Guidance:**
- Implement a `ConnectionManager` to track active user sessions.
- Create `/ws/notifications/{user_id}` endpoint.
- Use Redis Pub/Sub to listen for task events and forward them to the correct user's WebSocket.

### Task 7.5.2 – Task Progress Emitter - Agent_Backend_Async
**Objective:** Update background tasks to publish their status changes.
**Output:** Updates to `scraping.py` and `analysis.py`.
**Guidance:** **Depends on: Task 7.5.1 Output**
- In `scrape_competitor_task`, publish "SCRAPING_STARTED" and "SCRAPING_COMPLETE" events to Redis.
- In `analyze_competitor_task`, publish "ANALYSIS_STARTED" and "ANALYSIS_COMPLETE".
- Ensure payload includes `competitor_id` and `user_id`.

### Task 7.5.3 – Frontend WebSocket Hook - Agent_Frontend_Realtime
**Objective:** Create a reusable hook to listen for real-time updates.
**Output:** `frontend/src/hooks/use-socket.ts`.
**Guidance:** **Depends on: Task 7.5.1 Output by Agent_Backend_Async**
- Implement `useWebSocket` hook that connects to the backend on mount.
- Handle reconnection logic.
- Expose a listener for specific event types (e.g., `TASK_UPDATE`).

### Task 7.5.4 – Dashboard Refresh UI - Agent_Frontend_Realtime
**Objective:** Integrate the manual refresh button and progress indicators.
**Output:** Updates to `DashboardPage` and `CompetitorCard`.
**Guidance:** **Depends on: Task 7.5.3 Output, Task 7.4.1 Output by Agent_Backend_Async**
- Add "Refresh" button to Competitor cards (visible if manual refresh is allowed).
- When clicked, call API and display a loading spinner/progress bar.
- Listen via WebSocket for "ANALYSIS_COMPLETE" to re-fetch and update the UI data automatically.