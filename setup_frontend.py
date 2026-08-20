import os

base_dir = r'C:\ai-insight'
os.makedirs(os.path.join(base_dir, 'docs'), exist_ok=True)
os.makedirs(os.path.join(base_dir, 'frontend'), exist_ok=True)

# docs/AGENT_HANDOVER.md
handover_content = '''# Agent Handover Document

## Project Status
This is the **AI Research x Business Insight System**, currently at the MVP (Phase 1) stage.
The system is fully functional: it fetches AI papers from arXiv, tech news from RSS (TechCrunch), and uses Google Gemini (gemini-3.5-flash) to generate markdown insights.

## Quick Start
1. Workspace: C:\\ai-insight
2. Environment Variables: Stored in ackend/.env. Needs GEMINI_API_KEY.
3. Database: SQLite (ackend/insights.db).
4. To run: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
5. API Docs: http://localhost:8000/docs
6. UI: http://localhost:8000/

## Key Files
- ackend/main.py: App entry point. Mounts the frontend.
- ackend/api/endpoints.py: /generate-insight and /insights logic.
- ackend/db/: SQLAlchemy models and SQLite setup.
- ackend/core/gemini_client.py: Gemini API interactions.
- rontend/: Vanilla HTML/CSS/JS frontend.

## Next Steps for Future Agents
- Allow the user to select specific RSS feeds or arXiv categories from the UI.
- Implement automated cron jobs (e.g., APScheduler) to generate insights daily.
'''
with open(os.path.join(base_dir, 'docs', 'AGENT_HANDOVER.md'), 'w', encoding='utf-8') as f:
    f.write(handover_content)

# docs/ARCHITECTURE.md
architecture_content = '''# System Architecture

## Overview
A monolithic FastAPI backend serving a Vanilla JS/CSS Single Page Application (SPA).

## Components
1. **Backend (FastAPI)**
   - **Services Layer**: 
     - rxiv_fetcher.py: Queries arXiv API for latest AI/ML papers.
     - 
ews_fetcher.py: Parses RSS feeds for latest tech business news.
   - **Core Layer**:
     - gemini_client.py: Uses google-generativeai with gemini-3.5-flash to synthesize research and news into business ideas.
   - **Database Layer**:
     - database.py & models.py: SQLAlchemy ORM mapping to SQLite. Stores InsightReport.
   - **API Layer**:
     - endpoints.py: RESTful routes.
2. **Frontend (Vanilla HTML/CSS/JS)**
   - index.html: Responsive, Glassmorphism-styled UI.
   - style.css: Premium dark-mode aesthetics.
   - pp.js: Fetches data from backend endpoints and renders markdown via marked.js.
'''
with open(os.path.join(base_dir, 'docs', 'ARCHITECTURE.md'), 'w', encoding='utf-8') as f:
    f.write(architecture_content)

# docs/API_REFERENCE.md
api_ref_content = '''# API Reference

## POST /api/v1/generate-insight
Generates a new insight report, saves it to the SQLite database, and returns it.
- **Request Body**: None (Currently autonomous)
- **Response**:
  `json
  {
    "status": "success",
    "markdown_report": "# Insight...",
    "report_id": 1
  }
  `

## GET /api/v1/insights
Retrieves a paginated list of past insight reports from the database.
- **Query Params**: skip (int, default 0), limit (int, default 10)
- **Response**: Array of:
  `json
  {
    "id": 1,
    "title": "AI Business Insights - 2026-08-20 12:00",
    "markdown_content": "# Insight...",
    "created_at": "2026-08-20T12:00:00Z"
  }
  `
'''
with open(os.path.join(base_dir, 'docs', 'API_REFERENCE.md'), 'w', encoding='utf-8') as f:
    f.write(api_ref_content)

