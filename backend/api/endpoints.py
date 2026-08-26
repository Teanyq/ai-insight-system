from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session

from backend.services.arxiv_fetcher import fetch_latest_ai_papers
from backend.services.news_fetcher import fetch_recent_business_news
from backend.core.gemini_client import gemini_client
from backend.services.twitter_client import twitter_client
from backend.db.database import get_db
from backend.db.models import InsightReport, SystemConfig, UsedPaper


from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import status
import secrets

security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "secret")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

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
    markdown_content_detailed: str | None = None
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
def get_settings(db: Session = Depends(get_db), username: str = Depends(verify_admin)):
    config = get_or_create_config(db)
    return SystemConfigSchema(
        arxiv_query=config.arxiv_query,
        rss_url=config.rss_url,
        schedule_interval_hours=config.schedule_interval_hours
    )

@router.post("/settings", response_model=SystemConfigSchema)
def update_settings(settings: SystemConfigSchema, db: Session = Depends(get_db), username: str = Depends(verify_admin)):
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

import os

def run_insight_generation_task(db: Session):
    config = get_or_create_config(db)
    
    raw_papers = fetch_latest_ai_papers(max_results=100, search_query=config.arxiv_query)
    used_titles = {p.paper_title for p in db.query(UsedPaper.paper_title).all()}
    papers = [p for p in raw_papers if p['title'] not in used_titles][:3]
    
    if not papers:
        logger.warning("No new papers found after filtering used ones.")
        raise HTTPException(status_code=404, detail="No new papers found.")
        
    news = fetch_recent_business_news(max_results=3, hours=24, rss_url=config.rss_url)
    
    report_text = gemini_client.generate_insight_report(papers=papers, news=news)
    
    if report_text.startswith("Error:"):
        logger.error(f"Failed to generate report: {report_text}")
        raise HTTPException(status_code=500, detail=report_text)
        
    parts = report_text.split("====DETAIL_SECTION====")
    overview = parts[0].strip()
    detailed = parts[1].strip() if len(parts) > 1 else ""
    tweet_text_raw = parts[2].strip() if len(parts) > 2 else ""
    
    title = "AI Business Insights"
    for line in overview.split('\n'):
        line_stripped = line.strip()
        if line_stripped.startswith('# ') or line_stripped.startswith('## '):
            title = line_stripped.replace('# ', '').replace('## ', '').replace('**', '').strip()
            break
            
    db_report = InsightReport(
        title=title,
        markdown_content=overview,
        markdown_content_detailed=detailed
    )
    db.add(db_report)
    for p in papers:
        db.add(UsedPaper(paper_title=p['title']))
    db.commit()
    db.refresh(db_report)
    
    # Post to X (Twitter)
    if tweet_text_raw:
        # Clean up tweet text by removing any markdown headers like "### PART 3..." if generated
        lines = tweet_text_raw.split('\n')
        clean_lines = [line for line in lines if not line.strip().startswith('###')]
        clean_tweet = '\n'.join(clean_lines).strip()
        
        app_url_raw = os.getenv("APP_URL", "").strip()
        # https:// 等を取り除く
        app_url = app_url_raw.replace("https://", "").replace("http://", "").replace("[", "").replace("]", "").rstrip("/")
        
        # 記事に直接飛べるようにクエリパラメータ ?id=... を付与
        url_text = f"\n\n詳細はこちら: {app_url}/?id={db_report.id}" if app_url else ""
            
        # Twitterの文字数計算: URLは23文字、全角は2文字分で合計280文字が上限。
        # ツイート本文(全角)は安全を期して115文字程度まで許容できる。
        if len(clean_tweet) > 115:
            clean_tweet = clean_tweet[:115]
            # 途切れて読みにくくなるのを防ぐため、最後の句点(。)や感嘆符(！)で丸める
            last_punct = max(clean_tweet.rfind('。'), clean_tweet.rfind('！'), clean_tweet.rfind('!'))
            if last_punct > 0:
                clean_tweet = clean_tweet[:last_punct+1]
            else:
                clean_tweet = clean_tweet[:112] + "..."
                
        clean_tweet += url_text
            
        twitter_client.post_tweet(clean_tweet)
        
    logger.info("Insight report generated and saved successfully.")
    return overview, db_report.id

@router.post("/generate-insight", response_model=InsightResponse)
async def generate_insight(db: Session = Depends(get_db), username: str = Depends(verify_admin)):
    logger.info("Insight generation API called via Admin UI.")
    try:
        overview, report_id = run_insight_generation_task(db)
        return InsightResponse(
            status="success",
            markdown_report=overview,
            report_id=report_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/run-daily-job")
async def run_daily_job(token: str, db: Session = Depends(get_db)):
    expected_token = os.getenv("CRON_SECRET", "my-secret-token")
    if token != expected_token:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    logger.info("Insight generation API called via Cron Job.")
    try:
        overview, report_id = run_insight_generation_task(db)
        return {"status": "success", "message": "Daily job executed successfully."}
    except Exception as e:
        logger.error(f"Daily job failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights", response_model=List[InsightReportSchema])
def get_insights(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    reports = db.query(InsightReport).order_by(InsightReport.created_at.desc()).offset(skip).limit(limit).all()
    return reports
