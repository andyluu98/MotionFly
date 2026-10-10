"""Check (and optionally install) everything vn-video-studio needs.

  python doctor.py            check only, print a table and what to do
  python doctor.py --install  also create ~/.vn-video-studio/venv, install the Python
                              packages, download VieNeu, fix HF symlinks, warm Whisper

Runs with any Python 3.10+, standard library only.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home() / ".vn-video-studio"
VENV = HOME / "venv"
PY = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
HYPERFRAMES = "hyperframes@0.8.145"
PACKAGES = ["vieneu==3.8.3", "faster-whisper", "soundfile", "numpy", "scipy", "pillow"]
HERE = Path(__file__).resolve().parent
NPX = "npx.cmd" if os.name == "nt" else "npx"

rows: list[tuple[str, str, str]] = []


def run(cmd: list[str], timeout: int = 600) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
                           env={**os.environ, "PYTHONUTF8": "1"})
        return r.returncode, (r.stdout + r.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)


def row(name: str, ok: bool | None, note: str) -> bool:
    rows.append((name, "có" if ok else ("tùy chọn" if ok is None else "THIẾU"), note))
    return bool(ok)


def check_tools() -> bool:
    good = True
    code, out = run(["node", "--version"])
    major = int(out.lstrip("v").split(".")[0]) if code == 0 and out.startswith("v") else 0
    good &= row("Node.js 22+", major >= 22, out if code == 0 else "cài tại https://nodejs.org")
    for tool in ("ffmpeg", "ffprobe"):
        good &= row(tool, shutil.which(tool) is not None,
                    shutil.which(tool) or "cài tại https://ffmpeg.org/download.html rồi thêm vào PATH")
    if shutil.which("ffmpeg"):
        _, filters = run(["ffmpeg", "-hide_banner", "-filters"])
        need = [f for f in ("loudnorm", "aresample") if f" {f} " not in filters]
        good &= row("ffmpeg loudnorm", not need, "có" if not need else f"bản ffmpeg thiếu {need}; cài bản đầy đủ")
    row("uv (nên có)", shutil.which("uv") is not None or None,
        shutil.which("uv") or "không bắt buộc; https://docs.astral.sh/uv/")
    code, out = run([NPX, "-y", HYPERFRAMES, "--version"], timeout=300)
    good &= row("HyperFrames", code == 0, out.splitlines()[-1] if code == 0 else "cần Node.js; lỗi: " + out[-200:])
    skills = Path.home() / ".claude" / "skills" / "hyperframes-core"
    row("Skill HyperFrames cho Claude", skills.exists() or None,
        "đã cài" if skills.exists() else f"chạy: npx {HYPERFRAMES} skills")
    code, out = run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"])
    row("Card NVIDIA", (code == 0) or None, out if code == 0 else "không có: giọng chạy CPU, nhạc dùng synth")
    return good


def check_venv() -> bool:
    if not PY.exists():
        return row("Môi trường Python", False, f"chưa có {VENV}; chạy lại với --install")
    code, out = run([str(PY), "-c", "import vieneu, faster_whisper, soundfile, numpy, scipy, PIL; print('ok')"])
    return row("Môi trường Python", code == 0, str(VENV) if code == 0 else out[-300:])


TTS_PROBE = "from vieneu import Vieneu; t=Vieneu(); print('VOICES=%d' % len(t.list_preset_voices()))"


def check_tts() -> bool:
    code, out = run([str(PY), "-c", TTS_PROBE])
    if code != 0 and "External data path" in out:
        run([str(PY), str(HERE / "fix_hf_symlinks.py")])
        code, out = run([str(PY), "-c", TTS_PROBE])
    n = next((ln.split("=")[1] for ln in out.splitlines() if ln.startswith("VOICES=")), "?")
    return row("Giọng VieNeu", code == 0, f"{n} giọng có sẵn" if code == 0 else out[-300:])


def install() -> None:
    HOME.mkdir(parents=True, exist_ok=True)
    if not PY.exists():
        if shutil.which("uv"):
            run(["uv", "venv", str(VENV), "--python", "3.12"])
        else:
            run([sys.executable, "-m", "venv", str(VENV)])
    if shutil.which("uv"):
        code, out = run(["uv", "pip", "install", "--python", str(PY), *PACKAGES], timeout=1800)
    else:
        code, out = run([str(PY), "-m", "pip", "install", *PACKAGES], timeout=1800)
    print(out[-600:])
    print("Tải model VieNeu (lần đầu vài trăm MB)...")
    check_tts()
    print("Tải model Whisper large-v3-turbo (khoảng 1,6 GB)...")
    run([str(PY), "-c", "from faster_whisper import WhisperModel; WhisperModel('large-v3-turbo', device='cpu', "
                        "compute_type='int8')"], timeout=3600)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    a = ap.parse_args()
    print(f"vn-video-studio doctor | {platform.system()} {platform.release()} | Python {platform.python_version()}")
    if a.install:
        install()
        rows.clear()
    ok = check_tools()
    ok &= check_venv() and check_tts()
    w = max(len(r[0]) for r in rows)
    for name, state, note in rows:
        print(f"{name:<{w}}  {state:<8}  {note}")
    print("SAN SANG" if ok else "CHUA DU: xử lý các dòng THIẾU ở trên (hoặc chạy --install)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

