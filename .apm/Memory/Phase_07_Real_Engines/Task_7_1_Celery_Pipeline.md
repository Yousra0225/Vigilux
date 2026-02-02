# Task 7.1 - Celery & Redis Async Pipeline

## Overview
Implemented a Celery-based async task processing pipeline with Redis to handle long-running processes (radar scans, V-Score calculations) asynchronously, ensuring API responsiveness and scalability.

## Implementation Details

### 1. Dependencies Added
**File:** `backend/requirements.txt`

Added Celery and Redis dependencies:
```
celery[redis]>=5.3.0
redis>=5.0.0
```

### 2. Configuration
**File:** `backend/app/core/config.py`

Added Redis configuration settings:
- `REDIS_HOST`: Redis server hostname (default: "redis" for Docker)
- `REDIS_PORT`: Redis port (default: 6379)
- `REDIS_DB`: Redis database number (default: 0)
- `REDIS_URL`: Auto-constructed connection string

### 3. Celery Application
**File:** `backend/app/core/celery_app.py`

Created the Celery application instance with:
- **Broker/Backend:** Redis (configurable via settings)
- **Task Modules:** `app.tasks.radar`, `app.tasks.scoring`
- **Serialization:** JSON for tasks and results
- **Task Routing:** Separate queues for radar and scoring tasks
- **Result Expiration:** 24 hours

Configuration:
```python
celery_app = Celery(
    "vigilux",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.radar", "app.tasks.scoring"]
)
```

### 4. Radar Tasks
**File:** `backend/app/tasks/radar.py`

#### `perform_market_scan(query, user_id, num_results)`
- Simulates async market scanning (2-second processing time)
- Returns mock competitor data with threat scores
- Auto-retry on failure (max 3 retries with exponential backoff)

#### `add_competitors_from_scan(project_id, scan_results, user_id)`
- Adds competitors from scan results to a project
- Verifies project ownership before adding
- Returns list of added competitor IDs

### 5. Scoring Tasks
**File:** `backend/app/tasks/scoring.py`

#### `calculate_competitor_score(competitor_id)`
- Calculates V-Score based on recent events
- Uses average of last 10 event scores
- Updates competitor's score in database

#### `score_all_competitors(project_id)`
- Triggers scoring for all competitors in a project
- Returns list of task IDs for tracking

#### `process_event_and_score(competitor_id, event_type, description)`
- Compound task that:
  1. Creates a new event
  2. Calculates event score using ScoringService
  3. Triggers competitor V-Score recalculation

### 6. API Updates
**File:** `backend/app/api/v1/competitors.py`

#### New Endpoints:

##### GET `/api/v1/competitors/radar/scan`
**Async market scan** - Returns immediately with task_id:
```json
{
  "task_id": "uuid",
  "status": "PENDING",
  "message": "Market scan for 'keyword' started. Use /tasks/{task_id} to check status."
}
```

##### GET `/api/v1/competitors/tasks/{task_id}`
**Task status check** - Returns task status and results:
```json
{
  "task_id": "uuid",
  "status": "SUCCESS",
  "result": [...],
  "message": "Task completed successfully."
}
```

Possible status values: `PENDING`, `STARTED`, `SUCCESS`, `FAILURE`

#### Legacy Endpoint Preserved:
- GET `/api/v1/competitors/radar` - Still available for synchronous scans

### 7. Docker Compose Updates
**File:** `docker-compose.yml`

Added services:

#### Redis Service
```yaml
redis:
  image: redis:7-alpine
  container_name: vigilux-redis
  ports: ["6379:6379"]
  healthcheck: redis-cli ping
```

#### Worker Service
```yaml
worker:
  container_name: vigilux-worker
  command: celery -A app.core.celery_app worker --loglevel=info --queues=default,radar,scoring
  depends_on: [db, redis]
```

#### Flower Service (Optional - Monitoring)
```yaml
flower:
  container_name: vigilux-flower
  command: celery -A app.core.celery_app flower --port=5555
  ports: ["5555:5555"]
```

## Architecture

```
                    ┌─────────────────┐
                    │   FastAPI API   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     Redis       │
                    │  (Broker/Store) │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Celery Worker  │
                    │  - radar queue  │
                    │  - scoring queue│
                    └─────────────────┘
```

## Task Flow Example

### Async Market Scan
```
1. Client: GET /api/v1/competitors/radar/scan?query=saas
2. API: task = perform_market_scan.delay(query, user_id)
3. API: Returns {task_id, status: "PENDING"}
4. Worker: Processes task (2 seconds)
5. Client: GET /api/v1/competitors/tasks/{task_id}
6. API: Returns {status: "SUCCESS", result: [...]}
```

## API Usage Examples

### Trigger Async Scan
```bash
GET /api/v1/competitors/radar/scan?query=saas&num_results=5
Authorization: Bearer <token>
```

Response:
```json
{
  "task_id": "a1b2c3d4-...",
  "status": "PENDING",
  "message": "Market scan for 'saas' started. Use /tasks/a1b2c3d4-... to check status."
}
```

### Check Task Status
```bash
GET /api/v1/competitors/tasks/a1b2c3d4-...
Authorization: Bearer <token>
```

Response (when complete):
```json
{
  "task_id": "a1b2c3d4-...",
  "status": "SUCCESS",
  "result": [
    {
      "name": "SaaS Tech",
      "url": "https://www.saastech.com",
      "threat_score": 75,
      "market_presence": "High",
      "pitch": "...",
      "strengths": [...],
      "weaknesses": [...]
    }
  ],
  "message": "Task completed successfully."
}
```

## Docker Commands

### Start all services:
```bash
docker-compose up -d
```

### View worker logs:
```bash
docker-compose logs -f worker
```

### Access Flower monitoring:
```
http://localhost:5555
```

## Success Criteria
- [x] Celery worker starts and connects to Redis without errors
- [x] Launching a scan via API returns a `task_id` instantly
- [x] Worker logs show task execution
- [x] Task status endpoint returns results when complete

## Benefits
1. **API Responsiveness:** Long-running operations don't block API responses
2. **Scalability:** Multiple workers can process tasks in parallel
3. **Reliability:** Tasks are retried on failure with exponential backoff
4. **Monitoring:** Flower provides real-time task monitoring
5. **Queue Separation:** Different queues for radar and scoring allow independent scaling

## Future Enhancements
- Add periodic tasks using Celery Beat for automated competitor monitoring
- Implement task result caching for performance
- Add webhook notifications when tasks complete
- Implement task cancellation
- Add task prioritization
- Configure task rate limits per user
