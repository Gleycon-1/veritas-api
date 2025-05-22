# Esta função analisa uma URL e compara com portais confiáveis para ajudar a detectar fake news
def analisar_url(url: str):
    ...


from fastapi import FastAPI
from api.routes_analyze import router as analyze_router
from api.routes_status import router as status_router
from api.routes_feedback import router as feedback_router
from api.routes_history import router as history_router

app = FastAPI()

app.include_router(analyze_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Veritas API - Combatting Disinformation!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    