# frontend/index.html
html_content = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Insight Generator</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
    <div class="background-glow"></div>
    <div class="container">
        <header>
            <h1>AI Insight Engine</h1>
            <p>Bridging cutting-edge AI research with business strategy</p>
            <button id="generateBtn" class="primary-btn">
                <span class="btn-text">Generate New Insight</span>
                <div class="loader hidden"></div>
            </button>
        </header>

        <main>
            <div id="errorBox" class="error-box hidden"></div>
            
            <section class="insights-section">
                <div class="section-header">
                    <h2>Latest Reports</h2>
                    <span id="reportCount" class="badge">0</span>
                </div>
                <div id="reportsContainer" class="reports-grid">
                    <!-- Reports will be dynamically injected here -->
                </div>
            </section>
        </main>
    </div>

    <!-- Modal for viewing full report -->
    <div id="reportModal" class="modal hidden">
        <div class="modal-content glass-panel">
            <span class="close-btn">&times;</span>
            <h2 id="modalTitle">Report</h2>
            <div id="modalBody" class="markdown-body"></div>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>
'''
with open(os.path.join(base_dir, 'frontend', 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html_content)

# frontend/style.css
css_content = '''
:root {
    --bg-color: #0f172a;
    --text-color: #f8fafc;
    --primary: #3b82f6;
    --primary-hover: #2563eb;
    --card-bg: rgba(30, 41, 59, 0.7);
    --border-color: rgba(255, 255, 255, 0.1);
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-color);
    color: var(--text-color);
    line-height: 1.6;
    min-height: 100vh;
    overflow-x: hidden;
    position: relative;
}

.background-glow {
    position: fixed;
    top: -20%;
    left: -10%;
    width: 60%;
    height: 60%;
    background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, rgba(15,23,42,0) 70%);
    z-index: -1;
    pointer-events: none;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

header {
    text-align: center;
    margin-bottom: 4rem;
    padding-top: 2rem;
}

