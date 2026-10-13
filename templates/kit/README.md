# Bộ đồ nghề MotionFly (`window.MF`)

Không bắt buộc. Dùng khi muốn có ngay chất liệu đẹp và tránh các lỗi hay gặp; bỏ qua khi muốn tự vẽ theo cách riêng. `tools/assemble.py` tự chép `mf-kit.js` vào dự án và nạp trước mọi cảnh.

Cảnh mẫu dùng bộ đồ nghề (khoảng 40 dòng): `vi-du-canh.html`. Video mẫu đầy đủ đã duyệt: `examples/crayon-claude-tinh-nang-moi/` (ảnh tờ duyệt `01_to-duyet.jpg`).

## Bắt đầu một cảnh

```js
(() => {
  const K = MF.scene("s3", { bpm: 92, doc: document });   // luôn truyền document của cảnh
  const G = MF.geo, $ = K.$;
  $("defs").innerHTML = MF.style.crayon.defs("s3");      // gói chất liệu (có crayon, blueprint)
  K.pageIn(); K.drift(); K.pageOut(); K.boil();           // vào cảnh, camera trôi, ra cảnh, chất liệu "thở"
  K.draw("outline", K.A("hook"), 0.6, { pen: "#s3-pen" });
  K.write("title", 0.3, 0.35);
  K.done();                                               // đăng ký timeline, cảnh báo hình chạy sát cuối cảnh
})();
```

`K.$("ten")` lấy phần tử `#<cảnh>-ten`; `K.$("#id")`, `K.$(".lop")` cũng được.

## Hàm theo cảnh (`K`)

| Hàm | Làm gì | Lỗi nó chặn sẵn |
|---|---|---|
| `draw(el, t, dur, {steps, pen, opacity})` | Vẽ nét theo nhát (mặc định 8 nấc), bút đi theo đầu nét | Ẩn nét tới đúng lúc vẽ: không còn chấm đầu nét tròn trên giấy trống |
| `write(el, t, dur, {seed, tilt, lift})` | Chữ hiện từ trái sang phải, mỗi chữ cái nghiêng lệch theo công thức | Chuẩn hóa NFC (không tách dấu), gắn sẵn cờ cho phép chữ cái chạm nhau |
| `colour(els, t, dur, {from, steps})` | Tô màu theo hàng (left, right, top, bottom) | |
| `clip(fill, shape, grow)` | Giữ vùng tô trong hình, tràn nhẹ vài px như trẻ con tô | Màu không loang ra ngoài cả khung |
| `pop(els, t, dur, {origin, ease})` | Bật hình ra | |
| `pageIn()`, `drift()`, `pageOut()` | Lật trang vào, camera trôi chậm trên `#<cảnh>-cam`, lật trang ra 0,3 giây cuối | Camera và lật trang không giành nhau thuộc tính `x` |
| `boil(selector, fps)` | Đổi seed của mọi `feTurbulence` có class `<cảnh>-turb` (12 khung/giây) | |
| `beats(from, to)` | Danh sách phách nhạc (thời gian trong cảnh) | |
| `done({last})` | Gán `window.__timelines`; báo `MF <cảnh>: ... sát cuối cảnh` nếu còn tween mới chạy trong 0,6 giây trước lúc ra | Chữ viết dở ở khung cuối. Tween lặp trang trí (nhún theo phách) thì thêm `mfIdle: true` |

Biến có sẵn: `K.tl`, `K.DUR`, `K.A(key)`, `K.exitAt`, `K.root`.

## Hình học tay (`MF.geo`)

`wobRect(x, y, w, h, r, seed)`, `wobEll(cx, cy, rx, ry, seed)`, `hatch(x, y, w, h, {g, s, ov, seed, v})` (nét tô zíc zắc tràn viền), `hatchEll(...)`, `scrib(x0, x1, y, seed)` (chữ nguệch ngoạc thay chữ viết tay), `star(cx, cy, R, r, n)`. Tất cả tất định: cùng tham số luôn ra cùng hình.

## Gói chất liệu (`MF.style`)

- `crayon.defs(p)`: filter `p-fline` (nét sáp run tay), `p-fwax` (sáp lốm đốm trên thớ giấy, cho vùng tô), `p-ftxt` (chữ).
- `blueprint.defs(p)`: pattern `p-hatch` (gạch mặt cắt 45 độ), filter `p-glow`.

Style khác chưa có gói: tự viết filter theo style card, hoặc thêm gói mới vào `mf-kit.js`.
