"""Delivery Module - Sends briefing via Telegram or Email"""

from dotenv import load_dotenv; load_dotenv(); import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class TelegramDelivery:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send(self, message: str) -> bool:
        try:
            chunks = self._chunk_message(message, 4000)
            for i, chunk in enumerate(chunks):
                header = "\U0001F4E2 *AI MORNING BRIEFING*\U0001F310\n" if i == 0 else "\n_(continued...)_\n"
                full = header + chunk
                resp = requests.post(
                    f"{self.base_url}/sendMessage",
                    json={"chat_id": self.chat_id, "text": full,
                          "parse_mode": "HTML", "disable_web_page_preview": True},
                    timeout=30)
                if resp.status_code != 200:
                    print(f"Telegram error: {resp.text}")
                    return False
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
            split_at = message.rfind("\n\n", 0, max_size)
            if split_at == -1:
                split_at = max_size
            chunks.append(message[:split_at])
            message = message[split_at:].lstrip()
        return chunks

class EmailDelivery:
    def __init__(self):
        self.server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.to_email = os.getenv("EMAIL_TO", self.username)

    def send(self, subject, body):
        try:
            msg = MIMEMultipart('alternative')
            msg["Subject"] = subject
            msg["From"] = self.username
            msg["To"] = self.to_email
            msg.attach(MIMEText(body, 'plain'))
            html = body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html = "<html><body style='font-family:Arial;'>" + html + "</body></html>"
            msg.attach(MIMEText(html, 'html'))
            with smtplib.SMTP(self.server, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            print("Email: Sent")
            return True
        except Exception as e:
            print(f"Email failed: {e}")
            return False

def deliver(briefing, method="telegram"):
    date_str = datetime.now().strftime("%Y-%m-%d")
    if method == "telegram":
        return TelegramDelivery().send(briefing)
    elif method == "email":
        return EmailDelivery().send(f"AI Briefing - {date_str}", briefing)
    return False

if __name__ == "__main__":
    test = "\U0001F680 *Test*\U0001F680 Agent is working!"
    TelegramDelivery().send(test)
