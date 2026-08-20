import sqlite3
import os

db_path = r"C:\ai-insight\backend\insights.db"
if not os.path.exists(db_path):
    print("Database does not exist at:", db_path)
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE insight_reports ADD COLUMN markdown_content_detailed TEXT;")
        conn.commit()
        print("Successfully added markdown_content_detailed column.")
    except sqlite3.OperationalError as e:
        print("Error altering table (maybe it already exists?):", e)
    finally:
        conn.close()
