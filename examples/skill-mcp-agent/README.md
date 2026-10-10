# Ví dụ: Skill, MCP và Agent trong một phút

Video mẫu làm bằng chính plugin (style whiteboard, 9:16, 56 giây, giọng Ngọc Huyền, nhạc tổng hợp mood calm).

Thư mục này chỉ giữ đầu vào và các file cảnh; âm thanh, video không đưa vào repo. Dựng lại:

1. Chép thư mục này sang `videos/skill-mcp-agent/`.
2. Chạy lần lượt (biến `VV`, `PY` như skill `video-cai-dat`):

```bash
"$PY" "$VV/tools/voice/voice.py" videos/skill-mcp-agent
"$PY" "$VV/tools/timeline.py" videos/skill-mcp-agent
"$PY" "$VV/tools/music/synth.py" videos/skill-mcp-agent --duration <total trong words.json> --mood calm --seed 3
"$PY" "$VV/tools/audio/mix.py" mix videos/skill-mcp-agent
```

3. Render theo skill `dung-video` mục 5.

Các cảnh `compositions/s1.html` đến `s7.html` do 7 agent `dung-canh` dựng song song từ gói giao việc; `_nen.html` là lớp bảng trắng chung.
