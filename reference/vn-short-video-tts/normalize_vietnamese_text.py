"""Vietnamese text normalization for Google TTS.

Google Chirp3-HD vi-VN reads the text literally: "<5%" becomes "dấu bé năm
phần trăm" and "$52.6B" becomes "năm mươi hai phẩy sáu B". This module
rewrites those patterns into spoken Vietnamese before TTS sees them.

Order matters: currency/units → comparison symbols → acronyms → words.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

# Self-improving override dictionary: `pronunciation-overrides.json` lives
# next to this file. When Chirp3 mispronounces a word in a generated clip,
# we add one entry and every future clip gets it right. Loaded ONCE at
# module import so edits require a re-run of the pipeline (fine — each
# clip runs the pipeline fresh anyway).
_OVERRIDES_PATH = Path(__file__).resolve().parent / "pronunciation-overrides.json"
_OVERRIDES: dict[str, str] = {}  # lowercase-keyed, kept for pre-flight
_OVERRIDES_RAW: dict[str, str] = {}  # original casing, used for matching
if _OVERRIDES_PATH.exists():
    with _OVERRIDES_PATH.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    _OVERRIDES_RAW = {k: v for k, v in raw.items() if not k.startswith("_")}
    _OVERRIDES = {k.lower(): v for k, v in _OVERRIDES_RAW.items()}


def _spell_number(num_str: str) -> str:
    """Spell a small number for insertion into Vietnamese prose.

    Keep it natural-sounding; Google TTS reads plain digits fine.
    """
    return num_str  # let Google handle pure digits


def normalize_currency(text: str) -> str:
    """$52.6B → 52.6 tỷ đô la, $15T → 15 nghìn tỷ đô la, etc."""
    def repl(m: re.Match[str]) -> str:
        amount = m.group(1)
        unit = (m.group(2) or "").upper()
        unit_word = {
            "T": "nghìn tỷ",
            "B": "tỷ",
            "M": "triệu",
            "K": "nghìn",
        }.get(unit, "")
        return f"{amount} {unit_word} đô la".replace("  ", " ").strip()

    return re.sub(
        r"\$\s*(\d+(?:[.,]\d+)?)\s*([BMKT])?\b",
        repl,
        text,
    )


def normalize_comparisons(text: str) -> str:
    """Replace math/comparison symbols with spoken Vietnamese."""
    # "< 5%" or "<5%" → "dưới 5 phần trăm"
    text = re.sub(r"<\s*(\d)", r"dưới \1", text)
    # ">= 40%" → "trên 40 phần trăm" (loosely)
    text = re.sub(r">=?\s*(\d)", r"trên \1", text)
    # "~50%" → "khoảng 50"
    text = re.sub(r"~\s*(\d)", r"khoảng \1", text)
    # "→" or "->" → "lên"
    text = re.sub(r"\s*(->|→|=>)\s*", " lên ", text)
    return text


def normalize_percent(text: str) -> str:
    """40% → 40 phần trăm (but avoid double-converting)."""
    return re.sub(r"(\d+(?:[.,]\d+)?)\s*%", r"\1 phần trăm", text)


def normalize_year_range(text: str) -> str:
    """2025 – 2026 → năm 2025 đến năm 2026. Gives a smoother read."""
    return re.sub(
        r"(\b\d{4})\s*[–\-]\s*(\d{4}\b)",
        r"năm \1 đến năm \2",
        text,
    )


# English / tech acronyms → phonetic Vietnamese.
# Only applied to whole-word matches so "chat" doesn't eat "chất".
_ACRONYMS: dict[str, str] = {
    "AI": "ây ai",
    "API": "ây pi ai",
    "CAGR": "xi ây gi a",
    "B2B": "bê tu bê",
    "SaaS": "sát",
    "SDK": "ét đi kây",
    "CLI": "xi eo ai",
    "UI": "diu ai",
    "UX": "diu ích",
    "ROI": "a âu ai",
    "LLM": "eo eo em",
    "GPT": "gi pi ti",
    "IoT": "ai âu ti",
    "CEO": "xi i âu",
    "CTO": "xi ti âu",
    "KPI": "kây pi ai",
}

# English/brand words → Vietnamese phonetic (case-insensitive, whole-word).
_WORDS: dict[str, str] = {
    "agent": "ây-dần",
    "agents": "ây-dần",
    "chatbot": "chát bót",
    "bot": "bót",
    "blog": "blốc",
    "video": "vi-đi-ô",
    "youtube": "diu tup",
    "tiktok": "tích tốc",
    "facebook": "phây bút",
    "google": "gu gồ",
    "microsoft": "mai-cờ-rô-sóp",
    "openai": "ô-pen ây ai",
    "chatgpt": "chát-gi-pi-ti",
    "gartner": "gát-nờ",
    "mckinsey": "mặc kin-xi",
    "marketsandmarkets": "mác-két-en-mác-két",
    "app": "áp",
    "apps": "áp",
    "online": "on-lai",
    "offline": "óp-lai",
    "live": "lai",
    "team": "tim",
    "update": "áp-đết",
    "data": "đê-ta",
    "code": "cốt",
    "dev": "đép",
    "report": "ri-pọt",
}


def normalize_acronyms(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        return _ACRONYMS.get(m.group(0), m.group(0))

    # Case-sensitive for acronyms (all caps)
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in _ACRONYMS) + r")\b")
    return pattern.sub(repl, text)


def normalize_words(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        return _WORDS.get(m.group(0).lower(), m.group(0))

    pattern = re.compile(
        r"\b(" + "|".join(re.escape(k) for k in _WORDS) + r")\b",
        re.IGNORECASE,
    )
    return pattern.sub(repl, text)


# Vietnamese diacritic marks — if a word contains ANY of these, it's
# already Vietnamese and Chirp3 handles it reliably.
_VIETNAMESE_CHARS = set("àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ")


def find_foreign_words(text: str, known_overrides: set[str]) -> list[str]:
    """Return words likely to be proper nouns / brand names / English
    compound words that are NOT in the pronunciation override dictionary.

    Strict heuristic (minimize false positives):
    - starts with an uppercase letter (proper noun) OR contains an
      uppercase letter mid-word (camelCase / PascalCase brand)
    - contains no Vietnamese diacritic
    - length ≥ 4
    - not in known_overrides
    - not at sentence-start by itself (we still flag those — usually
      they're proper nouns in our narrations)

    Lowercase English words like "framework", "agent", "demo", "code"
    are intentionally NOT flagged — Chirp3 reads them acceptably in
    Vietnamese context, and filtering them was too noisy.
    """
    tokens = re.findall(r"[A-Za-zÀ-ỹ]+", text)
    seen: set[str] = set()
    out: list[str] = []
    for tok in tokens:
        key = tok.lower()
        if key in seen:
            continue
        seen.add(key)
        if len(tok) < 4:
            continue
        if any(c in _VIETNAMESE_CHARS for c in tok):
            continue  # has Vietnamese diacritic → safe
        if key in known_overrides:
            continue  # already overridden
        # Require uppercase signal (proper noun / brand)
        has_upper_first = tok[0].isupper()
        has_upper_mid = any(c.isupper() for c in tok[1:])
        if not (has_upper_first or has_upper_mid):
            continue
        out.append(tok)
    return out


def apply_pronunciation_overrides(text: str) -> str:
    """Replace user-approved problem words with Vietnamese phonetic spellings.

    Case-sensitivity rule: if the override KEY contains any uppercase
    letter, it's matched case-sensitively (so "AI" / "Ai" only match the
    exact casing, and the common Vietnamese word "ai" meaning "who" is
    left alone). All-lowercase keys are matched case-insensitively.

    Keys are sorted by length descending so longer keys (e.g. "how-to")
    win over shorter ones (e.g. "how").
    """
    if not _OVERRIDES:
        return text

    # Split into case-sensitive vs case-insensitive buckets. The raw JSON
    # holds the original keys; _OVERRIDES is keyed lowercase for lookup,
    # but we need to know the original form here — re-read keys from the
    # JSON each call? No, cache them alongside.
    # Quick: we rebuild from _OVERRIDES_RAW loaded below.
    cs_items = [(k, v) for k, v in _OVERRIDES_RAW.items() if any(c.isupper() for c in k)]
    ci_items = [(k, v) for k, v in _OVERRIDES_RAW.items() if not any(c.isupper() for c in k)]

    out = text

    # Case-sensitive pass (preserves user's exact key casing)
    if cs_items:
        cs_items.sort(key=lambda kv: len(kv[0]), reverse=True)
        cs_map = {k: v for k, v in cs_items}
        cs_pattern = re.compile(
            r"\b(" + "|".join(re.escape(k) for k, _ in cs_items) + r")\b"
        )
        out = cs_pattern.sub(lambda m: cs_map[m.group(0)], out)

    # Case-insensitive pass (traditional behaviour for lowercase keys)
    if ci_items:
        ci_items.sort(key=lambda kv: len(kv[0]), reverse=True)
        ci_map = {k.lower(): v for k, v in ci_items}
        ci_pattern = re.compile(
            r"\b(" + "|".join(re.escape(k) for k, _ in ci_items) + r")\b",
            re.IGNORECASE,
        )
        out = ci_pattern.sub(lambda m: ci_map[m.group(0).lower()], out)

    return out


def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize(text: str) -> str:
    """Run the full normalization pipeline in the right order.

    Pronunciation overrides (brand names, tech terms) are loaded from
    tts/pronunciation-overrides.json — empty file = no overrides = same
    behaviour as before. Add an entry when VieNeu reads a recurring word
    awkwardly (e.g. "HyperFrames" → "Hai-pờ Frêm").
    """
    out = text
    out = normalize_currency(out)
    out = normalize_comparisons(out)
    out = normalize_percent(out)
    out = normalize_year_range(out)
    out = apply_pronunciation_overrides(out)
    out = collapse_whitespace(out)
    return out


if __name__ == "__main__":
    samples = [
        "AI Agent sẽ thay đổi năm 2026",
        "Thị trường đạt $52.6B vào 2030",
        "<5% ứng dụng có AI Agent trong năm 2025",
        "Gartner dự báo $15T giao dịch B2B năm 2028",
        "Tăng trưởng CAGR 46.3% mỗi năm",
        "Từ 7.8 tỷ đô la năm 2025 lên 52.6 tỷ đô la năm 2030",
    ]
    for s in samples:
        print(f"IN : {s}\nOUT: {normalize(s)}\n")
