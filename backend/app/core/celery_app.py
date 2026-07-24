from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from app.tasks.base import BaseTask

# Initialize Celery application named 'vigilux'
# Set BaseTask as the default task class for automatic retry behavior
celery_app = Celery(
    "vigilux",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    task_base=BaseTask
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_routes={
        "app.tasks.radar.*": {"queue": "radar"},
        "app.tasks.scoring.*": {"queue": "scoring"},
        "app.tasks.scraping.*": {"queue": "radar"},
        "app.tasks.scheduler.*": {"queue": "default"},
    },
    beat_schedule={
        # Run tiered scheduler every hour
        # Checks for competitors due for scanning based on plan tier:
        # - Ultimate: Daily (24h)
        # - Growth: Weekly (7 days)
        # - Starter: Manual only (not scheduled)
        "run-tiered-scheduler": {
            "task": "app.tasks.scheduler.run_tiered_scheduler",
            "schedule": crontab(minute=0),  # Run every hour at :00
        },
    }
)

# Load tasks
celery_app.autodiscover_tasks(
    ["app.tasks.radar", "app.tasks.scoring", "app.tasks.scraping", "app.tasks.analysis", "app.tasks.scheduler"],
    force=True
)