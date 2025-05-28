import asyncio
from celery import Celery
from .config import settings
from .llm_integration import analyze_content_with_llm
from src.db import crud_operations as crud_operations
from ..db.database import get_db_session_sync
from typing import Optional, List
import os

print("DEBUG_TASK: src/core/tasks.py está sendo carregado!")

# Configuração do Celery
celery_app = Celery(
    "veritas_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_track_started=True,
    broker_connection_retry_on_startup=True,
    timezone='UTC',
    enable_utc=True,
)

def get_color_from_classification(classification: str) -> str:
    lower_classification = classification.lower()
    if "fake_news" in lower_classification or "noticia_falsa" in lower_classification or "desinformacao" in lower_classification:
        return "🔴"
    elif "verdadeiro" in lower_classification or "fato" in lower_classification or "confirmado" in lower_classification:
        return "🟢"
    elif "sátira" in lower_classification or "humor" in lower_classification or "ficcao" in lower_classification:
        return "⚪"
    elif "opinião" in lower_classification or "editorial" in lower_classification or "perspectiva" in lower_classification:
        return "🔵"
    elif "parcial" in lower_classification or "tendencioso" in lower_classification:
        return "🟠"
    else:
        return "⚫"

@celery_app.task(name="src.core.tasks.analyze_content_task", bind=True)
def analyze_content_task(self, analysis_id: str, content: str, preferred_llm: str):
    asyncio.run(_run_analysis_logic(analysis_id, content, preferred_llm))


async def _run_analysis_logic(analysis_id: str, content: str, preferred_llm: str):
    db = None
    try:
        db_generator = get_db_session_sync()
        db = next(db_generator)

        print(f"INFO: [Celery Task] Iniciando análise para ID: {analysis_id} com {preferred_llm}.")
        llm_result = {}
        try:
            llm_result = await analyze_content_with_llm(content, preferred_llm=preferred_llm)
            print(f"DEBUG: [Celery Task] Resultado do LLM para ID {analysis_id}: {llm_result}")
        except Exception as e:
            print(f"ERRO: [Celery Task] Falha ao chamar LLM para ID {analysis_id}: {e}")
            llm_result = {"classification": "error", "message": f"Erro na análise da LLM: {e}"}

        classification = llm_result.get("classification", "indefinido")
        message = llm_result.get("message", "Nenhuma justificativa fornecida pela LLM ou erro na análise.")
        sources = llm_result.get("sources", ["LLM_analysis"])

        # Chamar as funções usando o alias
        updated_analysis = crud_operations.update_analysis_details( # MUDANÇA AQUI
            db=db,
            analysis_id=analysis_id,
            classification=classification,
            status="completed" if classification.lower() != "error" else "failed",
            sources=sources,
            message=message
        )
        if not updated_analysis:
            print(f"ERRO: [Celery Task] Análise com ID {analysis_id} não encontrada ou falha na atualização (crud.py).")

        print(f"INFO: [Celery Task] Análise para ID: {analysis_id} concluída e BD atualizado.")

    except Exception as e:
        print(f"ERRO: [Celery Task] Falha crítica na análise de fundo para ID {analysis_id}: {e}")
        if db:
            try:
                crud_operations.update_analysis_status( # MUDANÇA AQUI
                    db=db,
                    analysis_id=analysis_id,
                    status="failed",
                    message=f"Erro crítico na análise: {e}"
                )
            except Exception as update_e:
                print(f"ERRO: [Celery Task] Falha ao atualizar status para 'failed' para ID {analysis_id}: {update_e}")
    finally:
        if db:
            db.close()