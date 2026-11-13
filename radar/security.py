"""Heuristic review helpers. These checks are not a security certification."""
import re

PATTERNS = [
    (r"base64\.b64decode\s*\(", "dynamic Base64 decoding"),
    (r"\b(eval|exec)\s*\(", "dynamic code execution"),
    (r"(?:curl|wget)\s+[^\n]+\|\s*(?:sh|bash)", "piped remote shell script"),
    (r"(?:\.ssh/id_rsa|wallet\.dat|xmrig|stratum\+tcp)", "sensitive-data/mining indicator"),
]


def review(text: str) -> str:
    flags = [label for pattern, label in PATTERNS if re.search(pattern, text, re.I)]
    return "Review indicators: " + ", ".join(flags) if flags else "No known pattern matched; not a safety guarantee"
