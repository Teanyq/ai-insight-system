import os

filepath = r"C:\ai-insight\frontend\admin.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add the closing brace before function setLoading
content = content.replace(
    "            }, 100);\n\n\n        function setLoading(isLoading) {",
    "            }, 100);\n        }\n\n        function setLoading(isLoading) {"
)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed admin.js closing brace.")
