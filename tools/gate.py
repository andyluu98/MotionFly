"""Render gate: a project may be rendered only when this prints GATE PASS.

Checks what a careful builder does and a hurried one skips:
  1. no scene is still the placeholder
  2. `hyperframes check` passes (MF kit warnings are listed)
  3. checks/sheet.jpg is newer than every scene file (the builder looked at the current frames)
  4. checks/review.md is newer than the sheet and says "KẾT LUẬN: ĐẠT" (an independent review happened)
  5. motion, measured on frames every --step seconds (captions band ignored):
     - no stretch longer than 1.5 s where the picture does not change (texture boil alone does not count)
     - a scene still changing a lot just before its exit is listed with the frame to open and check
       (a payoff on the last word is fine; letters still being written are not)

Usage: python gate.py <project> [--scene s3] [--step 0.5] [--skip-check] [--skip-review]
--scene runs only the motion test for one scene (what tools/scene_check.py calls).
Needs: npx (HyperFrames), Pillow.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageStat

HYPERFRAMES = "hyperframes@0.8.145"
NPX = "npx.cmd" if os.name == "nt" else "npx"
STATIC = 1.0        # mean abs difference (0..255) on a blurred quarter-size frame below which two frames count as the same picture
                    # (calibrated: crayon boil plus camera drift alone gives 1 to 2, a frozen frame gives about 0)
SETTLE = 6.0        # difference between 0.6 s before the exit and the exit itself above which the builder must look at the last frame
MAX_HOLD = 1.5      # longest allowed still stretch inside a scene (s)
END_HOLD = 2.5      # the last scene may hold its final picture this long


def snapshot(project: Path, times: list[float], out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.png"):
        f.unlink()
    r = subprocess.run([NPX, "-y", HYPERFRAMES, "snapshot", str(project), "--at", ",".join(f"{t:.2f}" for t in times),
                        "--no-end", "-o", str(out)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    files = sorted(out.glob("frame-*.png"), key=lambda f: int(re.search(r"frame-(\d+)", f.name).group(1)))
    if r.returncode or len(files) < len(times):
        raise SystemExit(f"GATE FAIL: snapshot lỗi ({len(files)}/{len(times)} ảnh)\n{r.stdout[-800:]}{r.stderr[-800:]}")
    return files


def prep(f: Path) -> Image.Image:
    im = Image.open(f).convert("L")
    w, h = im.size
    im = im.crop((0, 0, w, int(h * 0.84)))              # drop the captions band
    im = im.resize((w // 4, int(h * 0.84) // 4), Image.BILINEAR)
    return im.filter(ImageFilter.GaussianBlur(2))        # boil jitter (1 to 4 px) mostly vanishes here


def diff(a: Image.Image, b: Image.Image) -> float:
    return ImageStat.Stat(ImageChops.difference(a, b)).mean[0]


def motion(project: Path, tl: dict, only: str | None, step: float) -> tuple[list[str], list[str]]:
    scenes = [s for s in tl["scenes"] if not only or s["id"] == only]
    last_id = tl["scenes"][-1]["id"]
    plan = []   # (scene, time, kind)
    for s in scenes:
        last = s["id"] == last_id
        exit_at = s["end"] - (0.0 if last else 0.3)
        t = s["start"] + 0.5
        while t < exit_at - 0.05:
            plan.append((s, round(t, 2), "run"))
            t += step
        plan.append((s, round(exit_at - 0.65, 2), "pre"))
        plan.append((s, round(exit_at - 0.05, 2), "end"))
    files = snapshot(project, [p[1] for p in plan], project / "checks" / "gate")
    frames = [prep(f) for f in files]
    problems, looks = [], []
    for s in scenes:
        idx = [i for i, p in enumerate(plan) if p[0] is s and p[2] == "run"]
        still_from = None
        limit = END_HOLD if s["id"] == last_id else MAX_HOLD
        tail = s["end"] - END_HOLD if s["id"] == last_id else s["end"]
        for a, b in zip(idx, idx[1:]):
            same = diff(frames[a], frames[b]) < STATIC
            if same and still_from is None:
                still_from = plan[a][1]
            if (not same or b == idx[-1]) and still_from is not None:
                stop = plan[b][1] if same else plan[a][1]
                if stop - still_from > limit and still_from < tail:
                    problems.append(f"{s['id']}: hình đứng yên {stop - still_from:.1f} s ({still_from:.1f} đến {stop:.1f} s); thêm chuyển động phụ giữa hai neo")
                still_from = None
        pre = next(i for i, p in enumerate(plan) if p[0] is s and p[2] == "pre")
        end = next(i for i, p in enumerate(plan) if p[0] is s and p[2] == "end")
        d = diff(frames[pre], frames[end])
        if d > SETTLE:
            looks.append(f"{s['id']}: cuối cảnh hình còn đổi nhiều (độ lệch {d:.1f}); MỞ {files[end]} xem chữ, hình đã xong chưa")
    return problems, looks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--scene")
    ap.add_argument("--step", type=float, default=0.5)
    ap.add_argument("--skip-check", action="store_true")
    ap.add_argument("--skip-review", action="store_true")
    a = ap.parse_args()
    p = Path(a.project).resolve()
    tl = json.loads((p / "timeline.json").read_text(encoding="utf-8"))
    comp = p / "compositions"
    ids = [s["id"] for s in tl["scenes"] if not a.scene or s["id"] == a.scene]
    fails, notes = [], []

    for sid in ids:
        f = comp / f"{sid}.html"
        if not f.exists() or 'class="placeholder"' in f.read_text(encoding="utf-8"):
            fails.append(f"{sid}: cảnh vẫn là khung chờ, chưa dựng")
    if not a.scene and not a.skip_check:
        r = subprocess.run([NPX, "-y", HYPERFRAMES, "check"], cwd=p, capture_output=True, text=True, encoding="utf-8", errors="replace")
        out = r.stdout + r.stderr
        if "Check passed" not in out:
            fails.append("hyperframes check chưa qua: chạy `npx -y hyperframes@0.8.145 check` trong thư mục dự án và sửa hết error")
        notes += [m.strip() for m in re.findall(r"MF [^\n]+", out)]
    if not a.scene:
        sheet, review = p / "checks" / "sheet.jpg", p / "checks" / "review.md"
        newest = max((f.stat().st_mtime for f in comp.glob("*.html")), default=0)
        if not sheet.exists() or sheet.stat().st_mtime < newest:
            fails.append("tờ duyệt cũ hơn file cảnh: chạy tools/sheet.py rồi MỞ checks/sheet.jpg ra xem")
        if not a.skip_review:
            if not review.exists() or (sheet.exists() and review.stat().st_mtime < sheet.stat().st_mtime):
                fails.append("thiếu checks/review.md mới hơn tờ duyệt: chấm độc lập theo agents/nguoi-cham.md và ghi biên bản")
            elif not re.search(r"KẾT LUẬN:\s*ĐẠT", review.read_text(encoding="utf-8")):
                fails.append("checks/review.md chưa có dòng 'KẾT LUẬN: ĐẠT': sửa các lỗi blocker rồi chấm lại")
    if not fails or a.scene:
        bad, looks = motion(p, tl, a.scene, a.step)
        fails += bad
        notes += looks

    for n in notes:
        print("  chú ý:", n)
    for f in fails:
        print("  ✗", f)
    print("GATE PASS" if not fails else f"GATE FAIL ({len(fails)} lỗi)")
    raise SystemExit(0 if not fails else 1)


if __name__ == "__main__":
    main()
