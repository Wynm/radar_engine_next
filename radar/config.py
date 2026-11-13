"""Typed environment configuration for the modular radar."""
from dataclasses import dataclass
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class Settings:
    mode: str = "normal"
    gemini_api_key: str = ""
    github_token: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    reports_dir: Path = ROOT / "reports"
    memory_path: Path = ROOT / "memory.json"

    @classmethod
    def from_env(cls, mode: str | None = None) -> "Settings":
        selected = mode or os.getenv("RADAR_MODE", "normal")
        if selected not in {"normal", "full", "weekly"}:
            selected = "normal"
        return cls(
            mode=selected,
            gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
            github_token=os.getenv("GITHUB_TOKEN", "").strip(),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
        )
