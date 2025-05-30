import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient # Importe a classe InferenceClient

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_MODEL_ID = os.getenv("HUGGINGFACE_MODEL_ID")

if not HUGGINGFACE_API_KEY or not HUGGINGFACE_MODEL_ID:
    print("Erro: HUGGINGFACE_API_KEY ou HUGGINGFACE_MODEL_ID não encontrados no .env")
else:
    print(f"DEBUG: Chave Hugging Face carregada: {HUGGINGFACE_API_KEY[:5]}...")
    print(f"DEBUG: Modelo Hugging Face configurado: {HUGGINGFACE_MODEL_ID}")

    try:
        # Use o InferenceClient da huggingface_hub
        client = InferenceClient(
            token=HUGGINGFACE_API_KEY, # Use 'token' para a chave API
            model=HUGGINGFACE_MODEL_ID, # Especifique o modelo aqui
        )

        test_text = "Explique a fotossíntese em uma frase."
        print(f"\nTentando análise com Hugging Face (Modelo: {HUGGINGFACE_MODEL_ID})...")

        # Use client.text_generation para um texto simples, ou client.chat.completions.create para formato de chat
        # Vou usar text_generation para ser mais direto com a pergunta de uma frase.
        response = client.text_generation(prompt=test_text, max_new_tokens=50) # max_new_tokens para limitar a resposta

        print("\nResposta da Hugging Face:")
        print(response) # A resposta já é o texto puro
        print("\nConexão Hugging Face OK!")

    except Exception as e:
        print(f"Erro ao conectar ou usar a API Hugging Face: {e}")
        # Se for um erro de HTTP, tente printar mais detalhes
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status: {e.response.status_code}, Resposta: {e.response.text}")