---
name: dung-video
description: Dựng hình cho dự án video đã có giọng và phân cảnh: viết từng cảnh thành composition HyperFrames theo style, ghép, kiểm tra, xuất tờ duyệt, render và ghép âm thanh, phụ đề. Dùng trong bước 6 và 7 của /video-moi, hoặc khi người dùng nói "dựng lại cảnh", "render", "xuất video", "sửa hình cảnh X".
---

# Dựng video

Biến `VV`, `PY` như trong skill `video-cai-dat`. HF là `npx -y hyperframes@0.8.145`.

Đầu vào bắt buộc trong `<du-an>`: `storyboard.json`, `words.json`, `timeline.json` (chạy `"$PY" "$VV/tools/timeline.py" <du-an>`; còn `KW miss` thì sửa `kw` trong storyboard cho đúng chữ trong lời đọc rồi chạy lại), `mix.wav`.

## 1. Chuẩn bị theo style

1. Đọc `$VV/styles/<style>/STYLE.md` (style trong `storyboard.json`). Đọc cả mục "Bổ sung của MotionFly" ở cuối: mục đó thắng phần trên.
2. Viết `<du-an>/theme.css` với biến `:root` lấy từ color logic của style (và màu thương hiệu nếu brief có): `--bg`, `--ink`, `--accent`, các màu phụ, `--cap-bg`, `--cap-ink` (phụ đề phải đạt tương phản WCAG AA).
3. Viết `<du-an>/quy-uoc-chung.md`: bộ nét vẽ mọi cảnh phải dùng chung để video liền một khối (độ dày nét, cách vẽ nét xuất hiện, nghĩa của từng màu, cỡ chữ, hình mẫu lặp lại như nhân vật hay đồ vật, chuyển động vào và ra cảnh, vùng an toàn chừa phụ đề). Không có file này thì mỗi agent vẽ một kiểu.
4. Nếu style có nền liền suốt video (bảng trắng, giấy, lưới), viết `compositions/_nen.html` (sub-composition id `_nen`): bộ ghép tự đặt nó dưới mọi cảnh từ đầu tới cuối, và các cảnh để nền trong suốt.
5. Chạy `"$PY" "$VV/tools/assemble.py" <du-an>`: tạo `index.html`, chép font, tạo file khung chờ cho cảnh chưa có.

## 2. Dựng từng cảnh

Mỗi cảnh là một file `compositions/<id>.html` theo khuôn `$VV/templates/scene.html`.

- Từ 4 cảnh trở lên: giao mỗi cảnh cho một agent `dung-canh`, **phát tất cả trong cùng một tin nhắn** để chạy song song. Mỗi agent chỉ sửa đúng file cảnh của mình.
- Dưới 4 cảnh: tự dựng theo đúng các luật trong `agents/dung-canh.md`.
- **Không có công cụ giao agent con** (Codex, Antigravity, Gemini CLI...): dùng **chế độ tuần tự** bên dưới.

### Chế độ tuần tự (một mình dựng cả video)

Làm từng cảnh một, không viết hết rồi mới xem:
1. Đọc gói `checks/packets/<id>.md`, `$VV/agents/dung-canh.md`, `$VV/templates/kit/README.md` và xem `$VV/examples/crayon-claude-tinh-nang-moi/01_to-duyet.jpg` để biết mức chăm chút cần có.
2. Viết `compositions/<id>.html` (nên dùng bộ đồ nghề `window.MF` cho phần nét, chữ, tô, camera).
3. Chạy `"$PY" "$VV/tools/scene_check.py" <du-an> <id>`, **mở ảnh `checks/scene/<id>.jpg` ra xem** và sửa tới khi ảnh sạch và lệnh in `GATE PASS`.
4. Xong mới sang cảnh tiếp theo.

Khi đủ cảnh: làm mục 3, mục 4; vai người chấm thì tự đóng ở một lượt riêng theo đúng `$VV/agents/nguoi-cham.md`, chỉ nhìn ảnh, không nhìn code, rồi ghi `checks/review.md`.

Tạo gói giao việc cho mọi cảnh (thời gian cục bộ từng từ, neo `A("key")`, ý hình, cảnh trước và sau, biến màu, quy ước chung):

```bash
"$PY" "$VV/tools/packets.py" <du-an>
```

