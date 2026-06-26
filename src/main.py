#!/usr/bin/env python3
"""
AI Morning Intelligence Agent - Main Orchestrator
Uses FREE Groq API for analysis. Zero cost to operate.
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.collector import NewsCollector
from src.analyzer import AIAnalyzer
from src.delivery import deliver

log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"agent_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()])
logger = logging.getLogger(__name__)

def run_agent(delivery_method="telegram"):
    start = datetime.now()
    logger.info("=" * 60)
    logger.info("AI AGENT STARTING (FREE MODE)")
    logger.info("=" * 60)
    try:
        logger.info("[STAGE 1] Collecting news...")
        articles = NewsCollector().collect_all()
        if not articles:
            logger.warning("No articles. Exiting.")
            return
        logger.info(f"Collected {len(articles)} articles")

        logger.info("[STAGE 2] AI analysis (FREE Groq API)...")
        briefing = AIAnalyzer().analyze(articles)

        logger.info(f"[STAGE 3] Delivering via {delivery_method}...")
        success = deliver(briefing, method=delivery_method)

        elapsed = (datetime.now() - start).total_seconds()
        if success:
            logger.info(f"\u2705 SUCCESS! Delivered in {elapsed:.1f}s")
        else:
            logger.error("\u274c Delivery failed")
    except Exception as e:
        logger.error(f"Agent failed: {e}", exc_info=True)
    logger.info("=" * 60)

if __name__ == "__main__":
    method = sys.argv[1] if len(sys.argv) > 1 else "telegram"
    run_agent(delivery_method=method)
