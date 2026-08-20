import os
import re

style_css = r"C:\ai-insight\frontend\style.css"
with open(style_css, "r", encoding="utf-8") as f:
    content = f.read()

# Make h1 larger
content = content.replace(
""".markdown-body h1 {
    font-size: 2rem;""",
""".markdown-body h1 {
    font-size: 2.75rem;
    line-height: 1.2;"""
)

# Adjust overview-mode h2
content = content.replace(
""".overview-mode h2 {
    font-size: 2rem;""",
""".overview-mode h2 {
    font-size: 1.75rem;"""
)

with open(style_css, "w", encoding="utf-8") as f:
    f.write(content)

print("Adjusted heading sizes in style.css.")
