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
    
    # We want to replace <pre><code class="language-mermaid"> or <pre><code class="language-mermaid">\n with <div class="mermaid">
    # Let's use a safer replacement strategy.
    
    # We can do this with regex in JS. But it's easier to just update the JS file.
    
    # Let's find the old replacement lines
    # overviewHTML = overviewHTML.replace(/<code class="language-mermaid">/g, '<div class="mermaid">').replace(/<\/code><\/pre>/g, '</div>');
    
    new_replace = """
            // Fix mermaid classes for rendering, taking <pre> tags into account
            overviewHTML = overviewHTML.replace(/<pre><code class="language-mermaid">/g, '<div class="mermaid">').replace(/<\\/code><\\/pre>/g, '</div>');
            detailsHTML = detailsHTML.replace(/<pre><code class="language-mermaid">/g, '<div class="mermaid">').replace(/<\\/code><\\/pre>/g, '</div>');
            
            // Also handle cases where marked might not add the language class if Gemini omitted it (unlikely, but just in case)
            overviewHTML = overviewHTML.replace(/<pre><code>graph/g, '<div class="mermaid">graph').replace(/<pre><code>mindmap/g, '<div class="mermaid">mindmap').replace(/<pre><code>flowchart/g, '<div class="mermaid">flowchart');
"""
    
    # We will replace the entire block
    content = re.sub(
        r'// Fix mermaid classes for rendering.*?detailsHTML = detailsHTML\.replace\(.*?\);',
        new_replace.strip(),
        content,
        flags=re.DOTALL
    )
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)

print("Updated mermaid regex in JS files.")
