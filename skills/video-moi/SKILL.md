---
name: video-moi
description: Làm một video tiếng Việt hoàn chỉnh từ một yêu cầu, theo quy trình làm phim: ý tưởng, kịch bản, giọng đọc VieNeu, phân cảnh, nhạc nền, dựng hình bằng code, trộn âm, phụ đề, xuất MP4. Dùng khi người dùng gõ "/video-moi", "làm video", "dựng video giải thích", "video về chủ đề X", "làm clip ngắn", "biến bài này thành video", hoặc gửi tài liệu, link, bài nhạc và muốn có video.
---

# Làm video mới

Bạn là đạo diễn. Bạn tự viết kịch bản và phân cảnh, giao các bước kỹ thuật cho skill con: `giong-doc`, `nhac-nen`, `dung-video`. Biến `VV`, `PY` như trong skill `video-cai-dat`. Lần đầu trong phiên, chạy `python "$VV/tools/setup/doctor.py"`; chưa `SAN SANG` thì chuyển sang skill `video-cai-dat`.

Mỗi video là thư mục `videos/<slug>/` trong thư mục đang làm việc (slug không dấu, gạch nối). Mỗi bước ghi một file; bước sau chỉ đọc file đó. Tạo task list theo 7 bước dưới đây.

## Bước 1. Brief

Ghi `brief.json`:

```json
{"topic": "...", "audience": "...", "message": "một câu thông điệp lõi", "aspect": "9:16",
 "duration_s": 60, "style": "whiteboard", "voice": "Ngọc Huyền", "music": "synth:inspiring",
 "brand": {"colors": [], "name": ""}, "sources": [], "auto": false}
```

Chỉ hỏi khi thiếu thứ không đoán được, mỗi lần một câu, có phương án đề xuất đặt đầu. Mặc định: 9:16, 60 giây, giọng Ngọc Huyền, nhạc tổng hợp theo mood của style. Người dùng nói "tự làm hết" thì `auto: true`: bỏ các cổng duyệt, chỉ báo cáo cuối.

Chọn style: có 43 style, danh mục ở `$VV/styles/index.json` (mỗi mục có `slug`, tên tiếng Việt `vi`, nhóm `category_vi`, `dung_cho`, `mood` nhạc, `gpu`, `demo`). Đọc danh mục, chọn style có `dung_cho` khớp nội dung và đối tượng; người dùng nêu tên style (tiếng Việt hay tiếng Anh) thì tra theo `vi`, `en`, `slug`. Đọc `$VV/styles/<slug>/STYLE.md` của style đã chọn trước khi phân cảnh. Gợi ý nhanh khi người dùng chưa chọn:

| Nhu cầu | Style gợi ý |
|---|---|
| Đào tạo, giải thích khái niệm | whiteboard, iso-infographic, midcentury-toon, blueprint |
| Số liệu, báo cáo, tin tức | dataviz, swiss-motion, game-show |
| Sản phẩm, công nghệ | dark-keynote, living-screencast, hologram-hud, glass-product |
| Marketing, kể chuyện | paper-popup, risograph, crayon-book, watercolor, one-line |
| Văn hóa, lễ hội Á Đông | ink-wash, papercut-red, paper-lantern, shadow-puppet, ukiyoe |
| Giải trí, game, hoài niệm | pixel-rpg, cel-anime-80s, rubber-hose, silent-film, microgame |

Style có `gpu: true` (glass-product, lowpoly-island, brick-toy, tilt-shift) dựng 3D bằng WebGL: báo người dùng máy không có card đồ họa sẽ render chậm. Mood nhạc lấy từ trường `mood` của style.

Yêu cầu riêng của người dùng thắng luật style, trừ luật cấm của style (mâu thuẫn thật thì hỏi).

## Bước 2. Ý tưởng và kịch bản (cổng duyệt 1)