Lời giao cho mỗi agent: đọc `$VV/agents/dung-canh.md`, gói `checks/packets/<id>.md` và style card, rồi viết lại đúng file `compositions/<id>.html`. Nếu plugin chưa đăng ký agent `dung-canh` trong phiên, dùng agent đa năng và dặn nó đóng vai `dung-canh` theo file đó.

## 3. Ghép và kiểm tra

```bash
"$PY" "$VV/tools/assemble.py" <du-an>
cd <du-an> && npx -y hyperframes@0.8.145 check
```

Sửa đến khi `Check passed` và 0 error. Lỗi lint nằm ở file cảnh nào thì sửa file đó (hoặc giao lại đúng agent của cảnh đó). Cảnh báo `timeline_track_too_dense` của phụ đề là bình thường.

## 4. Tờ duyệt và người chấm

```bash
"$PY" "$VV/tools/sheet.py" <du-an> --extra 1
```

Mở `checks/sheet.jpg` bằng Read và tự soát: chữ tràn mép, chữ đè phụ đề (phụ đề chiếm 12 phần trăm đáy khung), tương phản thấp, cảnh trống, sai dấu tiếng Việt. Sau đó giao agent `nguoi-cham` (cuộc trò chuyện mới, chỉ đưa brief, storyboard, sheet và đường dẫn ảnh snap, không đưa lập luận của người dựng). Chép nguyên báo cáo của người chấm vào `checks/review.md` (dòng đầu `KẾT LUẬN: ĐẠT` hoặc `KẾT LUẬN: CHƯA ĐẠT`). Sửa các lỗi `blocker`, tạo lại tờ duyệt, chấm lại, tối đa 2 vòng; phần còn lại ghi vào báo cáo.

Đây là cổng duyệt 2 của `/video-moi`: gửi `checks/sheet.jpg` cho người dùng (SendUserFile nếu có) và chờ đồng ý, trừ khi người dùng đã nói "tự làm hết". Muốn xem có tiếng: `cd <du-an> && npx -y hyperframes@0.8.145 preview --background`.

## 5. Cổng chặn, render và ghép

Trước khi render, bắt buộc:

```bash
"$PY" "$VV/tools/gate.py" <du-an>
```

Chỉ render khi lệnh in `GATE PASS`. Cổng kiểm: không còn cảnh khung chờ, `hyperframes check` qua, tờ duyệt mới hơn file cảnh, có `checks/review.md` kết luận ĐẠT và chép đúng `Mã tờ duyệt` in trên `checks/sheet.jpg`, mọi số từ 2 chữ số trở lên trên hình có trong `script.json`, `brief.json` hay `storyboard.json`, không đoạn nào đứng yên quá 1,5 giây (đo trên ảnh chụp mỗi 0,5 giây). Dòng `chú ý` trỏ tới ảnh khung cuối cảnh cần mở ra xem. Không được sửa file `gate.py` hay viết review.md giả để qua cổng.


```bash
"$PY" "$VV/tools/assemble.py" <du-an> --no-audio
cd <du-an> && npx -y hyperframes@0.8.145 render --output renders/raw.mp4 > renders/render.log 2>&1
"$PY" "$VV/tools/audio/mix.py" srt <du-an>
"$PY" "$VV/tools/audio/mix.py" final <du-an> --video <du-an>/renders/raw.mp4 --name <ten-file>
"$PY" "$VV/tools/assemble.py" <du-an>
```

Render chạy nền (khoảng 2 giây máy cho mỗi giây video). Dòng `--no-audio` là bắt buộc: HyperFrames tự trộn âm cần bộ lọc ffmpeg mà bản rút gọn không có, và trộn lại sẽ đẩy đỉnh âm; `mix.py final` ghép `mix.wav` nguyên vẹn. Lệnh assemble cuối trả `index.html` về bản có tiếng để xem trước.

## 6. Kiểm cuối

- `ffprobe` file `renders/<ten-file>.mp4`: đúng kích thước, 30 fps, có luồng aac, thời lượng bằng `total` trong `words.json` (lệch dưới 0,1 s).
- `"$PY" "$VV/tools/audio/mix.py" measure <du-an>/renders/<ten-file>.mp4`: I trong -14 ± 0,5 LUFS, TP không quá -1,0.
- Trích 3 khung bằng ffmpeg ở giữa video và xem lại.

Giao: `renders/<ten-file>.mp4` (và `<ten-file>-nhe.mp4` nếu có), `phude.srt`, `checks/sheet.jpg`.
