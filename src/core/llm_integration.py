from typing import Optional, Any, Dict
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai
from openai import OpenAI
from huggingface_hub import InferenceClient
import json
import re
import traceback

from src.core.config import settings

# --- Configurações das LLMs ---

# Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    print("DEBUG: Gemini API configurada.")
else:
    print("WARNING: GEMINI_API_KEY não configurada no .env!")

# OpenAI
openai_client = None
if settings.OPENAI_API_KEY:
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    print("DEBUG: OpenAI API configurada.")
else:
    print("WARNING: OPENAI_API_KEY não configurada no .env!")

# Hugging Face
hf_client = None
if settings.HUGGINGFACE_API_KEY and settings.HUGGINGFACE_MODEL_ID:
    try:
        hf_client = InferenceClient(model=settings.HUGGINGFACE_MODEL_ID, token=settings.HUGGINGFACE_API_KEY)
        print(f"DEBUG: Hugging Face API configurada para o modelo: {settings.HUGGINGFACE_MODEL_ID}.")
    except Exception as e:
        print(f"ERROR: Falha ao inicializar o cliente Hugging Face: {e}. Verifique o modelo ou a chave.")
        hf_client = None # Garante que o cliente não será usado se a inicialização falhar
else:
    print("WARNING: HUGGINGFACE_API_KEY ou HUGGINGFACE_MODEL_ID não configurados no .env!")

