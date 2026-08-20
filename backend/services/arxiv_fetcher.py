import requests
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict

# ロギングの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

ARXIV_API_URL = "http://export.arxiv.org/api/query"

def fetch_latest_ai_papers(max_results: int = 5, search_query: str = "cat:cs.AI OR cat:cs.CL OR cat:cs.CV") -> List[Dict[str, str]]:
    """
    arXiv APIを呼び出し、AI関連（AI, NLP, CV）の最新論文を取得する。
    
    Args:
        max_results (int): 取得する最大件数 (デフォルト: 5)
        
    Returns:
        List[Dict[str, str]]: 論文のタイトルと要約（Abstract）を含む辞書のリスト
    """
    # 検索クエリ: cat:cs.AI OR cat:cs.CL OR cat:cs.CV
    # search_query is now an argument
    
    params = {
        "search_query": search_query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results
    }
    
    logger.info(f"arXivから論文を取得中... (クエリ: {search_query})")
    
    papers = []
    try:
        response = requests.get(ARXIV_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        # XMLのパース
        root = ET.fromstring(response.content)
        
        # Atomネームスペース
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        entries = root.findall('atom:entry', ns)
        for entry in entries:
            title_el = entry.find('atom:title', ns)
            summary_el = entry.find('atom:summary', ns)
            
            title = title_el.text.strip() if title_el is not None else "No Title"
            # 要約の改行をスペースに置換して整形
            summary = summary_el.text.strip().replace('\n', ' ') if summary_el is not None else "No Summary"
            
            papers.append({
                "title": title,
                "summary": summary
            })
            
        logger.info(f"arXivから {len(papers)} 件の論文を取得しました。")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"arXiv APIの通信に失敗しました: {e}")
    except ET.ParseError as e:
        logger.error(f"arXiv APIレスポンスのXMLパースに失敗しました: {e}")
    except Exception as e:
        logger.error(f"arXiv論文取得中に予期せぬエラーが発生しました: {e}")
        
    return papers

# テスト用実行ブロック
if __name__ == "__main__":
    latest_papers = fetch_latest_ai_papers(3)
    for i, paper in enumerate(latest_papers, 1):
        print(f"[{i}] {paper['title']}")
