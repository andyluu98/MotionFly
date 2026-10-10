## Quy ước chung của video "AI trong ngành xây dựng" (blueprint, bắt buộc)

Toàn video là MỘT tờ bản vẽ cyanotype. Mỗi cảnh là một "Hình" trên tờ đó (HÌNH 1 đến HÌNH 7). Nét trắng vẽ dần theo thứ tự kỹ thuật, chú thích di chuyển, khô và chính xác. Video phải **sinh động**: mỗi cảnh tối thiểu 12 phần tử có chuyển động riêng, mỗi câu lời đọc làm xuất hiện hoặc biến đổi ít nhất một nét.

### Nền và khung
- KHÔNG vẽ nền: `#<id>-root` để `background: transparent`. Tờ giấy xanh, lưới mờ, nếp gấp, khung viền đôi và dải tiêu đề "MOTIONFLY · BẢN VẼ SỐ 01" ở trên cùng đã có ở lớp `_nen`.
- Khung 1080x1920. Dải tiêu đề chiếm y 40 đến 110: không vẽ đè. Nội dung cảnh trong x 80 đến 1000, y 150 đến 1580. Đáy từ y 1640 dành cho phụ đề.
- Bọc nội dung trong `#<id>-stage`.

### Màu (chỉ xanh và trắng)
- Nét: `var(--line)` (trắng xanh nhạt). Nét phụ `var(--line-soft)`, nét mảnh `var(--hair)`.
- Vật đặc phải tô "giấy" `fill: var(--fill)` TRƯỚC khi vẽ đường bao, để che các nét phía sau (luật che khuất theo thứ tự vẽ).
- **Màu đỏ `var(--stamp)` chỉ dùng MỘT lần trong cả video**: con dấu "ĐÃ DUYỆT" ở cảnh s6. Các cảnh khác tuyệt đối không có màu nào ngoài xanh và trắng.
- Có thể có quầng sáng trắng nhẹ (`filter: drop-shadow(0 0 6px rgba(231,240,249,.5))`) ở đầu ngòi bút, không dùng màu khác.

### Nét và quy ước bản vẽ (SVG)
- Bốn độ dày: đường bao `var(--w-out)` (5px), chi tiết `var(--w-det)` (3px), mảnh và đường kích thước `var(--w-thin)` (2px), nét gạch mặt cắt `var(--w-hair)` (1,2px). `stroke-linecap: round`, `stroke-linejoin: round`, `fill: none` (trừ vật đặc tô `var(--fill)`).
- Kiểu nét: đường tâm `stroke-dasharray: 22 6 4 6`; nét khuất `10 7`; đường cắt mặt cắt `28 6 6 6 6 6`.
- **Thứ tự vẽ**: đường tâm, đường bao, chi tiết, gạch mặt cắt 45 độ (khoảng cách 10 đến 14px), đường kích thước (có mũi tên hoặc gạch chéo ở hai đầu, chữ số đặt trên đường), bóng số (vòng tròn có số, kèm đường dẫn), nhãn.
- **Vẽ nét có ngòi sáng**: tween `strokeDashoffset` từ độ dài về 0 (đo bằng `getTotalLength()`), ease `power1.inOut`; kèm một chấm tròn trắng 8px có quầng sáng chạy theo đầu nét (cập nhật vị trí bằng `getPointAtLength` trong `onUpdate` của tween, tính theo tiến độ tween, không dùng thời gian thực). Mỗi lớp nét bắt đầu đúng phách.
- **Chữ**: tiếng Việt có dấu dùng Be Vietnam Pro 600 đến 700, viết HOA cho nhãn kỹ thuật, giãn chữ 0,06em; chữ không dấu, số, mã hiệu dùng JetBrains Mono (khai báo `@font-face { font-family: "JetBrains Mono"; src: url("fonts/JetBrainsMono-Variable.ttf"); font-weight: 100 800; }`). Chữ "viết ra" từ trái sang phải bằng `clipPath: inset(0 100% 0 0)` về `inset(0 0% 0 0)` trong 0,3 đến 0,7 giây. Tiêu đề hình 44 đến 56px; nhãn 30 đến 40px; số kích thước 24 đến 28px.
- **Tiêu đề hình** ở góc trên trái vùng nội dung (x 80, y 150): "HÌNH n: TÊN", viết ra trong 0,5 giây đầu cảnh, kèm gạch chân nét mảnh.
- Hình là hình chiếu thẳng góc, mặt cắt, hoặc hình chiếu xiên/isometric bằng nét. **Không render 3D, không đổ bóng màu, không gradient màu.** Không vẽ người: nhân vật là vật được thiết kế (cánh tay robot vẽ kỹ thuật, bánh răng, com-pa, cần cẩu...).
- Ký hiệu phần mềm (AutoCAD, Revit, Excel): hộp kỹ thuật có tên viết bằng chữ, KHÔNG dùng logo.
- Không bịa số liệu: kích thước minh họa thì ghi nhãn nhỏ "VÍ DỤ"; bảng dự toán không điền số (ô khối lượng là nét gạch chờ).

### Chuyển động
- Nhịp nhạc 104 BPM tính từ 0 giây của video. Hàm lấy phách (thời gian cục bộ):
  ```js
  const BEAT = 60 / 104, S = window.__vv.scenes["<id>"].start;
  const beats = (from, to) => { const o = []; for (let k = Math.ceil((S + from) / BEAT); k * BEAT - S <= to; k++) o.push(k * BEAT - S); return o; };
  ```
- Cơ cấu chuyển động theo nấc như bộ thoát đồng hồ: bánh răng nhích một răng mỗi nửa phách (ease-out ngắn); cánh tay robot gập khớp có quán tính; bóng số bật ra `back.out(1.6)`.
- Camera: `#<id>-stage` đẩy vào rất chậm (scale 1 lên 1,03) suốt cảnh. Vào cảnh: `#<id>-stage` từ x +220, opacity 0 tới x 0, opacity 1 trong 0,45 giây (`power3.out`), như mắt lia ngang sang hình tiếp theo trên cùng tờ giấy. 0,3 giây cuối: x về -220, opacity 0 (`power2.in`). Cảnh cuối giữ hình.
- Không khung nào đứng yên quá 1,5 giây: giữa hai neo có chi tiết phụ (đường kích thước kéo ra, gạch mặt cắt chạy, xung tín hiệu chạy dọc dây, bóng số nhấp theo phách).

### Cấm
Không thẻ audio/video, không `data-start` trong cảnh, không `Math.random`, `Date`, `requestAnimationFrame`, `setTimeout`, `repeat: -1`. Chỉ tween `x`, `y`, `xPercent`, `yPercent`, `scale`, `rotation`, `opacity`, `clipPath`, `strokeDashoffset`, `attr`; không tween `top`, `left`, `width`, `height`, `letterSpacing`. Không dùng `mix-blend-mode`. Không tween `visibility`/`display`/`autoAlpha`.
