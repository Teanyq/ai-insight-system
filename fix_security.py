import os
import shutil

base_dir = r"C:\ai-insight"
frontend_dir = os.path.join(base_dir, "frontend")
backend_dir = os.path.join(base_dir, "backend")
templates_dir = os.path.join(backend_dir, "templates")

if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

src_admin = os.path.join(frontend_dir, "admin.html")
dst_admin = os.path.join(templates_dir, "admin.html")

if os.path.exists(src_admin):
    shutil.move(src_admin, dst_admin)
    print("Moved admin.html to templates.")

# Update main.py
main_py = os.path.join(backend_dir, "main.py")
with open(main_py, "r", encoding="utf-8") as f:
    content = f.read()

# Change the FileResponse path
content = content.replace(
    'return FileResponse(os.path.join(frontend_path, "admin.html"))',
    'return FileResponse(os.path.join(BASE_DIR, "backend", "templates", "admin.html"))'
)

with open(main_py, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated main.py security config.")
