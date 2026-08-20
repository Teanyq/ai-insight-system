import os

filepath = r"C:\ai-insight\backend\api\endpoints.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the broken split line
# The broken string is likely literally:
# for line in overview.split('
# '):

import re
fixed_content = re.sub(
    r"for line in overview\.split\('\n'\):",
    r"for line in overview.split('\\n'):",
    content
)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(fixed_content)
    
print("Fixed endpoints.py")
