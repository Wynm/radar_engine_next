#!/usr/bin/env python3
"""Fast, bounded radar profile: GitHub signals, local Markdown, no LLM calls."""
from __future__ import annotations
import argparse
import json
import logging
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG = logging.getLogger("radar.fast")
QUERIES = (
    "(ai-agent OR automation OR llm) stars:>=20",
    "(micro-saas OR saas-boilerplate OR api-wrapper) stars:>=10",
    "(ecommerce OR price-tracker OR market-analysis) stars:>=10",
)


def get(url: str, headers: dict[str, str] | None = None) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "AutonomousTechRadarFast/1.0", **(headers or {})})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def run() -> int:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    records, seen = [], set()
    for query in QUERIES:
        params = urllib.parse.urlencode({"q": f"{query} created:>={cutoff}", "sort": "stars", "order": "desc", "per_page": 5})
        try:
            payload = get("https://api.github.com/search/repositories?" + params, headers)
            for repo in payload.get("items", [])[:3]:
                if repo["id"] in seen or repo.get("fork") or repo.get("archived"):
                    continue
                seen.add(repo["id"])
                records.append({"name": repo["full_name"], "url": repo["html_url"],
                                "description": repo.get("description") or "No description",
                                "stars": repo.get("stargazers_count", 0), "language": repo.get("language")})
        except Exception as exc:
            LOG.warning("Fast GitHub query failed: %s", exc)
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
    output = reports / f"report_fast_{stamp}.md"
    lines = [f"# Fast Radar — {stamp} UTC", "", f"Found {len(records)} repositories.", ""]
    for item in records:
        lines += [f"## [{item['name']}]({item['url']})", "", item["description"],
                  f"", f"Stars: {item['stars']} · Language: {item['language'] or 'mixed'}", ""]
    output.write_text("\n".join(lines), encoding="utf-8")
    LOG.info("Saved %s (%d results)", output, len(records))
    return 0


def main() -> int:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        return run()
    except Exception:
        LOG.exception("Fast radar failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
