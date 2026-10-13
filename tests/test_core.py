import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in ("tools", "tools/voice", "tools/audio"):
    sys.path.insert(0, str(ROOT / p))

from mix import smooth, speech_mask, to_srt  # noqa: E402
from pron import spoken  # noqa: E402
from timeline import captions, find_kw, scene_spans  # noqa: E402
from voice import display_words, has_english, map_words, split_segments  # noqa: E402


def test_split_segments_pauses():
    segs = split_segments("s1", "Câu một. Câu hai! | Câu ba.")
    assert [s["text"] for s in segs] == ["Câu một.", "Câu hai!", "Câu ba."]
    assert segs[0]["pause_after"] == 0.35
    assert segs[1]["pause_after"] == 0.55
    assert [s["id"] for s in segs] == ["s1_1", "s1_2", "s1_3"]


def test_spoken_units_and_overrides():
    assert spoken("Tăng 46% & $52.6B") == "Tăng 46 phần trăm và 52.6 tỷ đô la"
    assert spoken("MCP giúp AI", {"MCP": "em xi pi"}) == "em xi pi giúp AI"
    assert spoken("ai cũng dùng AI", {"AI": "ây ai"}) == "ai cũng dùng ây ai"


def test_display_words_strip_punctuation():
    assert display_words("Skill, MCP và Agent.") == ["Skill", "MCP", "và", "Agent"]
    assert has_english("Claude rất mạnh") and has_english("dùng MCP") and has_english("một agent")
    assert not has_english("xin chào các bạn, con gà trong nhà")


def test_map_words_matches_and_interpolates():
    heard = [{"w": "em", "start": 0.0, "end": 0.2}, {"w": "xi", "start": 0.2, "end": 0.4},
             {"w": "pi", "start": 0.4, "end": 0.6}, {"w": "giúp", "start": 0.7, "end": 0.9},
             {"w": "AI", "start": 1.3, "end": 1.6}]
    out = map_words(["MCP", "giúp", "máy", "AI"], {"MCP": "em xi pi"}, heard)
    assert out[0] == {"w": "MCP", "start": 0.0, "end": 0.6}
    assert out[1]["start"] == 0.7
    assert 0.9 <= out[2]["start"] < out[2]["end"] <= 1.3   # "máy" not heard: interpolated
    assert out[3]["start"] == 1.3


def test_find_kw_nth():
    words = [{"w": w, "start": i} for i, w in enumerate(["Agent", "gọi", "MCP", "rồi", "gọi", "MCP"])]
    assert find_kw(words, "gọi MCP") == 1
    assert find_kw(words, "gọi MCP", 2) == 4
    assert find_kw(words, "Skill") is None


def test_scene_spans_tile_track():
    spans = scene_spans([{"id": "a", "start": 0.5}, {"id": "b", "start": 5.0}], ["a", "b"], 9.0)
    assert spans == [{"id": "a", "start": 0.0, "end": 4.75}, {"id": "b", "start": 4.75, "end": 9.0}]


def test_captions_split_and_hold():
    text = "Một hai ba bốn năm sáu bảy tám chín mười mười một mười hai mười ba"
    seg = {"id": "s1_1", "text": text}
    words = [{"seg": "s1_1", "w": w, "start": i * 0.2, "end": i * 0.2 + 0.15}
             for i, w in enumerate(display_words(text))]
    caps = captions([seg], words)
    assert len(caps) == 2 and all(len(c["text"]) <= 44 for c in caps)
    assert caps[0]["end"] <= caps[1]["start"]
    assert caps[-1]["end"] - caps[-1]["start"] >= 1.8 - 1e-9


