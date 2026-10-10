"""Voice-over for one video project: script.json -> voice.wav + words.json.

Steps (all cached, so re-running after editing one sentence only redoes that one):
  1. split each scene's "say" into segments (sentence ends and "|" pauses)
  2. synthesize N candidates per segment with VieNeu (spoken text from pron.py)
  3. transcribe every candidate with faster-whisper, score it against the text,
     keep the best, trim silence using the word timestamps
  4. join segments with fixed pauses into voice.wav and map every display word
     to its start/end time (words.json)

Usage:
  python voice.py <project_dir> [--candidates 2] [--asr large-v3-turbo] [--device cpu]
Run with the plugin venv (~/.vn-video-studio/venv). Pure helpers import no
heavy libraries so tests can load this module.

Candidate scoring and silence trimming follow the CES AI News kit
(asr_pick.py / align.py); word mapping uses difflib like that kit.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pron import load_overrides, spoken  # noqa: E402

SR = 48000
LEAD_IN = 0.5
PAUSE_SENTENCE = 0.35
PAUSE_BAR = 0.55
PAUSE_SCENE = 0.7
TAIL = 0.8
WEAK = 0.85
TEMPS = (0.7, 0.8, 0.9)

_WORD = re.compile(r"[\wÀ-ỹ][\wÀ-ỹ'’./%$-]*", re.UNICODE)
_VI = set("àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ")


# ---------- pure helpers ----------

def split_segments(scene_id: str, say: str) -> list[dict]:
    """Split on "|" (long pause) and sentence ends. Returns [{id, text, pause_after}]."""
    out: list[dict] = []
    bars = [b.strip() for b in say.split("|")]
    for bi, bar in enumerate(bars):
        sentences = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", bar) if s.strip()]
        for si, s in enumerate(sentences):
            last_in_bar = si == len(sentences) - 1
            pause = PAUSE_BAR if (last_in_bar and bi < len(bars) - 1) else PAUSE_SENTENCE
            out.append({"id": f"{scene_id}_{len(out) + 1}", "text": s, "pause_after": pause})
    return out


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\sÀ-ỹ]", " ", text.lower())).strip()


_VI_INITIAL = re.compile(r"^(ngh|ch|gh|gi|kh|ng|nh|ph|qu|th|tr|[bcdghklmnpqrstvx])?[aeiouy]")
_VI_FINAL = re.compile(r"[aeiouy](ch|ng|nh|[cmnpt])?$")


def has_english(text: str) -> bool:
    """True if a word cannot be Vietnamese: acronym, letters f/j/w/z, or an
    initial/final consonant cluster Vietnamese does not allow (Claude, Code-x, Agent)."""
    for w in display_words(text):
        if re.fullmatch(r"[A-Z0-9]{2,}", w):
            return True
        low = w.lower()
        if set(low) & _VI or not re.fullmatch(r"[a-z]+", low):
            continue
        if re.search(r"[fjwz]", low) or not _VI_INITIAL.match(low) or not _VI_FINAL.search(low):
            return True
    return False


def similarity(heard: str, expected: str) -> float:
    return difflib.SequenceMatcher(None, norm(heard), norm(expected)).ratio()


def display_words(text: str) -> list[str]:
    return [w.rstrip(".-/") for w in _WORD.findall(text) if w.rstrip(".-/")]


def map_words(display: list[str], overrides: dict[str, str], heard: list[dict]) -> list[dict]:
    """Give each display word a start/end from ASR words.

    Each display word expands to one or more spoken tokens (pron.spoken per word);
    spoken tokens are matched to ASR tokens with difflib; a display word takes the
    span of its matched tokens. Unmatched words are interpolated between neighbours.
    """
    owner: list[int] = []
    tokens: list[str] = []
    for i, w in enumerate(display):
        for t in norm(spoken(w, overrides)).split() or [norm(w)]:
            tokens.append(t)
            owner.append(i)
    asr_tokens = [norm(h["w"]) for h in heard]
    starts: list[float | None] = [None] * len(display)
    ends: list[float | None] = [None] * len(display)
    sm = difflib.SequenceMatcher(None, tokens, asr_tokens, autojunk=False)
    for a, b, size in sm.get_matching_blocks():
        for k in range(size):
            i, h = owner[a + k], heard[b + k]
            starts[i] = h["start"] if starts[i] is None else min(starts[i], h["start"])
            ends[i] = h["end"] if ends[i] is None else max(ends[i], h["end"])
    t0 = heard[0]["start"] if heard else 0.0
    t1 = heard[-1]["end"] if heard else 0.0
    known = [i for i, s in enumerate(starts) if s is not None]
    for i in range(len(display)):
        if starts[i] is not None:
            continue
        prev = max((k for k in known if k < i), default=None)
        nxt = min((k for k in known if k > i), default=None)
        a = ends[prev] if prev is not None else t0
        b = starts[nxt] if nxt is not None else t1
        lo = prev if prev is not None else -1
        hi = nxt if nxt is not None else len(display)
        frac = (i - lo) / (hi - lo)
        frac2 = (i + 1 - lo) / (hi - lo)
        starts[i] = a + (b - a) * frac
        ends[i] = a + (b - a) * frac2
    return [{"w": w, "start": round(starts[i], 3), "end": round(ends[i], 3)} for i, w in enumerate(display)]


def cache_key(voice: str, text: str, temp: float, k: int) -> str:
    return hashlib.sha1(f"{voice}|{text}|{temp}|{k}".encode("utf-8")).hexdigest()[:16]


# ---------- heavy steps ----------

def synthesize(project: Path, script: dict, n_cand: int) -> list[dict]:
    import numpy as np
    import soundfile as sf
    from vieneu import Vieneu

    overrides = load_overrides(script.get("pron"))
    voice = script.get("voice", "Ngọc Huyền")
    cache = project / "voice" / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    tts = None
    segments = []
    for scene in script["scenes"]:
        for seg in split_segments(scene["id"], scene["say"]):
            seg["scene"] = scene["id"]
            seg["spoken"] = spoken(seg["text"], overrides)
            n = max(n_cand, 3) if has_english(seg["text"]) else n_cand
            seg["candidates"] = []
            for k in range(n):
                temp = TEMPS[k % len(TEMPS)]
                path = cache / f"{cache_key(voice, seg['spoken'], temp, k)}.wav"
                if not path.exists():
                    if tts is None:
                        tts = Vieneu()
                    audio = np.asarray(tts.infer(seg["spoken"], voice=voice, temperature=temp), dtype=np.float32)
                    sf.write(path, audio, getattr(tts, "sample_rate", SR))
                seg["candidates"].append(str(path.relative_to(project)))
            segments.append(seg)
            print(f"synth {seg['id']}: {len(seg['candidates'])} bản", flush=True)
    return segments


def load_16k(path: Path):
    """Decode ourselves: newer PyAV rejects faster-whisper's `metadata_errors` argument."""
    from math import gcd

    import numpy as np
    import soundfile as sf
    from scipy.signal import resample_poly

    audio, sr = sf.read(path, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    g = gcd(16000, sr)
    return resample_poly(audio, 16000 // g, sr // g).astype(np.float32)


def score(project: Path, segments: list[dict], model_name: str, device: str) -> None:
    from faster_whisper import WhisperModel

    scores_path = project / "voice" / "scores.json"
    cached = json.loads(scores_path.read_text(encoding="utf-8")) if scores_path.exists() else {}
    model = None
    for seg in segments:
        best = None
        for rel in seg["candidates"]:
            if rel not in cached:
                if model is None:
                    model = WhisperModel(model_name, device=device, compute_type="int8")
                parts, _ = model.transcribe(load_16k(project / rel), language="vi", word_timestamps=True,
                                            beam_size=5, condition_on_previous_text=False)
                words = [{"w": w.word.strip(), "start": w.start, "end": w.end}
                         for p in parts for w in (p.words or [])]
                heard = " ".join(w["w"] for w in words)
                cached[rel] = {"heard": heard, "words": words, "score": round(similarity(heard, seg["spoken"]), 3)}
                scores_path.write_text(json.dumps(cached, ensure_ascii=False, indent=1), encoding="utf-8")
            if best is None or cached[rel]["score"] > cached[best]["score"]:
                best = rel
        seg["chosen"] = best
        seg["score"] = cached[best]["score"]
        seg["heard"] = cached[best]["words"]
        flag = "WEAK" if seg["score"] < WEAK else "ok"
        print(f"score {seg['id']}: {seg['score']:.2f} {flag} | {cached[best]['heard']}", flush=True)


def build(project: Path, script: dict, segments: list[dict]) -> dict:
    import numpy as np
    import soundfile as sf

    overrides = load_overrides(script.get("pron"))
    pieces = [np.zeros(int(LEAD_IN * SR), dtype=np.float32)]
    t = LEAD_IN
    words, segs_out, scenes = [], [], {}
    for idx, seg in enumerate(segments):
        audio, sr = sf.read(project / seg["chosen"], dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        if sr != SR:
            raise SystemExit(f"Sample rate {sr} khác {SR}: {seg['chosen']}")
        heard = seg["heard"]
        dur = len(audio) / SR
        a = max(0.0, heard[0]["start"] - 0.06) if heard else 0.0
        b = min(dur, heard[-1]["end"] + 0.15) if heard else dur
        clip = audio[int(a * SR): int(b * SR)]
        rel = [{"w": h["w"], "start": h["start"] - a, "end": h["end"] - a} for h in heard]
        start = t
        for m in map_words(display_words(seg["text"]), overrides, rel):
            words.append({"scene": seg["scene"], "seg": seg["id"], "w": m["w"],
                          "start": round(start + m["start"], 3), "end": round(start + m["end"], 3)})
        pieces.append(clip)
        t += len(clip) / SR
        segs_out.append({"id": seg["id"], "scene": seg["scene"], "text": seg["text"], "start": round(start, 3),
                         "end": round(t, 3), "score": seg["score"], "weak": seg["score"] < WEAK})
        sc = scenes.setdefault(seg["scene"], {"id": seg["scene"], "start": round(start, 3)})
        sc["end"] = round(t, 3)
        last = idx == len(segments) - 1
        next_scene = None if last else segments[idx + 1]["scene"]
        gap = TAIL if last else (PAUSE_SCENE if next_scene != seg["scene"] else seg["pause_after"])
        pieces.append(np.zeros(int(gap * SR), dtype=np.float32))
        t += gap
    voice = np.concatenate(pieces)
    peak = float(np.abs(voice).max()) or 1.0
    sf.write(project / "voice.wav", voice * (0.89 / peak), SR, subtype="PCM_16")
    result = {"total": round(len(voice) / SR, 3), "scenes": list(scenes.values()), "segments": segs_out, "words": words}
    (project / "words.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="script.json -> voice.wav + words.json")
    ap.add_argument("project")
    ap.add_argument("--candidates", type=int, default=2)
    ap.add_argument("--asr", default="large-v3-turbo")
    ap.add_argument("--device", default="cpu")
    a = ap.parse_args()
    project = Path(a.project).resolve()
    script = json.loads((project / "script.json").read_text(encoding="utf-8"))
    segments = synthesize(project, script, a.candidates)
    score(project, segments, a.asr, a.device)
    res = build(project, script, segments)
    weak = [s["id"] for s in res["segments"] if s["weak"]]
    print(f"VOICEDONE total={res['total']}s segments={len(res['segments'])} weak={weak or 'không'}")


if __name__ == "__main__":
    main()
