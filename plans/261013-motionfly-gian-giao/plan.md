# Kế hoạch: giàn giáo cho model yếu hơn (Codex, Antigravity) dùng MotionFly

Ngày 13/10/2026. Người dùng chọn "Làm đủ 5 mục rồi thử".

## Vì sao

Codex và Antigravity làm video bằng MotionFly ra kém đẹp, hay lỗi, làm xong không kiểm tra. Video Claude làm (claude-mods-dashboards-motion) đẹp nhờ ba thói quen: tự xem tờ duyệt rồi sửa, có người chấm độc lập, chia mỗi cảnh một agent. Viết thêm luật bằng chữ không chữa được (model lười đọc lướt; model mạnh bị bó, video na ná nhau). Hướng: giữ luật phong cách ở mức gợi ý, thêm giàn giáo bằng công cụ.

## Năm mục

1. **Cổng chặn tự động** `tools/gate.py <du-an>`: chỉ in `GATE PASS` khi
   - `hyperframes check` qua;
   - `checks/sheet.jpg` mới hơn mọi file cảnh;
   - `checks/review.md` mới hơn tờ duyệt và có dòng `KẾT LUẬN: ĐẠT`;
   - mỗi cảnh: không đoạn nào đứng yên quá 1,5 s (chụp mỗi 0,5 s, đo khác biệt ảnh, bỏ vùng phụ đề); khung trước lúc ra cảnh đã ổn định (không còn vẽ dở);
   - không có cảnh khung chờ (placeholder).
   `tools/scene_check.py <du-an> <id>`: chụp 3 khung của một cảnh và chạy phần đo của cổng cho riêng cảnh đó.
2. **Bộ đồ nghề** `templates/kit/mf-kit.js` (window.MF): vẽ nét có bút dẫn và chống chấm đầu nét, viết chữ lệch tay, tô theo hàng, bật hình, lật trang, trôi camera, boil, cảnh báo hình chạy sát cuối cảnh; hình học tay (wobRect, wobEll, hatch, scrib, star); gói chất liệu crayon, blueprint. Không bắt buộc. `assemble.py` chép vào dự án và nạp trước các cảnh. `templates/kit/README.md` hướng dẫn.
3. **Cảnh mẫu đã duyệt**: `examples/crayon-claude-tinh-nang-moi/` (brief, script, storyboard, theme, quy ước, 7 cảnh) để model biết "đẹp là thế nào".
4. **Chế độ tuần tự** trong `skills/dung-video/SKILL.md` cho môi trường không có agent con: dựng từng cảnh, `scene_check.py`, xem 3 ảnh, sửa, rồi mới sang cảnh sau; tự chấm theo `agents/nguoi-cham.md` và ghi `checks/review.md`.
5. **File vào cửa** `AGENTS.md` (Codex đọc, đã thử) và `GEMINI.md` (Antigravity, chưa xác nhận được vì `agy -p` treo) ở gốc repo, và lệnh tạo file này trong thư mục làm việc của người dùng.

Cập nhật kèm: `agents/dung-canh.md` (nhắc kit, cảnh mẫu, chống chấm đầu nét, chữ xong trước khi ra cảnh), `skills/video-moi/SKILL.md` bước 7 chạy cổng, `README.md`.

## Xong khi

- `gate.py` chạy trên dự án crayon: PASS sau khi có review.md; dự án cố ý lỗi (xóa review.md, cảnh đứng yên) thì FAIL đúng lý do.
- Một cảnh thử viết bằng kit qua `hyperframes check` và render được.
- Thử thật: giao Codex dựng lại 1 đến 2 cảnh theo chế độ tuần tự với kit và cổng chặn, so tờ duyệt với bản trước.

## Đợt 2 (13/10/2026): minh họa nhiều hơn, chặn bịa số và tự chấm giả

Bối cảnh: video Antigravity `videos/ai-agent-vuot-rao` qua cổng nhưng cả 5 cảnh cùng khuôn dashboard, 44 tới 86 chữ mỗi cảnh, s3 s4 không có hình SVG, số +480% 78.4% 54% không có nguồn, review.md tự khen.

1. Bộ icon Lucide (ISC) trong kit: `templates/kit/mf-icons.js` (`MF.icon`, `K.icon` vẽ được bằng `K.draw`), `tools/icon_find.py <từ>` tra tiếng Việt hoặc tiếng Anh.
2. `templates/kit/goi-y-catalog.md`: các khối `hyperframes catalog` hợp MotionFly theo mục đích, cách cài và gắn vào cảnh.
3. `gate.py`: số trên hình (chữ trong HTML và chuỗi trong script) phải có trong script.json, brief.json hoặc storyboard.json.
4. `sheet.py` in mã ngẫu nhiên lên tờ duyệt, chỉ lưu băm; `gate.py` đòi `review.md` chép đúng mã.
5. Phân cảnh: ẩn dụ chính và 2 tới 4 nhịp hình mỗi cảnh (video-moi bước 4, packets).

Xong khi: test đạt; gate FAIL đúng lý do trên dự án Antigravity (số bịa, thiếu mã); PASS trên dự án crayon sau khi chấm lại có mã; một cảnh thử dùng icon qua `hyperframes check`.
