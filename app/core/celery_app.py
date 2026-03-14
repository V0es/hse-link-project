from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "app.core", broker=settings.celery.broker_url, include=["app.links.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content="json",
)

celery_app.autodiscover_tasks()
