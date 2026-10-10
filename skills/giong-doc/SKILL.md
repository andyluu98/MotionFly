---
name: giong-doc
description: Sinh giọng đọc tiếng Việt bằng VieNeu-TTS từ script.json của một dự án video, tự chấm phát âm bằng Whisper, giữ bản đọc tốt nhất, lấy mốc thời gian từng từ (voice.wav, words.json). Dùng trong bước 3 của /video-moi, hoặc khi người dùng nói "sinh giọng", "đọc lại câu", "đổi giọng", "sửa phát âm".
---

# Giọng đọc

Biến `VV`, `PY` như trong skill `video-cai-dat`.

## Chạy

```bash
"$PY" "$VV/tools/voice/voice.py" <du-an> > <du-an>/voice.log 2>&1
```

Chạy nền nếu kịch bản dài hơn 1 phút. Xong khi log in `VOICEDONE`. Mọi bản sinh được cache theo nội dung: sửa một câu trong `script.json` rồi chạy lại thì chỉ câu đó được sinh lại.

## Đọc kết quả

- Mỗi câu in `score <id>: <điểm> ok|WEAK | <điều Whisper nghe được>`.
- Điểm chỉ để sàng lọc. WEAK do Whisper nghe sai tên tiếng Anh ("Claude" thành "Clock", "code" thành "cốt") không phải lỗi đọc.
- WEAK thật (đọc sai, nuốt chữ, đọc chữ số sai): sửa theo thứ tự
  1. viết lại câu cho có chủ ngữ tiếng Việt, tránh câu ngắn dưới 5 từ hoặc mở đầu bằng tên tiếng Anh;
  2. thêm mục vào `"pron"` trong `script.json`, ví dụ `"MCP": "em xi pi"` (khóa có chữ hoa thì khớp đúng hoa thường);
  3. chạy lại với `--candidates 4`.
- Từ cần sửa cho mọi dự án: thêm vào `~/.vn-video-studio/pron.json`.

## Giọng

Mặc định `Ngọc Huyền` (nữ, Bắc). Một số giọng có sẵn: Ngọc Huyền, Mai Anh (tin tức), Trúc Ly, Thùy Dung (Nam, tin tức), Hải Đăng, Thiện Minh (kể chuyện), Quang Sơn và Ngọc Trân (Trung). Xem đủ 25 giọng:

```bash
"$PY" -c "from vieneu import Vieneu; [print(v[0]) for v in Vieneu().list_preset_voices()]"
```

Đặt giọng ở khóa `"voice"` trong `script.json`.

## Đầu ra

- `voice.wav`: 48 kHz mono, có khoảng nghỉ: đầu 0,5 s, giữa câu 0,35 s, dấu `|` 0,55 s, giữa cảnh 0,7 s, cuối 0,8 s.
- `words.json`: `total`, `scenes` (mốc đầu cuối từng cảnh), `segments` (từng câu, điểm, cờ weak), `words` (từng từ hiển thị với `start`, `end`). Từ hiển thị giữ đúng chữ trong kịch bản, kể cả khi chữ đọc đã được đổi qua `pron`.
