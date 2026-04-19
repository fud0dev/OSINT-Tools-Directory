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
def load_existing_tools():
    if os.path.exists(TOOLS_JSON_PATH):
        with open(TOOLS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_tools(tools):
    with open(TOOLS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(tools, f, indent=2, ensure_ascii=False)

def search_new_tools():
    """Lógica de búsqueda real en GitHub, Reddit y RSS."""
    new_findings = []
    
    # 1. Búsqueda en GitHub (Tópico OSINT)
    try:
        from datetime import datetime, timedelta
        date_filter = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        gh_url = f"https://api.github.com/search/repositories?q=topic:osint+created:>{date_filter}&sort=stars"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
        resp = requests.get(gh_url, headers=headers)
        if resp.status_code == 200:
            for item in resp.json().get('items', []):
                new_findings.append({
                    'name': item['name'],
                    'url': item['html_url'],
                    'description': item['description'] or ""
                })
    except Exception as e:
        print(f"Error GitHub: {e}")

    # 2. Búsqueda en Reddit (r/osinttools)
    try:
        feed = feedparser.parse("https://www.reddit.com/r/osinttools/.rss")
        for entry in feed.entries:
            new_findings.append({
                'name': entry.title,
                'url': entry.link,
                'description': entry.summary[:200]
            })
    except Exception as e:
        print(f"Error Reddit: {e}")

    # 3. RSS Jake Creps (Newsletter)
    try:
        feed = feedparser.parse("https://jakecreps.com/feed/")
        for entry in feed.entries[:5]:
            new_findings.append({
                'name': entry.title,
                'url': entry.link,
                'description': entry.summary[:200]
            })
    except Exception as e:
        print(f"Error Newsletter: {e}")
        
    return new_findings

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
        if not url: continue
        if url.lower() in existing_urls: continue
        
        print(f"Analizando nueva herramienta: {item.get('name')}...")
        
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
            # Evitar colision de duplicados en la misma ejecucion
            existing_urls.add(url.lower())

    if new_adds:
        save_tools(existing_tools)
        print(f"Se han añadido {len(new_adds)} herramientas nuevas al sistema web.")
    else:
        print("No se encontraron herramientas nuevas.")

if __name__ == "__main__":
    main()
