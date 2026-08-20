import os

base_dir = r"C:\ai-insight"

gemini_path = os.path.join(base_dir, "backend", "core", "gemini_client.py")
with open(gemini_path, "r", encoding="utf-8") as f:
    gemini_code = f.read()

# Replace the prompt section
import re
new_prompt_code = """
        prompt = (
            "You are a world-class AI researcher and an elite business strategist. "
            "Your task is to analyze the latest AI research papers and recent business news, "
            "and synthesize a premium, highly actionable insight report in Japanese.\\n\\n"
            "Here is the data to analyze:\\n\\n"
        )
        
        prompt += "### Latest AI Research (arXiv)\\n"
        if papers:
            for i, p in enumerate(papers, 1):
                prompt += f"- **{p.get('title', 'No Title')}**\\n  {p.get('summary', 'No Summary')}\\n\\n"
        else:
            prompt += "No recent papers available.\\n\\n"
        
        prompt += "### Recent Business News\\n"
        if news:
            for i, n in enumerate(news, 1):
                prompt += f"- **{n.get('title', 'No Title')}**\\n  {n.get('summary', 'No Summary')}\\n\\n"
        else:
            prompt += "No recent news available.\\n\\n"
            
        prompt += \"\"\"
Please synthesize the information and generate a professional insight report in **Japanese**.
Use the exact structure below, and output strictly in Markdown format.
Use professional formatting (bolding, blockquotes, bullet points, and tables if useful).
The tone should be insightful, sophisticated, and actionable, similar to top-tier consulting reports.

# [A Catchy, Premium Title summarizing the core insight]

## 💡 Executive Summary
[Provide a 3-bullet point summary of the most critical takeaways. Use bolding for key terms.]

## 🔬 Deep Dive: 技術的ブレイクスルー
[Analyze the core technological advancements from the provided papers. Explain complex concepts clearly. Highlight why this research matters technically.]

## 📈 Business Implications: 市場へのインパクト
[Explain how these technical advancements affect the current business landscape. Cross-reference with the provided business news to show real-world momentum. What does this mean for enterprises and startups?]

## 🚀 Actionable Advice: リーダーへの提言
[Provide 2-3 concrete, actionable steps a business leader, strategist, or product manager should take immediately based on these insights.]
\"\"\"
"""

# Replace the entire generate_insight_report body related to prompt
# We will just rewrite the generate_insight_report function entirely to be safe.
new_gemini_code = """import google.generativeai as genai
import logging
from typing import List, Dict
from backend.core.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

class GeminiClient:
    def __init__(self):
        self.is_configured = False
        api_key = settings.GEMINI_API_KEY

        if not api_key or api_key == "your_gemini_api_key_here":
            logger.warning("GEMINI_API_KEY is not set.")
        else:
            genai.configure(api_key=api_key)
            self.is_configured = True

        self.model_name = 'gemini-3.5-flash'
        try:
            # Added system instruction for better persona
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction="You are a world-class AI researcher and an elite business strategist."
            )
        except Exception as e:
            logger.error(f"Gemini init error: {e}")
            self.model = None

    def generate_insight_report(self, papers: List[Dict[str, str]], news: List[Dict[str, str]]) -> str:
        if not self.is_configured or not self.model:
            return "Error: Gemini API is not configured."
        if not papers and not news:
            return "Error: No data available."

        prompt = (
            "Based on the following latest AI research papers and recent business news, "
            "synthesize a premium, highly actionable insight report in Japanese.\\n\\n"
            "Here is the data to analyze:\\n\\n"
        )
        
        prompt += "### Latest AI Research (arXiv)\\n"
        if papers:
            for i, p in enumerate(papers, 1):
                prompt += f"- **{p.get('title', 'No Title')}**\\n  {p.get('summary', 'No Summary')}\\n\\n"
        else:
            prompt += "No recent papers available.\\n\\n"
        
        prompt += "### Recent Business News\\n"
        if news:
            for i, n in enumerate(news, 1):
                prompt += f"- **{n.get('title', 'No Title')}**\\n  {n.get('summary', 'No Summary')}\\n\\n"
        else:
            prompt += "No recent news available.\\n\\n"
            
        prompt += \"\"\"
Please synthesize the information and generate a professional insight report in **Japanese**.
Use the exact structure below, and output strictly in Markdown format.
Use professional formatting (bolding, blockquotes, bullet points, and tables if useful).
The tone should be insightful, sophisticated, and actionable, similar to top-tier consulting reports.

# [A Catchy, Premium Title summarizing the core insight]

## 💡 Executive Summary
[Provide a 3-bullet point summary of the most critical takeaways. Use bolding for key terms.]

## 🔬 Deep Dive: 技術的ブレイクスルー
[Analyze the core technological advancements from the provided papers. Explain complex concepts clearly. Highlight why this research matters technically.]

## 📈 Business Implications: 市場へのインパクト
[Explain how these technical advancements affect the current business landscape. Cross-reference with the provided business news to show real-world momentum. What does this mean for enterprises and startups?]

## 🚀 Actionable Advice: リーダーへの提言
[Provide 2-3 concrete, actionable steps a business leader, strategist, or product manager should take immediately based on these insights.]
\"\"\"

        logger.info("Calling Gemini API with enhanced premium prompt...")
        try:
            response = self.model.generate_content(prompt)
            logger.info("Gemini API call success")
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"Report generation error: {e}"

gemini_client = GeminiClient()
"""

with open(gemini_path, "w", encoding="utf-8") as f:
    f.write(new_gemini_code)


# 2. Enhance Markdown Styling in style.css
style_path = os.path.join(base_dir, "frontend", "style.css")
with open(style_path, "a", encoding="utf-8") as f:
    f.write("""
/* Enhanced Markdown Typography for Premium Feel */
.markdown-body h1 {
    font-size: 2rem;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.5rem;
    border-bottom: none;
}

.markdown-body h2 {
    font-size: 1.5rem;
    color: #e2e8f0;
    margin-top: 2rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.markdown-body blockquote {
    border-left: 4px solid #8b5cf6;
    background: rgba(139, 92, 246, 0.1);
    padding: 1rem 1.5rem;
    margin: 1.5rem 0;
    border-radius: 0 8px 8px 0;
    color: #cbd5e1;
    font-style: italic;
}

.markdown-body ul {
    list-style-type: none;
    padding-left: 0;
}

.markdown-body ul li {
    position: relative;
    padding-left: 1.5rem;
    margin-bottom: 0.75rem;
    color: #cbd5e1;
}

.markdown-body ul li::before {
    content: "•";
    color: #8b5cf6;
    font-weight: bold;
    position: absolute;
    left: 0;
    font-size: 1.2em;
}

.markdown-body strong {
    color: #f8fafc;
    font-weight: 600;
}

.markdown-body table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    background: rgba(15, 23, 42, 0.4);
    border-radius: 8px;
    overflow: hidden;
}

.markdown-body th, .markdown-body td {
    padding: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #cbd5e1;
}

.markdown-body th {
    background: rgba(255, 255, 255, 0.05);
    color: #f8fafc;
    font-weight: 600;
    text-align: left;
}
""")

print("Phase 3 Prompt and UI Enhancement completed.")
