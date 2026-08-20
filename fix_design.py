import os

base_dir = r"C:\ai-insight"
files = [
    os.path.join(base_dir, "frontend", "public.js"),
    os.path.join(base_dir, "frontend", "admin.js")
]

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Change mermaid theme
    content = content.replace("mermaid.initialize({ startOnLoad: false, theme: 'dark' });", "mermaid.initialize({ startOnLoad: false, theme: 'default' });")
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)

# Update style.css to give mermaid blocks a solid, clean background
style_path = os.path.join(base_dir, "frontend", "style.css")
with open(style_path, "a", encoding="utf-8") as f:
    f.write("""
/* Mermaid Diagram Design Fix */
.mermaid {
    background-color: #f8fafc;
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    text-align: center;
    overflow-x: auto;
}
.mermaid svg {
    max-width: 100%;
    height: auto !important;
}
""")

print("Mermaid design updated.")
