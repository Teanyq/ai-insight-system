from sqlalchemy import Column, Integer, String, Text, DateTime
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

class UsedPaper(Base):
    __tablename__ = "used_papers"
    
    id = Column(Integer, primary_key=True, index=True)
    paper_title = Column(String, index=True, unique=True)
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
