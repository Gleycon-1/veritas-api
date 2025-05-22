from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session


from src.models.analysis import Analysis  # Schema de resposta (Pydantic)
from src.db.models import get_analysis_status  # Função de consulta ao banco
from src.db.database import get_db  # Dependência do banco

router = APIRouter()

@router.get("/status/{id}", response_model=Analysis)
def get_status(id: str, db: Session = Depends(get_db)):
    """
    Retorna o status de uma análise com base no ID.
    """
    analysis = get_analysis_status(db, id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis
