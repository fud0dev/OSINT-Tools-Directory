import re
import json
import os

def migrate_readme_to_json(readme_content):
    # Regex to find tool blocks
    # Pattern: ### NUMBER. [NAME](LINK)\n[NAME](LINK)\nDESCRIPTION\n```TAG1```\n```TAG2```...
    tool_blocks = re.split(r'### \d+\.', readme_content)
    
    tools = []
    
    for i, block in enumerate(tool_blocks[1:]):
        lines = block.strip().split('\n')
        if not lines: continue
        
        # Extract title and link
        # The first line is: [NAME](URL)
        title_match = re.search(r'\[(.*?)\]\((.*?)\)', lines[0])
        if not title_match: continue
        
        name = title_match.group(1)
        url = title_match.group(2)
        
        # Extract description and tags
        description_lines = []
        tags = []
        capturing_tags = False
        
        for line in lines[2:]: # Start from 3rd line to skip the repeated name/link
            line = line.strip()
            if not line: continue
            
            if line.startswith('```'):
                capturing_tags = not capturing_tags
                continue
            
            if capturing_tags:
                tags.append(line)
            else:
                # Basic heuristic for risk icons
                if "🔴" in line or "🟠" in line or "🟢" in line:
                    continue
                description_lines.append(line)
        
        description = " ".join(description_lines)
        
        # Heuristic for category based on first tag
        category = tags[0] if tags else "Otros"
        
        # Heuristic for Risk (based on search)
        # Note: the original readme labels risk as colored circles
        risk = "🟢 Bajo" # Default
        if "🔴" in block: risk = "🔴 Alto"
        elif "🟠" in block: risk = "🟠 Medio"

        tools.append({
            "id": i + 1,
            "nombre": name,
            "url": url,
            "descripcion": description,
            "categoria": category,
            "riesgo": risk,
            "tags": list(set(tags)),
            "fecha_agregado": "2026-04-19" # Current date for initial migration
        })
        
    return tools

if __name__ == "__main__":
    # In a real scenario, we read the actual README.md
    # For this task, I'll provide the script for the user to run
    print("Script de migración preparado.")
