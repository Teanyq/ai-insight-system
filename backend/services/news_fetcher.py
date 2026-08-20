import feedparser
import logging
from typing import List, Dict
from datetime import datetime, timedelta, timezone
from time import mktime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

# 例としてTechCrunchのRSSフィードを利用
RSS_FEED_URL = "https://techcrunch.com/feed/"

def fetch_recent_business_news(max_results: int = 3, hours: int = 24, rss_url: str = "https://techcrunch.com/feed/") -> List[Dict[str, str]]:
    """
    RSSフィードから直近のAIやSaaS関連のビジネスニュースを取得する。
    
    Args:
        max_results (int): 取得する最大件数
        hours (int): 過去何時間以内の記事を取得するか
        
    Returns:
        List[Dict[str, str]]: ニュースのタイトル、概要、リンクを含む辞書のリスト
    """
    logger.info(f"RSSフィードからニュースを取得中... ({rss_url})")
    news_items = []
    
    try:
        feed = feedparser.parse(rss_url)
        
        if feed.bozo:
            logger.error(f"RSSフィードのパースに失敗しました: {feed.bozo_exception}")
            # 完全にパース失敗した場合は空リストを返す
            if not feed.entries:
                return []

        # 現在時刻 (UTC) とタイムリミット
        now = datetime.now(timezone.utc)
        time_limit = now - timedelta(hours=hours)
        
        # フィルタリング用のキーワード
        keywords = ["ai", "artificial intelligence", "saas", "machine learning", "startup", "tech"]
        
        for entry in feed.entries:
            # 投稿時刻のチェック
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_time = datetime.fromtimestamp(mktime(entry.published_parsed), timezone.utc)
                if published_time < time_limit:
                    continue # 指定時間より古い記事はスキップ
            
            title = entry.title if hasattr(entry, 'title') else ""
            summary = entry.summary if hasattr(entry, 'summary') else ""
            link = entry.link if hasattr(entry, 'link') else ""
            
            # 簡易的なキーワードマッチング（タイトルまたはサマリーにキーワードが含まれるか）
            content_lower = (title + " " + summary).lower()
            if any(keyword in content_lower for keyword in keywords):
                # HTMLタグがsummaryに含まれる場合があるため、簡易に除去またはそのまま利用
                news_items.append({
                    "title": title,
                    "summary": summary[:200] + "..." if len(summary) > 200 else summary, # 長すぎる場合はカット
                    "link": link
                })
                
                if len(news_items) >= max_results:
                    break
                    
        logger.info(f"{len(news_items)} 件の関連ビジネスニュースを取得しました。")
        
    except Exception as e:
        logger.error(f"ニュース取得中に予期せぬエラーが発生しました: {e}")
        
    return news_items
