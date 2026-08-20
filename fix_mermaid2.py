import os
import re

base_dir = r"C:\ai-insight"
files = [
    os.path.join(base_dir, "frontend", "public.js"),
    os.path.join(base_dir, "frontend", "admin.js")
]

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_replace = """
            // Fix mermaid classes for rendering (Robust Regex)
            overviewHTML = overviewHTML.replace(/<pre><code[^>]*mermaid[^>]*>/gi, '<div class="mermaid">').replace(/<\\/code><\\/pre>/gi, '</div>');
            detailsHTML = detailsHTML.replace(/<pre><code[^>]*mermaid[^>]*>/gi, '<div class="mermaid">').replace(/<\\/code><\\/pre>/gi, '</div>');
"""
    
    content = re.sub(
        r'// Fix mermaid classes for rendering.*?detailsHTML = detailsHTML\.replace\(.*?\);',
        new_replace.strip(),
        content,
        flags=re.DOTALL
    )
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)

print("Applied robust regex for Mermaid.")
