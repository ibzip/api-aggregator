from celery import Celery
from app import config

celery_app = Celery(
    "aggregator_tasks",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND
)

from app.tasks import tasks  # or whatever the correct import path is

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    imports=("app.tasks.tasks", )
)
