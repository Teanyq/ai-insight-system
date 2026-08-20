import os

filepath = r"C:\ai-insight\backend\core\gemini_client.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add bullet point instruction to CRITICAL RULES
old_rules = """CRITICAL RULES:
1. NO MATH OR LATEX: NEVER use LaTeX math formulas (e.g., $$\\text{Regret} = ...$$ or $E=mc^2$). If the paper contains math, explain the *concept* using a simple, relatable everyday analogy (e.g., comparing it to picking a restaurant, playing a video game, or scrolling SNS). 
2. EXTREMELY SIMPLE LANGUAGE: Write in Japanese for an audience of college students. Keep it enthusiastic and accessible. Do not sound like an academic paper. Use relatable analogies (SNS, part-time jobs, university life, pop culture).
3. 1 PAPER = 1 THEME: Focus entirely on the PRIMARY THEME PAPER. Use the CONTEXT only to show how this connects to real-world trends they might know."""

new_rules = """CRITICAL RULES:
1. NO MATH OR LATEX: NEVER use LaTeX math formulas (e.g., $$\\text{Regret} = ...$$ or $E=mc^2$). If the paper contains math, explain the *concept* using a simple, relatable everyday analogy (e.g., comparing it to picking a restaurant, playing a video game, or scrolling SNS). 
2. BULLET POINTS OVER PARAGRAPHS: Minimize the use of long paragraphs. Explain almost everything using highly readable bullet points. Use standard text sentences ONLY for absolute minimum necessary context (e.g., a 1-sentence intro).
3. EXTREMELY SIMPLE LANGUAGE: Write in Japanese for an audience of college students. Keep it enthusiastic and accessible. Do not sound like an academic paper. Use relatable analogies (SNS, part-time jobs, university life, pop culture).
4. 1 PAPER = 1 THEME: Focus entirely on the PRIMARY THEME PAPER. Use the CONTEXT only to show how this connects to real-world trends they might know."""

content = content.replace(old_rules, new_rules)
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Added bullet point rule to prompt.")
