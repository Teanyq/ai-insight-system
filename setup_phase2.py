import os

base_dir = r"C:\ai-insight"

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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    arxiv_query = Column(String, default="cat:cs.AI OR cat:cs.CL OR cat:cs.CV")
    rss_url = Column(String, default="https://techcrunch.com/category/artificial-intelligence/feed/")
    schedule_interval_hours = Column(Integer, default=24)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
"""
with open(models_path, "w", encoding="utf-8") as f:
    f.write(models_content)

# 2. Update arxiv_fetcher.py to accept query
arxiv_path = os.path.join(base_dir, "backend", "services", "arxiv_fetcher.py")
with open(arxiv_path, "r", encoding="utf-8") as f:
    arxiv_code = f.read()
arxiv_code = arxiv_code.replace(
    'def fetch_latest_ai_papers(max_results: int = 5) -> List[Dict[str, str]]:',
    'def fetch_latest_ai_papers(max_results: int = 5, search_query: str = "cat:cs.AI OR cat:cs.CL OR cat:cs.CV") -> List[Dict[str, str]]:'
)
arxiv_code = arxiv_code.replace(
    'search_query = "cat:cs.AI OR cat:cs.CL OR cat:cs.CV"',
    '# search_query is now an argument'
)
with open(arxiv_path, "w", encoding="utf-8") as f:
    f.write(arxiv_code)

# 3. Update news_fetcher.py to accept rss_url
news_path = os.path.join(base_dir, "backend", "services", "news_fetcher.py")
with open(news_path, "r", encoding="utf-8") as f:
    news_code = f.read()
news_code = news_code.replace(
    'def fetch_recent_business_news(max_results: int = 5, hours: int = 24) -> List[Dict[str, str]]:',
    'def fetch_recent_business_news(max_results: int = 5, hours: int = 24, rss_url: str = "https://techcrunch.com/category/artificial-intelligence/feed/") -> List[Dict[str, str]]:'
)
news_code = news_code.replace(
    'TECHCRUNCH_AI_RSS = "https://techcrunch.com/category/artificial-intelligence/feed/"\n    feed = feedparser.parse(TECHCRUNCH_AI_RSS)',
    'feed = feedparser.parse(rss_url)'
)
with open(news_path, "w", encoding="utf-8") as f:
    f.write(news_code)

# 4. Update endpoints.py to add settings APIs and use them
endpoints_path = os.path.join(base_dir, "backend", "api", "endpoints.py")
endpoints_content = """from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session

from backend.services.arxiv_fetcher import fetch_latest_ai_papers
from backend.services.news_fetcher import fetch_recent_business_news
from backend.core.gemini_client import gemini_client
from backend.db.database import get_db
from backend.db.models import InsightReport, SystemConfig

logger = logging.getLogger(__name__)

router = APIRouter()

class InsightResponse(BaseModel):
    status: str = Field(..., description="Success or error status")
    markdown_report: str = Field(..., description="Generated Markdown report")
    report_id: int | None = Field(None, description="Database ID of the generated report")

class InsightReportSchema(BaseModel):
    id: int
    title: str
    markdown_content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SystemConfigSchema(BaseModel):
    arxiv_query: str
    rss_url: str
    schedule_interval_hours: int

def get_or_create_config(db: Session) -> SystemConfig:
    config = db.query(SystemConfig).first()
    if not config:
        config = SystemConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

@router.get("/settings", response_model=SystemConfigSchema)
def get_settings(db: Session = Depends(get_db)):
    config = get_or_create_config(db)
    return SystemConfigSchema(
        arxiv_query=config.arxiv_query,
        rss_url=config.rss_url,
        schedule_interval_hours=config.schedule_interval_hours
    )

@router.post("/settings", response_model=SystemConfigSchema)
def update_settings(settings: SystemConfigSchema, db: Session = Depends(get_db)):
    config = get_or_create_config(db)
    config.arxiv_query = settings.arxiv_query
    config.rss_url = settings.rss_url
    config.schedule_interval_hours = settings.schedule_interval_hours
    db.commit()
    db.refresh(config)
    
    # Restart scheduler to apply new interval
    from backend.core.scheduler import start_scheduler
    start_scheduler()
    
    return get_settings(db)

