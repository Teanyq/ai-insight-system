import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(r"C:\ai-insight\backend\db\database.py")))
print("BASE_DIR:", BASE_DIR)
print("DB URL:", f"sqlite:///{os.path.join(BASE_DIR, 'insights.db')}")

from sqlalchemy import create_engine
engine = create_engine(f"sqlite:///{os.path.join(BASE_DIR, 'insights.db')}")
print("Engine URL:", engine.url)
