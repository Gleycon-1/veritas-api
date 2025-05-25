# src/core/llm_integration.py

import os
import google.generativeai as genai
from openai import OpenAI
import json
import re # Importa regex para extrair JSON de strings
import traceback # Para imprimir o traceback completo do erro

from src.core.config import settings

# Configurações para Gemini
# Certifica-se de que a API Key está configurada antes de prosseguir
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    print("DEBUG: Gemini API configurada.")
else:
    print("WARNING: GEMINI_API_KEY não configurada no .env!")

# Configurações para OpenAI
openai_client = None
if settings.OPENAI_API_KEY:
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    print("DEBUG: OpenAI API configurada.")
else:
    print("WARNING: OPENAI_API_KEY não configurada no .env!")

# Função auxiliar para extrair JSON de strings (útil para Gemini que pode retornar Markdown)
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
        # Se não encontrar markdown, assume que o texto é o JSON direto
        json_str = text.strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        print(f"ERRO: Não foi possível decodificar JSON de: {json_str[:200]}...") # Log os primeiros 200 chars
        raise # Levanta o erro para ser capturado pela função principal


# Função principal para análise de conteúdo com LLM
async def analyze_content_with_llm(content: str, preferred_llm: str = "gemini") -> dict:
    # --- PROMPT MELHORADO PARA CLAREZA NAS CLASSIFICAÇÕES ---
    prompt = f"""
    Analise cuidadosamente o seguinte conteúdo e classifique-o usando UMA das seguintes categorias. Seja rigoroso na distinção.

    **Categorias e suas Definições:**
    - 'fake_news': Conteúdo comprovadamente falso ou enganoso, criado para desinformar. Busca enganar ativamente.
    - 'verdadeiro': Conteúdo factual, verificável e preciso, baseado em evidências ou dados confirmados.
    - 'sátira': Conteúdo humorístico, irônico ou que utiliza o exagero e a paródia. **Não tem intenção de enganar**, mas sim de divertir ou criticar de forma cômica.
    - 'opinião': Expressão de um ponto de vista pessoal, crença ou interpretação. Geralmente usa termos como 'eu acho', 'na minha opinião', e não se apresenta como fato universal. **Não busca disfarçar sua natureza subjetiva.**
    - 'parcial': Conteúdo que apresenta um viés claro, favorecendo ou desfavorecendo um lado, uma ideia ou um grupo. Pode usar linguagem carregada, omitir informações relevantes do outro lado, ou apresentar fatos de forma seletiva para influenciar o leitor. **Tenta parecer objetivo ou neutro, mas não é.**
    - 'indefinido': Conteúdo que é ambíguo, sem contexto claro, ou que não pode ser classificado em nenhuma das outras categorias devido à sua falta de sentido ou clareza.

    Forneça a classificação e uma breve mensagem/justificativa em formato JSON.
    Seja conciso na justificativa, mas explique por que escolheu a categoria.

    Exemplo de formato de resposta:
    ```json
    {{
        "classification": "fake_news",
        "message": "A análise indica que o conteúdo contém informações comprovadamente falsas sobre..."
    }}
    ```

    Conteúdo a ser analisado:
    "{content}"
    """
    # --- FIM DO PROMPT MELHORADO ---

    llm_options = []
    # Define a ordem de tentativa das LLMs. A preferencial vem primeiro.
    if preferred_llm.lower() == "openai" and settings.OPENAI_API_KEY:
        llm_options.append("openai")
        if settings.GEMINI_API_KEY: # Adiciona Gemini como fallback se a chave existir
            llm_options.append("gemini")
    elif preferred_llm.lower() == "gemini" and settings.GEMINI_API_KEY:
        llm_options.append("gemini")
        if settings.OPENAI_API_KEY: # Adiciona OpenAI como fallback se a chave existir
            llm_options.append("openai")
    else: # Se a preferencial não foi definida ou sua chave está faltando, tenta o que estiver disponível
        if settings.GEMINI_API_KEY:
            llm_options.append("gemini")
        if settings.OPENAI_API_KEY:
            llm_options.append("openai")

    if not llm_options:
        return {
            "classification": "error",
            "message": "Nenhuma LLM configurada ou disponível para análise. Verifique suas chaves de API no .env."
        }

    last_error_message = ""
    for llm_to_use in llm_options:
        try:
            if llm_to_use == "openai":
                if not openai_client: # Verificação adicional para garantir que o cliente foi inicializado
                    raise ValueError("OpenAI client not initialized, check API key in .env.")
                print("INFO: Tentando análise com OpenAI...")
                chat_completion = await openai_client.chat.completions.create(
                    model="gpt-3.5-turbo", # Você pode tentar "gpt-4" se tiver acesso e precisar de mais precisão
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"} # Solicita formato JSON diretamente
                )
                response_text = chat_completion.choices[0].message.content
                return json.loads(response_text) # Já deve vir como JSON válido

            elif llm_to_use == "gemini":
                if not settings.GEMINI_API_KEY: # Verificação adicional
                    raise ValueError("Gemini API key not configured in .env.")
                print("INFO: Tentando análise com Google Gemini...")
                model = genai.GenerativeModel('gemini-1.5-flash')

                # Tenta gerar conteúdo solicitando JSON diretamente
                try:
                    response = await model.generate_content_async(
                        prompt,
                        generation_config={"response_mime_type": "application/json"} # Força a resposta a ser JSON
                    )
                    response_text = response.text
                    return json.loads(response_text) # Tenta carregar o JSON
                except Exception as e:
                    print(f"WARNING: Gemini falhou ao gerar JSON diretamente: {e}. Tentando sem forçar e extraindo JSON.")
                    # Fallback: Se a primeira tentativa falhar, tente sem forçar o MIME type e extraia o JSON
                    response = await model.generate_content_async(prompt)
                    response_text = response.text
                    return extract_json_from_text(response_text)

        except Exception as e:
            last_error_message = f"Erro ao usar {llm_to_use}: {str(e)}"
            print(f"ERRO: {last_error_message}. Detalhes:")
            traceback.print_exc() # Imprime o traceback completo do erro para depuração
            continue # Continua para a próxima LLM na lista de opções

    # Se o loop terminar, significa que todas as LLMs tentadas falharam
    return {
        "classification": "error",
        "message": f"Todas as LLMs configuradas e tentadas falharam na análise. Último erro registrado: {last_error_message}"
    }