# Função auxiliar para extrair JSON de strings (útil para LLMs que podem retornar Markdown)
def extract_json_from_text(text: str) -> dict:
    """
    Tenta extrair um objeto JSON de uma string, mesmo que ele esteja
    envolto em blocos de código markdown (```json ... ```).
    """
    match = re.search(r"```json\s*\n(.*)\n\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        json_str = text.strip()
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        print(f"ERRO: Não foi possível decodificar JSON de: {json_str[:500]}...")
        raise

# Função principal para análise de conteúdo com LLM (ASSÍNCROMA)
async def analyze_content_with_llm(content: str, preferred_llm: str = "gemini") -> dict:
    prompt = f"""
    Sua tarefa é analisar o seguinte "Conteúdo a ser analisado" e classificá-lo rigorosamente usando APENAS UMA das categorias listadas abaixo. Baseie sua classificação EXCLUSIVAMENTE nas informações contidas no "Conteúdo a ser analisado" e nas definições fornecidas. Não adicione ressalvas ou interpretações adicionais que não sejam explicitamente solicitadas.

    **Categorias e suas Definições RIGOROSAS:**
    - 'fake_news': O "Conteúdo a ser analisado" contém informações comprovadamente falsas ou enganosas, criadas com intenção de desinformar ou manipular.
    - 'verdadeiro': O "Conteúdo a ser analisado" apresenta fatos verificáveis e precisos, baseados em evidências ou dados amplamente aceitos e confirmados (ex: dados históricos, geográficos, científicos consolidados).
    - 'sátira': O "Conteúdo a ser analisado" é humorístico, irônico, utiliza exagero ou paródia. Sua intenção NÃO é enganar, mas divertir ou criticar de forma cômica.
    - 'opinião': O "Conteúdo a ser analisado" expressa um ponto de vista pessoal, uma crença ou interpretação. Geralmente contém termos como 'eu acho', 'na minha opinião'. Ele se declara como subjetivo.
    - 'parcial': O "Conteúdo a ser analisado" demonstra um viés claro, favorecendo ou desfavorecendo um lado, ideia ou grupo. Pode omitir informações relevantes do outro lado, usar linguagem carregada ou apresentar fatos de forma seletiva para influenciar o leitor, mas tentando parecer objetivo.
    - 'indefinido': O "Conteúdo a ser analisado" é ambíguo, carece de contexto, é sem sentido ou contém informações insuficientes para uma classificação clara em qualquer das outras categorias.

    Sua resposta deve ser um objeto JSON contendo APENAS a 'classification' (uma das categorias acima) e uma 'message' (justificativa concisa de **por que o conteúdo se encaixa nessa classificação**, sem questionar ou adicionar informações externas).

    Exemplo de formato de resposta:
    ```json
    {{
        "classification": "verdadeiro",
        "message": "O conteúdo é factual e amplamente verificável, informando sobre..."
    }}
    ```

    Conteúdo a ser analisado:
    "{content}"
    """

    llm_options = []
    # Ordem de preferência para fallback: preferencial > Gemini > Hugging Face > OpenAI
    
    # 1. Adiciona a LLM preferencial primeiro, se configurada e disponível
    if preferred_llm.lower() == "gemini" and settings.GEMINI_API_KEY:
        llm_options.append("gemini")
    elif preferred_llm.lower() == "huggingface" and hf_client:
        llm_options.append("huggingface")
    elif preferred_llm.lower() == "openai" and openai_client:
        llm_options.append("openai")
    
    # 2. Adiciona as outras LLMs disponíveis como fallback, na ordem definida
    if "gemini" not in llm_options and settings.GEMINI_API_KEY:
        llm_options.append("gemini")
    if "huggingface" not in llm_options and hf_client:
        llm_options.append("huggingface")
    if "openai" not in llm_options and settings.OPENAI_API_KEY:
        llm_options.append("openai")

    if not llm_options:
        return {
            "classification": "error",
            "message": "Nenhuma LLM configurada ou disponível para análise. Verifique suas chaves de API no .env."
        }

    last_error_message = ""
    for llm_to_use in llm_options:
        try:
            if llm_to_use == "gemini":
                if not settings.GEMINI_API_KEY: raise ValueError("Gemini API key not configured in .env.")
                print("INFO: Tentando análise com Google Gemini...")
                model = genai.GenerativeModel('gemini-1.5-flash')
                try:
                    response = await model.generate_content_async(
                        prompt,
                        generation_config={"response_mime_type": "application/json"}
                    )
                    response_text = response.text
                    return json.loads(response_text)
                except Exception as e:
                    print(f"WARNING: Gemini falhou ao gerar JSON diretamente: {e}. Tentando sem forçar e extraindo JSON.")
                    response = await model.generate_content_async(prompt)
                    response_text = response.text
                    return extract_json_from_text(response_text)

            elif llm_to_use == "huggingface":
                if not hf_client: raise ValueError("Hugging Face client not initialized, check API key/model ID in .env.")
                print(f"INFO: Tentando análise com Hugging Face (modelo: {settings.HUGGINGFACE_MODEL_ID})....")
                hf_formatted_prompt = f"<s>[INST] {prompt} [/INST]"
                
                response_text = await asyncio.get_running_loop().run_in_executor(
                    executor,
                    lambda: hf_client.text_generation(
                        prompt=hf_formatted_prompt, 
                        max_new_tokens=500,
                        do_sample=False, 
                        return_full_text=False
                    )
                )
                return extract_json_from_text(response_text)

            elif llm_to_use == "openai":
                if not openai_client: raise ValueError("OpenAI client not initialized, check API key in .env.")
                print("INFO: Tentando análise com OpenAI...")
                chat_completion = await openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                response_text = chat_completion.choices[0].message.content
                return json.loads(response_text)

        except Exception as e:
            last_error_message = f"Erro ao usar {llm_to_use}: {str(e)}"
            print(f"ERRO: {last_error_message}. Detalhes:")
            traceback.print_exc()
            continue

    return {
        "classification": "error",
        "message": f"Todas as LLMs configuradas e tentadas falharam na análise. Último erro registrado: {last_error_message}"
    }

# --- Wrapper Síncrono para Celery ---
executor = ThreadPoolExecutor(max_workers=5) 

def analyze_content_sync(content: str, preferred_llm: str) -> Dict[str, Any]:
    """
    Wrapper síncrono para executar a função assíncrona analyze_content_with_llm
    dentro de um contexto de tarefa do Celery.
    """
    print(f"INFO: [LLM Sync Wrapper] Iniciando análise síncrona para Celery com LLM: {preferred_llm}")
    try:
        llm_result = asyncio.run(
            asyncio.wait_for(
                analyze_content_with_llm(content, preferred_llm), timeout=90
            )
        )
        
        print(f"DEBUG: [LLM Sync Wrapper] Resultado da LLM: {llm_result}")
        return llm_result

    except asyncio.TimeoutError:
        error_message = f"Erro na análise da LLM ({preferred_llm}): A inferência excedeu o tempo limite ({90} segundos)."
        print(f"ERRO: {error_message}")
        return {"classification": "error", "message": error_message}
    except Exception as e:
        error_message = f"Erro na análise da LLM ({preferred_llm}): {e}"
        print(f"ERRO: {error_message}")
        traceback.print_exc()
        return {"classification": "error", "message": error_message}