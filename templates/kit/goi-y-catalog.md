# Gợi ý khối chuyển động có sẵn (HyperFrames catalog)

HyperFrames, bộ máy MotionFly chạy bên dưới, có kho 447 khối chuyển động dựng sẵn. Dưới đây là các khối hợp video giải thích tiếng Việt, chạy được trên máy không có card đồ họa. Chọn theo việc cần làm, đừng tự viết lại thứ đã có.

Xem đủ kho: `npx -y hyperframes@0.8.145 catalog <từ khóa tiếng Anh>` (ví dụ `catalog arrow`, `catalog chart`).

## Cách gắn một khối vào cảnh

1. Cài vào dự án (chạy trong thư mục dự án):
   ```bash
   npx -y hyperframes@0.8.145 add terminal-simulator --no-clipboard
   ```
   Khối loại C (component) nằm ở `compositions/components/<tên>.html`; khối loại B (block) nằm ở `compositions/<tên>.html`.
2. Mở file vừa cài, đọc phần chú thích đầu file: nó ghi các biến (`data-composition-variables`) và thời lượng.
3. **Loại C**: gắn thẳng vào cảnh bằng một thẻ đặt chỗ trong `#<cảnh>-root`. `data-start` tính từ đầu cảnh, khung đặt chỗ quyết định vị trí và cỡ:
   ```html
   <div id="s3-term" data-composition-id="terminal-simulator"
        data-composition-src="compositions/components/terminal-simulator.html"
        data-variable-values='{"accent":"blue"}'
        data-start="1.2" data-duration="4" data-track-index="5"
        style="position:absolute;left:90px;top:420px;width:900px;height:620px"></div>
   ```
   Đã thử: gắn trong cảnh MotionFly qua `hyperframes check` và chạy đúng giờ.
4. **Loại B**: thường dựng sẵn cả một khung riêng (kích thước cố định). Đọc file để học cách làm rồi chép phần cần vào timeline cảnh của mình, đổi màu theo `theme.css`.
5. Màu và chữ của khối phải theo style của video: đặt qua biến nếu khối có, không thì chép về và sửa. Chữ tiếng Việt trong khối vẫn phải qua `hyperframes check`.

## Danh sách gợi ý theo việc

| Cần làm | Khối | Loại | Làm gì |
|---|---|---|---|
| Vẽ hình hiện dần | `whiteboard-ink` | C | Phác từng nét, đầu bút chạy theo nét; có sẵn hình bóng đèn, sơ đồ, tên lửa hoặc nét của bạn |
| | `svg-stroke-trace` | C | Một đường SVG tự vẽ ra, đường khép kín thì tô màu sau khi vẽ xong |
| | `ink-bleed-reveal` | C | Mực loang trên giấy rồi thu lại thành hình |
| Chỉ vào, nhấn mạnh | `hw-arrow` | C | Mũi tên vẽ tay, cong hoặc thẳng, có đầu mũi theo hướng |
| | `hw-callout-circle` | C | Vòng tròn vẽ tay khoanh một vật, nhãn bật ra |
| | `hw-box-label`, `hw-underline` | C | Khung chữ, gạch chân, gạch xóa vẽ tay |
| | `marker-highlight`, `inline-highlight` | C | Bút dạ quang tô lên đúng chữ được nói |
| | `outline-draw` | C | Viền bo tròn tự vẽ quanh một ô cần chú ý |
| Chữ ít mà có lực | `headline-slam` | C | Tiêu đề lớn đập vào khung, rung ba khung hình |
| | `kinetic-type-swap` | C | Câu giữ nguyên, một chữ xoay qua nhiều phương án rồi dừng |
| | `strikethrough-replace` | C | Gạch chữ cũ, hiện chữ mới (quan niệm sai thành đúng) |
| | `per-word-rise`, `scramble-reveal` | C | Từng chữ trồi lên; chữ chạy kiểu máy tính rồi khóa lại |
| Số liệu (chỉ số có nguồn) | `count-up` | C | Số đếm lên hoặc xuống, nảy nhẹ khi dừng |
| | `chart-story`, `animated-bar-chart` | C | Biểu đồ cột, đường, tròn dựng theo đúng số đưa vào |
| | `conic-progress-ring`, `decline-chart` | C | Vòng phần trăm; đường giảm kèm nền tối dần |
| | `bar-chart-race` | B | Các cột đua nhau theo thời gian |
| Máy tính, AI, phần mềm | `terminal-simulator` | C | Cửa sổ dòng lệnh gõ lệnh, chạy log |
| | `agent-cursor` | C | Con trỏ của agent tự gõ, bấm từng bước rồi ra dấu tích |
| | `chat-thread` | C | Cuộc trò chuyện tin nhắn đầy đủ bong bóng |
| | `notification-pileup` | C | Thông báo dồn dập chồng thành tháp (cảm giác quá tải) |
| | `code-typing`, `flowchart-vertical` | B | Code hiện từng chữ; sơ đồ quyết định dọc |
| So sánh, quan hệ | `comparison-split`, `before-after-wipe` | C | Trước và sau, vạch chia quét qua |
| | `constellation-hub`, `radial-surround` | C | Trung tâm và các nhánh tỏa ra, hiện theo lời đọc |
| | `avatar-cloud` | C | Cộng đồng người dùng nối về một điểm |
| Nhân vật, bản đồ | `lottie-character-walk` | B | Nhân vật bước vào, dừng, chỉ tay vào thẻ |
| | `world-map` | B | Bản đồ thế giới tô từng nước |
| Chuyển cảnh | `torn-paper-rip`, `paper-collage-reveal` | C | Xé giấy; mảnh giấy bay đi lộ cảnh sau (hợp style giấy, sáp) |
| | `iris-reveal`, `match-cut`, `morph-swap` | C | Mở vòng tròn; nối hình giống nhau; hình này biến thành hình kia |
| | `whip-pan-cut`, `zoom-through-transition` | C | Lia máy nhanh; phóng xuyên qua thẻ sang cảnh sau |
| Máy quay | `push-in`, `pull-back-reveal` | C | Đẩy vào chậm; lùi ra để lộ bối cảnh |
| | `pan-stations`, `focus-rack` | C | Lia ngang qua các trạm; chuyển nét giữa hai thẻ |
| | `camera-shake` | C | Rung máy cầm tay, tất định (render ra luôn giống nhau) |
| Điểm nhấn | `confetti`, `light-sweep-pass`, `hw-boil` | C | Pháo giấy; vệt sáng quét qua; nét vẽ tay "thở" |

## Nhớ

- Khối là đồ phụ. Hình chính của cảnh (ẩn dụ trung tâm) vẫn tự vẽ, có thể ghép icon (`K.icon`) và hình học tay (`MF.geo`).
- Mỗi video dùng vài khối hợp style, đừng nhét đủ loại: video sáp màu không đi với terminal bóng loáng.
- Tránh các khối có tag `webgpu`, `shader`, `3d` trừ khi style cần và máy có card đồ họa.
