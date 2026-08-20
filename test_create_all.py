from backend.api.endpoints import router as insight_router
from backend.db.database import engine, Base
print("Registered tables before create_all:", Base.metadata.tables.keys())
Base.metadata.create_all(bind=engine)
print("Tables after create_all:", Base.metadata.tables.keys())
