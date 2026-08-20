import os
endpoints_content = '''from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session

from backend.services.arxiv_fetcher import fetch_latest_ai_papers
from backend.services.news_fetcher import fetch_recent_business_news
from backend.core.gemini_client import gemini_client
from backend.db.database import get_db
from backend.db.models import InsightReport

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

@router.post("/generate-insight", response_model=InsightResponse)
async def generate_insight(db: Session = Depends(get_db)):
    logger.info("Insight generation API called.")
    try:
        papers = fetch_latest_ai_papers(max_results=3)
        news = fetch_recent_business_news(max_results=3, hours=24)
        
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
'''
with open(r'C:\ai-insight\backend\api\endpoints.py', 'w', encoding='utf-8') as f:
    f.write(endpoints_content)

main_content = '''from fastapi import FastAPI
from backend.api.endpoints import router as insight_router
from backend.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Research x Business Insight API",
    description="Backend MVP for AI Business Insights",
    version="1.0.0"
)

app.include_router(insight_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "status": "running",
        "message": "AI Insight System Backend is running. Please access /docs for Swagger UI."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
'''
with open(r'C:\ai-insight\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(main_content)

models_content = '''from sqlalchemy import Column, Integer, String, Text, DateTime
from backend.db.database import Base
from datetime import datetime, timezone

class InsightReport(Base):
    __tablename__ = "insight_reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    markdown_content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
'''
with open(r'C:\ai-insight\backend\db\models.py', 'w', encoding='utf-8') as f:
    f.write(models_content)

print('Files rewritten safely.')
