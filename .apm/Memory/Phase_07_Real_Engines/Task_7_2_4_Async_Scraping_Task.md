---
agent: Agent_Backend_Async
task_ref: Task 7.2.4
status: Completed
ad_hoc_delegation: false
compatibility_issues: false
important_findings: true
---

# Task Log: Task 7.2.4 - Async Scraping Task

## Summary
Created the Celery scraping task that orchestrates competitor data collection from Google Maps. The task uses the ScanningTask base class for resilient retry behavior and integrates with the Apify and Normalization services.

## Details
- Created `backend/app/tasks/scraping.py` with two tasks:
  - `scrape_competitor_task(competitor_id, location)`: Scrapes a single competitor from Google Maps
  - `scrape_all_competitors_task(project_id, location)`: Batch task that triggers scraping for all competitors in a project
- Tasks use the `ScanningTask` base class (7 retries, 900s max backoff) for handling rate limits and network failures
- Integrated with `apify_service.scrape_google_maps()` for data collection
- Integrated with `normalization_service.normalize_google_maps_data()` for data cleaning
- Updates competitor `url` and `score` fields in database after successful scrape
- Updated `celery_app.py` to autodiscover scraping tasks and route them to the `radar` queue
- Added placeholder for triggering `analyze_competitor_task` (Phase 7C)

## Output
- Created files: `backend/app/tasks/scraping.py`
  - `scrape_competitor_task`: Main scraping task with full error handling
  - `scrape_all_competitors_task`: Batch orchestration task

```python
@celery_app.task(base=ScanningTask, bind=True, name="app.tasks.scraping.scrape_competitor")
def scrape_competitor_task(self, competitor_id: str, location: Optional[str] = None):
    # 1. Validate competitor_id
    # 2. Retrieve competitor from DB
    # 3. Scrape Google Maps via apify_service
    # 4. Normalize data via normalization_service
    # 5. Update competitor record
    # 6. Trigger analysis task (placeholder)
```

- Modified files: `backend/app/core/celery_app.py`
  - Added `"app.tasks.scraping.*": {"queue": "radar"}` to task_routes
  - Added `"app.tasks.scraping"` to autodiscover_tasks list

## Issues
None

## Important Findings
The current `Competitor` model has limited fields for storing scraped data:
- Missing: `address`, `phone`, `last_scanned_at` fields
- Currently only updating: `url` and `score` fields
- Additional scraped data (website, phone, reviews) is logged but not persisted

**Recommendation**: Consider expanding the Competitor model schema to include:
- `address`: Optional[str]
- `phone`: Optional[str]
- `last_scanned_at`: Optional[datetime]
- `scraped_data_json`: Optional[dict] for storing full normalized data

## Next Steps
- Task 7.3.3 (Async Analysis Task) should implement `analyze_competitor_task` to complete the chain
- The scrape task currently logs where the analysis task would be triggered
- Consider Competitor model expansion to store full scraped data
