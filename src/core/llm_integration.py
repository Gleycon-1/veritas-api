import os
import asyncio
import json
import re
import traceback
import logging
from typing import Optional, Any, Dict, List
from concurrent.futures import ThreadPoolExecutor

import google.generativeai as genai
from openai import OpenAI
import anthropic
from huggingface_hub import InferenceClient

from src.core.config import settings
from src.core.Google Search_tool import GoogleSearchTool # Importa a ferramenta real

# Configura o logger
logger = logging.getLogger(__name__)

# --- Configurações das LLMs ---

# Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    logger.debug("Gemini API configurada.")
else:
    logger.warning("GEMINI_API_KEY não configurada no .env!")

# OpenAI
openai_client = None
if settings.OPENAI_API_KEY:
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    logger.debug("OpenAI API configurada.")
else:
    logger.warning("OPENAI_API_KEY não configurada no .env!")

# Claude AI
claude_client = None
if settings.CLAUDE_API_KEY:
    claude_client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)
    logger.debug("Claude AI API configurada.")
else:
    logger.warning("CLAUDE_API_KEY não configurada no .env! Claude AI será ignorado no fallback.")

# DeepSeek AI (usa o cliente OpenAI com base_url customizada)
deepseek_client = None
if settings.DEEPSEEK_API_KEY and settings.DEEPSEEK_BASE_URL:
    deepseek_client = OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=settings.DEEPSEEK_BASE_URL)
    logger.debug("DeepSeek AI API configurada.")
else:
    logger.warning("DEEPSEEK_API_KEY ou DEEPSEEK_BASE_URL não configurados no .env! DeepSeek AI será ignorado no fallback.")

# Hugging Face
hf_client = None
if settings.HUGGINGFACE_API_KEY and settings.HUGGINGFACE_MODEL_ID:
    try:
        hf_client = InferenceClient(model=settings.HUGGINGFACE_MODEL_ID, token=settings.HUGGINGFACE_API_KEY)
        logger.debug(f"Hugging Face API configurada para o modelo: {settings.HUGGINGFACE_MODEL_ID}.")
    except Exception as e:
        logger.error(f"Falha ao inicializar o cliente Hugging Face: {e}. Verifique o modelo ou a chave.")
        hf_client = None
else:
    logger.warning("HUGGINGFACE_API_KEY ou HUGGINGFACE_MODEL_ID não configurados no .env! Hugging Face será ignorado no fallback.")

# --- Inicialização do ThreadPoolExecutor ---
executor = ThreadPoolExecutor(max_workers=5) # Ajuste o número de workers conforme a necessidade

# --- Inicialização da Google Search Tool ---
Google Search_tool = None
if settings.Google Search_API_KEY and settings.Google Search_ENGINE_ID:
    try:
        Google Search_tool = GoogleSearchTool(
            api_key=settings.Google Search_API_KEY,
            custom_search_engine_id=settings.Google Search_ENGINE_ID
        )
        logger.debug("Google Search Tool configurada com sucesso.")
    except ValueError as e:
        logger.error(f"Erro ao inicializar Google Search Tool: {e}. Verifique as chaves no .env.")
        Google Search_tool = None
else:
    logger.warning("Google Search_API_KEY ou Google Search_ENGINE_ID não configurados no .env! A busca externa será desabilitada.")


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
        logger.error(f"Não foi possível decodificar JSON de: {json_str[:500]}...")
        raise

# Lista para armazenar as fontes usadas, acessível globalmente pela função de formatação
sources_list: List[str] = []

# Função para formatar os resultados da busca para o prompt da LLM
def format_search_results(results: List[Dict[str, Any]]) -> str:
    """
    Formata os resultados da busca para serem incluídos no prompt da LLM.
    """
    formatted_output = []
    if not results:
        return "Nenhum resultado de busca relevante encontrado."

    for i, result_set in enumerate(results):
        query = result_set.get("query", "Consulta desconhecida")
        snippets = []
        for j, item in enumerate(result_set.get("results", [])):
            title = item.get("source_title", "Sem título")
            snippet = item.get("snippet", "Sem snippet.")
            url = item.get("url", "#")
            snippets.append(f"  {j+1}. Título: {title}\n    Snippet: {snippet}\n    URL: {url}")
            
            # Adicionar a URL à lista de fontes global, se ela não estiver lá
            if url and url != "#" and url not in sources_list: 
                global sources_list 
                sources_list.append(url)
        
        if snippets:
            formatted_output.append(f"Resultados para a consulta '{query}':\n" + "\n".join(snippets))
        else:
            formatted_output.append(f"Resultados para a consulta '{query}': Nenhum snippet encontrado.")

    return "\n\n".join(formatted_output)


