"""storyboard.json + words.json -> timeline.json for the composition.

- Scenes tile the whole track: each starts a little before its first word, the
  first starts at 0, the last ends at the voice's end.
- Anchors resolve a keyword ("kw", words exactly as in the narration) to a time.
  A keyword that is not found is a hard error ("KW miss"), never a silent default.
- Captions: one line per chunk, at most 44 characters, held at least 1.8 s
  (shortened only to avoid overlapping the next chunk).

Usage: python timeline.py <project_dir> [--fps 30]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "voice"))
from voice import display_words, norm  # noqa: E402

SIZES = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080)}
SCENE_LEAD = 0.25
CAP_CHARS = 44
CAP_MIN = 1.8


def scene_spans(word_scenes: list[dict], order: list[str], total: float) -> list[dict]:
    starts = {s["id"]: s["start"] for s in word_scenes}
    spans = []
    for i, sid in enumerate(order):
        start = 0.0 if i == 0 else max(0.0, starts[sid] - SCENE_LEAD)
        spans.append({"id": sid, "start": round(start, 3)})
    for i, sp in enumerate(spans):
        sp["end"] = spans[i + 1]["start"] if i + 1 < len(spans) else round(total, 3)
    return spans


def find_kw(words: list[dict], kw: str, nth: int = 1) -> float | None:
    """Start time of the nth occurrence of kw (consecutive words) in words."""
    target = [norm(t) for t in display_words(kw)]
    toks = [norm(w["w"]) for w in words]
    seen = 0
    for i in range(len(toks) - len(target) + 1):
        if toks[i:i + len(target)] == target:
            seen += 1
            if seen == nth:
                return words[i]["start"]
    return None


def captions(segments: list[dict], words: list[dict]) -> list[dict]:
    out = []
    for seg in segments:
        sw = [w for w in words if w["seg"] == seg["id"]]
        raw = seg["text"].split()
        chunks, cur, cur_words, wi = [], [], [], 0
        for tok in raw:
            n = len(display_words(tok))
            tw = sw[wi:wi + n]
            wi += n
            if cur and len(" ".join(cur + [tok])) > CAP_CHARS:
                chunks.append((cur, cur_words))
                cur, cur_words = [], []
            cur.append(tok)
            cur_words += tw
        if cur:
            chunks.append((cur, cur_words))
        for toks, tw in chunks:
            if not tw:
                continue
            out.append({"text": " ".join(toks), "start": tw[0]["start"], "end": tw[-1]["end"]})
    for i, c in enumerate(out):
        limit = out[i + 1]["start"] if i + 1 < len(out) else c["end"] + CAP_MIN
        c["end"] = round(min(max(c["end"], c["start"] + CAP_MIN), limit), 3)
    return out


def build(project: Path, fps: int = 30) -> tuple[dict, list[str]]:
    sb = json.loads((project / "storyboard.json").read_text(encoding="utf-8"))
    wj = json.loads((project / "words.json").read_text(encoding="utf-8"))
    width, height = SIZES[sb.get("aspect", "9:16")]
    order = [s["id"] for s in sb["scenes"]]
    missing_voice = [sid for sid in order if sid not in {s["id"] for s in wj["scenes"]}]
    if missing_voice:
        raise SystemExit(f"Cảnh không có lời đọc trong words.json: {missing_voice}")
    spans = {s["id"]: s for s in scene_spans(wj["scenes"], order, wj["total"])}
    misses = []
    scenes = []
    for sc in sb["scenes"]:
        sw = [w for w in wj["words"] if w["scene"] == sc["id"]]
        anchors = {}
        for a in sc.get("anchors", []):
            t = find_kw(sw, a["kw"], a.get("nth", 1))
            if t is None:
                misses.append(f"{sc['id']}.{a['id']}: \"{a['kw']}\"")
                continue
            anchors[a["id"]] = round(max(spans[sc["id"]]["start"], t + a.get("off", -0.1)), 3)
        scenes.append({**spans[sc["id"]], "anchors": anchors})
    tl = {"fps": fps, "width": width, "height": height, "duration": wj["total"], "style": sb.get("style"),
          "scenes": scenes, "captions": captions(wj["segments"], wj["words"]), "words": wj["words"]}
    (project / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    return tl, misses


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()
    tl, misses = build(Path(a.project).resolve(), a.fps)
    for m in misses:
        print(f"KW miss: {m}")
    print(f"TIMELINE duration={tl['duration']}s scenes={len(tl['scenes'])} captions={len(tl['captions'])}")
    sys.exit(1 if misses else 0)


if __name__ == "__main__":
    main()
