"""Write one hand-off packet per scene for the dung-canh agents.

Reads timeline.json, storyboard.json, theme.css and the optional per-video shared
rules file quy-uoc-chung.md (drawing vocabulary every scene must share: stroke,
recurring characters/props, enter/exit motion, safe area). Writes
checks/packets/<scene>.md with local word times and A("key") anchors.

Usage: python packets.py <project_dir>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]


def main() -> None:
    p = Path(sys.argv[1]).resolve()
    tl = json.loads((p / "timeline.json").read_text(encoding="utf-8"))
    sb_all = json.loads((p / "storyboard.json").read_text(encoding="utf-8"))
    sb = {s["id"]: s for s in sb_all["scenes"]}
    theme = (p / "theme.css").read_text(encoding="utf-8") if (p / "theme.css").exists() else "(chưa có theme.css)"
    shared_file = p / "quy-uoc-chung.md"
    shared = shared_file.read_text(encoding="utf-8") if shared_file.exists() else ""
    style = sb_all.get("style", "")
    has_bg = (p / "compositions" / "_nen.html").exists()
    order = [s["id"] for s in tl["scenes"]]
    out = p / "checks" / "packets"
    out.mkdir(parents=True, exist_ok=True)
    for i, s in enumerate(tl["scenes"]):
        sid, dur = s["id"], s["end"] - s["start"]
        words = "\n".join(f"  {w['start'] - s['start']:6.2f} - {w['end'] - s['start']:6.2f}  {w['w']}"
                          for w in tl["words"] if w["scene"] == sid)
        anchors = "\n".join(f'  A("{k}") = {v - s["start"]:.2f} s' for k, v in s["anchors"].items())
        prev = sb[order[i - 1]]["visual"] if i else "(không, đây là cảnh mở đầu)"
        nxt = sb[order[i + 1]]["visual"] if i + 1 < len(order) else "(không, cảnh cuối: giữ hình 0,3 giây cuối)"
        beats = "\n".join(f"  {k + 1}. {b}" for k, b in enumerate(sb[sid].get("beats", []))) or "  (storyboard chưa có beats: tự chia 2 đến 4 nhịp hình theo các câu)"
        bg = ("Nền: KHÔNG vẽ nền; `#<id>-root` để background: transparent (đã có lớp nền chung `_nen`)."
              if has_bg else "Nền: tự vẽ nền theo style trong cảnh.")
        text = f"""# Gói giao việc cảnh {sid}

Cảnh: {sid}   File: {(p / 'compositions' / f'{sid}.html').as_posix()}
Khung: {tl['width']}x{tl['height']}   Độ dài cảnh: {dur:.2f} s (thời gian cục bộ 0 đến {dur:.2f})
Style: {(PLUGIN / 'styles' / style / 'STYLE.md').as_posix()}
{bg}
Biến màu (theme.css, dùng bằng var(--...)):
{theme}
Lời đọc của cảnh (thời gian cục bộ, giây):
{words}

Neo có sẵn:
{anchors}

Ẩn dụ chung của video: {sb_all.get('metaphor', '(không ghi)')}
Ý hình (storyboard): {sb[sid].get('visual', '')}
Nhịp hình (mỗi nhịp là một việc nhìn thấy, đúng lúc câu tương ứng được đọc):
{beats}
Đồ nghề: icon `K.icon` (tra tên: tools/icon_find.py), khối dựng sẵn: {(PLUGIN / 'templates' / 'kit' / 'goi-y-catalog.md').as_posix()}
Vào: {sb[sid].get('in', '')}   Ra: {sb[sid].get('out', '')}
Cảnh trước: {prev}
Cảnh sau: {nxt}

{shared}
"""
        (out / f"{sid}.md").write_text(text, encoding="utf-8")
    print(f"PACKETS {len(order)} -> {out}")


if __name__ == "__main__":
    main()
