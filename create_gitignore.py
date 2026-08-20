import os

base_dir = r"C:\ai-insight"
gitignore_path = os.path.join(base_dir, ".gitignore")

gitignore_content = """# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Database
*.db
backend/insights.db

# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Logs
*.log
uvicorn.log

# VS Code / IDEs
.vscode/
.idea/
"""

with open(gitignore_path, "w", encoding="utf-8") as f:
    f.write(gitignore_content)

print("Created .gitignore")
