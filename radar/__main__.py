"""CLI entry point: python -m radar [normal|full|weekly]."""
import argparse
import logging
from .config import Settings
from .engine import run


def main() -> int:
    parser = argparse.ArgumentParser(description="Modular technology opportunity radar")
    parser.add_argument("mode", choices=("normal", "full", "weekly"), nargs="?", default=None)
    args = parser.parse_args()
    logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(message)s")
    run(Settings.from_env(args.mode))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
