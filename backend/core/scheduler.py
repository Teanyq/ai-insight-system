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
        from backend.api.endpoints import run_insight_generation_task
        run_insight_generation_task(db)
        logger.info("Scheduled insight generated and saved successfully.")
    except Exception as e:
        logger.error(f"Error in scheduled job: {e}")
    finally:
        db.close()

def run_healing_agent():
    logger.info("Starting healing agent to fix malformed reports...")
    db = SessionLocal()
    try:
        reports = db.query(InsightReport).filter(InsightReport.title == 'AI Business Insights').all()
        for report in reports:
            logger.info(f"Healing report ID {report.id}...")
            new_title = gemini_client.fix_report_title(report.markdown_content)
            if new_title and new_title != "AI Business Insights":
                report.title = new_title
                logger.info(f"Report ID {report.id} healed. New title: {new_title}")
        db.commit()
    except Exception as e:
        logger.error(f"Error in healing agent: {e}")
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
    
    _scheduler.add_job(
        run_healing_agent,
        'interval',
        hours=12,
        id='healing_agent_job',
        replace_existing=True
    )
    
    logger.info(f"Scheduled job configured to run every {interval} hours. Healing agent runs every 12 hours.")