def test_captions_no_orphan_word():
    text = "Skill là cuốn sổ tay quy trình của nhân viên đó."
    seg = {"id": "a", "text": text}
    words = [{"seg": "a", "w": w, "start": i * 0.3, "end": i * 0.3 + 0.2} for i, w in enumerate(display_words(text))]
    caps = captions([seg], words, limit=34)
    assert len(caps) == 2
    assert min(len(c["text"]) for c in caps) >= 15 and all(len(c["text"]) <= 34 for c in caps)


def test_duck_envelope_and_srt():
    mask = speech_mask([{"start": 1.0, "end": 1.5}, {"start": 1.6, "end": 2.0}], 4.0)
    assert mask[150] == 1.0 and mask[155] == 1.0 and mask[300] == 0.0   # 0.1 s gap bridged
    env = smooth(mask)
    assert 0 < env[90] < 1 and env[150] == 1.0 and 0 < env[230] < 1
    assert to_srt([{"start": 1.5, "end": 3.25, "text": "Xin chào"}]) == "1\n00:00:01,500 --> 00:00:03,250\nXin chào\n\n"


def test_assemble_loads_kit(tmp_path):
    import json
    from assemble import build
    (tmp_path / "timeline.json").write_text(json.dumps({"width": 1080, "height": 1920, "duration": 4.0, "captions": [],
        "scenes": [{"id": "s1", "start": 0.0, "end": 4.0, "anchors": {}}]}), encoding="utf-8")
    (tmp_path / "storyboard.json").write_text(json.dumps({"title": "t", "scenes": [{"id": "s1", "visual": "x"}]}), encoding="utf-8")
    page = build(tmp_path, audio=False).read_text(encoding="utf-8")
    assert '<script src="kit/mf-kit.js"></script>' in page
    assert (tmp_path / "kit" / "mf-kit.js").exists()


def test_gate_still_vs_moving():
    from PIL import Image, ImageDraw
    import gate
    a = Image.new("RGB", (1080, 1920), "#f4efe3")
    b = a.copy()
    ImageDraw.Draw(b).rectangle((200, 300, 800, 900), fill="#2b2d6e")
    tmp = Path(__file__).parent
    pa, pb = tmp / "_ga.png", tmp / "_gb.png"
    a.save(pa); b.save(pb)
    try:
        fa, fb = gate.prep(pa), gate.prep(pb)
        assert gate.diff(fa, fa) < gate.STATIC
        assert gate.diff(fa, fb) > gate.SETTLE
    finally:
        pa.unlink(); pb.unlink()


def test_gate_numbers_need_a_source(tmp_path):
    import json
    import gate
    (tmp_path / "script.json").write_text(json.dumps({"scenes": [{"id": "s1", "say": "Có 56.069 sao."}]}), encoding="utf-8")
    comp = tmp_path / "compositions"
    comp.mkdir()
    (comp / "s1.html").write_text('<template><div><style>.a{font-weight:700}</style><p>56.069 sao</p>'
                                  '<span data-deco>3200</span><svg><path d="M120 300 L400 500"/></svg>'
                                  '<script>el.textContent = "Tăng 480%"; gsap.to(x, {x: 260});</script></div></template>', encoding="utf-8")
    out = gate.numbers(tmp_path, ["s1"])
    assert len(out) == 1 and "480" in out[0] and "56.069" not in out[0] and "3200" not in out[0]


def test_gate_review_code(tmp_path):
    import hashlib
    import gate
    (tmp_path / "checks").mkdir()
    (tmp_path / "checks" / ".sheet-code").write_text(hashlib.sha256(b"K7QM4X").hexdigest(), encoding="utf-8")
    assert gate.code_ok(tmp_path, "KẾT LUẬN: ĐẠT\nMã tờ duyệt: K7QM4X")
    assert not gate.code_ok(tmp_path, "KẾT LUẬN: ĐẠT\nMã tờ duyệt: AAAAAA")


def test_icon_find_vietnamese():
    from icon_find import find
    assert find(["máy chủ"])[0][0] == "server"
    assert any(n == "fence" for n, _ in find(["hàng rào"]))
