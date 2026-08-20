# Agent Handover Document

## Project Status
This is the **AI Research x Business Insight System**, currently at the MVP (Phase 1) stage.
The system is fully functional: it fetches AI papers from arXiv, tech news from RSS (TechCrunch), and uses Google Gemini (gemini-3.5-flash) to generate markdown insights.

## Quick Start
1. Workspace: C:\ai-insight
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
