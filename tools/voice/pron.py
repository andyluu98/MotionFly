"""Rewrite display text into what VieNeu should read.

VieNeu v3 Turbo is bilingual (sea-g2p), so English words are read natively; only
symbols and units need spelling out. Per-word fixes come from an overrides map
(script.json "pron" plus the user's global file). Display text, subtitles and
on-screen labels always keep the original wording.

Adapted from reference/vn-short-video-tts/normalize_vietnamese_text.py (the
owner's earlier project).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

GLOBAL_OVERRIDES = Path.home() / ".vn-video-studio" / "pron.json"

_UNITS = {"T": "nghìn tỷ", "B": "tỷ", "M": "triệu", "K": "nghìn"}


def _currency(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        unit = _UNITS.get((m.group(2) or "").upper(), "")
        return f"{m.group(1)} {unit} đô la".replace("  ", " ")

    return re.sub(r"\$\s*(\d+(?:[.,]\d+)?)\s*([BMKT])?\b", repl, text)


def _symbols(text: str) -> str:
    text = re.sub(r"<\s*(\d)", r"dưới \1", text)
    text = re.sub(r">=?\s*(\d)", r"trên \1", text)
    text = re.sub(r"~\s*(\d)", r"khoảng \1", text)
    text = re.sub(r"\s*(->|→|=>)\s*", " sang ", text)
    text = re.sub(r"(\d+(?:[.,]\d+)?)\s*%", r"\1 phần trăm", text)
    text = re.sub(r"\s*&\s*", " và ", text)
    return text


def load_overrides(extra: dict[str, str] | None = None) -> dict[str, str]:
    out: dict[str, str] = {}
    if GLOBAL_OVERRIDES.exists():
        raw = json.loads(GLOBAL_OVERRIDES.read_text(encoding="utf-8"))
        out.update({k: v for k, v in raw.items() if not k.startswith("_")})
    if extra:
        out.update(extra)
    return out


def _apply_overrides(text: str, overrides: dict[str, str]) -> str:
    """Keys with an uppercase letter match case-sensitively ("AI" must not eat
    the Vietnamese "ai"); lowercase keys match case-insensitively. Longest first."""
    for key in sorted(overrides, key=len, reverse=True):
        flags = 0 if any(c.isupper() for c in key) else re.IGNORECASE
        text = re.sub(rf"(?<![\wÀ-ỹ]){re.escape(key)}(?![\wÀ-ỹ])", overrides[key], text, flags=flags)
    return text


def spoken(text: str, overrides: dict[str, str] | None = None) -> str:
    out = _currency(text)
    out = _symbols(out)
    out = _apply_overrides(out, overrides or {})
    return re.sub(r"\s+", " ", out).strip()


if __name__ == "__main__":
    for s in ["MCP giúp AI dùng công cụ", "Thị trường đạt $52.6B, tăng 46% mỗi năm", "Skill & Agent"]:
        print(s, "->", spoken(s, {"MCP": "em xi pi"}))
