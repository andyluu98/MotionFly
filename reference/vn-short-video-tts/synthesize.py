"""Synthesize Vietnamese voice-over via local VieNeu-TTS (Gradio server).

Talks to a Gradio app running at http://localhost:7860 that exposes the
VieNeu-TTS model. Uses preset voice "Đoan (nữ miền Nam)" by default.

For each scene: derive narration, call the local TTS, concatenate audio
with a small silence gap, and write back measured durations so the
Remotion composition syncs perfectly.

Outputs:
    public/voice.wav              — concatenated mono wav
    public/idea-with-audio.json   — idea copy with real durations + audio ref

Usage:
    python tts/synthesize.py scripts/ai-agent-market-2026.json
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

from gradio_client import Client

from normalize_vietnamese_text import normalize, find_foreign_words, _OVERRIDES

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
VOICE_WAV = PUBLIC / "voice.wav"
OUT_JSON = PUBLIC / "idea-with-audio.json"

# Local Gradio TTS server
TTS_URL = "http://localhost:7860/"
VOICE_PRESET = "Doan"  # API value; UI label is "Đoan (nữ miền Nam)"
VIE_NEU_BACKBONE = os.environ.get("VIENEU_BACKBONE", "VieNeu-TTS-v2-Turbo (CPU)")
VIE_NEU_CODEC = os.environ.get("VIENEU_CODEC", "NeuCodec (Distill)")
VIE_NEU_DEVICE = os.environ.get("VIENEU_DEVICE", "Auto")
SCENE_GAP_SEC = 0.35
# News-style faster narration. 1.0 = natural, 1.15 = slightly faster,
# 1.25 = newsreader pace. Applied via ffmpeg atempo (pitch-preserving).
NARRATION_SPEED = 1.18


def derive_narration(scene: dict) -> str:
    """Build default narration text for a scene if `narration` is missing."""
    if "narration" in scene and scene["narration"]:
        return scene["narration"]
    t = scene.get("type", "")
    if t == "title":
        return f"{scene['title']}, {scene['subtitle']}."
    if t == "bigNumber":
        out = f"{scene['label']}, lên tới {scene['value']}"
        if scene.get("note"):
            out += f", {scene['note']}"
        return out + "."
    if t == "barChart":
        bars = scene.get("bars", [])
        if len(bars) >= 2:
            a, b = bars[0], bars[1]
            return (
                f"{scene['title']}: năm {a['label']} chỉ {a['display']}, "
                f"nhưng sang năm {b['label']} đã tăng vọt lên {b['display']}."
            )
        joined = ", ".join(f"{b['label']} {b['display']}" for b in bars)
        return f"{scene['title']}: {joined}."
    if t == "lineChart":
        pts = scene.get("points", [])
        if pts:
            first, last = pts[0], pts[-1]
            return (
                f"{scene['title']}: từ {first['value']} tỷ đô la năm {first['label']}, "
                f"thị trường tăng lên {last['value']} tỷ đô la vào năm {last['label']}."
            )
        return scene["title"]
    if t == "closing":
        return f"{scene['title']}. {scene['subtitle']}"
    if t == "quote":
        base = f"{scene['text']}. — {scene['author']}"
        if scene.get("role"):
            base += f", {scene['role']}"
        return base + "."
    if t == "bulletList":
        joined = ". ".join(item["text"] for item in scene.get("items", []))
        return f"{scene['title']}. {joined}."
    if t == "comparison":
        left = scene["left"]
        right = scene["right"]
        return (
            f"{scene['title']}. {left['label']}: {left['value']}."
            f" {right['label']}: {right['value']}."
        )
    if t == "timeline":
        events = scene.get("events", [])
        joined = ". ".join(f"{e['date']}: {e['label']}" for e in events)
        return f"{scene['title']}. {joined}."
    if t == "iconGrid":
        joined = ". ".join(item["label"] for item in scene.get("items", []))
        return f"{scene['title']}. {joined}."
    if t == "imageReveal":
        base = scene["title"]
        if scene.get("caption"):
            base += f". {scene['caption']}"
        return base + "."
    if t == "codeSnippet":
        # Don't narrate raw code — title only.
        return f"{scene['title']}."
    if t == "ranking":
        items = scene.get("items", [])
        joined = ". ".join(f"Hạng {item['rank']}: {item['label']}" for item in items)
        return f"{scene['title']}. {joined}."
    if t == "pullQuote":
        return scene["text"]
    return scene.get("title") or scene.get("label") or ""


def synthesize_one(client: Client, text: str, voice: str) -> tuple[bytes, int]:
    """Call local VieNeu-TTS. Returns (raw PCM16 mono bytes, sample_rate)."""
    result = client.predict(
        text=text,
        voice_choice=voice,
        custom_audio=None,
        custom_text="",
        generation_mode="Standard (Một lần)",
        use_batch=False,
        max_batch_size_run=1,
        temperature=0.5,
        max_chars_chunk=256,
        api_name="/synthesize_speech",
    )
    # result is (audio_filepath, status_str)
    audio_path = result[0] if isinstance(result, (list, tuple)) else result
    with wave.open(str(audio_path), "rb") as w:
        sr = w.getframerate()
        nch = w.getnchannels()
        sw = w.getsampwidth()
        frames = w.readframes(w.getnframes())
    if sw != 2:
        raise RuntimeError(f"expected 16-bit PCM, got {sw * 8}-bit")
    if nch == 2:
        # Downmix stereo → mono by picking left channel
        frames = b"".join(frames[i : i + 2] for i in range(0, len(frames), 4))
    return frames, sr


def write_wav(path: Path, pcm: bytes, sample_rate: int) -> float:
    """Write raw PCM16 mono bytes to a WAV file. Return duration seconds."""
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm)
    frames = len(pcm) // 2
    return frames / sample_rate


def synthesize(idea_path: Path) -> None:
    with idea_path.open("r", encoding="utf-8") as f:
        idea = json.load(f)

    PUBLIC.mkdir(parents=True, exist_ok=True)

    print(f"[tts] connecting to {TTS_URL}")
    client = Client(TTS_URL)

    # Fresh gradio_client sessions have an empty preset dropdown until
    # /load_model populates it. LMDeploy disabled — user's box lacks CUDA v12.1.
    print(f"[tts] loading model ({VIE_NEU_BACKBONE})...")
    client.predict(
        backbone_choice=VIE_NEU_BACKBONE,
        codec_choice=VIE_NEU_CODEC,
        device_choice=VIE_NEU_DEVICE,
        force_lmdeploy=False,
        custom_model_id="",
        custom_base_model=None,
        custom_hf_token="",
        api_name="/load_model",
    )
    voice = VOICE_PRESET
    print(f"[tts] using voice preset: {voice}")

    pieces: list[bytes] = []
    cursor = 0.0
    all_foreign: set[str] = set()
    sample_rate: int | None = None

    for i, scene in enumerate(idea["scenes"]):
        raw = derive_narration(scene)
        text = normalize(raw)
        foreign = find_foreign_words(text, set(_OVERRIDES.keys()))
        if foreign:
            all_foreign.update(foreign)
        print(f"[tts] {i + 1}/{len(idea['scenes'])} {scene['id']}: {text[:70]}")

        pcm, sr = synthesize_one(client, text, voice)
        if sample_rate is None:
            sample_rate = sr
        elif sr != sample_rate:
            raise RuntimeError(f"sample rate changed mid-stream: {sample_rate} → {sr}")

        # Audio PCM + silence gaps stay at natural speed; ffmpeg atempo
        # later shortens the whole concatenated wav by NARRATION_SPEED.
        # Scene durations must match the POST-speedup timeline.
        raw_dur = (len(pcm) // 2) / sample_rate
        dur = raw_dur / NARRATION_SPEED
        gap = SCENE_GAP_SEC / NARRATION_SPEED

        scene["durationSec"] = round(dur + gap, 3)
        scene["_narration"] = text
        scene["_audioStart"] = round(cursor, 3)
        scene["_audioEnd"] = round(cursor + dur, 3)
        cursor += dur + gap

        pieces.append(pcm)
        pieces.append(b"\x00\x00" * int(SCENE_GAP_SEC * sample_rate))

    if sample_rate is None:
        print("[tts] ERROR: no scenes to synthesize")
        sys.exit(1)

    full_pcm = b"".join(pieces)
    total = write_wav(VOICE_WAV, full_pcm, sample_rate)
    print(f"[tts] wrote {VOICE_WAV} ({total:.1f}s @ {sample_rate}Hz)")

    # News-style speedup: ffmpeg atempo preserves pitch. Skip if speed≈1.
    if abs(NARRATION_SPEED - 1.0) > 0.001:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            print(
                "[tts] ERROR: ffmpeg not found on PATH — required for narration speed-up.\n"
                "       Install with: winget install Gyan.FFmpeg  (or download from ffmpeg.org)"
            )
            sys.exit(1)
        else:
            tmp = VOICE_WAV.with_suffix(".tmp.wav")
            subprocess.run(
                [
                    ffmpeg, "-y", "-loglevel", "error",
                    "-i", str(VOICE_WAV),
                    "-filter:a", f"atempo={NARRATION_SPEED}",
                    str(tmp),
                ],
                check=True,
            )
            tmp.replace(VOICE_WAV)

            # Measure the ACTUAL wav after atempo (ffmpeg rounding can
            # leave it slightly off raw/SPEED) and rescale all scene
            # timestamps proportionally so HyperFrames visuals stay in sync.
            with wave.open(str(VOICE_WAV), "rb") as w:
                actual_total = w.getnframes() / w.getframerate()
            expected_total = cursor
            scale = actual_total / expected_total if expected_total > 0 else 1.0
            print(
                f"[tts] applied atempo={NARRATION_SPEED} → expected {expected_total:.2f}s, "
                f"actual {actual_total:.2f}s (rescale x{scale:.4f})"
            )
            if abs(scale - 1.0) > 0.001:
                for s in idea["scenes"]:
                    s["durationSec"] = round(s["durationSec"] * scale, 3)
                    if "_audioStart" in s:
                        s["_audioStart"] = round(s["_audioStart"] * scale, 3)
                    if "_audioEnd" in s:
                        s["_audioEnd"] = round(s["_audioEnd"] * scale, 3)
                cursor = actual_total

    idea["_totalSec"] = round(cursor, 3)
    idea["_audioSrc"] = "voice.wav"
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(idea, f, ensure_ascii=False, indent=2)
    print(f"[tts] wrote {OUT_JSON}")

    if all_foreign:
        print("\n" + "=" * 60)
        print("⚠  PRE-FLIGHT: foreign/English-looking words sent to TTS")
        print("   (not in pronunciation-overrides.json):")
        for w in sorted(all_foreign):
            print(f"   - {w}")
        print("   → If any read wrong in the clip, add them to")
        print("     tts/pronunciation-overrides.json and re-run.")
        print("=" * 60 + "\n")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python synthesize.py <idea.json>")
        return 1
    synthesize(Path(sys.argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
