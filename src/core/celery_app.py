# src/core/celery_app.py
from celery import Celery
import eventlet # Importe eventlet AQUI
eventlet.monkey_patch() # CHAME monkey_patch() BEM NO INÍCIO

from src.core.config import settings # Para pegar as configurações do Redis

# Configuração do Celery
celery_app = Celery(
    "veritas_api", # Nome da sua aplicação Celery
    broker=settings.CELERY_BROKER_URL,    # Use a variável correta para o broker
    backend=settings.CELERY_RESULT_BACKEND # Use a variável correta para o backend
)

# Adicione aqui para que as tarefas sejam descobertas automaticamente
# Isso diz ao Celery para procurar tarefas em src.core/tasks.py
celery_app.autodiscover_tasks(['src.core'], related_name='tasks')

# Configurações adicionais para o Celery (opcional, mas recomendado)
celery_app.conf.update(
    task_track_started=True,          # Permite rastrear tarefas em estado "STARTED"
    task_acks_late=True,              # Acknowledge tasks after they are executed
    task_reject_on_worker_lost=True   # Rejeitar tarefa se o worker morrer
)