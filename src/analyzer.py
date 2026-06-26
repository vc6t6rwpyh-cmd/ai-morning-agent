"""
AI Analysis Engine - FREE version using Groq API
Uses Llama 3.1 70B via Groq's generous free tier
"""

from dotenv import load_dotenv; load_dotenv(); import os
from groq import Groq
from typing import List, Dict
from datetime import datetime

class AIAnalyzer:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    SYSTEM_PROMPT = """You are a senior business intelligence analyst preparing a morning briefing for a management consultant.

Your task: Analyze the provided news articles and create a structured, professional briefing that:

1. IDENTIFIES key trends and patterns across multiple sources
2. HIGHLIGHTS stories with strategic business implications
3. CONNECTS dots between seemingly unrelated developments
4. PROVIDES context on why each story matters for business decision-making
5. SEPARATES Vietnam-specific news from global developments

Tone: Professional yet accessible. Write as if briefing a smart executive who values clarity over jargon.

Structure the output with these exact sections:
- EXECUTIVE SUMMARY (3-4 bullet points of the most important developments)
- VIETNAM SPOTLIGHT (2-3 key stories affecting Vietnam's business/tech landscape)
- GLOBAL AI LANDSCAPE (major AI developments and their business implications)
- TECHNOLOGY & BUSINESS (significant tech/business news with analysis)
- ECONOMIC INDICATORS (market moves, policy changes, macro trends)
- WHAT TO WATCH (emerging stories or trends that may develop further)

Rules:
- Be specific, not vague. Name companies, people, and numbers when available.
- Explain WHY something matters, not just WHAT happened.
- Cross-reference related stories to show pattern recognition.
- Keep total length to approximately 800-1000 words.
- Use bullet points for readability.
- Include source attribution for key claims."""

    def analyze(self, articles: List[Dict]) -> str:
        """Generate briefing from collected articles using FREE Groq API"""
        input_text = self._format_articles(articles)
        print("Sending to Groq (FREE) for analysis...")

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"Here are today's news articles. Create the morning briefing:\n\n{input_text}"}
            ],
            temperature=0.5,
            max_tokens=2000
        )

        briefing = response.choices[0].message.content
        print("Analysis complete! (Used FREE Groq API)")
        return briefing

    def _format_articles(self, articles: List[Dict]) -> str:
        lines = ["NEWS ARTICLES FOR ANALYSIS:", "=" * 50, ""]
        by_category = {}
        for a in articles:
            cat = a["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(a)
        for category, items in by_category.items():
            lines.append(f"\n--- {category.upper()} ({len(items)} articles) ---")
            for item in items[:10]:
                lines.append(f"Title: {item['title']}")
                lines.append(f"Source: {item['source']}")
                if item["summary"]:
                    lines.append(f"Summary: {item['summary'][:200]}")
                lines.append("")
        return "\n".join(lines)

if __name__ == "__main__":
    from collector import NewsCollector
    collector = NewsCollector()
    articles = collector.collect_all()
    analyzer = AIAnalyzer()
    briefing = analyzer.analyze(articles)
    print("\n" + "=" * 60)
    print("GENERATED BRIEFING (FREE):")
    print("=" * 60)
    print(briefing[:500] + "...")
