import requests
import feedparser
import os
import json
from datetime import datetime
from groq_utils import get_tool_analysis

# Configuración
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TOOLS_JSON_PATH = "data/tools.json"
README_PATH = "README.md"

def load_existing_tools():
    if os.path.exists(TOOLS_JSON_PATH):
        with open(TOOLS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_tools(tools):
    with open(TOOLS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(tools, f, indent=2, ensure_ascii=False)

def generate_readme(tools):
    """Genera el README.md a partir del JSON de herramientas."""
    header = """# OSINT Tools Directory

Colección centralizada de herramientas para investigadores y profesionales de la seguridad.

> [!TIP]
> **Versión Web**: Puedes ver este directorio en un formato mucho más visual y buscador en: [https://fud0dev.github.io/OSINT-Tools-Directory/](https://fud0dev.github.io/OSINT-Tools-Directory/)

---

"""
    
    # Agrupar por categorías
    categories = {}
    for tool in tools:
        cat = tool['categoria']
        if cat not in categories: categories[cat] = []
        categories[cat].append(tool)
        
    content = header
    content += "## 📂 Directorio\n\n"
    
    for cat, items in categories.items():
        content += f"### {cat}\n\n"
        for item in items:
            content += f"#### [{item['nombre']}]({item['url']})\n"
            content += f"{item['descripcion']}\n\n"
            content += f"**Riesgo:** {item['riesgo']} | **Tags:** {', '.join(item['tags'])}\n\n"
            content += "---\n\n"
    
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

def search_new_tools():
    """Lógica de búsqueda (GitHub, Reddit, RSS) - Simplificada para el ejemplo"""
    # ... (Aquí iría la lógica de requests.get a GitHub Search y RSS feeds)
    # Por ahora devolvemos una lista vacía para no fallar sin API Key
    return []

def main():
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY no configurada.")
        return

    existing_tools = load_existing_tools()
    existing_urls = {t['url'].lower() for t in existing_tools}
    
    findings = search_new_tools()
    new_adds = []
    
    for item in findings:
        url = item.get('url') or item.get('html_url')
        if url.lower() in existing_urls: continue
        
        analysis = get_tool_analysis(GROQ_API_KEY, {
            'name': item.get('name'),
            'url': url,
            'description': item.get('description')
        })
        
        if analysis:
            new_id = max([t['id'] for t in existing_tools]) + 1 if existing_tools else 1
            tool_entry = {
                "id": new_id,
                "nombre": analysis['nombre'],
                "url": url,
                "descripcion": analysis['descripcion_es'],
                "categoria": analysis['categoria'],
                "riesgo": analysis['riesgo'],
                "tags": analysis['tags'],
                "fecha_agregado": datetime.now().strftime('%Y-%m-%d')
            }
            existing_tools.append(tool_entry)
            new_adds.append(tool_entry)

    if new_adds:
        save_tools(existing_tools)
        generate_readme(existing_tools)
        print(f"Se han añadido {len(new_adds)} herramientas nuevas.")
    else:
        print("No se encontraron herramientas nuevas.")

if __name__ == "__main__":
    main()
