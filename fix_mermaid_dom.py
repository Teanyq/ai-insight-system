import os
import re

base_dir = r"C:\ai-insight"
files = [
    os.path.join(base_dir, "frontend", "public.js"),
    os.path.join(base_dir, "frontend", "admin.js")
]

new_replace = """
            // Fix mermaid classes for rendering (Robust DOM Parsing)
            function processMermaid(htmlContent) {
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = htmlContent;
                const mermaidBlocks = tempDiv.querySelectorAll('code[class*="language-mermaid"], code.mermaid');
                mermaidBlocks.forEach(block => {
                    const parentPre = block.parentElement;
                    if (parentPre && parentPre.tagName === 'PRE') {
                        const newDiv = document.createElement('div');
                        newDiv.className = 'mermaid';
                        // textContent automatically unescapes HTML entities like &gt;
                        newDiv.textContent = block.textContent; 
                        parentPre.replaceWith(newDiv);
                    }
                });
                return tempDiv.innerHTML;
            }
            
            overviewHTML = processMermaid(overviewHTML);
            detailsHTML = processMermaid(detailsHTML);
"""

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = re.sub(
        r'// Fix mermaid classes for rendering.*?detailsHTML = detailsHTML\.replace\(.*?\);',
        new_replace.strip(),
        content,
        flags=re.DOTALL
    )
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)

print("Applied DOM-based robust Mermaid fix.")
