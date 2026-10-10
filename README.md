# vn-video-studio

Plugin Claude Code làm video tiếng Việt trọn gói. Anh nhập một yêu cầu, Claude đi hết quy trình làm phim: ý tưởng, kịch bản, giọng đọc, phân cảnh, nhạc nền, dựng hình, trộn âm, phụ đề, xuất MP4.

```
/video-moi Làm video 1 phút giải thích Skill, MCP và Agent trong Claude Code, style whiteboard
```

## Quy trình

| Bước | Việc | Ra file | Duyệt |
|---|---|---|---|
| 1 | Brief: chủ đề, khán giả, style, độ dài, giọng | `brief.json` | Hỏi khi thiếu |
| 2 | Ý tưởng, kịch bản theo cảnh | `script.json` | Có |
| 3 | Giọng VieNeu, tự chấm phát âm bằng Whisper, mốc từng từ | `voice.wav`, `words.json` | |
| 4 | Phân cảnh neo theo từ khóa lời đọc | `storyboard.json`, `timeline.json` | |
| 5 | Nhạc nền, nhạc tự hạ khi có lời, -14 LUFS | `mix.wav` | |
| 6 | Dựng từng cảnh bằng code (agent song song), kiểm tra, người chấm độc lập | `compositions/`, `checks/sheet.jpg` | Có |
| 7 | Render, ghép âm thanh, phụ đề | `renders/*.mp4`, `phude.srt` | |

Nói "tự làm hết" để bỏ các bước duyệt.

## Style dựng sẵn

`whiteboard`, `iso-infographic`, `dataviz`, `swiss-motion`, `dark-keynote`, `paper-popup`. Mỗi style là một file `styles/<tên>/STYLE.md`; thêm style mới chỉ cần thêm thư mục, không sửa code.

## Cài đặt

Cần có sẵn: [Claude Code](https://claude.com/claude-code), [Node.js](https://nodejs.org) 22 trở lên, Python 3.10 trở lên, [ffmpeg](https://ffmpeg.org/download.html) trong PATH. Nên có [uv](https://docs.astral.sh/uv/).

```
/plugin marketplace add andyluu98/Video-ai-claude
/plugin install vn-video-studio@vn-video-studio
/video-cai-dat
```

`/video-cai-dat` kiểm máy, báo thiếu gì, rồi tự tải phần còn lại (khoảng 2 đến 3 GB): môi trường Python ở `~/.vn-video-studio/venv`, giọng VieNeu, model Whisper.

Không có card NVIDIA vẫn chạy: giọng dùng CPU, nhạc dùng file anh đưa hoặc nhạc tổng hợp bằng code. Repo không kèm file nhạc của bên thứ ba vì điều khoản các kho nhạc miễn phí cấm phân phối lại.

## Cấu trúc

```
skills/      video-moi (điều phối), giong-doc, nhac-nen, dung-video, video-cai-dat
agents/      dung-canh (dựng một cảnh), nguoi-cham (chấm độc lập)
styles/      style card (nguồn ghi đầu mỗi file)
tools/       voice/ (VieNeu, Whisper), music/synth.py, audio/mix.py, timeline.py, assemble.py, sheet.py, setup/
templates/   khuôn cảnh, font Be Vietnam Pro
vendor/      code chép từ repo khác, giấy phép gốc
```

## Nguồn

Lắp ghép từ HyperFrames, lemo-opuscar, bestagentkits/motion-video-skill, VieNeu-TTS, faster-whisper và một số repo khác. Chi tiết từng file, phiên bản, giấy phép: [NOTICE.md](NOTICE.md).

## Giấy phép

Code của repo: MIT ([LICENSE](LICENSE)). Phần chép từ nơi khác giữ giấy phép gốc (xem NOTICE.md).
