"""Find Lucide icon names for a word (Vietnamese or English) before drawing with K.icon.

Usage: python icon_find.py <từ khóa> [<từ khóa> ...]
  python icon_find.py robot      -> bot, bot-message-square, ...
  python icon_find.py "hàng rào" -> fence, ...
"""

from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

TAGS = Path(__file__).resolve().parents[1] / "templates" / "kit" / "icon-tags.json"

# common Vietnamese words in explainer videos -> English search terms
VI = {
    "robot": "bot robot", "người": "user person", "người dùng": "user", "nhóm": "users group", "đám đông": "users",
    "hàng rào": "fence", "tường lửa": "brick-wall firewall shield", "tường": "brick-wall wall", "cửa": "door",
    "khóa": "lock", "mở khóa": "lock-open unlock", "chìa khóa": "key", "khiên": "shield", "an toàn": "shield-check safe",
    "cảnh báo": "triangle-alert warning alert", "nguy hiểm": "skull danger siren", "lỗi": "bug circle-x error",
    "máy tính": "laptop monitor computer", "điện thoại": "smartphone phone", "máy chủ": "server", "dữ liệu": "database",
    "đám mây": "cloud", "mạng": "network wifi globe", "internet": "globe wifi", "web": "globe browser",
    "mã": "code terminal", "lập trình": "code terminal", "dòng lệnh": "terminal", "tệp": "file", "thư mục": "folder",
    "tài liệu": "file-text document", "báo cáo": "file-chart clipboard report", "biểu đồ": "chart bar-chart line-chart",
    "tăng": "trending-up arrow-up", "giảm": "trending-down arrow-down", "tiền": "dollar banknote coins wallet",
    "thời gian": "clock timer", "lịch": "calendar", "tin nhắn": "message-square mail", "trò chuyện": "message-circle chat",
    "email": "mail", "thông báo": "bell notification", "tìm kiếm": "search", "kính lúp": "search magnifier",
    "cài đặt": "settings cog", "bánh răng": "cog settings", "công cụ": "wrench hammer tool", "sửa": "wrench pencil",
    "ý tưởng": "lightbulb idea", "não": "brain", "trí tuệ": "brain sparkles", "ai": "brain sparkles bot cpu",
    "chip": "cpu chip", "tia sét": "zap", "nhanh": "zap rocket gauge", "tên lửa": "rocket", "mục tiêu": "target",
    "cờ": "flag", "ngôi sao": "star", "trái tim": "heart", "thích": "thumbs-up heart", "đúng": "check circle-check",
    "sai": "x circle-x", "câu hỏi": "circle-question-mark help", "mắt": "eye", "ẩn": "eye-off", "camera": "camera",
    "video": "video clapperboard film", "âm nhạc": "music", "micro": "mic", "loa": "volume speaker",
    "nhà": "house home", "công ty": "building office", "văn phòng": "building briefcase", "trường học": "school graduation",
    "sách": "book", "học": "graduation-cap book-open", "giỏ hàng": "shopping-cart", "cửa hàng": "store",
    "xe": "car truck", "máy bay": "plane", "bản đồ": "map map-pin", "vị trí": "map-pin", "trái đất": "earth globe",
    "kết nối": "plug link cable", "liên kết": "link", "chia sẻ": "share", "tải lên": "upload", "tải xuống": "download",
    "lá chắn": "shield", "vượt rào": "fence footprints", "chạy": "play footprints", "dừng": "octagon-x square circle-stop",
    "pin": "battery", "năng lượng": "battery-charging zap", "lửa": "flame", "nước": "droplet waves", "cây": "tree-pine sprout",
    "hộp": "box package", "gói": "package", "quà": "gift", "cúp": "trophy", "huy chương": "medal award",
}


def norm(s: str) -> str:
    return unicodedata.normalize("NFC", s.strip().lower())


def find(words: list[str], limit: int = 12) -> list[tuple[str, list[str]]]:
    tags = json.loads(TAGS.read_text(encoding="utf-8"))
    terms = []
    for w in words:
        w = norm(w)
        terms += VI.get(w, w).split()
    score = {}
    for name, tg in tags.items():
        s = 0
        for t in terms:
            if t == name or name.startswith(t + "-"):
                s += 3
            elif t in name:
                s += 2
            elif any(t in x for x in tg):
                s += 1
        if s:
            score[name] = s
    best = sorted(score, key=lambda n: (-score[n], len(n)))[:limit]
    return [(n, tags[n][:5]) for n in best]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    hits = find(sys.argv[1:])
    if not hits:
        print("Không thấy. Thử từ tiếng Anh (ví dụ: shield, server, rocket) hoặc tự vẽ bằng MF.geo.")
    for n, tg in hits:
        print(f"{n:28s} {', '.join(tg)}")
