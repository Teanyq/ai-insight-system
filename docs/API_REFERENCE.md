# API Reference

## POST /api/v1/generate-insight
Generates a new insight report, saves it to the SQLite database, and returns it.
- **Request Body**: None (Currently autonomous)
- **Response**:
  `json
  {
    "status": "success",
    "markdown_report": "# Insight...",
    "report_id": 1
  }
  `

## GET /api/v1/insights
Retrieves a paginated list of past insight reports from the database.
- **Query Params**: skip (int, default 0), limit (int, default 10)
- **Response**: Array of:
  `json
  {
    "id": 1,
    "title": "AI Business Insights - 2026-08-20 12:00",
    "markdown_content": "# Insight...",
    "created_at": "2026-08-20T12:00:00Z"
  }
  `
