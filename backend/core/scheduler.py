from apscheduler.schedulers.background import BackgroundScheduler
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
