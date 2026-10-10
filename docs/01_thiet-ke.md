# Thiết kế: MotionFly

Ngày: 10/10/2026. Trạng thái: anh duyệt hướng "lắp ghép" trong phiên ngày 10/10/2026.

## 1. Mục tiêu

Plugin Claude Code: người dùng gõ `/video-moi` kèm yêu cầu (chủ đề, nội dung, style, độ dài, có thể kèm file nhạc). Plugin đi trọn quy trình làm phim: ý tưởng, kịch bản, giọng đọc tiếng Việt, phân cảnh, nhạc nền, dựng hình, trộn âm, xuất MP4 và phụ đề.

Nguyên tắc chính: **không tự viết lại thứ cộng đồng đã làm tốt**. Linh kiện lớn cài làm phụ thuộc; code nhỏ của repo MIT thì chép đúng file cần, ghi nguồn; phần tự viết chỉ là lớp nối và quy trình.

Tiêu chí xong của bản đầu: từ một câu yêu cầu, ra video 1080x1920 hoặc 1920x1080, 30 fps, có giọng VieNeu, nhạc nền tự hạ khi có lời, phụ đề tiếng Việt đúng dấu, âm lượng -14 LUFS, chạy được trên Windows.

## 2. Ba nhóm thành phần

| Nhóm | Gồm | Cách có |
|---|---|---|
| A. Trong repo | skills, agents, style card, script Python, mẫu HTML, NOTICE, file giấy phép | Cài plugin là có |
| B. Tự tải bằng `/video-cai-dat` | HyperFrames (npx, ghim phiên bản), venv Python ở `~/.motionfly/venv` có `vieneu`, `faster-whisper`, `soundfile`, `numpy`; model VieNeu và Whisper từ Hugging Face | Một lệnh, nguồn chính thức |
| C. Người dùng tự có | Claude Code, Node.js 22 trở lên, Python 3.10 trở lên (hoặc `uv`), ffmpeg | `/video-cai-dat` kiểm và báo thiếu |
| Tùy chọn | Card NVIDIA (ACE-Step sinh nhạc), Claude in Chrome và tài khoản ChatGPT (tạo ảnh) | Không có vẫn chạy |

Venv đặt ở thư mục người dùng (không đặt trong thư mục cache của plugin) để cập nhật plugin không xóa venv và model.

## 3. Lấy gì, từ đâu

| Nguồn | Giấy phép | Lấy | Cách |
|---|---|---|---|
| heygen-com/hyperframes | Apache-2.0 | Dựng HTML thành MP4, lint, check, snapshot, render; skill tác giả composition | Phụ thuộc qua `npx hyperframes`, không chép code |
| lemomo-ai/lemo-opuscar (commit a75e2b3) | MIT | Khuôn style card và các `STYLE.md` được chọn | Chép, thêm phần đầu ghi nguồn, Việt hóa phần dùng chung |
| bestagentkits/motion-video-skill (commit a73702b) | MIT | `fit-beat-grid.py`, `verify-arrangement.py`, `measure-mix-balance.py`; quy tắc trộn âm và neo theo từ | Chép vào `vendor/`, đọc từng dòng trước khi chép |
| latent-spaces/brag | MIT | Ý tưởng tone preset, chữ phải hiện đủ lâu | Học ý, không chép kho nhạc |
| edenfunf/reelmimic | MIT | Tách người dựng và người chấm; file quyết định xong | Học ý |
| JohnHeibel/ClaudeAnimationBase | MIT | Luật hoạt hình (mỗi cảnh có việc xảy ra, thời gian theo số ý người xem phải đọc) | Tóm thành luật trong skill dựng, ghi nguồn |
| pnnbao97/VieNeu-TTS | Apache-2.0 | Giọng đọc | Phụ thuộc `pip install vieneu` |
| faster-whisper | MIT | Chấm phát âm, mốc từng từ | Phụ thuộc |
| Bộ CES của anh, vn-short-video | của anh | Bảng phát âm thuật ngữ Anh, cách chọn bản đọc tốt nhất, chuẩn hóa chữ số tiếng Việt | Viết lại cho Windows (UTF-8, không đường dẫn Linux) |

Không lấy: OpenMontage (AGPL), onetake (cấm thương mại), hypit (giấy phép hạn chế), PDoomVideo (không giấy phép), Remotion (license công ty), MusicGen (cấm thương mại).

Mọi thứ chép về được ghi trong `NOTICE.md` (repo, file, commit, giấy phép, đã sửa gì); văn bản giấy phép gốc giữ trong `vendor/licenses/`.

## 4. Luồng và file trung gian

Mỗi video là một thư mục `videos/<slug>/` trong thư mục người dùng đang làm việc. Mỗi bước ghi đúng một file, bước sau chỉ đọc file đó.

