import os

base_dir = r"C:\ai-insight"
files = [
    os.path.join(base_dir, "frontend", "public.js"),
    os.path.join(base_dir, "frontend", "admin.js")
]

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We need to add a closing brace before function showError
    content = content.replace(
        "            }, 100);\n\n\n        function showError(msg) {",
        "            }, 100);\n        }\n\n        function showError(msg) {"
    )
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)

print("Added missing closing brace.")
