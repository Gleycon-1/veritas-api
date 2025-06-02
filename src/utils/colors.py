# src/utils/colors.py

def get_color_from_classification(classification: str) -> str:
    """
    Mapeia uma classificação de conteúdo para uma cor específica.

    Args:
        classification (str): A categoria de classificação retornada pelo LLM.

    Returns:
        str: A representação da cor correspondente à classificação (ex: "green", "red").
             Retorna "black" (Indefinido/Erro) se a classificação não for reconhecida.
    """
    # As chaves aqui devem corresponder exatamente às strings que a LLM retorna
    # para a 'classification' no JSON.
    color_map = {
        "verdadeiro": "green",
        "fake_news": "red",
        "sátira": "white",  # Use "white" ou "grey" conforme sua preferência visual no frontend
        "opinião": "blue",
        "parcial": "orange",
        "indefinido": "black",
        "error": "black" # Mapeamento explícito para o status de erro
    }
    
    # Converte a classificação para minúsculas para garantir correspondência flexível
    return color_map.get(classification.lower(), "black")