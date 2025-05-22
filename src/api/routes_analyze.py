from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class AnalyzeRequest(BaseModel):
    texto: str

class AnalyzeResponse(BaseModel):
    classificacao: str  # verde, vermelho, cinza, azul
    cor: str            # 🟢, 🔴, ⚪, 🔵
    mensagem: str

def mock_analyze_text(texto: str):
    texto_lower = texto.lower()
    if "fake" in texto_lower or "mentira" in texto_lower:
        return "vermelho", "🔴", "Fake news identificada."
    elif "verdade" in texto_lower or "confirmado" in texto_lower:
        return "verde", "🟢", "Conteúdo verificado como verdadeiro."
    elif "opinião" in texto_lower or "sátira" in texto_lower or "meme" in texto_lower:
        return "azul", "🔵", "Conteúdo identificado como opinião, sátira ou meme."
    else:
        return "cinza", "⚪", "Conteúdo ainda em análise."

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    if not request.texto.strip():
        raise HTTPException(status_code=400, detail="Texto não pode ser vazio.")
    classificacao, cor, mensagem = mock_analyze_text(request.texto)
    return AnalyzeResponse(classificacao=classificacao, cor=cor, mensagem=mensagem)