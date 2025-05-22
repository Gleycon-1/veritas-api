from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class Feedback(BaseModel):
    analysis_id: str
    user_feedback: str

@router.post("/feedback")
async def receive_feedback(feedback: Feedback):
    # Aqui você pode adicionar a lógica para processar o feedback
    # Por exemplo, armazenar no banco de dados ou atualizar o modelo
    return {"message": "Feedback recebido com sucesso", "feedback": feedback}