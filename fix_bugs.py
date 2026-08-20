import os

base_dir = r"C:\ai-insight"

# 1. Fix news_fetcher.py
news_path = os.path.join(base_dir, "backend", "services", "news_fetcher.py")
with open(news_path, "r", encoding="utf-8") as f:
    news_code = f.read()

news_code = news_code.replace(
    'def fetch_recent_business_news(max_results: int = 3, hours: int = 24) -> List[Dict[str, str]]:',
    'def fetch_recent_business_news(max_results: int = 3, hours: int = 24, rss_url: str = "https://techcrunch.com/feed/") -> List[Dict[str, str]]:'
)
news_code = news_code.replace(
    'logger.info(f"RSSフィードからニュースを取得中... ({RSS_FEED_URL})")',
    'logger.info(f"RSSフィードからニュースを取得中... ({rss_url})")'
)
news_code = news_code.replace(
    'feed = feedparser.parse(RSS_FEED_URL)',
    'feed = feedparser.parse(rss_url)'
)

with open(news_path, "w", encoding="utf-8") as f:
    f.write(news_code)

# 2. Fix index.html
index_path = os.path.join(base_dir, "frontend", "index.html")
index_html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Insight Generator</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
    <div class="background-glow"></div>
    <div class="container">
        <header>
            <h1>AI Insight Engine</h1>
            <p>Bridging cutting-edge AI research with business strategy</p>
        </header>

        <main>
            <div id="errorBox" class="error-box hidden"></div>
            
            <section class="insights-section">
                <div class="section-header">
                    <h2>Latest Reports</h2>
                    <span id="reportCount" class="badge">0</span>
                </div>
                <div id="reportsContainer" class="reports-grid">
                    <!-- Reports will be dynamically injected here -->
                </div>
            </section>
        </main>
    </div>

    <!-- Modal for viewing full report -->
    <div id="reportModal" class="modal hidden">
        <div class="modal-content glass-panel">
            <span class="close-btn">&times;</span>
            <h2 id="modalTitle">Report</h2>
            <div id="modalBody" class="markdown-body"></div>
        </div>
    </div>

    <script src="public.js"></script>
</body>
</html>
"""
with open(index_path, "w", encoding="utf-8") as f:
    f.write(index_html_content)

print("Bugs fixed.")
