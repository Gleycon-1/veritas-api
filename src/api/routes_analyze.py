from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from core.llm_integration import analisar_conteudo_llm
    llm_enabled = True
except ImportError:
    llm_enabled = False

router = APIRouter()

class AnalyzeRequest(BaseModel):
    text: str

@router.post("/analyze")
def analyze(request: AnalyzeRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Texto não pode ser vazio.")
    
    if llm_enabled:
        try:
            resultado = analisar_conteudo_llm(request.text)
            return {"resultado": resultado}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # fallback para análise mock
        texto_lower = request.text.lower()
        if "fake" in texto_lower or "mentira" in texto_lower:
            classificacao, cor, mensagem = "vermelho", "🔴", "Fake news identificada."
        elif "verdade" in texto_lower or "confirmado" in texto_lower:
            classificacao, cor, mensagem = "verde", "🟢", "Conteúdo verificado como verdadeiro."
        elif "opinião" in texto_lower or "sátira" in texto_lower or "meme" in texto_lower:
            classificacao, cor, mensagem = "azul", "🔵", "Conteúdo identificado como opinião, sátira ou meme."
        else:
            classificacao, cor, mensagem = "cinza", "⚪", "Conteúdo ainda em análise."
        return {"classificacao": classificacao, "cor": cor, "mensagem": mensagem}
