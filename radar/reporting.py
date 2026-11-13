"""Markdown report and Telegram output helpers."""
import html
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .config import Settings


def write_report(items: list[dict[str, Any]], settings: Settings) -> Path:
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
    parts = [f"# Radar report — {stamp} UTC\n", f"Mode: {settings.mode}\n"]
    for item in items:
        parts.append(f"## {item['title']}\n\n- Source: {item['source']}\n- URL: {item['url']}\n- Metrics: {item['metrics']}\n\n{item.get('analysis', '')}\n")
    path = settings.reports_dir / f"report_{settings.mode}_{stamp}.md"
    path.write_text("\n---\n".join(parts), encoding="utf-8")
    return path


def notify(items: list[dict[str, Any]], settings: Settings) -> None:
    if not settings.telegram_bot_token or not settings.telegram_chat_id or not items:
        return
    chunks = [f"📡 <b>Radar update</b> — {html.escape(settings.mode)}"]
    for item in items:
        chunks.append(f"\n\n<b>{html.escape(item['title'])}</b>\n{html.escape(item['metrics'])}\n"
                      f"<a href=\"{html.escape(item['url'], quote=True)}\">Open source</a>\n\n"
                      f"{html.escape(item.get('analysis', '')[:1200])}")
    token, chat = settings.telegram_bot_token, settings.telegram_chat_id
    for text in chunks:
        payload = json.dumps({"chat_id": chat, "text": text[:3900], "parse_mode": "HTML",
                              "disable_web_page_preview": True}).encode()
        request = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=payload,
                                         headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=20):
                pass
        except Exception:
            continue
