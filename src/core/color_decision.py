def determine_color(score):
    if score >= 0.8:
        return "🟢"  # Verde - Conteúdo verificado como verdadeiro
    elif score >= 0.5:
        return "⚪"  # Cinza - Conteúdo ainda em análise
    elif score >= 0.2:
        return "🔵"  # Azul - Neutro (opinião, sátira, meme)
    else:
        return "🔴"  # Vermelho - Fake news identificada

def classify_content(content_analysis):
    score = content_analysis.get('trust_score', 0)
    return determine_color(score)