@router.post("/generate-insight", response_model=InsightResponse)
async def generate_insight(db: Session = Depends(get_db)):
    logger.info("Insight generation API called.")
    try:
        config = get_or_create_config(db)
        
        papers = fetch_latest_ai_papers(max_results=3, search_query=config.arxiv_query)
        news = fetch_recent_business_news(max_results=3, hours=24, rss_url=config.rss_url)
        
        report = gemini_client.generate_insight_report(papers=papers, news=news)
        
        if report.startswith("Error:") or report.startswith("Error:"):
            logger.error(f"Failed to generate report: {report}")
            raise HTTPException(status_code=500, detail=report)
            
        db_report = InsightReport(
            title=f"AI Business Insights - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            markdown_content=report
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
            
        logger.info("Insight report generated and saved successfully.")
        return InsightResponse(
            status="success",
            markdown_report=report,
            report_id=db_report.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights", response_model=List[InsightReportSchema])
def get_insights(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    reports = db.query(InsightReport).order_by(InsightReport.created_at.desc()).offset(skip).limit(limit).all()
    return reports
"""
with open(endpoints_path, "w", encoding="utf-8") as f:
    f.write(endpoints_content)

# 5. Create scheduler.py
scheduler_path = os.path.join(base_dir, "backend", "core", "scheduler.py")
scheduler_content = """from apscheduler.schedulers.background import BackgroundScheduler
import logging
from backend.db.database import SessionLocal
from backend.db.models import SystemConfig, InsightReport
from backend.services.arxiv_fetcher import fetch_latest_ai_papers
from backend.services.news_fetcher import fetch_recent_business_news
from backend.core.gemini_client import gemini_client
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler()

def scheduled_insight_generation():
    logger.info("Starting scheduled insight generation job...")
    db = SessionLocal()
    try:
        config = db.query(SystemConfig).first()
        if not config:
            config = SystemConfig()
            db.add(config)
            db.commit()
            db.refresh(config)
            
        papers = fetch_latest_ai_papers(max_results=3, search_query=config.arxiv_query)
        news = fetch_recent_business_news(max_results=3, hours=24, rss_url=config.rss_url)
        
        report = gemini_client.generate_insight_report(papers=papers, news=news)
        
        if report.startswith("Error:") or report.startswith("Error:"):
            logger.error(f"Scheduled generation failed: {report}")
            return
            
        db_report = InsightReport(
            title=f"AI Business Insights (Auto) - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            markdown_content=report
        )
        db.add(db_report)
        db.commit()
        logger.info("Scheduled insight generated and saved successfully.")
    except Exception as e:
        logger.error(f"Error in scheduled job: {e}")
    finally:
        db.close()

def start_scheduler():
    global _scheduler
    db = SessionLocal()
    try:
        config = db.query(SystemConfig).first()
        if not config:
            interval = 24
        else:
            interval = config.schedule_interval_hours
    finally:
        db.close()

    if _scheduler.running:
        _scheduler.remove_all_jobs()
    else:
        _scheduler.start()
        logger.info("APScheduler started.")
        
    _scheduler.add_job(
        scheduled_insight_generation,
        'interval',
        hours=interval,
        id='auto_insight_job',
        replace_existing=True
    )
    logger.info(f"Scheduled job configured to run every {interval} hours.")
"""
with open(scheduler_path, "w", encoding="utf-8") as f:
    f.write(scheduler_content)

# 6. Update main.py to integrate scheduler
main_path = os.path.join(base_dir, "backend", "main.py")
main_content = """from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api.endpoints import router as insight_router
from backend.db.database import engine, Base
from backend.core.scheduler import start_scheduler
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Research x Business Insight API",
    description="Backend MVP for AI Business Insights",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    start_scheduler()

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
"""
with open(main_path, "w", encoding="utf-8") as f:
    f.write(main_content)

# 7. Update frontend index.html and style.css and app.js
index_path = os.path.join(base_dir, "frontend", "index.html")
with open(index_path, "r", encoding="utf-8") as f:
    index_html = f.read()

settings_btn = '''
            <div class="header-actions">
                <button id="generateBtn" class="primary-btn">
                    <span class="btn-text">Generate New Insight</span>
                    <div class="loader hidden"></div>
                </button>
                <button id="settingsBtn" class="secondary-btn">⚙️ Settings</button>
            </div>
'''
import re
index_html = re.sub(
    r'<button id="generateBtn" class="primary-btn">.*?</button>',
    settings_btn,
    index_html,
    flags=re.DOTALL
)

settings_modal = '''
    <!-- Settings Modal -->
    <div id="settingsModal" class="modal hidden">
        <div class="modal-content glass-panel" style="max-width: 500px;">
            <span class="close-btn" id="closeSettingsBtn">&times;</span>
            <h2>System Settings</h2>
            <div class="settings-form">
                <div class="form-group">
                    <label>arXiv Search Query</label>
                    <input type="text" id="arxivQueryInput" />
                </div>
                <div class="form-group">
                    <label>Tech News RSS URL</label>
                    <input type="text" id="rssUrlInput" />
                </div>
                <div class="form-group">
                    <label>Auto-Generate Interval (Hours)</label>
                    <input type="number" id="intervalInput" min="1" max="168" />
                </div>
                <button id="saveSettingsBtn" class="primary-btn" style="width: 100%; justify-content: center; margin-top: 1rem;">Save Settings</button>
            </div>
        </div>
    </div>
'''
index_html = index_html.replace('<script src="app.js"></script>', settings_modal + '\n    <script src="app.js"></script>')

with open(index_path, "w", encoding="utf-8") as f:
    f.write(index_html)

style_path = os.path.join(base_dir, "frontend", "style.css")
with open(style_path, "a", encoding="utf-8") as f:
    f.write("""
.header-actions {
    display: flex;
    justify-content: center;
    gap: 1rem;
    align-items: center;
}

.secondary-btn {
    background-color: transparent;
    color: #cbd5e1;
    border: 1px solid #475569;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.secondary-btn:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
}

.settings-form .form-group {
    margin-bottom: 1.5rem;
    text-align: left;
}

.settings-form label {
    display: block;
    margin-bottom: 0.5rem;
    color: #94a3b8;
    font-size: 0.9rem;
}

.settings-form input {
    width: 100%;
    padding: 0.75rem;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid #475569;
    border-radius: 6px;
    color: white;
    font-size: 1rem;
    font-family: 'Inter', sans-serif;
}

.settings-form input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
}
""")

app_js_path = os.path.join(base_dir, "frontend", "app.js")
app_js_content = """
(function() {
    try {
        const generateBtn = document.getElementById('generateBtn');
        const settingsBtn = document.getElementById('settingsBtn');
        const reportsContainer = document.getElementById('reportsContainer');
        const reportCount = document.getElementById('reportCount');
        const errorBox = document.getElementById('errorBox');
        
        const modal = document.getElementById('reportModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const closeBtn = document.querySelector('.close-btn');

        const settingsModal = document.getElementById('settingsModal');
        const closeSettingsBtn = document.getElementById('closeSettingsBtn');
        const saveSettingsBtn = document.getElementById('saveSettingsBtn');

        const arxivQueryInput = document.getElementById('arxivQueryInput');
        const rssUrlInput = document.getElementById('rssUrlInput');
        const intervalInput = document.getElementById('intervalInput');

        fetchReports();

        if (generateBtn) generateBtn.addEventListener('click', generateInsight);
        if (settingsBtn) settingsBtn.addEventListener('click', openSettings);
        if (saveSettingsBtn) saveSettingsBtn.addEventListener('click', saveSettings);
        
        if (closeBtn) closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
        if (closeSettingsBtn) closeSettingsBtn.addEventListener('click', () => settingsModal.classList.add('hidden'));

        window.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.add('hidden');
            if (e.target === settingsModal) settingsModal.classList.add('hidden');
        });

        async function openSettings() {
            try {
                const res = await fetch('/api/v1/settings');
                if (res.ok) {
                    const data = await res.json();
                    arxivQueryInput.value = data.arxiv_query;
                    rssUrlInput.value = data.rss_url;
                    intervalInput.value = data.schedule_interval_hours;
                }
            } catch (err) {
                console.error('Failed to load settings', err);
            }
            settingsModal.classList.remove('hidden');
        }

        async function saveSettings() {
            const btnText = saveSettingsBtn.textContent;
            saveSettingsBtn.textContent = 'Saving...';
            saveSettingsBtn.disabled = true;

            try {
                const res = await fetch('/api/v1/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        arxiv_query: arxivQueryInput.value,
                        rssUrl: rssUrlInput.value, // BUG: Needs to be rss_url
                        rss_url: rssUrlInput.value,
                        schedule_interval_hours: parseInt(intervalInput.value)
                    })
                });
                if (!res.ok) throw new Error('Failed to save settings');
                settingsModal.classList.add('hidden');
            } catch (err) {
                showError(err.message);
            } finally {
                saveSettingsBtn.textContent = btnText;
                saveSettingsBtn.disabled = false;
            }
        }

        async function fetchReports() {
            try {
                const res = await fetch('/api/v1/insights');
                if (!res.ok) throw new Error('Failed to fetch reports. Status: ' + res.status);
                
                const reports = await res.json();
                renderReports(reports);
            } catch (err) {
                console.error(err);
                showError('Error loading reports: ' + err.message);
            }
        }

        async function generateInsight() {
            setLoading(true);
            try {
                const res = await fetch('/api/v1/generate-insight', { method: 'POST' });
                if (!res.ok) {
                    const errorData = await res.json().catch(() => ({}));
                    throw new Error(errorData.detail || 'Generation failed with status ' + res.status);
                }
                await fetchReports();
            } catch (err) {
                console.error(err);
                showError('Error generating: ' + err.message);
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
                let previewText = report.markdown_content ? report.markdown_content.replace(/[#*`]/g, '').substring(0, 150) + '...' : '';

                card.innerHTML = `
                    <h3>${report.title}</h3>
                    <div class="date">${dateStr}</div>
                    <div class="preview">${previewText}</div>
                `;
                card.addEventListener('click', () => openReport(report));
                reportsContainer.appendChild(card);
            });
        }

        function openReport(report) {
            modalTitle.textContent = report.title;
            if (typeof marked !== 'undefined') {
                modalBody.innerHTML = marked.parse(report.markdown_content || '');
            } else {
                modalBody.innerHTML = '<pre>' + (report.markdown_content || '') + '</pre>';
            }
            modal.classList.remove('hidden');
        }

        function setLoading(isLoading) {
            if (!generateBtn) return;
            const btnText = generateBtn.querySelector('.btn-text');
            const loader = generateBtn.querySelector('.loader');
            
            generateBtn.disabled = isLoading;
            if (isLoading) {
                btnText.textContent = 'Generating...';
                if(loader) loader.classList.remove('hidden');
            } else {
                btnText.textContent = 'Generate New Insight';
                if(loader) loader.classList.add('hidden');
            }
        }

        function showError(msg) {
            if(!errorBox) return;
            errorBox.textContent = msg;
            errorBox.classList.remove('hidden');
            setTimeout(() => {
                errorBox.classList.add('hidden');
            }, 5000);
        }
    } catch(e) {
        const eb = document.getElementById('errorBox');
        if(eb) {
            eb.textContent = 'Critical JS Error: ' + e.message;
            eb.classList.remove('hidden');
        }
    }
})();
"""
with open(app_js_path, "w", encoding="utf-8") as f:
    f.write(app_js_content)

print("Phase 2 deployment script finished.")
