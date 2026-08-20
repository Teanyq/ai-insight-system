import os
import shutil

base_dir = r"C:\ai-insight"

# Delete existing DB to reset schema
db_path = os.path.join(base_dir, "test.db")
if os.path.exists(db_path):
    os.remove(db_path)

# 1. Update models.py
models_path = os.path.join(base_dir, "backend", "db", "models.py")
models_content = """from sqlalchemy import Column, Integer, String, Text, DateTime
from backend.db.database import Base
from datetime import datetime, timezone

class InsightReport(Base):
    __tablename__ = "insight_reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    markdown_content = Column(Text)
    markdown_content_detailed = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    arxiv_query = Column(String, default="cat:cs.AI OR cat:cs.CL OR cat:cs.CV")
    rss_url = Column(String, default="https://techcrunch.com/feed/")
    schedule_interval_hours = Column(Integer, default=24)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
"""
with open(models_path, "w", encoding="utf-8") as f:
    f.write(models_content)


# 2. Update gemini_client.py
gemini_path = os.path.join(base_dir, "backend", "core", "gemini_client.py")
gemini_content = """import google.generativeai as genai
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
                system_instruction="You are a world-class AI researcher and an elite business strategist."
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
            f"Your task is to analyze the following PRIMARY research paper, and synthesize a premium, highly actionable insight report in Japanese.\\n\\n"
            f"### [PRIMARY THEME PAPER]\\n"
            f"- **{main_paper.get('title', 'No Title')}**\\n  {main_paper.get('summary', 'No Summary')}\\n\\n"
        )
        
        prompt += "### [CONTEXT: Other Recent Papers]\\n"
        if context_papers:
            for i, p in enumerate(context_papers, 1):
                prompt += f"- **{p.get('title', 'No Title')}**\\n  {p.get('summary', 'No Summary')}\\n\\n"
        else:
            prompt += "No additional papers.\\n\\n"
        
        prompt += "### [CONTEXT: Recent Business News]\\n"
        if news:
            for i, n in enumerate(news, 1):
                prompt += f"- **{n.get('title', 'No Title')}**\\n  {n.get('summary', 'No Summary')}\\n\\n"
        else:
            prompt += "No recent news available.\\n\\n"
            
        prompt += \"\"\"
Please synthesize this information focusing heavily on the PRIMARY THEME PAPER, using the CONTEXT to expand on its applications and current market trends.
Write entirely in Japanese.

You MUST split your response into TWO parts, separated exactly by the following delimiter on its own line:
====DETAIL_SECTION====

### PART 1: Visual Overview (Above the delimiter)
This section is for executives. It must be highly visual, using VERY LARGE text concepts and diagrams.
Use Markdown ````mermaid ... ```` blocks to generate AS MANY DIAGRAMS AS NECESSARY (e.g., a flowchart of the technology, a mindmap of business applications, or an architecture diagram). 
Keep paragraphs extremely short. Emphasize visual clarity. Do NOT use markdown tables here, rely on mermaid graphs instead.

Structure for Part 1:
# [Catchy, Premium Title]
## 🎯 Core Concept
[Extremely concise summary of the primary paper]
## 📊 Visual Breakdown
[At least 1 Mermaid diagram explaining the core tech or business impact]
## 🚀 Business Impact
[Short visual summary of the impact]

====DETAIL_SECTION====

### PART 2: Deep Dive Details (Below the delimiter)
This section is for engineers, researchers, and deep-dive analysts.
Write an extensive, detailed analysis of the primary paper, how it compares to the context papers/news, methodology, limitations, and a deep-dive into the technical breakthrough.

Structure for Part 2:
## 🔬 Technical Deep Dive
[Detailed explanation of the paper's methodology and breakthrough]
## 🌐 Context & Market Landscape
[How this relates to the other papers and news provided]
## 💡 Comprehensive Action Plan
[Extensive actionable advice and future outlook]
\"\"\"

        logger.info("Calling Gemini API with single-paper focus and detailed split...")
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
    f.write(gemini_content)


# 3. Update endpoints.py
endpoints_path = os.path.join(base_dir, "backend", "api", "endpoints.py")
with open(endpoints_path, "r", encoding="utf-8") as f:
    endpoints_code = f.read()

import re
endpoints_code = endpoints_code.replace(
    'class InsightReportSchema(BaseModel):\n    id: int\n    title: str\n    markdown_content: str\n    created_at: datetime',
    'class InsightReportSchema(BaseModel):\n    id: int\n    title: str\n    markdown_content: str\n    markdown_content_detailed: str | None = None\n    created_at: datetime'
)

new_gen_logic = """
        report_text = gemini_client.generate_insight_report(papers=papers, news=news)
        
        if report_text.startswith("Error:"):
            logger.error(f"Failed to generate report: {report_text}")
            raise HTTPException(status_code=500, detail=report_text)
            
        parts = report_text.split("====DETAIL_SECTION====")
        overview = parts[0].strip()
        detailed = parts[1].strip() if len(parts) > 1 else ""
        
        # Extract title from overview
        title = "AI Business Insights"
        for line in overview.split('\\n'):
            if line.startswith('# '):
                title = line.replace('# ', '').strip()
                break
                
        db_report = InsightReport(
            title=title,
            markdown_content=overview,
            markdown_content_detailed=detailed
        )
        db.add(db_report)
