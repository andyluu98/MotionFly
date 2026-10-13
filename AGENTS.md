# MotionFly: làm video tiếng Việt (hướng dẫn cho Codex, Antigravity, Gemini CLI)

Thư mục này làm video bằng MotionFly. Mã MotionFly là thư mục chứa file này (gọi là `VV`).
Python của MotionFly: `~/.motionfly/venv/Scripts/python.exe` trên Windows, `~/.motionfly/venv/bin/python` trên macOS, Linux (gọi là `PY`). Làm video ở thư mục khác thì chạy `python VV/tools/setup/entry.py <thư-mục>` để tạo file hướng dẫn này ở đó. Người dùng giao việc bằng tiếng Việt; trả lời tiếng Việt.

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
