from backend.db.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
print("Tables:", inspector.get_table_names())
for table in inspector.get_table_names():
    print(f"\nColumns in {table}:")
    for column in inspector.get_columns(table):
        print(f"- {column['name']}: {column['type']}")

import os
print("\nEngine database path:")
print(engine.url.database)
print("File exists?", os.path.exists(engine.url.database) if engine.url.database else "No db")
