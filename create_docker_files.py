import os

base_dir = r"C:\ai-insight"

req_content = """fastapi==0.103.1
uvicorn==0.23.2
sqlalchemy==2.0.20
google-genai==0.3.0
python-dotenv==1.0.0
apscheduler==3.10.4
feedparser==6.0.10
arxiv==1.4.8
"""
with open(os.path.join(base_dir, "requirements.txt"), "w", encoding="utf-8") as f:
    f.write(req_content)

dockerfile_content = """# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
with open(os.path.join(base_dir, "Dockerfile"), "w", encoding="utf-8") as f:
    f.write(dockerfile_content)

docker_compose_content = """version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      # Mount the sqlite db so it persists between container restarts
      - ./backend/insights.db:/app/backend/insights.db
    env_file:
      - .env
    restart: unless-stopped
"""
with open(os.path.join(base_dir, "docker-compose.yml"), "w", encoding="utf-8") as f:
    f.write(docker_compose_content)

env_example_content = """# === AI Insight Engine - Environment Variables ===
# Copy this file to .env and fill in your actual values.

# Your Gemini API Key (Required)
GEMINI_API_KEY=your_gemini_api_key_here
"""
with open(os.path.join(base_dir, ".env.example"), "w", encoding="utf-8") as f:
    f.write(env_example_content)

print("Created all Docker deployment files.")
