from typing import Any, Dict
import openai
import os

# Configurações da API do OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_content(content: str) -> Dict[str, Any]:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": f"Analyze the following content for its veracity: {content}"}
        ]
    )
    return response.choices[0].message['content']

def classify_content(content: str) -> str:
    analysis_result = analyze_content(content)
    # Lógica para classificar o conteúdo com base na resposta do LLM
    # Aqui você pode implementar regras específicas para determinar a cor
    return analysis_result  # Retorna a classificação baseada na análise do LLM

import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def analisar_conteudo_llm(texto: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",  # ou "gpt-3.5-turbo" se quiser algo mais leve
        messages=[
            {"role": "system", "content": "Você é um verificador de fatos."},
            {"role": "user", "content": f"Analise o seguinte conteúdo e diga se é confiável ou não, e por quê:\n\n{texto}"}
        ],
        temperature=0.4,
        max_tokens=500
    )

    return response.choices[0].message['content']
