"""Application orchestration for the modular radar."""
import logging
from typing import Any
from .analysis import analyze
from .config import Settings
from .reporting import notify, write_report
from .security import review
from .sources import collect

LOG = logging.getLogger(__name__)


def run(settings: Settings) -> list[dict[str, Any]]:
    items = collect(settings)
    for item in items:
        item["security"] = review(item["title"] + " " + item["description"])
        item["analysis"] = analyze(item, settings)
    path = write_report(items, settings)
    notify(items, settings)
    LOG.info("Collected %d items; report written to %s", len(items), path)
    return items
