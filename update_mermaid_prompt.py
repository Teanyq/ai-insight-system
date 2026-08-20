import os

filepath = r"C:\ai-insight\backend\core\gemini_client.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the prompt section regarding Visual Breakdown to include strict Mermaid rules
old_mermaid_prompt = "## 📊 図解でサクッと理解！ (Visual Breakdown)\n[Use Markdown ````mermaid ... ```` blocks to generate a simple flowchart or mindmap. Keep the text inside the diagram VERY simple Japanese. Do NOT use markdown tables here.]"

new_mermaid_prompt = """## 📊 図解でサクッと理解！ (Visual Breakdown)
[Use Markdown ````mermaid ... ```` blocks to generate a simple flowchart or mindmap. Keep the text inside the diagram VERY simple Japanese. 
CRITICAL MERMAID RULES: 
- You MUST enclose all node text in double quotes to prevent syntax errors (e.g., A["ヤバいAI技術"] --> B("生活が激変")).
- Do not use markdown tables here.]"""

content = content.replace(old_mermaid_prompt, new_mermaid_prompt)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated prompt for stricter Mermaid syntax.")
