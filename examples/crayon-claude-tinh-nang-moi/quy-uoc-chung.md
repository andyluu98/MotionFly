## Quy ước chung của video "Ba trang sách mới của Claude" (crayon-book, bắt buộc)

Cả video là MỘT cuốn sách tranh vẽ sáp màu đang được vẽ ngay trước mắt người xem. Mỗi cảnh là một trang được vẽ dần và tô màu dần theo lời đọc. Vẽ và tô màu chính là cốt truyện. Video phải **sinh động**: mỗi cảnh tối thiểu 12 phần tử có chuyển động riêng, mỗi câu lời đọc làm xuất hiện hoặc biến đổi ít nhất một nét.

### Nền và khung
- KHÔNG vẽ nền giấy: `#<id>-root` để `background: transparent`. Giấy ngà có thớ, viền tối nhẹ, gáy sách mờ bên trái đã có ở lớp `_nen`.
- Khung 1080x1920. Nội dung trong x 70 đến 1010, y 110 đến 1600. Đáy từ y 1640 dành cho phụ đề (chữ in của sách), không vẽ gì vào đó.
- Bọc nội dung trong `#<id>-stage`.

### Hộp sáp (chỉ dùng các biến này, không thêm màu)
- Nét viền mọi vật: `var(--ink)` (chàm). **Không bao giờ dùng màu đen.**
- Màu tô: `--accent` (san hô, là "món quà mới" của trang), `--c-sky`, `--c-lemon`, `--c-grass`, `--c-plum`, `--c-orange`, `--c-pink`, `--c-brown`, `--c-white` (sáp trắng: chấm sáng ở mắt, lấp lánh).
- **Màu nước duy nhất `var(--wash)` chỉ dùng ở cảnh s5** (một vệt màu nước xanh quét qua làm hiện chữ viết bằng sáp trắng). Các cảnh khác không có màu nước.

### Chất sáp (bắt buộc, đây là thứ làm nên style)
Khai báo trong SVG của cảnh, mọi filter và pattern đặt id có tiền tố `<id>-`:
1. **Nét sáp run tay**: filter `feTurbulence` (type fractalNoise, baseFrequency 0.035, numOctaves 2) + `feDisplacementMap` scale 3 đến 5, áp lên nhóm nét viền.
2. **Sáp bám đỉnh thớ giấy**: filter thứ hai cho vùng tô: `feTurbulence` (baseFrequency 0.9, numOctaves 2) đổi thành alpha bằng `feColorMatrix`, rồi `feComposite operator="in"` với hình tô, để vùng tô lốm đốm như sáp trên giấy sần (chừa khoảng 15 đến 25 phần trăm điểm giấy).
3. **Tô bằng nét gạch zíc zắc**, không tô phẳng: vùng tô lớn là một `path` zíc zắc dày 18 đến 28px theo một hướng chéo, **tràn ra ngoài viền vài px** như trẻ con tô, kèm một lượt gạch chéo nhạt hơn (opacity 0.5).
4. **Sống động (boil)**: hình đứng yên vẫn "thở": đổi thuộc tính `seed` của các `feTurbulence` bằng `tl.set(turb, { attr: { seed: n } }, t)` mỗi 1/6 giây (12 khung/giây, đổi mỗi 2 khung), lặp bằng vòng for trong timeline (không `repeat: -1`): `for (let t = 0, k = 0; t < DUR; t += 1/6, k++) tl.set(turb, { attr: { seed: 1 + (k % 5) } }, t);`
- Độ dày: viền vật chính `var(--w-out)` (7px), chi tiết `var(--w-det)`, nét nhỏ `var(--w-thin)`. `stroke-linecap: round`, `stroke-linejoin: round`.