"""
# Replace the old generation logic
endpoints_code = re.sub(
    r'report = gemini_client\.generate_insight_report\(papers=papers, news=news\).*?db\.add\(db_report\)',
    new_gen_logic.strip(),
    endpoints_code,
    flags=re.DOTALL
)
endpoints_code = endpoints_code.replace('markdown_report=report,', 'markdown_report=overview,')

with open(endpoints_path, "w", encoding="utf-8") as f:
    f.write(endpoints_code)

# 4. Update Frontend UI
def inject_mermaid_and_tabs(html_content):
    # Add mermaid script if not present
    if "mermaid.min.js" not in html_content:
        html_content = html_content.replace('</head>', '    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>\n</head>')
    
    # Replace modal content
    new_modal = """
    <!-- Modal for viewing full report -->
    <div id="reportModal" class="modal hidden">
        <div class="modal-content glass-panel" style="max-width: 900px; width: 95%;">
            <span class="close-btn">&times;</span>
            <h2 id="modalTitle">Report</h2>
            <div class="tabs">
                <button class="tab-btn active" id="tabOverview">💡 Overview</button>
                <button class="tab-btn" id="tabDetails">📄 Details</button>
            </div>
            <div id="modalBodyOverview" class="markdown-body tab-content overview-mode"></div>
            <div id="modalBodyDetails" class="markdown-body tab-content hidden"></div>
        </div>
    </div>
    """
    html_content = re.sub(
        r'<!-- Modal for viewing full report -->.*?</div>\s*</div>',
        new_modal,
        html_content,
        flags=re.DOTALL
    )
    return html_content

public_html_path = os.path.join(base_dir, "frontend", "index.html")
with open(public_html_path, "r", encoding="utf-8") as f:
    public_html = f.read()
with open(public_html_path, "w", encoding="utf-8") as f:
    f.write(inject_mermaid_and_tabs(public_html))

admin_html_path = os.path.join(base_dir, "frontend", "admin.html")
with open(admin_html_path, "r", encoding="utf-8") as f:
    admin_html = f.read()
with open(admin_html_path, "w", encoding="utf-8") as f:
    f.write(inject_mermaid_and_tabs(admin_html))


# 5. Update CSS
style_path = os.path.join(base_dir, "frontend", "style.css")
with open(style_path, "a", encoding="utf-8") as f:
    f.write("""
/* Tabs */
.tabs {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 0.5rem;
}
.tab-btn {
    background: none;
    border: none;
    color: #94a3b8;
    font-size: 1.1rem;
    cursor: pointer;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    transition: all 0.2s;
}
.tab-btn:hover {
    background: rgba(255, 255, 255, 0.05);
    color: white;
}
.tab-btn.active {
    color: white;
    background: rgba(139, 92, 246, 0.2);
    font-weight: bold;
}
.overview-mode {
    font-size: 1.25rem;
    line-height: 1.8;
}
.overview-mode h2 {
    font-size: 2rem;
    color: #a78bfa;
}
""")

# 6. Update JS files
def inject_js_logic(js_path):
    with open(js_path, "r", encoding="utf-8") as f:
        js_code = f.read()
    
    # Init mermaid
    js_code = js_code.replace("fetchReports();", "mermaid.initialize({ startOnLoad: false, theme: 'dark' });\n        fetchReports();")
    
    # Update openReport function
    new_open_report = """
        const tabOverview = document.getElementById('tabOverview');
        const tabDetails = document.getElementById('tabDetails');
        const modalBodyOverview = document.getElementById('modalBodyOverview');
        const modalBodyDetails = document.getElementById('modalBodyDetails');
        
        if (tabOverview) {
            tabOverview.addEventListener('click', () => {
                tabOverview.classList.add('active');
                tabDetails.classList.remove('active');
                modalBodyOverview.classList.remove('hidden');
                modalBodyDetails.classList.add('hidden');
            });
        }
        if (tabDetails) {
            tabDetails.addEventListener('click', () => {
                tabDetails.classList.add('active');
                tabOverview.classList.remove('active');
                modalBodyDetails.classList.remove('hidden');
                modalBodyOverview.classList.add('hidden');
            });
        }

        function openReport(report) {
            const modalTitle = document.getElementById('modalTitle');
            const modal = document.getElementById('reportModal');
            
            modalTitle.textContent = report.title;
            
            // Render Markdown
            let overviewHTML = marked.parse(report.markdown_content || '');
            let detailsHTML = marked.parse(report.markdown_content_detailed || 'No details available.');
            
            // Fix mermaid classes for rendering
            overviewHTML = overviewHTML.replace(/<code class="language-mermaid">/g, '<div class="mermaid">').replace(/<\\/code><\\/pre>/g, '</div>');
            detailsHTML = detailsHTML.replace(/<code class="language-mermaid">/g, '<div class="mermaid">').replace(/<\\/code><\\/pre>/g, '</div>');
            
            modalBodyOverview.innerHTML = overviewHTML;
            modalBodyDetails.innerHTML = detailsHTML;
            
            // Reset tabs
            tabOverview.click();
            
            modal.classList.remove('hidden');
            
            // Render mermaid diagrams
            setTimeout(() => {
                mermaid.init(undefined, document.querySelectorAll('.mermaid'));
            }, 100);
        }
    """
    js_code = re.sub(r'function openReport\(report\) \{.*?\}', new_open_report.strip(), js_code, flags=re.DOTALL)
    
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_code)

inject_js_logic(os.path.join(base_dir, "frontend", "public.js"))
inject_js_logic(os.path.join(base_dir, "frontend", "admin.js"))

print("Phase 4 implementation complete.")
