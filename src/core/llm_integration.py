# src/core/llm_integration.py

import os
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv
import json # Importa json para lidar com as respostas em JSON

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Configuração das APIs ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Inicializa o cliente Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-pro')
else:
    gemini_model = None
    print("WARNING: GEMINI_API_KEY não configurada. A análise com Gemini não estará disponível.")

# Inicializa o cliente OpenAI
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None
    print("WARNING: OPENAI_API_KEY não configurada. A análise com OpenAI não estará disponível.")

# --- Funções de Análise ---

def analyze_with_gemini(text: str) -> dict:
    """
    Analisa o conteúdo textual usando a API do Google Gemini.
    Retorna uma classificação e uma mensagem.
    """
    if not gemini_model:
        return {"classification": "error", "message": "API do Gemini não configurada."}

    try:
        prompt = (
            "Analise o seguinte conteúdo textual e classifique-o como 'fake_news', 'verdadeiro', "
            "'sátira', ou 'opinião'. Se for uma sátira ou opinião, indique. "
            "Se for fake news, justifique brevemente. Se for verdadeiro, justifique brevemente. "
            "Se for sátira, explique por que. Se for opinião, justifique brevemente. "
            "Retorne a classificação e a justificativa em um formato JSON: "
            '{"classification": "tipo", "message": "justificativa"}'
            "\n\nConteúdo: " + text
        )
        response = gemini_model.generate_content(prompt)
        response_text = response.text.strip()

        try:
            result = json.loads(response_text)
            if "classification" in result and "message" in result:
                return result
            else:
                raise ValueError("Formato JSON inesperado da resposta do Gemini.")
        except json.JSONDecodeError:
            print(f"DEBUG: Resposta do Gemini não é JSON: {response_text}")
            # Fallback para extração heurística se o JSON falhar
            lower_text = response_text.lower()
            if "fake_news" in lower_text:
                classification = "fake_news"
            elif "verdadeiro" in lower_text:
                classification = "verdadeiro"
            elif "sátira" in lower_text:
                classification = "sátira"
            elif "opinião" in lower_text:
                classification = "opinião"
            else:
                classification = "indefinido"
            return {"classification": classification, "message": response_text}

    except Exception as e:
        print(f"Erro ao analisar com Gemini: {e}")
        return {"classification": "error", "message": f"Erro na análise com Gemini: {e}"}

def analyze_with_openai(text: str) -> dict:
    """
    Analisa o conteúdo textual usando a API do OpenAI (ChatGPT).
    Retorna uma classificação e uma mensagem.
    """
    if not openai_client:
        return {"classification": "error", "message": "API da OpenAI não configurada."}

    try:
        prompt_messages = [
            {"role": "system", "content": "Você é um assistente especializado em análise de texto para detectar desinformação."},
            {"role": "user", "content": (
                "Analise o seguinte conteúdo textual e classifique-o como 'fake_news', 'verdadeiro', "
                "'sátira', ou 'opinião'. Se for uma sátira ou opinião, indique. "
                "Se for fake news, justifique brevemente. Se for verdadeiro, justifique brevemente. "
                "Se for sátira, explique por que. Se for opinião, justifique brevemente. "
                "Retorne a classificação e a justificativa em um formato JSON: "
                '{"classification": "tipo", "message": "justificativa"}'
                "\n\nConteúdo: " + text
            )}
        ]

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo", # Ou "gpt-4", dependendo do seu acesso/preferência
            messages=prompt_messages,
            response_format={ "type": "json_object" } # Garante resposta em JSON para OpenAI (requer gpt-3.5-turbo-1106 ou superior)
        )

        response_content = response.choices[0].message.content
        result = json.loads(response_content)

        if "classification" in result and "message" in result:
            return result
        else:
            raise ValueError("Formato JSON inesperado da resposta da OpenAI.")

    except Exception as e:
        print(f"Erro ao analisar com OpenAI: {e}")
        return {"classification": "error", "message": f"Erro na análise com OpenAI: {e}"}


def analyze_content_with_llm(text: str, preferred_llm: str = "gemini") -> dict:
    """
    Função principal para analisar conteúdo usando um LLM selecionado.
    """
    if preferred_llm.lower() == "gemini":
        print("INFO: Usando Gemini para análise.")
        return analyze_with_gemini(text)
    elif preferred_llm.lower() == "openai":
        print("INFO: Usando OpenAI para análise.")
        return analyze_with_openai(text)
    else:
        return {"classification": "error", "message": "LLM não suportado. Escolha 'gemini' ou 'openai'."}

# Exemplo de uso (apenas para teste direto do arquivo)
if __name__ == "__main__":
    # Carrega as variáveis de ambiente para este script de teste também
    load_dotenv()
    test_text_fake = "Pesquisadores descobriram que beber água magnetizada cura todas as doenças."
    test_text_true = "A Terra é o terceiro planeta do sistema solar."
    test_text_satire = "Cientistas descobrem que o humor do seu gato afeta as marés."
    test_text_opinion = "A inteligência artificial é a tecnologia mais promissora do século XXI."

    print("\n--- Testando com Gemini ---")
    print(analyze_content_with_llm(test_text_fake, preferred_llm="gemini"))
    print(analyze_content_with_llm(test_text_true, preferred_llm="gemini"))
    print(analyze_content_with_llm(test_text_satire, preferred_llm="gemini"))
    print(analyze_content_with_llm(test_text_opinion, preferred_llm="gemini"))

    print("\n--- Testando com OpenAI ---")
    print(analyze_content_with_llm(test_text_fake, preferred_llm="openai"))
    print(analyze_content_with_llm(test_text_true, preferred_llm="openai"))
    print(analyze_content_with_llm(test_text_satire, preferred_llm="openai"))
    print(analyze_content_with_llm(test_text_opinion, preferred_llm="openai"))