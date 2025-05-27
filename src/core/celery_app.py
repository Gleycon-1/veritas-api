# src/core/celery_app.py

from celery import Celery
from src.core.config import settings # Para pegar as configurações do Redis

# Configuração do Celery
# Redis será o broker (fila de tarefas) e o backend de resultados (onde os resultados das tarefas são armazenados)
celery_app = Celery(
    "veritas_api", # Nome da sua aplicação Celery
    broker=settings.REDIS_URL,       # URL do seu servidor Redis (e.g., "redis://localhost:6379/0")
    backend=settings.REDIS_URL,      # Usando o mesmo Redis para armazenar resultados
    include=['src.core.tasks'] # Inclui o arquivo onde suas tarefas estarão definidas
)

# Configurações adicionais para o Celery (opcional, mas recomendado)
celery_app.conf.update(
    task_track_started=True,        # Permite rastrear tarefas em estado "STARTED"
    task_acks_late=True,            # Acknowledge tasks after they are executed
    task_reject_on_worker_lost=True # Rejeitar tarefa se o worker morrer
)