## Quy ước chung của video "5 repo GitHub hot nhất tuần" (dark-keynote, bắt buộc)

Mục tiêu của video này là khoe khả năng chuyển động: **giàu animation, sinh động, chính xác như sân khấu ra mắt sản phẩm**. Mỗi cảnh tối thiểu 15 phần tử có chuyển động riêng, chia 3 lớp:
1. Lớp chính: giao diện kể chuyện (thẻ repo, số lớn, cửa sổ, terminal...).
2. Lớp phụ: chip, biểu tượng, đường nối có chấm dữ liệu chạy dọc, nhãn chữ đơn cách.
3. Lớp môi trường: 10 đến 24 "gói dữ liệu" nhỏ (chấm 6 đến 10px kèm vệt sáng) chạy THẲNG theo đường lưới 48px, màu `var(--c1)`, `var(--c2)`, `var(--c3)` hạ độ bão hòa; vị trí, hướng, độ trễ lấy từ hàm hash theo chỉ số (không Math.random). Không trôi lượn hình sin.

### Nền và khung
- KHÔNG vẽ nền: `#<id>-root` để `background: transparent`. Sân khấu tối, lưới mảnh, quầng sáng đã có ở lớp `_nen`.
- Khung 1080x1920. Nội dung chính trong y 200 đến 1560, x 72 đến 1008. Đáy từ y 1640 dành cho phụ đề.
- Bọc toàn bộ nội dung trong `#<id>-cam` (camera) rồi `#<id>-stage`. Camera đẩy vào chậm suốt cảnh (scale 1 lên 1,05, transformOrigin giữa khung) và có thể có một cú "whip" ngắn khi đổi ý.

### Màu và chữ
- Thang trung tính lạnh: bề mặt `var(--s1)`, `var(--s2)`, `var(--s3)`, viền 1px `var(--line)`, vệt sáng mép trên 1px `var(--hi)`, chữ `var(--ink)`, `var(--ink2)`, `var(--ink3)`.
- **Một màu nhấn duy nhất** `var(--accent)` (xanh chanh, có glow `text-shadow: 0 0 28px var(--accent-glow)`): chỉ dành cho con số sao tăng trong tuần của cảnh (hoặc con số chính của cảnh). Không tô xanh chanh cho thứ khác cùng lúc.
- Chữ tiếng Việt: Be Vietnam Pro (700 đến 800 cho tiêu đề, 500 cho chữ thường). Tên repo, lệnh, nhãn nhỏ: JetBrains Mono, khai báo thêm `@font-face { font-family: "JetBrains Mono"; src: url("fonts/JetBrainsMono-Variable.ttf"); font-weight: 100 800; }`. Nhãn nhỏ viết hoa, giãn chữ 0,12em.
- Tiêu đề một dòng mỗi lúc. Số lớn dùng Be Vietnam Pro 800, giãn chữ -0,04em.

### Thành phần dùng chung (vẽ giống nhau ở mọi cảnh)
- **Thẻ repo**: bo góc 28px, nền `var(--s2)`, viền `var(--line)`, bóng `0 30px 60px rgba(0,0,0,.5)`. Thanh tiêu đề: biểu tượng quyển sách nhỏ (SVG tự vẽ, không dùng logo GitHub) + `owner/repo` JetBrains Mono 30 đến 34px màu `var(--ink2)`, tên repo `var(--ink)`. Dưới là dòng mô tả ngắn và hàng chỉ số: ngôi sao + số.
- **Số đếm nhảy**: tween một object `{v:0}` tới con số đích trong 1,0 đến 1,4 giây, ease `power3.out`, `onUpdate` ghi chữ với dấu chấm ngăn hàng nghìn kiểu Việt (8.319). Tự viết hàm định dạng, không dùng `toLocaleString`.
- **Huy hiệu hạng**: "#1" đến "#5", Be Vietnam Pro 800, cao 240 đến 300px, màu trắng sang `var(--ink3)` dạng gradient chữ; xuất hiện bằng mặt nạ trồi từ dưới lên kèm một vệt sáng quét ngang.
- **Chip "+N tuần này"**: viên thuốc nền `var(--s3)`, chữ JetBrains Mono, số dùng `var(--accent)`.

### Chuyển động
- Mọi thứ khớp lưới và khớp nhịp. Nhịp nhạc 104 BPM tính từ 0 giây của video. Dùng hàm này trong script cảnh để lấy các phách (thời gian cục bộ):
  ```js
  const BEAT = 60 / 104, S = window.__vv.scenes["<id>"].start;
  const beats = (from, to) => { const o = []; for (let k = Math.ceil((S + from) / BEAT); k * BEAT - S <= to; k++) o.push(k * BEAT - S); return o; };
  ```
  Cho số nhấn, chip, chấm lưới nhấp nhẹ (scale 1 lên 1,04 rồi về) đúng phách, nhất là sau khi số đếm xong.
- Phần tử xuất hiện ngắn và có "tính cách": thả rơi nảy, búng, trượt vào, bật ra; 0,2 đến 0,35 giây; ease `back.out(1.4)`. Mỗi loại phần tử một kiểu xuất hiện.
- Bay theo đường cong (dùng hai tween x, y lệch ease, hoặc motion theo bezier bằng tính tay), vượt nhẹ rồi dừng.
- Ánh sáng là công cụ hé lộ: vệt gradient sáng quét qua thẻ hoặc số khi chúng xuất hiện.
- Biến mất phải được thiết kế: thu về một điểm, kiểu tắt màn hình CRT (scaleY về 0,02 rồi scaleX về 0), không chỉ mờ dần.
- Vào cảnh: `#<id>-stage` từ scale 1,12, mờ 8px, opacity 0 tới bình thường trong 0,4 giây (`power3.out`). 0,3 giây cuối cảnh: tắt kiểu CRT cả stage (cảnh cuối thì giữ hình, không tắt).
- Hình phải xuất hiện đúng lúc từ khóa được đọc (dùng `A("key")`); giữa hai neo vẫn có chuyển động phụ, không khung nào đứng yên quá 1,5 giây.

### Cấm
Không thẻ audio/video, không `data-start` bên trong cảnh, không `Math.random`, `Date`, `requestAnimationFrame`, `setTimeout`, `repeat: -1` (lặp thì dùng số lần hữu hạn), không tween `visibility`/`display`/`autoAlpha` trên phần tử class `clip`, không logo thương hiệu thật (GitHub, Reddit, YouTube...): dùng ô vuông bo góc có chữ cái đầu hoặc biểu tượng hình học tự vẽ, kèm tên viết bằng chữ.
