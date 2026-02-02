from celery import Celery
import os

# Get Redis configuration from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")

celery_app = Celery(
    "worker",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.tasks.radar.*": {"queue": "radar"},
        "app.tasks.scoring.*": {"queue": "scoring"},
    }
)

# Load tasks
celery_app.autodiscover_tasks(["app.tasks.radar", "app.tasks.scoring"], force=True)