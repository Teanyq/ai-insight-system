import os

base_dir = r"C:\ai-insight"
files = [
    os.path.join(base_dir, "frontend", "public.js"),
    os.path.join(base_dir, "frontend", "admin.js")
]

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove the bad else block
    bad_code = """        } else {
                modalBody.innerHTML = '<pre>' + (report.markdown_content || '') + '</pre>';
            }
            modal.classList.remove('hidden');
        }"""
    
    # Ensure there's a proper closing brace for openReport
    if bad_code in content:
        content = content.replace(bad_code, "")
        
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)

print("Fixed syntax errors in JS files.")
