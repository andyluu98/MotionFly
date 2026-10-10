---
name: video-cai-dat
description: Kiểm tra và cài đặt mọi thứ vn-video-studio cần (Node.js, ffmpeg, HyperFrames, môi trường Python, giọng VieNeu, Whisper). Dùng khi người dùng mới cài plugin, gõ "/video-cai-dat", "cài đặt video", "kiểm tra máy làm video", hoặc khi một bước làm video báo thiếu công cụ.
---

# Cài đặt vn-video-studio

Biến dùng chung cho mọi skill của plugin (chạy trong Bash):

```bash
VV="${CLAUDE_PLUGIN_ROOT}"
PY="$HOME/.vn-video-studio/venv/Scripts/python.exe"; [ -x "$PY" ] || PY="$HOME/.vn-video-studio/venv/bin/python"
export PYTHONUTF8=1 HF_HUB_DISABLE_PROGRESS_BARS=1
```

## Bước 1. Kiểm tra

Chạy bằng Python hệ thống bất kỳ (3.10 trở lên):

```bash
python "$VV/tools/setup/doctor.py"
```

Đọc bảng kết quả. Dòng `THIẾU` ở nhóm bắt buộc (Node.js 22+, ffmpeg, ffprobe, ffmpeg loudnorm, HyperFrames) thì báo người dùng tự cài, kèm link trong cột ghi chú. Không tự cài phần mềm hệ thống.

## Bước 2. Cài phần Python và model

Nếu thiếu "Môi trường Python" hoặc "Giọng VieNeu", hỏi người dùng một câu xác nhận (sẽ tải khoảng 2 đến 3 GB: gói Python, model VieNeu, model Whisper large-v3-turbo), rồi chạy nền:

```bash
python "$VV/tools/setup/doctor.py" --install > "$HOME/.vn-video-studio/install.log" 2>&1
```

Lệnh này tạo venv ở `~/.vn-video-studio/venv` (dùng `uv` nếu có), cài `vieneu`, `faster-whisper`, `soundfile`, `numpy`, `scipy`, tải model, và tự sửa lỗi symlink của bộ đệm Hugging Face (ONNX Runtime báo "External data path escapes model directory").

## Bước 3. Skill HyperFrames cho Claude

Nếu dòng "Skill HyperFrames cho Claude" là `tùy chọn` (chưa cài), đề nghị người dùng chạy `npx hyperframes@0.8.145 skills`. Có bộ skill này thì bước dựng hình viết composition chuẩn hơn; không có vẫn chạy được nhờ quy tắc trong skill `dung-video`.

## Kết thúc

Chạy lại Bước 1. Thấy `SAN SANG` thì báo người dùng gõ `/video-moi` kèm yêu cầu video.

Ghi chú máy không có card NVIDIA: giọng VieNeu chạy CPU (khoảng 0,4 giây cho mỗi giây giọng trên máy tầm trung), nhạc nền dùng file người dùng đưa hoặc nhạc tổng hợp bằng code.