### Vẽ dần và tô dần
- **Nét viền vẽ dần**: tween `strokeDashoffset` từ độ dài về 0 trong 0,4 đến 0,9 giây (đo bằng `getTotalLength()`), ease `steps(8)` để thấy từng nhát sáp.
- **Tô màu theo hàng**: vùng tô hiện dần bằng `clipPath: inset(...)` chạy theo hướng gạch, ease `steps(6)`.
- **Chữ trên trang** (tiêu đề, nhãn): Be Vietnam Pro 700 (font duy nhất có đủ dấu), màu `var(--ink)`, mỗi chữ cái nghiêng lệch nhẹ khác nhau (rotate -4 đến 4 độ, y lệch 0 đến 3px, tính bằng công thức theo chỉ số ký tự, không random), hiện từ trái sang phải trong khoảng 0,35 giây mỗi dòng. Tiêu đề trang 72 đến 96px; nhãn 38 đến 52px. Số và ký hiệu không dấu có thể dùng JetBrains Mono.
- Khai báo font: `@font-face { font-family: "Be Vietnam Pro"; src: url("fonts/BeVietnamPro-Bold.ttf"); font-weight: 700; }` (JetBrains Mono nếu dùng: `src: url("fonts/JetBrainsMono-Variable.ttf"); font-weight: 100 800;`).

### Hình mẫu lặp lại (để cả video là một cuốn sách)
- **Số trang**: góc trên phải mỗi cảnh có số trang viết tay trong vòng tròn sáp (s1 không có; s2, s3: "1"; s4: "2"; s5, s6: "3"; s7: "4").
- **Cửa sổ Claude Code** (s2, s3): khung chữ nhật bo góc vẽ tay, thanh trên có 3 chấm (san hô, chanh, cỏ), bên trong vài dòng chữ nguệch ngoạc bằng nét sáp và một dấu nhắc `>`.
- **Đồ vật có mặt** (luật "trẻ con vẽ"): mắt chấm tròn chàm có chấm sáng sáp trắng, má hồng `--c-pink`. Dùng cho: thùng kho dữ liệu (s4), cuốn sách lật (s5), cây bút sáp (s1, s7). Không vẽ người thật; nhân vật chỉ là bút sáp và đồ vật có mặt (riêng s6 có một người que đơn giản vẫy tay, và một bóng người thật bị gạch chéo).
- **Bút sáp dẫn đường**: một cây bút sáp (thân màu, giấy bọc có sọc, đầu nhọn mòn) đi theo đầu nét đang vẽ ở các nét quan trọng (vị trí lấy bằng `getPointAtLength` theo tiến độ tween).
- Không dùng logo thật của Anthropic, Claude hay hãng nào; tên sản phẩm viết bằng chữ tay.

### Chuyển động và camera
- Nhịp nhạc 92 BPM tính từ 0 giây của video. Hàm lấy phách (thời gian cục bộ):
  ```js
  const BEAT = 60 / 92, S = window.__vv.scenes["<id>"].start;
  const beats = (from, to) => { const o = []; for (let k = Math.ceil((S + from) / BEAT); k * BEAT - S <= to; k++) o.push(k * BEAT - S); return o; };
  ```
- Mọi thứ vẽ ra đi theo nấc 12 khung/giây (`steps`), chỉ camera chạy mượt.
- Camera: `#<id>-stage` trôi rất chậm (scale 1 lên 1,04, kèm dịch 10 đến 20px) suốt cảnh.
- Vào cảnh "lật trang": `#<id>-stage` từ `rotation: 6, x: 260, opacity: 0` (transformOrigin "0% 50%") tới bình thường trong 0,45 giây (`power3.out`). Ra cảnh 0,3 giây cuối: `x: -240, rotation: -5, opacity: 0` (`power2.in`). Cảnh cuối s7 giữ hình đến hết.
- Không khung nào đứng yên quá 1,5 giây: giữa hai neo có chi tiết phụ (lấp lánh sáp trắng nhấp theo phách, bút sáp nhún, thêm một lượt gạch tô, mắt đồ vật chớp).

### Cấm
Không thẻ audio/video, không `data-start` trong cảnh, không `Math.random`, `Date`, `requestAnimationFrame`, `setTimeout`, `repeat: -1`. Chỉ tween `x`, `y`, `xPercent`, `yPercent`, `scale`, `rotation`, `opacity`, `clipPath`, `strokeDashoffset`, `attr`; không tween `top`, `left`, `width`, `height`, `letterSpacing`, `fontSize`. Không `mix-blend-mode`. Không tween `visibility`/`display`/`autoAlpha`. Không màu đen, không gradient màu trên vật (chỉ vệt màu nước ở s5), không đổ bóng mềm kiểu đồ họa phẳng.
