import os
from pathlib import Path
from dotenv import load_dotenv

# config.py のあるディレクトリ(core)から見て親ディレクトリ(backend)の .env を絶対パスで指定
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    """
    アプリケーション全体の設定を管理するクラス
    """
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

settings = Settings()
