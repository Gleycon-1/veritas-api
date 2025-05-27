# src/core/tasks.py

import asyncio
from src.core.celery_app import celery_app
from src.core.llm_integration import analyze_content_with_llm
from src.db import crud_operations
from src.db.database import get_db_session_sync # Importar uma função para obter sessão SQLAlchemy síncrona
from datetime import datetime
from typing import List, Optional

# NOTA: O Celery worker roda em um processo separado e não pode usar dependências assíncronas do FastAPI (Depends).
# Precisamos de uma maneira de obter uma sessão de BD síncrona dentro da tarefa Celery.

# --- Função Auxiliar para Mapear Classificação para Cor (Copiada de routes_analyze.py) ---
def get_color_from_classification(classification: str) -> str:
    """
    Mapeia a classificação do LLM para um emoji de cor.
    """
    lower_classification = classification.lower()
    if "fake_news" in lower_classification or "noticia_falsa" in lower_classification or "desinformacao" in lower_classification:
        return "🔴" # Vermelho para fake news
    elif "verdadeiro" in lower_classification or "fato" in lower_classification or "confirmado" in lower_classification:
        return "🟢" # Verde para verdadeiro
    elif "sátira" in lower_classification or "humor" in lower_classification or "ficcao" in lower_classification:
        return "⚪" # Branco/Cinzento para sátira
    elif "opinião" in lower_classification or "editorial" in lower_classification or "perspectiva" in lower_classification:
        return "🔵" # Azul para opinião
    elif "parcial" in lower_classification or "tendencioso" in lower_classification:
        return "🟠" # Laranja para parcial
    else:
        return "⚫" # Preto para indefinido/erro

# --- Tarefa Celery para Análise ---
@celery_app.task(bind=True) # `bind=True` permite acessar `self` (a instância da tarefa)
def analyze_content_task(self, analysis_id: str, content: str, preferred_llm: str):
    # A tarefa Celery é síncrona por padrão.
    # Se analyze_content_with_llm for assíncrona, precisamos executá-la dentro de um loop de eventos asyncio.
    loop = asyncio.get_event_loop()
    if loop.is_running(): # Se já há um loop rodando (ex: em ambientes de teste), crie uma nova tarefa
        task = loop.create_task(_run_analysis_logic(analysis_id, content, preferred_llm))
        loop.run_until_complete(task)
    else: # Caso contrário, crie um novo loop (comum em workers Celery)
        loop.run_until_complete(_run_analysis_logic(analysis_id, content, preferred_llm))

async def _run_analysis_logic(analysis_id: str, content: str, preferred_llm: str):
    """
    Lógica de análise real que será executada pela tarefa Celery.
    Isolada para poder ser chamada de forma assíncrona.
    """
    # A tarefa Celery não tem acesso direto às dependências do FastAPI (como get_db)
    # Precisamos obter uma sessão de BD síncrona aqui.
    db = None
    try:
        # Pega uma sessão do banco de dados síncrona.
        # Precisamos de um get_db_session_sync em src/db/database.py
        db = next(get_db_session_sync()) # Obtém a sessão do gerador

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

        # Atualizar a análise no banco de dados
        updated_analysis = crud_operations.update_analysis_details(
            db=db,
            analysis_id=analysis_id,
            classification=classification,
            status="completed" if classification != "error" else "failed",
            sources=sources,
            message=message
        )
        if not updated_analysis:
            print(f"ERRO: [Celery Task] Análise com ID {analysis_id} não encontrada para atualização.")

        print(f"INFO: [Celery Task] Análise para ID: {analysis_id} concluída e BD atualizado.")

    except Exception as e:
        print(f"ERRO: [Celery Task] Falha crítica na análise de fundo para ID {analysis_id}: {e}")
        # Tentar atualizar o status para 'failed' mesmo em caso de erro crítico
        if db:
            try:
                crud_operations.update_analysis_status(
                    db=db,
                    analysis_id=analysis_id,
                    status="failed",
                    message=f"Erro crítico na análise: {e}"
                )
            except Exception as update_e:
                print(f"ERRO: [Celery Task] Falha ao atualizar status para 'failed' para ID {analysis_id}: {update_e}")
    finally:
        if db:
            db.close() # Fechar a sessão do banco de dados no final da tarefa