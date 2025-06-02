# src/celery_utils.py

from celery import Celery
from src.core.config import settings

# Configura o Celery
celery_app = Celery(
    "veritas_api",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['src.core.tasks'] # Certifique-se de que sua tarefa está incluída aqui
)

# Opcional: Configurações adicionais, se houver
celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1
)

print("DEBUG: src/celery_utils.py está sendo carregado e celery_app configurado.")