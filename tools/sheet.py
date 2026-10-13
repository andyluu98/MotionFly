"""Contact sheet for review: one frame per scene, taken after its last anchor
(or near the scene end), composed into checks/sheet.jpg with scene id and time.

Usage: python sheet.py <project_dir> [--extra 0.5]
Needs: npx (HyperFrames), Pillow.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HYPERFRAMES = "hyperframes@0.8.145"
NPX = "npx.cmd" if os.name == "nt" else "npx"
FONT = Path(__file__).resolve().parents[1] / "templates" / "fonts" / "BeVietnamPro-Bold.ttf"


def sample_times(timeline: dict, extra: float) -> list[tuple[str, float]]:
    out = []
    for s in timeline["scenes"]:
        last = max(s["anchors"].values(), default=s["start"])
        t = min(s["end"] - 0.15, max(last + 1.0, s["start"] + (s["end"] - s["start"]) * 0.7))
        out.append((s["id"], round(t, 2)))
        if extra and s["end"] - s["start"] > 6:
            out.append((s["id"] + "·giữa", round(s["start"] + (s["end"] - s["start"]) * 0.4, 2)))
    return sorted(out, key=lambda x: x[1])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--extra", type=float, default=0.0, help="1 = also sample the middle of long scenes")
    a = ap.parse_args()
    p = Path(a.project).resolve()
    tl = json.loads((p / "timeline.json").read_text(encoding="utf-8"))
    picks = sample_times(tl, a.extra)
    snap = p / "checks" / "snap"
    snap.mkdir(parents=True, exist_ok=True)
    for f in snap.glob("*.png"):
        f.unlink()
    at = ",".join(str(t) for _, t in picks)
    r = subprocess.run([NPX, "-y", HYPERFRAMES, "snapshot", str(p), "--at", at, "--no-end", "-o", str(snap)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    files = sorted(snap.glob("*.png"))
    if r.returncode or len(files) < len(picks):
        raise SystemExit(f"snapshot lỗi ({len(files)}/{len(picks)} ảnh):\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
    w, h = tl["width"], tl["height"]
    tw = 360 if h > w else 480
    th = int(tw * h / w)
    cols = min(len(files), 5 if h > w else 3)
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 44)), "#111")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 22)
    for i, (f, (sid, t)) in enumerate(zip(files, picks)):
        x, y = (i % cols) * tw, (i // cols) * (th + 44)
        sheet.paste(Image.open(f).convert("RGB").resize((tw, th)), (x, y))
        draw.text((x + 10, y + th + 8), f"{sid}  {t:.1f}s", fill="#eee", font=font)
    out = p / "checks" / "sheet.jpg"
    sheet.save(out, quality=85)
    print(f"SHEET {out} ({len(files)} khung)")


if __name__ == "__main__":
    main()
