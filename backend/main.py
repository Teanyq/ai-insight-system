from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api.endpoints import router as insight_router
from backend.db.database import engine, Base
from backend.core.scheduler import start_scheduler
import os

# Create database tables
Base.metadata.create_all(bind=engine)

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

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

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import status, Depends, HTTPException
from fastapi.responses import FileResponse
import secrets

security = HTTPBasic()

def verify_admin_page(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "secret")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/admin", include_in_schema=False)
def admin_page(username: str = Depends(verify_admin_page)):
    return FileResponse(os.path.join(BASE_DIR, "backend", "templates", "admin.html"))

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {"status": "Frontend not found, but backend is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
