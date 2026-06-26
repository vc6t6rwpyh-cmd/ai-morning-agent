"""
News Collector - Fetches news from RSS feeds
Covers: Vietnam news, Global AI/Tech/Business/Economy
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict

class NewsCollector:
    def __init__(self):
        self.articles = []
        self.cutoff_date = datetime.now() - timedelta(hours=48)

    VIETNAM_RSS = [
        {"name": "VnExpress (Tech)", "url": "https://vnexpress.net/rss/so-hoa.rss"},
        {"name": "VnExpress (Business)", "url": "https://vnexpress.net/rss/kinh-doanh.rss"},
        {"name": "Tuoi Tre (Tech)", "url": "https://tuoitre.vn/rss/cong-nghe.rss"},
        {"name": "Thanh Nien (Tech)", "url": "https://thanhnien.vn/rss/cong-nghe.rss"},
        {"name": "VietnamNet (Business)", "url": "https://vietnamnet.vn/rss/kinh-doanh.rss"},
    ]

    GLOBAL_RSS = [
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
        {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
        {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
        {"name": "Ars Technica", "url": "https://arstechnica.com/feed/"},
        {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/"},
    ]

    def fetch_rss(self, source: Dict) -> List[Dict]:
        articles = []
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:8]:
                published = self._parse_date(entry)
                if published and published < self.cutoff_date:
                    continue
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", entry.get("description", ""))[:300],
                    "source": source["name"],
                    "published": published or datetime.now(),
                    "category": self._categorize(source["name"]),
                })
        except Exception as e:
            print(f"RSS Error {source['name']}: {e}")
        return articles

    def fetch_hacker_news(self) -> List[Dict]:
        articles = []
        try:
            resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
            story_ids = resp.json()[:10]
            for sid in story_ids:
                story_resp = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=10)
                story = story_resp.json()
                if story and story.get("title"):
                    articles.append({
                        "title": story["title"],
                        "link": story.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "summary": "",
                        "source": "Hacker News",
                        "published": datetime.now(),
                        "category": "technology",
                    })
        except Exception as e:
            print(f"HN Error: {e}")
        return articles

    def _parse_date(self, entry):
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6])
        except:
            pass
        return datetime.now()

    def _categorize(self, source_name: str) -> str:
        if any(x in source_name.lower() for x in ["vnexpress", "tuoi tre", "thanh nien", "vietnamnet"]):
            return "vietnam"
        if any(x in source_name.lower() for x in ["techcrunch", "verge", "wired", "ars", "hacker"]):
            return "technology"
        if "venturebeat" in source_name.lower():
            return "ai"
        return "business"

    def collect_all(self) -> List[Dict]:
        all_articles = []
        print("Fetching Vietnam news...")
        for source in self.VIETNAM_RSS:
            articles = self.fetch_rss(source)
            all_articles.extend(articles)
            print(f"  {source['name']}: {len(articles)} articles")
        print("Fetching global tech news...")
        for source in self.GLOBAL_RSS:
            articles = self.fetch_rss(source)
            all_articles.extend(articles)
            print(f"  {source['name']}: {len(articles)} articles")
        print("Fetching Hacker News...")
        articles = self.fetch_hacker_news()
        all_articles.extend(articles)
        print(f"  Hacker News: {len(articles)} articles")
        all_articles.sort(key=lambda x: x["published"], reverse=True)
        print(f"\nTotal articles collected: {len(all_articles)}")
        return all_articles

if __name__ == "__main__":
    collector = NewsCollector()
    articles = collector.collect_all()
    print(f"\nFirst 3 articles:")
    for a in articles[:3]:
        print(f"- [{a['category']}] {a['title'][:80]}...")
