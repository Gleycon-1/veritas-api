# src/core/tasks.py

from src.celery_utils import celery_app
from src.db.database import SyncSessionLocal
from src.models.analysis import Analysis # Corrigido para src.models.analysis
from src.core.llm_integration import analyze_content_sync
from src.core.config import settings
from src.utils.colors import get_color_from_classification # Assumindo que este arquivo existe

print("DEBUG_TASK: src/core/tasks.py carregado.")

@celery_app.task
def analyze_content_task(analysis_id: str, content: str, preferred_llm: str):
    print(f"CELERY_TASK ▶️ Iniciando análise para ID: {analysis_id} com LLM: {preferred_llm}")

    try:
        with SyncSessionLocal() as db:
            # Chama função síncrona que faz análise via LLM
            llm_result = analyze_content_sync(content, preferred_llm)

            # Extrair resultados do LLM. Certifique-se que analyze_content_sync retorna isso.
            classification = llm_result.get("classification", "error")
            message = llm_result.get("message", "Erro desconhecido na análise LLM.")
            # Se você espera fontes, pode adicionar aqui também:
            # sources = llm_result.get("sources", "") 

            color = get_color_from_classification(classification)

            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

            if analysis:
                analysis.status = "completed" if classification != "error" else "failed"
                analysis.classification = classification
                analysis.message = message # ATUALIZADO: Usando o campo 'message'
                analysis.color = color
                # analysis.sources = sources # Se você adicionar o campo sources aqui

                db.commit()
                db.refresh(analysis)

                print(f"CELERY_TASK ✅ Análise {analysis_id} concluída: {classification} {color}")
            else:
                print(f"CELERY_TASK ⚠️ Análise com ID {analysis_id} não encontrada no banco.")
    
    except Exception as e:
        print(f"CELERY_TASK ❌ Erro durante análise {analysis_id}: {e}")

        # Tenta atualizar a análise para status de erro (se ainda possível)
        try:
            with SyncSessionLocal() as db:
                analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
                if analysis:
                    analysis.status = "failed"
                    analysis.classification = "error"
                    analysis.message = f"Erro interno durante análise: {e}" # ATUALIZADO: Usando o campo 'message'
                    analysis.color = get_color_from_classification("error")
                    db.commit()
                    db.refresh(analysis)
        except Exception as inner_e:
            print(f"CELERY_TASK ❗ Erro ao salvar fallback de erro no BD: {inner_e}") 
