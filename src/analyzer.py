"""
SEAN'S AI BRIEF PODCAST ANALYZER
"""
import os
from groq import Groq
from typing import List, Dict
from datetime import datetime


class AIAnalyzer:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    SYSTEM_PROMPT = """You are the co-host of "AI BRIEF Podcast," delivering a professional daily news briefing for Dr. Sean Watts.

Create the briefing in THIS EXACT FORMAT:

📻 AI BRIEF PODCAST - DAILY NEWS DIGEST
For: Dr. Sean Watts
Date: [today's date]

=== HEADLINE STORIES ===
Top 3-4 biggest stories with context on WHY they matter

=== BUSINESS & ECONOMY ===
Market moves, deals, corporate news

=== WORLD NEWS ===
International developments

=== TECHNOLOGY & AI ===
Tech breakthroughs, AI developments

=== CANADA FOCUS ===
Canadian-specific news

=== WHAT TO WATCH ===
Emerging trends

RULES:
- Be specific: name companies, people, dollar amounts
- Explain WHY it matters, not just WHAT happened
- Connect related stories
- Professional podcast tone
- 800-1200 words"""

    def analyze(self, articles: List[Dict]) -> str:
        input_text = self._format_articles(articles)
        print("Sending to Groq for AI analysis...")
        response = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"Create today's AI BRIEF Podcast briefing:\n\n{input_text}"}
            ],
            temperature=0.5,
            max_tokens=2500
        )
        briefing = response.choices[0].message.content
        print("Analysis complete!")
        return briefing

    def _format_articles(self, articles: List[Dict]) -> str:
        lines = [f"DAILY INTELLIGENCE - {datetime.now().strftime('%Y-%m-%d')}", "=" * 50]
        by_category = {}
        for a in articles:
            cat = a.get("category", "general")
            by_category.setdefault(cat, []).append(a)
        cat_names = {
            "headlines": "HEADLINE STORIES",
            "business": "BUSINESS & ECONOMY",
            "world": "WORLD NEWS",
            "technology": "TECHNOLOGY & AI",
            "canada": "CANADA FOCUS",
        }
        for category, items in sorted(by_category.items(), key=lambda x: -len(x[1])):
            name = cat_names.get(category, category.upper())
            lines.extend([f"\n--- {name} ({len(items)} articles) ---"])
            for item in items[:8]:
                lines.append(f"\nTitle: {item['title']}")
                lines.append(f"Source: {item['source']}")
                if item.get("summary"):
                    lines.append(f"Summary: {item['summary'][:200]}")
        return "\n".join(lines)
