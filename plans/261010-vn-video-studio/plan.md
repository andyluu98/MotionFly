# Plan: vn-video-studio bản đầu

Thiết kế: [docs/01_thiet-ke.md](../../docs/01_thiet-ke.md). Anh duyệt và cho triển khai ngày 10/10/2026.

| # | Việc | Xong khi | Trạng thái |
|---|---|---|---|
| 1 | Khung plugin: plugin.json, marketplace.json, LICENSE, README, NOTICE, .gitignore | `claude plugin validate` không lỗi | [x] |
| 2 | `/video-cai-dat`: doctor.py kiểm Node, Python/uv, ffmpeg, HyperFrames; tạo venv, cài vieneu và faster-whisper, sửa symlink HF, nạp thử model | Chạy trên máy anh báo đủ | [x] |
| 3 | Giọng: `tools/voice/voice.py` (synth có cache, chấm Whisper, mốc từng từ, ghép voice.wav, words.json), `pron.py` | Test pytest phần thuần; sinh được câu thử | [x] |
| 4 | Timeline: `tools/timeline.py` (cảnh, neo kw, phụ đề), báo `KW miss` | Test pytest | [x] |
| 5 | Nhạc và trộn: `tools/music/synth.py`, `tools/audio/mix.py` (duck theo words, loudnorm 2 lượt, srt, remux), chép `fit-beat-grid.py` | Test đường bao; mix đo -14 LUFS | [x] |
| 6 | Style: chép 6 STYLE.md từ lemo-opuscar kèm khối nguồn; font Be Vietnam Pro (OFL) | NOTICE liệt kê đủ | [x] |
| 7 | Skills `video-moi`, `giong-doc`, `nhac-nen`, `dung-video`; agents `dung-canh`, `nguoi-cham`; mẫu composition | Đọc lại đủ luồng 7 bước | [x] |
| 8 | Video mẫu 1 phút "Skill, MCP, Agent" chạy bằng chính plugin | ffprobe, ebur128 đạt; tờ tĩnh không lỗi | [x] |
| 9 | Push GitHub riêng tư `andyluu98/Video-ai-claude` (quét file nhạy cảm trước) | Push xong | [ ] |

Sau bản đầu: ACE-Step, MV khớp lời bài hát, ảnh ChatGPT qua trình duyệt.
