"""Network helpers and source adapters for the modular radar."""
import json
import urllib.parse
import urllib.request
from typing import Any
from .config import Settings

DOMAINS = {
    "AI and automation": "(ai-agent OR automation OR workflow OR llm OR mcp-server)",
    "Micro-SaaS": "(micro-saas OR saas-boilerplate OR niche-tool OR api-wrapper)",
    "Data and commerce": "(ecommerce OR price-tracker OR web-scraper OR market-analysis)",
}


def get_json(url: str, settings: Settings, timeout: int = 15) -> Any:
    headers = {"User-Agent": "AutonomousTechRadar/1.0", "Accept": "application/vnd.github+json"}
    if settings.github_token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def github(settings: Settings) -> list[dict[str, Any]]:
    from datetime import datetime, timedelta, timezone
    days = 7 if settings.mode == "normal" else 1
    created = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    found = []
    for domain, terms in DOMAINS.items():
        q = f"{terms} created:>={created} stars:>={'50' if settings.mode == 'normal' else '0'}"
        params = urllib.parse.urlencode({"q": q, "sort": "stars" if settings.mode == "normal" else "updated", "order": "desc", "per_page": 8})
        try:
            response = get_json("https://api.github.com/search/repositories?" + params, settings)
            for repo in response.get("items", [])[:1 if settings.mode == "normal" else 2]:
                found.append({"uid": f"gh_{repo['id']}", "source": "GitHub", "domain": domain,
                              "title": repo["full_name"], "url": repo["html_url"],
                              "description": repo.get("description") or "No description",
                              "metrics": f"{repo.get('stargazers_count', 0)} stars", "stars": repo.get("stargazers_count", 0)})
        except Exception:
            # Keep source failures isolated; the engine can continue with other adapters.
            continue
    return found


def hacker_news(settings: Settings) -> list[dict[str, Any]]:
    feed = "topstories" if settings.mode == "normal" else "newstories"
    try:
        ids = get_json(f"https://hacker-news.firebaseio.com/v0/{feed}.json", settings)[:30]
    except Exception:
        return []
    found = []
    for story_id in ids:
        try:
            item = get_json(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", settings)
            if not item or not item.get("url") or not item.get("title"):
                continue
            found.append({"uid": f"hn_{story_id}", "source": "Hacker News", "domain": "Technology",
                          "title": item["title"], "url": item["url"], "description": item["title"],
                          "metrics": f"{item.get('score', 0)} points", "stars": item.get("score", 0)})
            if len(found) >= 1:
                break
        except Exception:
            continue
    return found


def collect(settings: Settings) -> list[dict[str, Any]]:
    items = github(settings) + hacker_news(settings)
    return list({item["uid"]: item for item in items}.values())