h1 {
    font-size: 3rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    background: linear-gradient(to right, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

header p {
    color: #94a3b8;
    margin-bottom: 2rem;
}

.primary-btn {
    background-color: var(--primary);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.primary-btn:hover {
    background-color: var(--primary-hover);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.primary-btn:disabled {
    background-color: #475569;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.loader {
    width: 16px;
    height: 16px;
    border: 2px solid #fff;
    border-bottom-color: transparent;
    border-radius: 50%;
    display: inline-block;
    animation: rotation 1s linear infinite;
}

@keyframes rotation {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.hidden {
    display: none !important;
}

.error-box {
    background-color: rgba(239, 68, 68, 0.1);
    border: 1px solid #ef4444;
    color: #fca5a5;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 2rem;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.badge {
    background-color: #1e293b;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.875rem;
    color: #94a3b8;
}

.reports-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
}

.report-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
    cursor: pointer;
    transition: all 0.3s ease;
}

.report-card:hover {
    transform: translateY(-5px);
    border-color: rgba(96, 165, 250, 0.5);
    box-shadow: 0 10px 25px rgba(0,0,0, 0.2);
}

.report-card h3 {
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
    color: #e2e8f0;
}

.report-card .date {
    font-size: 0.875rem;
    color: #64748b;
    margin-bottom: 1rem;
}

.report-card .preview {
    font-size: 0.95rem;
    color: #cbd5e1;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Modal */
.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(5px);
    z-index: 1000;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 2rem;
    overflow-y: auto;
}

.glass-panel {
    background: rgba(30, 41, 59, 0.95);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    width: 100%;
    max-width: 800px;
    padding: 2.5rem;
    position: relative;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

.close-btn {
    position: absolute;
    top: 1.5rem;
    right: 1.5rem;
    font-size: 2rem;
    color: #94a3b8;
    cursor: pointer;
    line-height: 1;
}

.close-btn:hover {
    color: white;
}

#modalTitle {
    margin-bottom: 1.5rem;
    padding-right: 2rem;
    font-size: 1.5rem;
    color: #f1f5f9;
}

.markdown-body {
    color: #cbd5e1;
}

.markdown-body h1, .markdown-body h2, .markdown-body h3 {
    color: #e2e8f0;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}

.markdown-body h2 {
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 0.5rem;
}

.markdown-body p {
    margin-bottom: 1rem;
}

.markdown-body ul, .markdown-body ol {
    margin-bottom: 1rem;
    padding-left: 1.5rem;
}

.markdown-body li {
    margin-bottom: 0.25rem;
}

.markdown-body strong {
    color: #60a5fa;
}
'''
with open(os.path.join(base_dir, 'frontend', 'style.css'), 'w', encoding='utf-8') as f:
    f.write(css_content)

# frontend/app.js
js_content = '''
document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generateBtn');
    const reportsContainer = document.getElementById('reportsContainer');
    const reportCount = document.getElementById('reportCount');
    const errorBox = document.getElementById('errorBox');
    
    const modal = document.getElementById('reportModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    const closeBtn = document.querySelector('.close-btn');

    fetchReports();

    generateBtn.addEventListener('click', generateInsight);
    
    closeBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });

    async function fetchReports() {
        try {
            const res = await fetch('/api/v1/insights');
            if (!res.ok) throw new Error('Failed to fetch reports');
            
            const reports = await res.json();
            renderReports(reports);
        } catch (err) {
            showError(err.message);
        }
    }

    async function generateInsight() {
        setLoading(true);
        try {
            const res = await fetch('/api/v1/generate-insight', { method: 'POST' });
            if (!res.ok) {
                const errorData = await res.json();
                throw new Error(errorData.detail || 'Generation failed');
            }
            await fetchReports();
        } catch (err) {
            showError(err.message);
        } finally {
            setLoading(false);
        }
    }

    function renderReports(reports) {
        reportCount.textContent = reports.length;
        reportsContainer.innerHTML = '';
        
        if (reports.length === 0) {
            reportsContainer.innerHTML = '<p style="color: #64748b; grid-column: 1/-1;">No reports generated yet.</p>';
            return;
        }

        reports.forEach(report => {
            const card = document.createElement('div');
            card.className = 'report-card';
            
            const dateStr = new Date(report.created_at).toLocaleString('ja-JP');
            
            const previewText = report.markdown_content.replace(/[#*]/g, '').substring(0, 150) + '...';

            card.innerHTML = 
                <h3></h3>
                <div class="date"></div>
                <div class="preview"></div>
            ;

            card.addEventListener('click', () => openReport(report));
            reportsContainer.appendChild(card);
        });
    }

    function openReport(report) {
        modalTitle.textContent = report.title;
        modalBody.innerHTML = marked.parse(report.markdown_content);
        modal.classList.remove('hidden');
    }

    function setLoading(isLoading) {
        const btnText = generateBtn.querySelector('.btn-text');
        const loader = generateBtn.querySelector('.loader');
        
        generateBtn.disabled = isLoading;
        if (isLoading) {
            btnText.textContent = 'Generating... (This takes a minute)';
            loader.classList.remove('hidden');
        } else {
            btnText.textContent = 'Generate New Insight';
            loader.classList.add('hidden');
        }
    }

    function showError(msg) {
        errorBox.textContent = msg;
        errorBox.classList.remove('hidden');
        setTimeout(() => {
            errorBox.classList.add('hidden');
        }, 5000);
    }
});
'''
with open(os.path.join(base_dir, 'frontend', 'app.js'), 'w', encoding='utf-8') as f:
    f.write(js_content)

# Update backend/main.py to serve static files
main_content = '''from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api.endpoints import router as insight_router
from backend.db.database import engine, Base
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Research x Business Insight API",
    description="Backend MVP for AI Business Insights",
    version="1.0.0"
)

app.include_router(insight_router, prefix="/api/v1")

# Mount frontend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_path = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {"status": "Frontend not found, but backend is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
'''
with open(os.path.join(base_dir, 'backend', 'main.py'), 'w', encoding='utf-8') as f:
    f.write(main_content)

print('All docs and frontend files generated successfully.')
