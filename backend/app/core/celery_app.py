from celery import Celery
from app.core.config import settings

# Initialize Celery application named 'vigilux'
celery_app = Celery(
    "vigilux",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
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
    }
)

# Load tasks
celery_app.autodiscover_tasks(["app.tasks.radar", "app.tasks.scoring"], force=True)