# System Architecture

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
