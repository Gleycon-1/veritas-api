# src/core/celery_app.py
from celery import Celery
import eventlet
eventlet.monkey_patch() # CHAME monkey_patch() BEM NO INÍCIO

from src.core.config import settings

celery_app = Celery(
    "veritas_api",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.autodiscover_tasks(['src.core'], related_name='tasks')

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True
)