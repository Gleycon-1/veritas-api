# src/db/crud_operations.py

from sqlalchemy.orm import Session
from src.db.models import AnalysisModel
from src.models import analysis as schemas # Importa os schemas Pydantic
from datetime import datetime
import json # Importar para lidar com JSON string em 'sources'

# --- Funções CRUD para o modelo Analysis ---

def get_analysis_by_id(db: Session, analysis_id: str): # analysis_id agora é str (UUID)
    """
    Busca uma análise pelo seu ID.
    """
    db_analysis = db.query(AnalysisModel).filter(AnalysisModel.id == analysis_id).first()
    if db_analysis and db_analysis.sources:
        # Deserializa a string JSON de 'sources' de volta para uma lista
        try:
            db_analysis.sources = json.loads(db_analysis.sources)
        except json.JSONDecodeError:
            # Em caso de erro na deserialização, trate como uma lista vazia ou erro
            db_analysis.sources = [] # Ou raise an error, dependendo do que você quer fazer
    return db_analysis

def create_analysis(db: Session, analysis_data: schemas.AnalysisCreate):
    """
    Cria uma nova entrada de análise no banco de dados.
    """
    # Serializa a lista de 'sources' para uma string JSON antes de salvar
    # Se analysis_data.sources for None ou vazio, salva como None ou '{}'
    sources_json = json.dumps(analysis_data.sources) if analysis_data.sources else None

    db_analysis = AnalysisModel(
        content=analysis_data.content,
        classification=analysis_data.classification,
        status=analysis_data.status,
        sources=sources_json,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow() # Define updated_at na criação
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)

    # Deserializa 'sources' de volta para lista para o objeto retornado (consistência com Pydantic)
    if db_analysis.sources:
        try:
            db_analysis.sources = json.loads(db_analysis.sources)
        except json.JSONDecodeError:
            db_analysis.sources = []
    return db_analysis

def update_analysis_status(db: Session, analysis_id: str, new_status: str): # analysis_id agora é str
    """
    Atualiza o status de uma análise existente.
    """
    # Pega o objeto do banco de dados diretamente, não o Pydantic model do get_analysis_by_id
    analysis_to_update = db.query(AnalysisModel).filter(AnalysisModel.id == analysis_id).first()
    if analysis_to_update:
        analysis_to_update.status = new_status
        analysis_to_update.updated_at = datetime.utcnow() # Atualiza updated_at
        db.commit()
        db.refresh(analysis_to_update)

        # Deserializa 'sources' antes de retornar para consistência com o schema Pydantic
        if analysis_to_update.sources:
            try:
                analysis_to_update.sources = json.loads(analysis_to_update.sources)
            except json.JSONDecodeError:
                analysis_to_update.sources = []
    return analysis_to_update

def delete_analysis(db: Session, analysis_id: str): # analysis_id agora é str
    """
    Exclui uma análise do banco de dados pelo seu ID.
    """
    db_analysis = db.query(AnalysisModel).filter(AnalysisModel.id == analysis_id).first()
    if db_analysis:
        db.delete(db_analysis)
        db.commit()
    return db_analysis # Retorna o objeto que foi deletado, ou None