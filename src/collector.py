"""
SEAN'S CBC RADIO NEWS COLLECTOR
Fetches: CBC Top Stories, World, Business, Technology, Canada
"""
import feedparser
import requests
import re
from datetime import datetime, timedelta
from typing import List, Dict


class NewsCollector:
    def __init__(self):
        self.cutoff_date = datetime.now() - timedelta(hours=48)

    RSS_FEEDS = [
        {"name": "CBC Top Stories", "url": "https://www.cbc.ca/webfeed/rss/rss-topstories"},
        {"name": "CBC World News", "url": "https://www.cbc.ca/webfeed/rss/rss-world"},
        {"name": "CBC Business", "url": "https://www.cbc.ca/webfeed/rss/rss-business"},
        {"name": "CBC Technology", "url": "https://www.cbc.ca/webfeed/rss/rss-technology"},
        {"name": "CBC Canada", "url": "https://www.cbc.ca/webfeed/rss/rss-canada"},
        {"name": "CBC British Columbia", "url": "https://www.cbc.ca/webfeed/rss/rss-canada-britishcolumbia"},
        {"name": "CBC Toronto", "url": "https://www.cbc.ca/webfeed/rss/rss-canada-toronto"},
        {"name": "CBC Ottawa", "url": "https://www.cbc.ca/webfeed/rss/rss-canada-ottawa"},
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
                    "summary": self._clean_html(entry.get("summary", entry.get("description", "")))[:300],
                    "source": source["name"],
                    "published": published or datetime.now(),
                    "category": self._categorize(source["name"]),
                })
        except Exception as e:
            print(f"  RSS Error {source['name']}: {e}")
        return articles

    def _parse_date(self, entry):
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                return datetime(*entry.published_parsed[:6])
        except:
            pass
        return datetime.now()

    def _clean_html(self, raw: str) -> str:
        clean = re.sub(r'<[^>]+>', '', raw)
        return clean.strip()

    def _categorize(self, source_name: str) -> str:
        name = source_name.lower()
        if "business" in name:
            return "business"
        if "technology" in name:
            return "technology"
        if "world" in name:
            return "world"
        if "top" in name:
            return "headlines"
        return "canada"

    def collect_all(self):
        all_articles = []
        print("=" * 50)
        print("SEAN'S CBC RADIO NEWS AGENT")
        print("=" * 50)
        for source in self.RSS_FEEDS:
            articles = self.fetch_rss(source)
            all_articles.extend(articles)
            print(f"  {source['name']}: {len(articles)} articles")
        all_articles.sort(key=lambda x: x['published'], reverse=True)
        print(f"\nTOTAL ARTICLES: {len(all_articles)}")
        print("=" * 50)
        return all_articles
