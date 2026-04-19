from groq import Groq
import os
import time
import random
import json

def get_tool_analysis(api_key, repo_info):
    """
    Analyzes an OSINT tool using Groq to translate, categorize and define risk.
    repo_info should be a dict with: 'name', 'url', 'description', 'full_text'
    """
    if not api_key:
        return None
        
    client = Groq(api_key=api_key)
    model_id = "llama-3.3-70b-versatile"
    
    prompt = f"""
    Eres un experto en ciberseguridad y OSINT. Tu tarea es analizar una herramienta encontrada en GitHub y formatearla para un directorio profesional.
    
    INFORMACIÓN DE LA HERRAMIENTA:
    Nombre: {repo_info.get('name')}
    URL: {repo_info.get('url')}
    Descripción original: {repo_info.get('description')}
    
    TAREAS:
    1. Traduce la descripción al español de forma profesional y concisa (máximo 2 frases).
    2. Categoriza la herramienta en UNA de estas categorías: [GitHub, LinkedIn, Instagram, Twitter, Facebook, Snapchat, Reddit, Pinterest, OSINT General, Otros].
    3. Asigna un nivel de riesgo (🔴 Alto | 🟠 Medio | 🟢 Bajo) basándote en su funcionalidad (ej: scraping agresivo es Alto/Medio, visualización pública es Bajo).
    4. Sugiere 3 tags cortos en español.

    REGLA: Devuelve ÚNICAMENTE un objeto JSON con esta estructura exacta:
    {{
        "nombre": "nombre",
        "descripcion_es": "descripción traducida",
        "categoria": "Categoría elegida",
        "riesgo": "🔴 Alto | 🟠 Medio | 🟢 Bajo",
        "tags": ["tag1", "tag2", "tag3"]
    }}
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_id,
                response_format={"type": "json_object"}
            )
            return json.loads(chat_completion.choices[0].message.content)
            
        except Exception as e:
            time.sleep(2 ** attempt)
            print(f"Error en Groq (Intento {attempt+1}): {str(e)}")
                
    return None
