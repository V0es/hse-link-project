from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "app", broker=settings.celery.broker_url, include=["app.links.tasks"]
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

celery_app.conf.beat_schedule = {
    "sync_stats": {
        "task": "sync_stats",
        "schedule": 60.0,
    },
    "flush_abandoned_links": {
        "task": "flush_abandoned_links",
        "schedule": 60.0,
    },
}