# Função principal para análise de conteúdo com LLM (ASSÍNCROMA)
async def analyze_content_with_llm(content: str, preferred_llm: str = "gemini") -> dict:
    global sources_list 
    sources_list = [] # Limpa a lista de fontes para cada nova análise

    search_results_context = ""
    queries_to_execute: List[str] = []
    query_gen_error: Optional[str] = None

    try:
        # FASE 1: LLM gera as consultas de busca usando a ferramenta `Google Search`
        logger.info("Solicitando à LLM que gere consultas de busca para RAG...")
        
        # A ferramenta Google Search é exposta globalmente pelo ambiente.
        # Precisamos definir a especificação da ferramenta para que a LLM saiba como usá-la.
        tool_definitions = [
            {
                "name": "Google Search",
                "description": "Uma ferramenta para realizar buscas na internet e obter informações.",
                "function_declarations": [
                    {
                        "name": "search",
                        "description": "Executa uma ou mais consultas de busca na internet. Retorna uma lista de resultados, cada um contendo a consulta original e os snippets encontrados.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "queries": {
                                    "type": "ARRAY",
                                    "items": {"type": "STRING"},
                                    "description": "Uma lista de strings de consulta de busca."
                                }
                            },
                            "required": ["queries"]
                        }
                    }
                ]
            }
        ]

        # Inicia a conversa para a geração de queries
        chat_history_for_queries = [
            {"role": "user", "parts": [
                f"""
                Você é um especialista em verificação de fatos. Dada a "Notícia para Análise", sua tarefa é identificar as principais afirmações factuais e gerar até 3 **consultas de busca na internet** altamente relevantes para verificar a veracidade dessas afirmações ou para obter contexto adicional.

                Use a ferramenta `Google Search` para isso. Sua resposta DEVE ser uma chamada à ferramenta, formatada EXATAMENTE como um JSON com a chave "queries" contendo uma lista de strings. Nenhuma outra conversa ou texto deve ser incluído na sua resposta, apenas a chamada à ferramenta.

                Exemplo de saída:
                ```json
                {{
                  "queries": ["fato 1 verificação", "informação crucial tópico 2"]
                }}
                ```

                Notícia para Análise:
                "{content}"
                """
            ]}
        ]

        # Tenta com LLMs que suportam tool calling para gerar as queries
        query_gen_llm_options = []
        if settings.GEMINI_API_KEY: query_gen_llm_options.append("gemini")
        if settings.OPENAI_API_KEY: query_gen_llm_options.append("openai")
        if settings.DEEPSEEK_API_KEY and settings.DEEPSEEK_BASE_URL: query_gen_llm_options.append("deepseek")

        for q_llm in query_gen_llm_options:
            try:
                current_llm_for_query_gen = q_llm
                if q_llm == "gemini":
                    # Certifique-se de que o modelo Gemini é configurado para responder com tool_calls
                    query_model = genai.GenerativeModel('gemini-1.5-flash', tools=tool_definitions)
                    query_response_obj = await asyncio.get_running_loop().run_in_executor(
                        executor,
                        lambda: query_model.generate_content(chat_history_for_queries, tools=tool_definitions, tool_choice={"function": "search"})
                    )
                    
                    # Processa a resposta do Gemini para extrair a chamada da ferramenta
                    if query_response_obj.candidates and query_response_obj.candidates[0].content.parts:
                        part = query_response_obj.candidates[0].content.parts[0]
                        if hasattr(part, 'function_call') and part.function_call and part.function_call.name == "search":
                            queries_to_execute = part.function_call.args.get("queries", [])
                            logger.info(f"Queries geradas por {q_llm}: {queries_to_execute}")
                            break # Queries geradas com sucesso
                        else:
                            logger.warning(f"{q_llm} não gerou chamada de ferramenta 'search' ou formato inesperado. Parte: {part}")
                            query_gen_error = f"{q_llm} não gerou chamada de ferramenta 'search' esperada."
                    else:
                        logger.warning(f"{q_llm} response structure not as expected. {query_response_obj.text}")
                        query_gen_error = f"{q_llm} não gerou resposta esperada."

                elif q_llm == "openai" or q_llm == "deepseek":
                    client_to_use = openai_client if q_llm == "openai" else deepseek_client
                    if not client_to_use: raise ValueError(f"{q_llm} client not initialized.")

                    chat_completion = await client_to_use.chat.completions.create(
                        model="gpt-3.5-turbo" if q_llm == "openai" else "deepseek-chat", # Escolha o modelo apropriado
                        messages=[{"role": "user", "content": chat_history_for_queries[0]["parts"][0]["text"]}],
                        tools=[
                            {
                                "type": "function",
                                "function": {
                                    "name": "search",
                                    "description": "Executa uma ou mais consultas de busca na internet.",
                                    "parameters": {
                                        "type": "object",
                                        "properties": {
                                            "queries": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                                "description": "Uma lista de strings de consulta de busca."
                                            }
                                        },
                                        "required": ["queries"]
                                    }
                                }
                            }
                        ],
                        tool_choice={"type": "function", "function": {"name": "search"}} # Força o uso da ferramenta search
                    )
                    tool_calls = chat_completion.choices[0].message.tool_calls
                    if tool_calls and tool_calls[0].function.name == "search":
                        queries_to_execute = json.loads(tool_calls[0].function.arguments).get("queries", [])
                        logger.info(f"Queries geradas por {q_llm}: {queries_to_execute}")
                        break # Queries geradas com sucesso
                    else:
                        logger.warning(f"{q_llm} não gerou chamada de ferramenta 'search'.")
                        query_gen_error = f"{q_llm} não gerou chamada de ferramenta 'search' esperada."
                
            except Exception as e:
                query_gen_error = f"Erro ao gerar queries com {q_llm}: {str(e)}"
                logger.warning(f"{query_gen_error}")
                traceback.print_exc()
                queries_to_execute = [] # Garante que queries_to_execute é redefinido em caso de erro

        if not queries_to_execute:
            logger.warning("Nenhuma consulta de busca foi gerada ou as LLMs de geração de consulta falharam. Prosseguindo sem contexto de busca.")
            # Se não houver queries, a search_results_context permanece vazia
        else:
            # FASE 2: Executa as consultas de busca usando a ferramenta real `Google Search`
            if Google Search_tool: # Verifica se a ferramenta foi inicializada com sucesso
                logger.info(f"Executando busca com Google Search para queries: {queries_to_execute}")
                
                # Aqui, você invoca a ferramenta `GoogleSearchTool` real.
                raw_search_results = await asyncio.get_running_loop().run_in_executor(
                    executor,
                    lambda: Google Search_tool.search(queries=queries_to_execute)
                )
                logger.info(f"Resultados brutos da busca recebidos.")
                search_results_context = format_search_results(raw_search_results)
                logger.info("Contexto de busca formatado para LLM.")
            else:
                logger.warning("Google Search Tool não está configurada. Pulando a execução da busca.")
                search_results_context = "A ferramenta de busca externa não está configurada, então a análise não pôde usar informações da internet."

    except Exception as e:
        logger.error(f"Erro durante a fase de geração/execução de busca: {e}")
        traceback.print_exc()
        search_results_context = "Erro ao buscar informações externas. A análise pode ser limitada."
        # Ainda tenta analisar o conteúdo, mesmo que sem busca externa.

    # FASE 3: LLM gera a análise final usando o conteúdo original e o contexto de busca (RAG)
    logger.info("Solicitando à LLM que analise o conteúdo com o contexto de busca...")
    
    # Prompt para a LLM fazer a verificação de fatos e classificação
    rag_prompt = f"""
    Você é a **Veritas API**, um sistema avançado de verificação de fatos. Sua tarefa é analisar o "Conteúdo para Análise" e, usando o "Contexto de Busca" fornecido, classificá-lo em uma das seguintes categorias.

    Sua resposta DEVE ser um objeto JSON com as chaves `classification`, `color` e `justification`.

    **Categorias e Cores:**
    * 🟢 **Verde**: `verdadeiro` - Conteúdo factual, verificável e preciso, baseado em evidências ou dados confirmados.
    * 🔴 **Vermelho**: `fake_news` - Conteúdo comprovadamente falso ou enganoso, criado para manipular.
    * ⚪ **Branco/Cinzento**: `sátira` - Conteúdo humorístico, irônico ou que utiliza o exagero e a paródia. Não tem intenção de enganar, mas de divertir ou criticar de forma cômica.
    * 🔵 **Azul**: `opinião` - Expressão de um ponto de vista pessoal, crença ou interpretação. Geralmente se declara como tal e não busca disfarçar sua natureza subjetiva.
    * 🟠 **Laranja**: `tendencioso` - Conteúdo que apresenta um viés claro, favorecendo ou desfavorecendo um lado, uma ideia ou um grupo. Pode usar linguagem carregada e tenta parecer objetivo ou neutro, mas não é.
    * ⚫ **Preto**: `indefinido` - Conteúdo ambíguo, sem contexto, com informações insuficientes para uma classificação clara, ou quando ocorre um erro técnico na análise.

    **Instruções para Classificação:**
    1.  Leia cuidadosamente o "Conteúdo para Análise".
    2.  Considere o "Contexto de Busca" como sua fonte primária de verdade externa. Compare as afirmações do conteúdo com as informações do contexto.
    3.  Se o contexto refutar claramente uma afirmação chave, considere `fake_news`.
    4.  Se o contexto corroborar fortemente as afirmações, considere `verdadeiro`.
    5.  Se o conteúdo parecer humorístico e não pretender enganar, é `sátira`.
    6.  Se for um ponto de vista pessoal e não factual, é `opinião`.
    7.  Se apresentar apenas um lado da história ou usar linguagem carregada para influenciar, é `parcial`.
    8.  Se, mesmo com o contexto, ainda houver ambiguidade ou falta de informação conclusiva, é `indefinido`.
    9.  Forneça uma `justification` clara e concisa, mencionando fatos do contexto de busca quando aplicável.

    ---
    Conteúdo para Análise:
    "{content}"

    ---
    Contexto de Busca (informações relevantes da internet):
    "{search_results_context}"

    ---
    Sua resposta JSON:
    """

    llm_response = {"classification": "indefinido", "color": "⚫", "justification": "Não foi possível realizar a análise completa devido a um erro interno ou falta de contexto."}
    
    # LLMs para a fase final de análise (priorize as que você tem acesso e que performam bem)
    analysis_llm_options = [preferred_llm] # Começa com a preferida
    # Adicione outras LLMs na ordem de preferência para fallback, se a primeira falhar
    if "gemini" not in analysis_llm_options and settings.GEMINI_API_KEY: analysis_llm_options.append("gemini")
    if "openai" not in analysis_llm_options and settings.OPENAI_API_KEY: analysis_llm_options.append("openai")
    if "deepseek" not in analysis_llm_options and settings.DEEPSEEK_API_KEY: analysis_llm_options.append("deepseek")
    if "claude" not in analysis_llm_options and settings.CLAUDE_API_KEY: analysis_llm_options.append("claude")
    if "huggingface" not in analysis_llm_options and settings.HUGGINGFACE_API_KEY: analysis_llm_options.append("huggingface")


    for current_llm in analysis_llm_options:
        try:
            logger.info(f"Tentando análise final com LLM: {current_llm}")
            
            if current_llm == "gemini" and settings.GEMINI_API_KEY:
                model = genai.GenerativeModel('gemini-1.5-pro' if 'pro' in preferred_llm else 'gemini-1.5-flash') # Use o modelo apropriado
                response_obj = await asyncio.get_running_loop().run_in_executor(
                    executor,
                    lambda: model.generate_content(rag_prompt)
                )
                response_text = response_obj.text
            
            elif current_llm == "openai" and openai_client:
                chat_completion = await openai_client.chat.completions.create(
                    model="gpt-4-turbo" if 'gpt-4' in preferred_llm else "gpt-3.5-turbo",
                    messages=[{"role": "user", "content": rag_prompt}]
                )
                response_text = chat_completion.choices[0].message.content
            
            elif current_llm == "claude" and claude_client:
                response = await claude_client.messages.create(
                    model="claude-3-opus-20240229" if 'opus' in preferred_llm else "claude-3-sonnet-20240229", 
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": rag_prompt}
                    ]
                )
                response_text = response.content[0].text 
            
            elif current_llm == "deepseek" and deepseek_client:
                chat_completion = await deepseek_client.chat.completions.create(
                    model="deepseek-chat", 
                    messages=[{"role": "user", "content": rag_prompt}]
                )
                response_text = chat_completion.choices[0].message.content

            elif current_llm == "huggingface" and hf_client:
                # Hugging Face InferenceClient pode ser mais complexo para estruturar prompts conversacionais/JSON
                response_text = hf_client.text_generation(rag_prompt, max_new_tokens=1000)

            else:
                raise ValueError(f"LLM {current_llm} não configurada ou não suportada para análise final.")

            # Tenta extrair e validar o JSON da resposta da LLM
            parsed_response = extract_json_from_text(response_text)
            
            # Validação das chaves esperadas no JSON
            if all(key in parsed_response for key in ["classification", "color", "justification"]):
                llm_response = parsed_response
                logger.info(f"Análise final obtida com sucesso usando {current_llm}.")
                break 
            else:
                logger.warning(f"LLM {current_llm} retornou JSON inválido/incompleto. Response: {response_text[:500]}...")
        
        except Exception as e:
            logger.error(f"Falha na análise final com {current_llm}: {e}")
            traceback.print_exc()

    # Mapeamento final para garantir a cor correta
    color_map = {
        "verdadeiro": "🟢",
        "fake_news": "🔴",
        "sátira": "⚪",
        "opinião": "🔵",
        "tendencioso": "🟠",
        "indefinido": "⚫"
    }
    llm_response["color"] = color_map.get(llm_response["classification"], "⚫")
    
    # Adiciona as fontes utilizadas na resposta final
    llm_response["sources"] = sources_list 

    return llm_response

