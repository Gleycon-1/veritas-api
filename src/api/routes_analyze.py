 # src/api/routes_analyze.py

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

# Importa o módulo de integração com os LLMs
from src.core.llm_integration import analyze_content_with_llm
# Importa as operações CRUD para salvar o resultado da análise
from src.db import crud_operations
from src.db.database import get_db
from src.models.analysis import AnalysisCreate # Importa os schemas de Pydantic
from src.models.user import User # Importa o modelo de usuário
from src.core.users import current_active_user # Importa a dependência de usuário ativo

# Define o APIRouter com um prefixo e tags para organizar no Swagger UI
router = APIRouter(
    prefix="/analyze", # Este roteador será responsável pelo endpoint /analyze
    tags=["AI Analysis"] # Tag para agrupar no Swagger UI
)

# --- Schemas Pydantic para o Endpoint /analyze ---

class AnalyzeRequest(BaseModel):
    content: str = Field(..., description="O conteúdo textual a ser analisado.")
    # Permite escolher qual LLM usar, com Gemini como padrão
    preferred_llm: Optional[str] = Field("gemini", description="LLM preferencial para análise (gemini, openai ou huggingface).")

class AnalyzeResponse(BaseModel):
    id: str
    content: str
    classification: str
    status: str
    sources: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    color: str = Field(..., description="Cor associada à classificação (ex: '🟢', '🔴', '⚪', '🔵').")
    message: Optional[str] = Field(None, description="Mensagem ou justificativa da análise pelo LLM.")


# --- Função Auxiliar para Mapear Classificação para Cor ---
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

# --- Endpoint /analyze ---

@router.post("/", response_model=AnalyzeResponse, status_code=status.HTTP_201_CREATED)
async def analyze_content_endpoint(
    request_data: AnalyzeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user) # <-- AQUI: Adiciona a dependência de autenticação
):
    """
    Analisa um conteúdo textual usando um modelo de linguagem (LLM)
    e armazena o resultado no banco de dados. Este endpoint requer autenticação.
    """
    content = request_data.content
    preferred_llm = request_data.preferred_llm

    # 1. Chamar a LLM para análise
    print(f"INFO: Recebida solicitação para analisar conteúdo com {preferred_llm}.")
    llm_result = {}
    try:
        llm_result = await analyze_content_with_llm(content, preferred_llm=preferred_llm)
        print(f"DEBUG: Resultado do LLM: {llm_result}")
    except Exception as e:
        print(f"ERRO: Falha ao chamar LLM: {e}")
        # Definir um resultado padrão em caso de falha da LLM
        llm_result = {"classification": "error", "message": f"Erro na análise da LLM: {e}"}

    classification = llm_result.get("classification", "indefinido")
    message = llm_result.get("message", "Nenhuma justificativa fornecida pela LLM ou erro na análise.")
    
    # 2. Mapear classificação para cor
    color = get_color_from_classification(classification)

    # 3. Preparar dados para salvar no banco de dados
    analysis_create_data = AnalysisCreate(
        content=content,
        classification=classification,
        status="completed" if classification != "error" and classification != "indefinido" else "failed", # Marca como concluído
        sources=["LLM_analysis"], # Indica que a fonte é a análise de LLM
    )

    # 4. Salvar a análise no banco de dados
    try:
        # Você pode considerar adicionar o user.id aqui se quiser vincular a análise ao usuário
        db_analysis = crud_operations.create_analysis(db=db, analysis_data=analysis_create_data)
        print(f"DEBUG: Análise salva no BD com ID: {db_analysis.id}")
    except Exception as e:
        print(f"ERRO: Falha ao salvar análise no BD: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Falha ao salvar análise no banco de dados: {e}")

    # 5. Construir a resposta final
    response_data = AnalyzeResponse(
        id=str(db_analysis.id), # Garante que o ID seja uma string
        content=db_analysis.content,
        classification=db_analysis.classification,
        status=db_analysis.status,
        sources=db_analysis.sources,
        created_at=db_analysis.created_at,
        updated_at=db_analysis.updated_at,
        color=color, # Adiciona a cor
        message=message # Adiciona a mensagem da LLM
    )
    
    return response_data