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