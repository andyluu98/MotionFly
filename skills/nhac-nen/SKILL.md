---
name: nhac-nen
description: Chọn hoặc tạo nhạc nền cho dự án video, đo nhịp, rồi trộn với giọng (nhạc tự hạ khi có lời, chuẩn -14 LUFS). Dùng trong bước 5 của /video-moi, hoặc khi người dùng gửi file nhạc, nói "đổi nhạc", "nhạc sôi động hơn", "nhạc nhỏ lại".
---

# Nhạc nền

Biến `VV`, `PY` như trong skill `video-cai-dat`.

## Chọn nguồn (theo thứ tự)

1. **Người dùng đưa file nhạc:** chép vào `<du-an>/music/bgm.<đuôi>` rồi chuyển sang `bgm.wav`:
   `ffmpeg -y -i <file> -ar 48000 -ac 2 <du-an>/music/bgm.wav`. Nhạc ngắn hơn video thì báo người dùng (bộ trộn sẽ để lặng phần thiếu).
2. **ACE-Step** (chưa có trong bản này; khi được cài sẽ ghi ở đây).
3. **Nhạc tổng hợp bằng code** (mặc định khi không có 1 và 2):

```bash
"$PY" "$VV/tools/music/synth.py" <du-an> --duration <total trong words.json> --mood <mood> [--bpm N] [--seed N]
```

Chọn `mood` theo style và nội dung:

| mood | Nhịp mặc định | Hợp với |
|---|---|---|
| calm | 84 | whiteboard, giải thích chậm, chủ đề nghiêm túc |
| inspiring | 96 | explainer, đào tạo, câu chuyện tích cực |
| upbeat | 112 | quảng cáo, promo, swiss-motion |
| tech | 104 | dark-keynote, sản phẩm công nghệ, dataviz |

Đổi `--seed` để có giai điệu khác cùng mood. Không bao giờ tải nhạc từ web về đóng gói vào repo hay dự án nếu người dùng không đưa file và không xác nhận giấy phép.

## Đo nhịp (khi cần cắt cảnh theo beat)

Nhạc tổng hợp đã có `music/beats.json`. Nhạc người dùng đưa thì đo bằng script chép từ bestagentkits:

```bash
"$PY" "$VV/vendor/bestagentkits/fit-beat-grid.py" <du-an>/music/bgm.wav --min-bpm 70 --max-bpm 140
```

Ghi BPM và BEAT0 in ra vào `music/beats.json` (`{"bpm":..,"beat0":..,"source":"fit-beat-grid"}`). Cột dB từng ô nhịp cho biết chỗ nhạc dâng (build) và bùng (drop): đặt cảnh cao trào của kịch bản trùng chỗ drop nếu được.

## Trộn

```bash
"$PY" "$VV/tools/audio/mix.py" mix <du-an> [--music-db -6] [--duck-db 5]
```

- `--music-db`: nhạc so với giọng khi đang nói (mặc định -6 dB). Người dùng nói "nhạc nhỏ lại" thì giảm (-9); "không nghe thấy nhạc" thì tăng (-4).
- `--duck-db`: nhạc to thêm bao nhiêu lúc không có lời (mặc định 5 dB).
- In `MIXDONE I=<LUFS> TP=<dBTP>`. Đạt khi I trong khoảng -14 ± 0,5 và TP không quá -1,0.
