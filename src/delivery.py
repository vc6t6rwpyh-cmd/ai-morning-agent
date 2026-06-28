"""
SEAN'S TELEGRAM DELIVERY
"""
import os
import requests
from datetime import datetime


class TelegramDelivery:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send(self, message: str) -> bool:
        try:
            chunks = self._chunk_message(message, 3800)
            for i, chunk in enumerate(chunks):
                if i == 0:
                    header = (
                        f"📻 *AI BRIEF PODCAST - Daily News*\n"
                        f"🎙️ *Prepared for: Dr. Sean Watts*\n"
                        f"🕐 {datetime.now().strftime('%A, %B %d, %Y')}\n"
                        f"{'━' * 30}\n\n"
                    )
                    chunk = header + chunk
                if i > 0:
                    chunk = "_(continued...)_\n\n" + chunk
                resp = requests.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": chunk,
                        "parse_mode": "Markdown",
                        "disable_web_page_preview": False,
                    },
                    timeout=30
                )
                if resp.status_code != 200:
                    print(f"Telegram error: {resp.text}")
            print(f"Telegram: Sent {len(chunks)} message(s)")
            return True
        except Exception as e:
            print(f"Telegram failed: {e}")
            return False

    def _chunk_message(self, message, max_size):
        if len(message) <= max_size:
            return [message]
        chunks = []
        while message:
            if len(message) <= max_size:
                chunks.append(message)
                break
            split_at = message.rfind('\n\n', 0, max_size)
            if split_at == -1:
                split_at = message.rfind('\n', 0, max_size)
            if split_at == -1:
                split_at = max_size
            chunks.append(message[:split_at])
            message = message[split_at:].lstrip()
        return chunks


def deliver(briefing, method="telegram"):
    if method == "telegram":
        return TelegramDelivery().send(briefing)
    return False
