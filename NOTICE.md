# Ghi nguồn (NOTICE)

vn-video-studio lắp ghép từ các dự án mã nguồn mở dưới đây. Code và tài liệu chép về giữ nguyên giấy phép gốc; văn bản giấy phép nằm trong `vendor/licenses/`.

## Chép vào repo

| Thành phần trong repo | Nguồn | Phiên bản | Giấy phép | Đã sửa gì |
|---|---|---|---|---|
| `styles/whiteboard/STYLE.md` | [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) `styles/whiteboard/STYLE.md` | commit a75e2b3 | MIT | Thêm khối nguồn đầu file và mục "Bổ sung của vn-video-studio" |
| `styles/iso-infographic/STYLE.md` | lemo-opuscar `styles/iso-infographic/STYLE.md` | commit a75e2b3 | MIT | Như trên |
| `styles/dataviz/STYLE.md` | lemo-opuscar `styles/dataviz/STYLE.md` | commit a75e2b3 | MIT | Như trên |
| `styles/swiss-motion/STYLE.md` | lemo-opuscar `styles/swiss-motion/STYLE.md` | commit a75e2b3 | MIT | Như trên |
| `styles/dark-keynote/STYLE.md` | lemo-opuscar `styles/dark-keynote/STYLE.md` | commit a75e2b3 | MIT | Như trên |
| `styles/paper-popup/STYLE.md` | lemo-opuscar `styles/paper-popup/STYLE.md` | commit a75e2b3 | MIT | Như trên |
| `vendor/bestagentkits/fit-beat-grid.py` | [bestagentkits/motion-video-skill](https://github.com/bestagentkits/motion-video-skill) `skills/motion-video/scripts/fit-beat-grid.py` | commit a73702b | MIT | Không sửa |
| `templates/fonts/BeVietnamPro-*.ttf` | [google/fonts](https://github.com/google/fonts/tree/main/ofl/bevietnampro) (Be Vietnam Pro Project Authors) | nhánh main, lấy ngày 10/10/2026 | SIL OFL 1.1 | Không sửa |

## Học ý tưởng, không chép code

| Ý tưởng | Nguồn | Giấy phép |
|---|---|---|
| Mức trộn nhạc dưới giọng khoảng 6 dB, loudnorm hai lượt, ghép lại bản mix gốc sau render, neo hình theo từ | bestagentkits/motion-video-skill | MIT |
| Luật hoạt hình: mỗi cảnh có việc xảy ra, thời gian theo số ý người xem phải đọc | [JohnHeibel/ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase) | MIT |
| Tách người dựng và người chấm, hai mức blocker/polish, file quyết định xong | [edenfunf/reelmimic](https://github.com/edenfunf/reelmimic) | MIT |
| Tone preset, chữ phải hiện đủ lâu | [latent-spaces/brag](https://github.com/latent-spaces/brag) | MIT |
| Cổng duyệt, chia cảnh cho agent con, contact sheet | heygen-com/hyperframes (skill music-to-video) | Apache-2.0 |
| Chọn bản đọc tốt nhất bằng Whisper, bảng phát âm, mốc từng từ, ước lượng nhịp đọc | Bộ CES AI News và ces-video-whiteboard (của chủ repo) | của chủ repo |
| Chuẩn hóa tiền tệ, phần trăm, ký hiệu khi đọc | `reference/vn-short-video-tts/` (dự án cũ của chủ repo) | của chủ repo |

## Phụ thuộc cài khi chạy (không chép vào repo)

| Phụ thuộc | Vai trò | Giấy phép |
|---|---|---|
| [HyperFrames](https://github.com/heygen-com/hyperframes) 0.8.145 (npx) | Dựng HTML thành MP4, lint, check, snapshot | Apache-2.0 |
| [GSAP](https://gsap.com) 3.14.2 (CDN) | Chuyển động trong composition | Giấy phép GSAP (miễn phí) |
| [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS) 3.8.3 (pip `vieneu`) | Giọng đọc tiếng Việt | Apache-2.0 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Chấm phát âm, mốc từng từ | MIT |
| numpy, scipy, soundfile, Pillow | Xử lý âm thanh, ảnh | BSD, MIT-CMU |
| ffmpeg (người dùng tự cài) | Đọc ghi âm thanh, video | LGPL/GPL tùy bản |
