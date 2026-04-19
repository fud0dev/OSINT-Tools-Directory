import sys
import os
import json
from datetime import datetime
from groq_utils import get_tool_analysis

TOOLS_JSON_PATH = "data/tools.json"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def load_existing_tools():
    if os.path.exists(TOOLS_JSON_PATH):
        with open(TOOLS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_tools(tools):
    with open(TOOLS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(tools, f, indent=2, ensure_ascii=False)

def main():
    if len(sys.argv) < 2:
        print("Uso: python process_issue.py <URL>")
        sys.exit(1)

    url = sys.argv[1].strip()
    if not url.startswith("http"):
        print("URL inválida.")
        sys.exit(1)

    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY no configurada.")
        sys.exit(1)

    print(f"Analizando herramienta desde Issue: {url}")

    existing_tools = load_existing_tools()
    existing_urls = {t['url'].lower(): t['id'] for t in existing_tools}

    if url.lower() in existing_urls:
        print(f"La herramienta ya existe en la base de datos con ID {existing_urls[url.lower()]}.")
        sys.exit(0)

    # Para process_issue no tenemos el nombre previo, lo dejamos vacio para que Groq lo infiera o extraiga.
    analysis = get_tool_analysis(GROQ_API_KEY, {
        'name': "Herramienta a determinar por IA",
        'url': url,
        'description': "Por favor, infiere la descripcion examinando la URL en tu conocimiento."
    })

    if analysis:
        new_id = max([t['id'] for t in existing_tools]) + 1 if existing_tools else 1
        tool_entry = {
            "id": new_id,
            "nombre": analysis.get('nombre', 'Unknown Tool'),
            "url": url,
            "descripcion": analysis.get('descripcion_es', 'Sin descripción'),
            "categoria": analysis.get('categoria', 'Otros'),
            "riesgo": analysis.get('riesgo', '🟢 Bajo'),
            "tags": analysis.get('tags', []),
            "fecha_agregado": datetime.now().strftime('%Y-%m-%d')
        }
        
        existing_tools.append(tool_entry)
        save_tools(existing_tools)
        print(f"Éxito: Herramienta añadida -> {tool_entry['nombre']}")
    else:
        print("Error: La IA no devolvió un análisis válido.")
        sys.exit(1)

if __name__ == "__main__":
    main()