| # | Bước | Skill | File ra | Cổng duyệt |
|---|---|---|---|---|
| 1 | Hiểu yêu cầu, chọn style, tỉ lệ khung, độ dài, giọng | `video-moi` | `brief.json` | Hỏi khi thiếu |
| 2 | Ý tưởng, kịch bản theo cảnh | `video-moi` | `script.json` | Có |
| 3 | Giọng: sinh từng câu, chấm bằng Whisper, giữ bản tốt nhất, lấy mốc từng từ | `giong-doc` | `voice/*.wav`, `voice.wav`, `words.json` | Không |
| 4 | Phân cảnh trên mốc giọng thật: mỗi cảnh hình gì, xuất hiện ở từ nào, chuyển cảnh | `video-moi` | `storyboard.json`, `timeline.json` | Có (kèm tờ ảnh tĩnh sau bước 6a) |
| 5 | Nhạc nền: file của người dùng, hoặc ACE-Step, hoặc nhạc tổng hợp bằng code; đo nhịp | `nhac-nen` | `music/bgm.wav`, `music/beats.json` | Không |
| 6a | Dựng từng cảnh thành HTML theo style; sub-agent mỗi cảnh một file | `dung-video` | `index.html`, `compositions/*.html` | Không |
| 6b | Trộn âm: nhạc hạ theo khoảng có lời, loudnorm hai lượt -14 LUFS | `dung-video` | `mix.wav` | Không |
| 6c | Kiểm: HyperFrames check, neo từ khóa không trượt, snapshot tờ tĩnh, người chấm độc lập | `dung-video` | `checks/` | Không |
| 7 | Render, ghép âm, phụ đề `.srt`, bản nhẹ dưới 27 MiB | `dung-video` | `renders/<slug>.mp4`, `phude.srt` | Có (trước render cuối) |

Người dùng nói "tự làm hết" thì bỏ các cổng, chỉ báo cáo cuối.

### Định dạng chính

`script.json`:
```json
{"title": "...", "voice": "Ngọc Huyền", "aspect": "9:16",
 "scenes": [{"id": "s1", "say": "Câu 1. Câu 2.", "intent": "ý cảnh cần truyền đạt"}],
 "pron": {"MCP": "em xi pi"}}
```

`words.json`: `{"total": 61.2, "words": [{"scene": "s1", "w": "Claude", "start": 1.42, "end": 1.80}]}`

`timeline.json`: mốc bắt đầu, kết thúc từng cảnh và danh sách neo `{"scene","kw","t"}` dùng cho composition; neo không tìm thấy từ thì lỗi `KW miss`, không lặng lẽ dùng giây cứng.

## 5. Style

`styles/<slug>/STYLE.md`: đầu file có khối nguồn (repo, file, commit, giấy phép, đã sửa gì), thân giữ khuôn 11 mục của lemo-opuscar. Style chỉ chứa luật đúng với mọi video cùng style. Yêu cầu riêng của người dùng thắng luật style, trừ luật cấm của style (mâu thuẫn thật thì hỏi).

Bản đầu chép 6 style: `whiteboard`, `iso-infographic`, `dataviz`, `swiss-motion`, `dark-keynote`, `paper-popup`. Thêm style sau chỉ cần thêm thư mục, không sửa code.

Bổ sung bắt buộc cho tiếng Việt ở mọi style: font phải có đủ dấu (mặc định Be Vietnam Pro); phụ đề tối đa 44 ký tự mỗi dòng, giữ tối thiểu 1,8 giây.

## 6. Nhạc nền

Thứ tự nguồn: (1) file người dùng đưa; (2) ACE-Step 1.5 chạy local nếu đã cài (giai đoạn sau); (3) nhạc tổng hợp bằng code `tools/music/synth.py` (hợp âm nền và nhịp nhẹ, theo mood, BPM, độ dài; cùng tham số thì cùng kết quả). Repo không đóng gói file nhạc của bên thứ ba vì điều khoản các kho miễn phí cấm phân phối lại.

Trộn: nhạc hạ khoảng 8 dB trong khoảng có lời dựa trên `words.json` (đường bao, attack 0,2 s, release 0,5 s), rồi loudnorm hai lượt `I=-14, TP=-1.5`. Đo lại bằng ebur128 sau render.

## 7. Hình ảnh

Mặc định vẽ bằng code (HTML, SVG, Canvas, GSAP) trong composition HyperFrames. Ảnh từ ChatGPT là tùy chọn: Claude điều khiển trình duyệt, tạo ảnh, tải về `assets/`, ghi nguồn vào `assets/manifest.json`; chỉ dùng khi style hoặc người dùng cần.

Luật dựng: mỗi cảnh là hàm thuần của thời gian (không `Math.random`, không `Date`); mỗi câu lời đọc làm xuất hiện hoặc biến đổi ít nhất một hình; chữ trên hình là nhãn ngắn, không chép nguyên lời đọc.

## 8. Lỗi và phục hồi

- Mỗi bước kiểm file đầu vào; thiếu thì báo rõ bước nào chưa chạy.
- Giọng: câu có điểm Whisper dưới 0,85 bị gắn WEAK, sinh lại tối đa 3 lần rồi giữ bản tốt nhất và báo.
- Sinh giọng cache theo hash (giọng, chữ, nhiệt độ): sửa một câu chỉ sinh lại câu đó.
- Render chạy nền, log ra file; render lỗi thì không xóa file trung gian.

## 9. Kiểm thử

- Script Python có test `pytest` cho phần thuần (chuẩn hóa chữ, dựng timeline, neo từ khóa, đường bao ducking).
- Kiểm thật: chạy `/video-cai-dat` trên máy anh; làm video mẫu 1 phút "Skill, MCP, Agent là gì"; đo ffprobe, ebur128, kiểm tờ tĩnh.

## 10. Ngoài phạm vi bản đầu

ACE-Step, MV khớp lời bài hát có sẵn, ảnh ChatGPT tự động hoàn toàn, giao diện web. Ghi vào lộ trình, làm sau khi bản đầu chạy ổn.
