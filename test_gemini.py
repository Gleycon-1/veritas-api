import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Erro: GEMINI_API_KEY não encontrada no .env. Verifique seu arquivo .env!")
else:
    print(f"DEBUG: Chave Gemini carregada: {api_key[:5]}...")
    try:
        genai.configure(api_key=api_key)

        print("\nListando modelos disponíveis:")
        for m in genai.list_models():
            # Apenas imprima modelos que suportam 'generateContent'
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name} (Suporta generateContent)")

        # Corrigido: Agora está usando o nome completo do modelo
        print("\nTentando usar o modelo 'models/gemini-1.5-pro'...")
        model = genai.GenerativeModel('models/gemini-1.5-pro') # <<-- AQUI ESTÁ CERTO!
        response = model.generate_content("Qual a capital da França?")
        print("Resposta do Gemini:")
        print(response.text)
        print("\nConexão Gemini OK!")
    except Exception as e:
        print(f"Erro ao conectar ou usar a API Gemini: {e}")