# src/core/llm_integration.py (Atualizado com todos os prints de depuração)

from typing import Optional, Any, Dict
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from huggingface_hub import InferenceClient

executor = ThreadPoolExecutor(max_workers=5)

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "HuggingFaceH4/zephyr-7b-beta")
print(f"DEBUG_LLM_ENV: HF_MODEL_NAME (lido do ambiente ou padrão): '{HF_MODEL_NAME}'")

hf_client = InferenceClient(model=HF_MODEL_NAME, token=HF_API_KEY)

if not hf_client:
    raise ValueError("Erro ao inicializar o cliente Hugging Face. Verifique a chave API e o modelo.")

def _analyze_with_huggingface(content: str) -> Dict[str, Any]:
    print("INFO: Tentando análise com Hugging Face...")
    try:
        response = hf_client.text_generation(
            content,
            max_new_tokens=250,
            temperature=0.7,
            do_sample=True,
            return_full_text=False
            # REMOVIDO: o argumento 'timeout' daqui, pois a função text_generation() não o aceita
        )
        
        generated_text = response.strip()

        classification = "indefinido"
        message = "Análise preliminar do Hugging Face."
        sources = ["HuggingFace_LLM_analysis"]

        if "fake news" in generated_text.lower() or "noticia falsa" in generated_text.lower() or "desinformação" in generated_text.lower():
            classification = "fake_news"
        elif "verdadeiro" in generated_text.lower() or "fato" in generated_text.lower() or "confirmado" in generated_text.lower():
            classification = "verdadeiro"
        elif "sátira" in generated_text.lower() or "humor" in generated_text.lower() or "ficcao" in generated_text.lower():
            classification = "sátira"
        elif "opinião" in generated_text.lower() or "editorial" in generated_text.lower() or "perspectiva" in generated_text.lower():
            classification = "opinião"
        elif "parcial" in generated_text.lower() or "tendencioso" in generated_text.lower():
            classification = "parcial"
        else:
            classification = "indefinido"

        message = generated_text
        
        return {"classification": classification, "message": message, "sources": sources}
    except Exception as e:
        # Este bloco agora capturará erros reais da API ou outras exceções
        print(f"ERRO: Erro ao usar huggingface: {e}")
        return {"classification": "error", "message": f"Erro ao usar huggingface: {e}"}

def analyze_content_sync(content: str, preferred_llm: str) -> Dict[str, Any]:
    print(f"INFO: [LLM Sync Wrapper] Iniciando análise síncrona com LLM: {preferred_llm}")
    
    llm_functions = {
        "huggingface": _analyze_with_huggingface, 
        HF_MODEL_NAME: _analyze_with_huggingface,
    }

    # --- PRINTS DE DEPURACAO DESCOMENTADOS ---
    print(f"DEBUG_LLM: Valor de preferred_llm recebido: '{preferred_llm}'")
    print(f"DEBUG_LLM: Tipo de preferred_llm: {type(preferred_llm)}")
    print(f"DEBUG_LLM: Chaves no llm_functions: {list(llm_functions.keys())}")
    print(f"DEBUG_LLM: 'huggingface' está em llm_functions.keys(): {'huggingface' in llm_functions.keys()}")
    print(f"DEBUG_LLM: '{HF_MODEL_NAME}' está em llm_functions.keys(): {HF_MODEL_NAME in llm_functions.keys()}")
    # --- FIM PRINTS DE DEPURACAO ---

    if preferred_llm not in llm_functions:
        print(f"ERRO: [LLM Sync Wrapper] LLM preferida '{preferred_llm}' não configurada ou inválida. As chaves disponíveis são: {list(llm_functions.keys())}. Verifique `llm_integration.py` e variáveis de ambiente.")
        return {"classification": "error", "message": f"LLM preferida '{preferred_llm}' não configurada ou inválida. Verifique `llm_integration.py`."}

    try:
        loop = asyncio.get_event_loop()
        llm_future = loop.run_in_executor(executor, llm_functions[preferred_llm], content)
        
        # O timeout é aplicado AQUI para a execução da tarefa no executor.
        # Defina um tempo limite razoável (por exemplo, 60 a 120 segundos)
        llm_result = loop.run_until_complete(asyncio.wait_for(llm_future, timeout=90)) # Mantido em 90 segundos

        print(f"DEBUG: [LLM Sync Wrapper] Resultado da LLM: {llm_result}")
        return llm_result

    except asyncio.TimeoutError:
        error_message = f"Erro na análise da LLM ({preferred_llm}): A inferência excedeu o tempo limite ({90} segundos)."
        print(f"ERRO: {error_message}")
        return {"classification": "error", "message": error_message}
    except Exception as e:
        error_message = f"Erro na análise da LLM ({preferred_llm}): {e}"
        print(f"ERRO: {error_message}")
        # Lógica de fallback para LLMs alternativas, se houver
        for llm_name, llm_func in llm_functions.items():
            if llm_name != preferred_llm:
                print(f"INFO: Tentando LLM alternativa: {llm_name}")
                try:
                    alt_future = loop.run_in_executor(executor, llm_func, content)
                    # Aplica timeout também para a LLM alternativa
                    alt_result = loop.run_until_complete(asyncio.wait_for(alt_future, timeout=90))
                    
                    if alt_result.get("classification") != "error":
                        print(f"INFO: LLM alternativa {llm_name} obteve sucesso.")
                        return alt_result
                except asyncio.TimeoutError:
                    print(f"ERRO: LLM alternativa {llm_name} excedeu o tempo limite.")
                    error_message += f"\nFalha na LLM alternativa {llm_name} (timeout)."
                except Exception as alt_e:
                    print(f"ERRO: Falha na LLM alternativa {llm_name}: {alt_e}")
                    error_message += f"\nFalha na LLM alternativa {llm_name}: {alt_e}"
        
        return {"classification": "error", "message": f"Todas as LLMs configuradas e tentadas falharam na análise. Último erro registrado: {error_message}"}