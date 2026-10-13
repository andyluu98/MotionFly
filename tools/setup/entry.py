"""Write AGENTS.md (Codex) and GEMINI.md (Gemini CLI, Antigravity) into a working folder, so agents other than
Claude Code find the MotionFly workflow. Existing files are moved to _backup/ first, never overwritten.

Usage: python entry.py <thu-muc-lam-video> [--vv <duong-dan-MotionFly>]
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
from pathlib import Path

VV = Path(__file__).resolve().parents[2]

TEXT = """# MotionFly: làm video tiếng Việt (hướng dẫn cho Codex, Antigravity, Gemini CLI)

Thư mục này làm video bằng MotionFly. Mã MotionFly nằm ở: `{vv}` (gọi là `VV`).
Python của MotionFly: `{py}` (gọi là `PY`). Người dùng giao việc bằng tiếng Việt; trả lời tiếng Việt.

## Khi người dùng muốn làm video

Đọc và làm theo đúng thứ tự: `VV/skills/video-moi/SKILL.md` (điều phối 7 bước), rồi các skill con nó gọi:
`VV/skills/giong-doc/SKILL.md`, `VV/skills/nhac-nen/SKILL.md`, `VV/skills/dung-video/SKILL.md`.
Lần đầu chạy `"PY" "VV/tools/setup/doctor.py"`; chưa `SAN SANG` thì làm theo `VV/skills/video-cai-dat/SKILL.md`.

## Ba điều làm nên video đẹp (đừng bỏ)

1. **Bạn không có agent con**: dựng theo "Chế độ tuần tự" trong `VV/skills/dung-video/SKILL.md`. Mỗi cảnh: viết, chạy `"PY" "VV/tools/scene_check.py" <du-an> <id>`, MỞ ảnh `checks/scene/<id>.jpg` ra nhìn, sửa, rồi mới sang cảnh sau.
2. **Nhìn mẫu trước khi vẽ**: `VV/examples/crayon-claude-tinh-nang-moi/01_to-duyet.jpg` là mức chăm chút cần đạt. Bộ đồ nghề `window.MF` (`VV/templates/kit/README.md`) cho sẵn nét sáp, chữ viết tay, tô màu, lật trang; dùng để hình đẹp ngay, sáng tạo ý hình là phần của bạn.
3. **Cổng chặn**: chỉ render khi `"PY" "VV/tools/gate.py" <du-an>` in `GATE PASS`. Thiếu bước là cổng báo lỗi kèm việc cần làm. Không sửa `gate.py`, không viết `checks/review.md` giả.

## Luật chung

- Không bịa số liệu, tên, tính năng: tra nguồn và ghi vào `brief.json`.
- Không ký tự gạch ngang dài trong lời đọc và chữ trên hình.
- Mỗi lần chỉ hỏi người dùng một câu khi thật cần; người dùng nói "tự làm hết" thì không hỏi.
"""


def write(target: Path, vv: Path) -> list[Path]:
    py = Path.home() / ".motionfly" / "venv" / ("Scripts/python.exe" if (Path.home() / ".motionfly/venv/Scripts").exists() else "bin/python")
    body = TEXT.format(vv=vv.as_posix(), py=py.as_posix())
    out = []
    for name in ("AGENTS.md", "GEMINI.md"):
        f = target / name
        if f.exists():
            bk = target / "_backup"
            bk.mkdir(exist_ok=True)
            shutil.move(str(f), bk / f"{f.stem}_{dt.datetime.now():%y%m%d-%H%M}{f.suffix}")
        f.write_text(body, encoding="utf-8")
        out.append(f)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--vv", default=str(VV))
    a = ap.parse_args()
    t = Path(a.target).resolve()
    t.mkdir(parents=True, exist_ok=True)
    for f in write(t, Path(a.vv).resolve()):
        print("ENTRY", f)
