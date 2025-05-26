# src/core/llm_integration.py

import os
import google.generativeai as genai
from openai import OpenAI
from huggingface_hub import InferenceClient # Importa o cliente Hugging Face
import json
import re # Importa regex para extrair JSON de strings
import traceback # Para imprimir o traceback completo do erro

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
        # Teste básico para ver se o cliente consegue se conectar (opcional, mas útil)
        # Tenta uma chamada simples para verificar a conexão sem consumir muito
        # Nota: Alguns modelos podem não suportar o método `text_generation` para testes vazios.
        # Por isso, o teste real é feito dentro da função analyze_content_with_llm.
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
    # Ordem de preferência para fallback: preferencial > Gemini > Hugging Face > OpenAI
    # O OpenAI é deixado por último ou como backup "se pagar" por causa da questão de custo.
    
    # 1. Adiciona a LLM preferencial primeiro, se configurada e disponível
    if preferred_llm.lower() == "gemini" and settings.GEMINI_API_KEY:
        llm_options.append("gemini")
    elif preferred_llm.lower() == "huggingface" and hf_client:
        llm_options.append("huggingface")
    elif preferred_llm.lower() == "openai" and openai_client:
        llm_options.append("openai")
    
    # 2. Adiciona as outras LLMs disponíveis como fallback, na ordem definida
    # (Evita adicionar duplicatas se a preferencial já foi adicionada)
    if "gemini" not in llm_options and settings.GEMINI_API_KEY:
        llm_options.append("gemini")
    if "huggingface" not in llm_options and hf_client:
        llm_options.append("huggingface")
    if "openai" not in llm_options and settings.OPENAI_API_KEY: # OpenAI ainda é uma opção caso a chave seja válida no futuro
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
                    # Tenta gerar conteúdo solicitando JSON diretamente
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

            elif llm_to_use == "huggingface":
                if not hf_client: raise ValueError("Hugging Face client not initialized, check API key/model ID in .env.")
                print(f"INFO: Tentando análise com Hugging Face (modelo: {settings.HUGGINGFACE_MODEL_ID})...")
                # A InferenceClient.text_generation não tem um response_format direto para JSON.
                # Precisamos confiar que o prompt instruirá o modelo a gerar JSON e depois parsear.
                # Para modelos instruídos como o Mistral, o prompt precisa ser formatado.
                # https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2#instruction-format
                hf_formatted_prompt = f"<s>[INST] {prompt} [/INST]"
                
                response_text = hf_client.text_generation(
                    hf_formatted_prompt, 
                    max_new_tokens=500, # Limite de tokens para a resposta
                    do_sample=False,    # Para respostas mais determinísticas (melhor para JSON)
                    return_full_text=False # Não retorna o prompt junto com a resposta
                )
                return extract_json_from_text(response_text)

            elif llm_to_use == "openai":
                if not openai_client: raise ValueError("OpenAI client not initialized, check API key in .env.")
                print("INFO: Tentando análise com OpenAI...")
                chat_completion = await openai_client.chat.completions.create(
                    model="gpt-3.5-turbo", # ou "gpt-4" se tiver acesso
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"} # Solicita formato JSON diretamente
                )
                response_text = chat_completion.choices[0].message.content
                return json.loads(response_text) # Já deve vir como JSON válido

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