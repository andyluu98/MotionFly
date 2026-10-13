"""Check ONE scene right after building it (sequential mode, no sub-agents):
assembles the project, saves 3 frames of the scene side by side in checks/scene/<id>.jpg
(just after its first anchor, at its middle, just before its exit), then runs the motion part of the gate.
Open the picture and fix what you see before moving to the next scene.

Usage: python scene_check.py <project> <scene_id>
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402
from assemble import build  # noqa: E402

FONT = Path(__file__).resolve().parents[1] / "templates" / "fonts" / "BeVietnamPro-Bold.ttf"


def main() -> None:
    p, sid = Path(sys.argv[1]).resolve(), sys.argv[2]
    build(p)
    tl = json.loads((p / "timeline.json").read_text(encoding="utf-8"))
    s = next(x for x in tl["scenes"] if x["id"] == sid)
    last = s["id"] == tl["scenes"][-1]["id"]
    first = min(s["anchors"].values(), default=s["start"] + 0.5)
    exit_at = s["end"] - (0.0 if last else 0.3)
    times = [round(min(first + 0.6, exit_at - 0.2), 2), round((s["start"] + exit_at) / 2, 2), round(exit_at - 0.05, 2)]
    files = gate.snapshot(p, times, p / "checks" / "scene" / sid)
    w, h = Image.open(files[0]).size
    tw, th = 360, int(360 * h / w)
    sheet = Image.new("RGB", (3 * tw + 20, th + 44), "#111")
    d, font = ImageDraw.Draw(sheet), ImageFont.truetype(str(FONT), 22)
    for i, (f, t) in enumerate(zip(files, times)):
        sheet.paste(Image.open(f).convert("RGB").resize((tw, th)), (i * (tw + 10), 0))
        d.text((i * (tw + 10) + 10, th + 8), f"{sid}  {t:.2f}s  {['sau neo đầu', 'giữa cảnh', 'trước khi ra'][i]}", fill="#eee", font=font)
    out = p / "checks" / "scene" / f"{sid}.jpg"
    sheet.save(out, quality=85)
    print(f"SCENE {out}")
    print("Mở ảnh trên ra xem: chữ tràn mép, chữ đè phụ đề, chỗ trống, chấm bẩn, chữ viết dở ở khung cuối, sai dấu.")
    r = subprocess.run([sys.executable, str(Path(__file__).with_name("gate.py")), str(p), "--scene", sid], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print(r.stdout.strip())


if __name__ == "__main__":
    main()
