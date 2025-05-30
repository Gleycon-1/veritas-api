# src/db/sync_crud_operations.py (DEVE CONTER ISSO)

from sqlalchemy.orm import Session as SyncSession
from src.db.models import AnalysisModel
from datetime import datetime
import json
from typing import Optional, List

def update_analysis_details_sync(
    db: SyncSession,
    analysis_id: str,
    classification: str,
    status: str,
    sources: List[str],
    message: Optional[str] = None,
    color: Optional[str] = None
) -> Optional[AnalysisModel]:
    try:
        analysis = db.query(AnalysisModel).filter(AnalysisModel.id == analysis_id).first()

        if analysis:
            analysis.classification = classification
            analysis.status = status
            analysis.sources = json.dumps(sources) if sources is not None else json.dumps([])
            analysis.message = message
            analysis.updated_at = datetime.utcnow()
            
            if color is not None:
                analysis.color = color
            
            db.add(analysis)
            db.commit()
            db.refresh(analysis)

            if analysis.sources:
                try:
                    analysis.sources = json.loads(analysis.sources)
                except json.JSONDecodeError:
                    analysis.sources = []
            return analysis
        else:
            print(f"DEBUG: update_analysis_details_sync - Análise com ID {analysis_id} não encontrada para atualização.")
            return None
    except Exception as e:
        db.rollback()
        print(f"ERRO: update_analysis_details_sync - Falha ao atualizar análise {analysis_id}: {e}")
        return None

def update_analysis_status_sync(
    db: SyncSession,
    analysis_id: str,
    status: str,
    message: Optional[str] = None
) -> Optional[AnalysisModel]:
    try:
        analysis_to_update = db.query(AnalysisModel).filter(AnalysisModel.id == analysis_id).first()

        if analysis_to_update:
            analysis_to_update.status = status
            if message is not None:
                analysis_to_update.message = message
            analysis_to_update.updated_at = datetime.utcnow()
            
            db.add(analysis_to_update)
            db.commit()
            db.refresh(analysis_to_update)

            if analysis_to_update.sources:
                try:
                    analysis_to_update.sources = json.loads(analysis_to_update.sources)
                except json.JSONDecodeError:
                    analysis_to_update.sources = []
            return analysis_to_update
        else:
            print(f"DEBUG: update_analysis_status_sync - Análise com ID {analysis_id} não encontrada para atualização de status.")
            return None
    except Exception as e:
        db.rollback()
        print(f"ERRO: update_analysis_status_sync - Falha ao atualizar status de análise {analysis_id}: {e}")
        return None