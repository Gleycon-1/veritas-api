from typing import Optional, Any, Dict
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai
from openai import OpenAI
import anthropic # Importa a biblioteca do Claude AI (precisa estar instalada)
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

# Claude AI
claude_client = None
if settings.CLAUDE_API_KEY: # Só inicializa se a chave estiver presente no .env
    claude_client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)
    print("DEBUG: Claude AI API configurada.")
else:
    print("WARNING: CLAUDE_API_KEY não configurada no .env! Claude AI será ignorado no fallback.")

# DeepSeek AI (usa o cliente OpenAI com base_url customizada)
deepseek_client = None
if settings.DEEPSEEK_API_KEY and settings.DEEPSEEK_BASE_URL:
    deepseek_client = OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=settings.DEEPSEEK_BASE_URL)
    print("DEBUG: DeepSeek AI API configurada.")
else:
    print("WARNING: DEEPSEEK_API_KEY ou DEEPSEEK_BASE_URL não configurados no .env! DeepSeek AI será ignorado no fallback.")

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
    print("WARNING: HUGGINGFACE_API_KEY ou HUGGINGFACE_MODEL_ID não configurados no .env! Hugging Face será ignorado no fallback.")

# Função auxiliar para extrair JSON de strings (útil para LLMs que podem retornar Markdown)
def extract_json_from_text(text: str) -> dict:
    """
    Tenta extrair um objeto JSON de uma string, mesmo que ele esteja
    envolto em blocos de código markdown (```json ... ```).
    """
    # Tenta encontrar um bloco de código JSON em markdown
    match = re.search(r"```json\s*\n(.*)\n\s*```", text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # Se não encontrar markdown, tenta o texto direto como JSON
        json_str = text.strip()
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        print(f"ERRO: Não foi possível decodificar JSON de: {json_str[:500]}...") # Log os primeiros 500 chars para depuração
        raise # Levanta o erro para ser capturado pela função principal

# Função principal para análise de conteúdo com LLM (ASSÍNCROMA)
async def analyze_content_with_llm(content: str, preferred_llm: str = "gemini") -> dict:
    prompt = f"""
    Sua tarefa é analisar o seguinte "Conteúdo a ser analisado" e classificá-lo rigorosamente usando APENAS UMA das categorias listadas abaixo. Baseie sua classificação EXCLUSIVAMENTE nas informações contidas no "Conteúdo a ser analisado" e nas definições fornecidas. Não adicione ressalvas ou interpretações adicionais que não sejam explicitamente solicitadas.

    **Categorias e suas Definições RIGOROSAS:**
    - 'fake_news': O "Conteúdo a ser analisado" contém informações comprovadamente falsas ou enganosas, criadas com intenção de desinformar ou manipular.
    - 'verdadeiro': O "Conteúdo a ser analisado" apresenta fatos verificáveis e precisos, baseados em evidências ou dados amplamente aceitos e confirmados (ex: dados históricos, geográficos, científicos consolidados).
    - 'sátira': O "Conteúdo a ser analisado" é humorístico, irônico, utiliza o exagero, a paródia ou o absurdo **com uma intenção CLARA e EVIDENTE de divertir, criticar ou comentar de forma cômica.**
    - 'opinião': O "Conteúdo a ser analisado" expressa um ponto de vista pessoal, uma crença ou interpretação. Geralmente contém termos como 'eu acho', 'na minha opinião'. Ele se declara como subjetivo.
    - 'tendencioso': O "Conteúdo a ser analisado" apresenta um viés claro, favorecendo ou desfavorecendo um lado, ideia ou grupo. Ele pode omitir informações relevantes do outro lado, usar linguagem carregada ou apresentar fatos de forma seletiva para tentar influenciar o leitor, mas tentando parecer objetivo ou neutro.
    - 'indefinido': O "Conteúdo a ser analisado" é uma coleção de palavras ou frases semanticamente incoerentes, fragmentadas, sem qualquer estrutura lógica ou narrativa discernível. **Não é possível inferir qualquer intenção comunicativa clara ou propósito (seja humorístico, crítico, informativo, ou de expressar uma opinião). É simplesmente sem sentido.**

    Sua resposta deve ser um objeto JSON contendo APENAS a 'classification' (uma das categorias acima) e uma 'message' (justificativa detalhada em **português**, explicando os pontos que levaram a essa conclusão e fornecendo exemplos do texto ou contexto relevante, se aplicável). A justificativa deve ser informativa e clara.

    Exemplo de formato de resposta:
    ```json
    {{
        "classification": "verdadeiro",
        "message": "O conteúdo é verdadeiro porque as informações sobre a população de São Paulo e sua posição no hemisfério sul são corroboradas por dados oficiais do Censo de 2022 do IBGE, que é uma fonte de dados demográficos amplamente reconhecida."
    }}
    ```

    Conteúdo a ser analisado:
    "{content}"
    """

    llm_options = []
    # Ordem de preferência para fallback: preferred_llm > DeepSeek > Gemini > OpenAI > Claude > Hugging Face
    
    # 1. Adiciona a LLM preferencial (passada como argumento ou padrão 'gemini')
    # Se o usuário especificou 'deepseek' como preferred_llm, ele será o primeiro.
    if preferred_llm.lower() == "deepseek" and deepseek_client: # DEEPSEEK AGORA É O PREFERENCIAL SE SOLICITADO
        llm_options.append("deepseek")
    elif preferred_llm.lower() == "gemini" and settings.GEMINI_API_KEY:
        llm_options.append("gemini")
    elif preferred_llm.lower() == "openai" and openai_client:
        llm_options.append("openai")
    elif preferred_llm.lower() == "claude" and claude_client:
        llm_options.append("claude")
    elif preferred_llm.lower() == "huggingface" and hf_client:
        llm_options.append("huggingface")
    
    # 2. Adiciona as outras LLMs disponíveis como fallback, na ordem definida (se ainda não foram adicionadas)
    # Esta seção garante que, se a LLM preferencial não estiver disponível, as outras serão tentadas nesta ordem.
    # A ordem aqui reflete a sua preferência geral.
    if "deepseek" not in llm_options and deepseek_client:
        llm_options.append("deepseek")
    if "gemini" not in llm_options and settings.GEMINI_API_KEY:
        llm_options.append("gemini")
    if "openai" not in llm_options and openai_client:
        llm_options.append("openai")
    if "claude" not in llm_options and claude_client:
        llm_options.append("claude")
    if "huggingface" not in llm_options and hf_client:
        llm_options.append("huggingface")


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
                    # Usando run_in_executor para evitar problemas de loop de eventos com a API do Gemini
                    response_object = await asyncio.get_running_loop().run_in_executor(
                        executor,
                        lambda: model.generate_content(
                            prompt,
                            generation_config={"response_mime_type": "application/json"}
                        )
                    )
                    response_text = response_object.text
                    return json.loads(response_text)
                except Exception as e:
                    print(f"WARNING: Gemini falhou ao gerar JSON diretamente: {e}. Tentando sem forçar e extraindo JSON.")
                    response_object = await asyncio.get_running_loop().run_in_executor(
                        executor,
                        lambda: model.generate_content(prompt)
                    )
                    response_text = response_object.text
                    return extract_json_from_text(response_text)

            elif llm_to_use == "openai":
                if not openai_client: raise ValueError("OpenAI client not initialized, check API key in .env.")
                print("INFO: Tentando análise com OpenAI...")
                # O cliente OpenAI é assíncrono e geralmente não precisa de run_in_executor
                chat_completion = await openai_client.chat.completions.create(
                    model="gpt-3.5-turbo", # ou "gpt-4" se tiver acesso
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"} # Solicita formato JSON diretamente
                )
                response_text = chat_completion.choices[0].message.content
                return json.loads(response_text) # Já deve vir como JSON válido

            elif llm_to_use == "claude":
                if not claude_client: raise ValueError("Claude AI client not initialized, check API key in .env.")
                print("INFO: Tentando análise com Claude AI...")
                # O cliente Claude é assíncrono e geralmente não precisa de run_in_executor
                claude_response = await claude_client.messages.create(
                    model="claude-3-haiku-20240307", # Use o modelo Claude de sua preferência (haiku, sonnet, opus)
                    max_tokens=500, # Ajuste conforme necessário
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    # Claude não tem um response_format direto como OpenAI/Gemini,
                    # então vamos confiar no prompt para JSON e extrair
                )
                response_text = claude_response.content[0].text # A resposta de Claude é uma lista de content blocks
                return extract_json_from_text(response_text)

            elif llm_to_use == "deepseek": # AGORA É O PREFERENCIAL SE SOLICITADO
                if not deepseek_client: raise ValueError("DeepSeek AI client not initialized, check API key/base URL in .env.")
                print("INFO: Tentando análise com DeepSeek AI...")
                # DeepSeek usa a API compatível com OpenAI, então a chamada é similar
                deepseek_completion = await deepseek_client.chat.completions.create(
                    model="deepseek-chat", # Use o modelo DeepSeek de sua preferência (deepseek-chat, deepseek-coder)
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"} # Solicita formato JSON diretamente
                )
                response_text = deepseek_completion.choices[0].message.content
                return json.loads(response_text)

            elif llm_to_use == "huggingface":
                if not hf_client: raise ValueError("Hugging Face client not initialized, check API key/model ID in .env.")
                print(f"INFO: Tentando análise com Hugging Face (modelo: {settings.HUGGINGFACE_MODEL_ID})....")
                hf_formatted_prompt = f"<s>[INST] {prompt} [/INST]"
                
                # A função hf_client.text_generation é síncrona, então precisa de run_in_executor
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

        except Exception as e:
            last_error_message = f"Erro ao usar {llm_to_use}: {str(e)}"
            print(f"ERRO: {last_error_message}. Detalhes:")
            traceback.print_exc() # Imprime o traceback completo do erro para depuração
            continue # Continua para a próxima LLM na lista de opções

    # Se o loop terminar, significa que todas as LLMs configuradas e tentadas falharam
    return {
        "classification": "error",
        "message": f"Todas as LLMs configuradas e tentadas falharam na análise. Último erro registrado: {last_error_message}"
    }

# --- Wrapper Síncrono para Celery ---
# O executor deve ser definido uma vez globalmente para ser reutilizado.
executor = ThreadPoolExecutor(max_workers=5) 

def analyze_content_sync(content: str, preferred_llm: str) -> Dict[str, Any]:
    """
    Wrapper síncrono para executar a função assíncrona analyze_content_with_llm
    dentro de um contexto de tarefa do Celery.
    """
    print(f"INFO: [LLM Sync Wrapper] Iniciando análise síncrona para Celery com LLM: {preferred_llm}")
    try:
        # Usando asyncio.run() para criar e gerenciar um novo loop de eventos
        # para a corrotina dentro da thread do Celery worker.
        llm_result = asyncio.run(
            asyncio.wait_for(
                analyze_content_with_llm(content, preferred_llm), timeout=90 # Mantenha 90s ou ajuste se necessário
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
        traceback.print_exc() # Imprime o traceback completo do erro para depuração
        return {"classification": "error", "message": error_message}