1. Nguồn: có tài liệu hoặc link thì đọc trước; tin tức, số liệu, tên sản phẩm phải tra nguồn gốc, không bịa. Ghi nguồn vào `brief.json`.
2. Ý tưởng: một câu móc (hook) ở 3 giây đầu, một mạch (vấn đề, cơ chế, ví dụ, kết), một hình ảnh ẩn dụ trung tâm giữ suốt video.
3. Viết `script.json`:

```json
{"title": "...", "voice": "Ngọc Huyền", "aspect": "9:16",
 "scenes": [{"id": "s1", "say": "Câu nói. | Câu sau khoảng nghỉ.", "intent": "ý cảnh cần truyền đạt"}],
 "pron": {}}
```

Luật lời đọc:
- 1 phút khoảng 150 đến 170 từ (VieNeu đọc khoảng 3,4 từ mỗi giây, cộng khoảng nghỉ). 5 đến 9 cảnh cho 1 phút.
- Mỗi cảnh 1 đến 3 câu, mỗi câu dưới 25 từ, văn nói tự nhiên. `|` tạo khoảng nghỉ 0,55 giây.
- Câu có chủ ngữ tiếng Việt; tránh câu dưới 5 từ và câu mở đầu bằng tên tiếng Anh (VieNeu dễ đọc sai).
- Số viết chữ số; không gạch ngang dài; không emoji.

Gửi người dùng bảng: cảnh, lời đọc, ý hình dự kiến. Chờ duyệt (bỏ qua nếu `auto`).

## Bước 3. Giọng

Theo skill `giong-doc`. Xong khi có `voice.wav`, `words.json`, không còn câu WEAK thật.

## Bước 4. Phân cảnh

Viết `storyboard.json` dựa trên mốc giọng thật trong `words.json`:

```json
{"title": "...", "aspect": "9:16", "style": "whiteboard",
 "scenes": [{"id": "s1", "visual": "mô tả hình: vật gì, bố cục, chuyển động",
             "anchors": [{"id": "hook", "kw": "từ đúng như lời đọc", "nth": 1, "off": -0.1}],
             "in": "cách vào cảnh", "out": "cách sang cảnh sau"}]}
```

- Mỗi câu lời đọc có ít nhất một neo; `kw` là một hoặc vài từ liên tiếp viết đúng như trong `say`.
- Hình phải đúng thứ người trong nghề thấy thật (kiểm thử phần mềm là terminal chạy test, không phải ống nghiệm).
- Chạy `"$PY" "$VV/tools/timeline.py" <du-an>`; sửa đến khi không còn `KW miss`.

## Bước 5. Nhạc nền

Theo skill `nhac-nen`: chọn nguồn, rồi trộn ra `mix.wav`.

## Bước 6. Dựng và duyệt hình (cổng duyệt 2)

Theo skill `dung-video` mục 1 đến 4. Gửi tờ duyệt `checks/sheet.jpg`, chờ duyệt (bỏ qua nếu `auto`).

## Bước 7. Render và giao (cổng duyệt 3 nếu người dùng muốn xem bản nháp trước)

Theo skill `dung-video` mục 5 và 6. Tên file `<slug>-<ddmmyyyy>`.

Báo cáo cuối: đường dẫn tuyệt đối của MP4, SRT, tờ duyệt; độ dài; style; giọng; nguồn nhạc; số đo loudness; câu nào đã sửa phát âm; chỗ nào dùng ví dụ tự đặt (để người dùng xác nhận); nguồn tư liệu dạng link.

## Ảnh từ ChatGPT (tùy chọn)

Mặc định mọi hình vẽ bằng code. Chỉ khi người dùng yêu cầu, hoặc style cần ảnh thật (nhân vật, bối cảnh khó vẽ bằng code) và người dùng đồng ý: dùng trình duyệt (Claude in Chrome) mở ChatGPT của người dùng, tạo ảnh không chữ, tải về `<du-an>/assets/`, ghi `assets/manifest.json` (file, prompt, nguồn "ChatGPT", ngày). Chữ và số luôn dựng bằng code, không để trong ảnh. Xin phép người dùng trước khi tải file.
