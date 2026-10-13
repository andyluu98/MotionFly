# MotionFly: làm video tiếng Việt (hướng dẫn cho Codex, Antigravity, Gemini CLI)

Thư mục này làm video bằng MotionFly. Mã MotionFly là thư mục chứa file này (gọi là `VV`).
Python của MotionFly: `~/.motionfly/venv/Scripts/python.exe` trên Windows, `~/.motionfly/venv/bin/python` trên macOS, Linux (gọi là `PY`). Làm video ở thư mục khác thì chạy `python VV/tools/setup/entry.py <thư-mục>` để tạo file hướng dẫn này ở đó. Người dùng giao việc bằng tiếng Việt; trả lời tiếng Việt.

## Khi người dùng muốn làm video

Đọc và làm theo đúng thứ tự: `VV/skills/video-moi/SKILL.md` (điều phối 7 bước), rồi các skill con nó gọi:
`VV/skills/giong-doc/SKILL.md`, `VV/skills/nhac-nen/SKILL.md`, `VV/skills/dung-video/SKILL.md`.
Lần đầu chạy `"PY" "VV/tools/setup/doctor.py"`; chưa `SAN SANG` thì làm theo `VV/skills/video-cai-dat/SKILL.md`.

## Bốn điều làm nên video đẹp (đừng bỏ)

1. **Bạn không có agent con**: dựng theo "Chế độ tuần tự" trong `VV/skills/dung-video/SKILL.md`. Mỗi cảnh: viết, chạy `"PY" "VV/tools/scene_check.py" <du-an> <id>`, MỞ ảnh `checks/scene/<id>.jpg` ra nhìn, sửa, rồi mới sang cảnh sau.
2. **Nhìn mẫu trước khi vẽ**: `VV/examples/crayon-claude-tinh-nang-moi/01_to-duyet.jpg` là mức chăm chút cần đạt. Bộ đồ nghề `window.MF` (`VV/templates/kit/README.md`) cho sẵn nét sáp, chữ viết tay, tô màu, lật trang; dùng để hình đẹp ngay, sáng tạo ý hình là phần của bạn.
3. **Minh họa trước, chữ sau**: mỗi cảnh là một hình ẩn dụ đang diễn ra (vật, người, hành động), chữ chỉ là nhãn vài từ. Cảnh kiểu "tiêu đề + thẻ chữ + thẻ số" là hỏng. Đồ nghề có sẵn, đừng tự vẽ từ số không: 1.879 icon nét (`"PY" "VV/tools/icon_find.py" <từ>`, đặt bằng `K.icon`, vẽ dần bằng `K.drawIcon`) và các khối chuyển động dựng sẵn (mũi tên vẽ tay, khoanh tròn, đếm số, biểu đồ, terminal, chuyển cảnh) trong `VV/templates/kit/goi-y-catalog.md`.
4. **Cổng chặn**: chỉ render khi `"PY" "VV/tools/gate.py" <du-an>` in `GATE PASS`. Thiếu bước là cổng báo lỗi kèm việc cần làm. Không sửa `gate.py`, không viết `checks/review.md` giả: biên bản phải chép `Mã tờ duyệt` in trên `checks/sheet.jpg`, nghĩa là phải mở ảnh ra xem. Mọi số trên hình phải có trong lời đọc hoặc `brief.json` mục `facts` kèm nguồn.

## Luật chung

- Không bịa số liệu, tên, tính năng: tra nguồn và ghi vào `brief.json`.
- Không ký tự gạch ngang dài trong lời đọc và chữ trên hình.
- Mỗi lần chỉ hỏi người dùng một câu khi thật cần; người dùng nói "tự làm hết" thì không hỏi.
