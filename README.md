# Autonomous Tech Radar

Three implementations are planned for this repository so you can choose the right balance between capability, maintainability, and runtime:

1. **Production** — the default single-file engine (`radar_engine.py`), with bounded network requests, persistent state, source adapters, reports, optional Gemini analysis and Telegram notifications. Generated code is saved for review and is never executed by the radar.
2. **Professional / modular** — a maintainable package (`radar/`) with focused modules, typed configuration, test seams, and the same behavior split by responsibility.
3. **Fast / lightweight** — `radar_engine_fast.py`, a reduced-dependency, bounded collector for quick scheduled runs; it skips expensive optional analysis and deep page fetching.

## Status

These variants are not considered complete until the repository contains their implementation and the CI checks pass. Never add API keys or bot tokens to tracked files; configure them as environment variables or GitHub Actions secrets.

## Modes

- `normal`: popular / high-signal discoveries.
- `full`: relaxed discovery filters.
- `weekly`: synthesize recent reports.

## Local checks

```sh
python -m py_compile radar_engine.py radar_engine_fast.py
python -m unittest discover -s tests -v
```

See the relevant implementation and workflow for the exact environment variables and deployment instructions.


**//**
# Autonomous Tech Radar

Technology opportunity discovery with three complementary implementations:

- **Production single-file engine** — `radar_engine.py`, standard library only; bounded GitHub, Hacker News and Hugging Face collection, optional Gemini analysis, reports, persistent memory, Telegram notifications, weekly synthesis. Generated/downloaded code is never executed.
- **Professional modular edition** — `python -m radar [normal|full|weekly]`; package under `radar/` with configuration, sources, security review, analysis, reporting and orchestration separated for maintainability.
- **Fast edition** — `python radar_engine_fast.py`; bounded GitHub-only scan and Markdown output, no LLM call or notification request.

## Run

Python 3.11+; no third-party packages are needed.

```bash
python radar_engine.py normal
python radar_engine.py full
python radar_engine.py weekly
python -m radar normal
python radar_engine_fast.py
python -m unittest discover -s tests -v
