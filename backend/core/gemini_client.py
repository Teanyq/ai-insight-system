import google.generativeai as genai
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
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction="You are a charismatic, extremely easy-to-understand tech influencer who breaks down complex AI research for college students and young professionals. Your tone is energetic, accessible, and completely free of academic jargon."
            )
        except Exception as e:
            logger.error(f"Gemini init error: {e}")
            self.model = None

    def generate_insight_report(self, papers: List[Dict[str, str]], news: List[Dict[str, str]]) -> str:
        if not self.is_configured or not self.model:
            return "Error: Gemini API is not configured."
        if not papers:
            return "Error: No papers available to focus on."

        main_paper = papers[0]
        context_papers = papers[1:]

        prompt = (
            f"Your task is to analyze the following PRIMARY research paper, and synthesize an incredibly engaging, ultra-accessible explanation in Japanese targeted at college students and young people.\n\n"
            f"### [PRIMARY THEME PAPER]\n"
            f"- **{main_paper.get('title', 'No Title')}**\n  {main_paper.get('summary', 'No Summary')}\n\n"
        )
        
        prompt += "### [CONTEXT: Other Recent Papers]\n"
        if context_papers:
            for i, p in enumerate(context_papers, 1):
                prompt += f"- **{p.get('title', 'No Title')}**\n  {p.get('summary', 'No Summary')}\n\n"
        else:
            prompt += "No additional papers.\n\n"
        
        prompt += "### [CONTEXT: Recent Business News]\n"
        if news:
            for i, n in enumerate(news, 1):
                prompt += f"- **{n.get('title', 'No Title')}**\n  {n.get('summary', 'No Summary')}\n\n"
        else:
            prompt += "No recent news available.\n\n"
            
        prompt += """
CRITICAL RULES:
1. NO MATH OR LATEX: NEVER use LaTeX math formulas (e.g., $$\text{Regret} = ...$$ or $E=mc^2$). If the paper contains math, explain the *concept* using a simple, relatable everyday analogy (e.g., comparing it to picking a restaurant, playing a video game, or scrolling SNS). 
2. BULLET POINTS OVER PARAGRAPHS: Minimize the use of long paragraphs. Explain almost everything using highly readable bullet points. Use standard text sentences ONLY for absolute minimum necessary context (e.g., a 1-sentence intro).
3. EXTREMELY SIMPLE LANGUAGE: Write in Japanese for an audience of college students. Keep it enthusiastic and accessible. Do not sound like an academic paper. Use relatable analogies (SNS, part-time jobs, university life, pop culture).
4. 1 PAPER = 1 THEME: Focus entirely on the PRIMARY THEME PAPER. Use the CONTEXT only to show how this connects to real-world trends they might know.
5. STRICT FORMATTING: DO NOT include any conversational filler (e.g. "Sure, here is the report"). The VERY FIRST characters of your response MUST be '# [Title]'.

You MUST split your response into THREE parts, separated exactly by the following delimiter on its own line:
====DETAIL_SECTION====

### PART 1: Visual Overview (Above the first delimiter)
This section should be highly visual, punchy, and instantly understandable.

Structure for Part 1:
# [Catchy, clickbait-style but accurate Title]
## 🎯 要するに何がスゴイの？ (Core Concept)
[Extremely concise summary of the primary paper using an everyday analogy]
## 📊 図解でサクッと理解！ (Visual Breakdown)
[Use Markdown ````mermaid ... ```` blocks to generate a simple flowchart or mindmap. Keep the text inside the diagram VERY simple Japanese. 
CRITICAL MERMAID RULES: 
- You MUST enclose all node text in double quotes to prevent syntax errors (e.g., A["ヤバいAI技術"] --> B("生活が激変")).
- Do not use markdown tables here.]
## 🚀 私たちの生活はどう変わる？ (Life Impact)
[Short summary of how this will impact young people's lives or future careers]

====DETAIL_SECTION====

### PART 2: Deep Dive Details (Between the delimiters)
This section is for those who want to know a bit more, but STILL keep the language simple and math-free.

Structure for Part 2:
## 🔬 どんな仕組みなの？ (Technical Deep Dive)
[Explain the paper's methodology and breakthrough without any math. Use metaphors.]
## 🌐 世の中のトレンドとの繋がり (Context & Market Landscape)
[How this relates to the other papers and news provided. Connect it to familiar tech like ChatGPT, TikTok, or iPhone if possible.]
## 💡 若者向けの未来アクション (Action Plan)
[What should a college student or young professional do with this knowledge? Actionable advice for their future.]

====DETAIL_SECTION====

### PART 3: X (Twitter) Post (Below the second delimiter)
Write a highly engaging, news-style tweet to share this insight on X. 
Rules for the tweet:
- Content: Start with an attention-grabbing emoji (e.g., 🚨, 🚀, 💡, 🔥) and ONE extremely catchy, punchy hook sentence. Following that, provide a super concise abstract (1-2 sentences) that makes anyone curious about the core breakthrough.
- Tone: DO NOT use polite language (敬語・ですます調は一切禁止). Use sharp, assertive "だ・である" or engaging colloquial phrasing. Make it sound like a provocative tech alert that demands immediate attention.
- Formatting: MUST finish the final sentence cleanly with punctuation like '。' or '！'. DO NOT leave sentences hanging.
- Length: STRICTLY under 110 characters (Japanese).
- DO NOT INCLUDE URLs or links (the backend will append the app URL automatically).
- Do not use hashtags unless highly relevant (max 1).
"""

        logger.info("Calling Gemini API with youth-targeted prompt...")
        try:
            response = self.model.generate_content(prompt)
            logger.info("Gemini API call success")
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"Report generation error: {e}"

    def fix_report_title(self, content: str) -> str:
        if not self.is_configured or not self.model:
            return "AI Business Insights"
        prompt = (
            "Extract a catchy, clickbait-style but accurate title from the following Markdown report. "
            "Output ONLY the title string itself. Do NOT output markdown symbols like # or **, and do not output any conversational filler.\n\n"
            f"REPORT:\n{content}"
        )
        try:
            response = self.model.generate_content(prompt)
            title = response.text.strip().replace('#', '').replace('**', '').strip()
            return title if title else "AI Business Insights"
        except Exception as e:
            logger.error(f"Gemini fix_title error: {e}")
            return "AI Business Insights"

gemini_client = GeminiClient()
