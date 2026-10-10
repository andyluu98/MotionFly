"""Deterministic background music made in code (fallback when the user gives no
track and ACE-Step is not installed). Same arguments -> same file.

Layers: warm pad (additive saw, soft roll-off), plucked arpeggio, bass, and for
energetic moods a soft kick and hi-hat. Writes music/bgm.wav (48 kHz stereo) and
music/beats.json ({bpm, beat0, bars}) so scenes can snap to the grid.

Usage: python synth.py <project_dir> --duration 62 [--mood calm|upbeat|tech|inspiring] [--bpm 96] [--seed 1]
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

SR = 48000

MOODS = {
    #           progression (semitones from root, minor uses 'm'), bpm, drums, root midi
    "calm":      (["I", "vi", "IV", "V"], 84, False, 50),
    "inspiring": (["vi", "IV", "I", "V"], 96, True, 50),
    "upbeat":    (["I", "V", "vi", "IV"], 112, True, 52),
    "tech":      (["i", "VI", "III", "VII"], 104, True, 45),
}
DEGREES = {"I": (0, "maj"), "ii": (2, "min"), "iii": (4, "min"), "IV": (5, "maj"), "V": (7, "maj"),
           "vi": (9, "min"), "i": (0, "min"), "III": (3, "maj"), "VI": (8, "maj"), "VII": (10, "maj")}


def hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def chord(root: int, degree: str) -> list[int]:
    off, q = DEGREES[degree]
    third = 4 if q == "maj" else 3
    base = root + off
    return [base, base + third, base + 7]


def env(n: int, attack: float, release: float) -> np.ndarray:
    e = np.ones(n, dtype=np.float32)
    a, r = min(n, int(attack * SR)), min(n, int(release * SR))
    if a:
        e[:a] = np.linspace(0, 1, a)
    if r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def pad_note(f: float, n: int, rng: np.random.Generator) -> np.ndarray:
    t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float32)
    for det in (-0.06, 0.06):
        ff = f * 2 ** (det / 12)
        ph = rng.uniform(0, 2 * math.pi)
        for k in range(1, 9):
            out += (np.sin(2 * math.pi * ff * k * t + ph * k) / k ** 1.6).astype(np.float32)
    return out * env(n, 0.4, 0.6) * 0.06


def pluck(f: float, n: int) -> np.ndarray:
    t = np.arange(n) / SR
    tone = np.sin(2 * math.pi * f * t) + 0.35 * np.sin(4 * math.pi * f * t) + 0.12 * np.sin(6 * math.pi * f * t)
    return (tone * np.exp(-t / 0.28) * env(n, 0.004, 0.05)).astype(np.float32) * 0.11


def bass(f: float, n: int) -> np.ndarray:
    t = np.arange(n) / SR
    tone = np.sin(2 * math.pi * f * t) + 0.25 * np.sin(4 * math.pi * f * t)
    return (tone * env(n, 0.01, 0.12)).astype(np.float32) * 0.16


def kick(n: int) -> np.ndarray:
    t = np.arange(n) / SR
    freq = 45 + 75 * np.exp(-t / 0.04)
    ph = 2 * math.pi * np.cumsum(freq) / SR
    return (np.sin(ph) * np.exp(-t / 0.16)).astype(np.float32) * 0.32


def hat(n: int, rng: np.random.Generator) -> np.ndarray:
    noise = rng.standard_normal(n).astype(np.float32)
    hp = np.diff(noise, prepend=0.0)
    t = np.arange(n) / SR
    return (hp * np.exp(-t / 0.025)).astype(np.float32) * 0.035


def render(duration: float, mood: str, bpm: int | None, seed: int) -> tuple[np.ndarray, dict]:
    prog, default_bpm, drums, root = MOODS[mood]
    bpm = bpm or default_bpm
    rng = np.random.default_rng(seed)
    beat = 60 / bpm
    bars = math.ceil((duration + 2) / (4 * beat))
    total = int(bars * 4 * beat * SR) + SR
    L = np.zeros(total, dtype=np.float32)
    R = np.zeros(total, dtype=np.float32)

    def add(sig: np.ndarray, start: float, pan: float = 0.0) -> None:
        i = int(start * SR)
        j = min(total, i + len(sig))
        L[i:j] += sig[: j - i] * (1 - max(0, pan))
        R[i:j] += sig[: j - i] * (1 + min(0, pan))

    for b in range(bars):
        notes = chord(root, prog[b % len(prog)])
        t0 = b * 4 * beat
        bar_n = int(4 * beat * SR) + int(0.6 * SR)
        for m in notes:
            add(pad_note(hz(m + 12), bar_n, rng), t0)
        arp = [notes[0] + 24, notes[1] + 24, notes[2] + 24, notes[1] + 24]
        for s in range(8):
            add(pluck(hz(arp[s % 4] + (12 if s >= 4 and b % 2 else 0)), int(0.6 * SR)), t0 + s * beat / 2,
                pan=0.35 if s % 2 else -0.35)
        for q in range(4 if drums else 1):
            add(bass(hz(notes[0] - 12), int(beat * SR * (1 if drums else 4))), t0 + q * beat)
        if drums and b > 0:
            for q in range(4):
                if mood == "upbeat" or q % 2 == 0:
                    add(kick(int(0.4 * SR)), t0 + q * beat)
                add(hat(int(0.1 * SR), rng), t0 + q * beat + beat / 2)

    n = int(duration * SR)
    out = np.stack([L[:n], R[:n]], axis=1)
    fade = min(n, int(2.0 * SR))
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    fin = min(n, int(1.0 * SR))
    out[:fin] *= np.linspace(0, 1, fin)[:, None]
    out *= 0.89 / (np.abs(out).max() or 1.0)
    return out, {"bpm": bpm, "beat0": 0.0, "bars": bars, "mood": mood, "seed": seed, "source": "synth.py"}


def main() -> None:
    import soundfile as sf

    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--mood", default="inspiring", choices=sorted(MOODS))
    ap.add_argument("--bpm", type=int)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    out_dir = Path(a.project).resolve() / "music"
    out_dir.mkdir(parents=True, exist_ok=True)
    audio, meta = render(a.duration, a.mood, a.bpm, a.seed)
    sf.write(out_dir / "bgm.wav", audio, SR, subtype="PCM_16")
    (out_dir / "beats.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"MUSICDONE {out_dir / 'bgm.wav'} bpm={meta['bpm']} bars={meta['bars']}")


if __name__ == "__main__":
    main()