# Exemplo de uso (apenas para teste direto do script)
async def main():
    test_content_true = "A Terra é redonda e orbita o Sol. Isso é comprovado por séculos de observações científicas."
    test_content_false = "Vacinas causam autismo em crianças, é um fato comprovado pela ciência."
    test_content_opinion = "A pizza é a melhor comida do mundo e deve ser consumida diariamente."
    test_content_satire = "Cientistas descobrem que respirar causa envelhecimento, e o ar será proibido."
    test_content_partial = "O novo imposto só afeta os ricos, sendo uma medida justa para redistribuir a riqueza."
    
    print(f"\n--- Analisando: '{test_content_true}' ---")
    result_true = await analyze_content_with_llm(test_content_true)
    print(f"Resultado: {result_true}\n")

    print(f"\n--- Analisando: '{test_content_false}' ---")
    result_false = await analyze_content_with_llm(test_content_false)
    print(f"Resultado: {result_false}\n")

    print(f"\n--- Analisando: '{test_content_opinion}' ---")
    result_opinion = await analyze_content_with_llm(test_content_opinion)
    print(f"Resultado: {result_opinion}\n")

    print(f"\n--- Analisando: '{test_content_satire}' ---")
    result_satire = await analyze_content_with_llm(test_content_satire)
    print(f"Resultado: {result_satire}\n")
    
    print(f"\n--- Analisando: '{test_content_partial}' ---")
    result_partial = await analyze_content_with_llm(test_content_partial)
    print(f"Resultado: {result_partial}\n")

if __name__ == "__main__":
    # Para rodar este script independentemente (sem FastAPI), você precisará de um arquivo .env
    # com as chaves de API configuradas. Ex:
    # GEMINI_API_KEY="SUA_CHAVE_GEMINI"
    # OPENAI_API_KEY="SUA_CHAVE_OPENAI"
    # CLAUDE_API_KEY="SUA_CHAVE_CLAUDE"
    # DEEPSEEK_API_KEY="SUA_CHAVE_DEEPSEEK"
    # DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
    # HUGGINGFACE_API_KEY="SUA_CHAVE_HF"
    # HUGGINGFACE_MODEL_ID="google/flan-t5-large" # Exemplo, escolha um modelo de texto apropriado
    # Google Search_API_KEY="SUA_CHAVE_DE_API_DO_GOOGLE_CLOUD"
    # Google Search_ENGINE_ID="SEU_ID_DO_MECANISMO_DE_BUSCA_PROGRAMAVEL"
    
    # Configure logging para ver as mensagens de DEBUG/INFO/WARNING
    logging.basicConfig(level=logging.INFO) # Mude para logging.DEBUG para mais detalhes

    asyncio.run(main())