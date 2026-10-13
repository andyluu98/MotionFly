"""timeline.json -> index.html (HyperFrames host) for a project.

- one sub-composition host per scene (compositions/<id>.html); a missing scene file
  gets a placeholder so the video can be previewed and rendered early
- window.__vv exposes scene spans and anchors; scenes call window.__vv.local(id, key)
- burned captions as timed clips (styled by theme.css variables)
- the mix as the only <audio> element (preview); --no-audio drops it for render,
  because HyperFrames' own audio mix needs ffmpeg filters that minimal builds lack
  and re-encoding would move the true peak; mix.py final muxes mix.wav instead
- fonts copied from the plugin (Be Vietnam Pro, OFL)
- optional compositions/_nen.html: a shared background layer under all scenes
- the optional helper kit (templates/kit/*.js) copied to <project>/kit and loaded before the scenes (window.MF)

Usage: python assemble.py <project_dir> [--no-audio]
"""

from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
FONTS = PLUGIN / "templates" / "fonts"
SCENE_TEMPLATE = PLUGIN / "templates" / "scene.html"
KIT = PLUGIN / "templates" / "kit"
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
WEIGHTS = {"Regular": 400, "Medium": 500, "Bold": 700, "ExtraBold": 800}


def font_faces() -> str:
    return "\n".join(
        f'      @font-face {{ font-family: "Be Vietnam Pro"; src: url("fonts/BeVietnamPro-{n}.ttf"); font-weight: {w}; }}'
        for n, w in WEIGHTS.items())


def placeholder(sid: str, w: int, h: int, note: str) -> str:
    return (SCENE_TEMPLATE.read_text(encoding="utf-8")
            .replace("{{SID}}", sid).replace("{{W}}", str(w)).replace("{{H}}", str(h))
            .replace("{{NOTE}}", html.escape(note)))


def build(project: Path, audio: bool = True) -> Path:
    tl = json.loads((project / "timeline.json").read_text(encoding="utf-8"))
    sb = json.loads((project / "storyboard.json").read_text(encoding="utf-8"))
    notes = {s["id"]: s.get("visual", "") for s in sb["scenes"]}
    w, h, dur = tl["width"], tl["height"], tl["duration"]
    (project / "fonts").mkdir(exist_ok=True)
    for f in FONTS.glob("*.ttf"):
        if not (project / "fonts" / f.name).exists():
            shutil.copy2(f, project / "fonts" / f.name)
    (project / "kit").mkdir(exist_ok=True)
    for f in KIT.glob("*.js"):   # always refresh: the kit is plugin code, not project content
        shutil.copy2(f, project / "kit" / f.name)
    comp = project / "compositions"
    comp.mkdir(exist_ok=True)
    theme = project / "theme.css"
    if not theme.exists():
        theme.write_text(":root {\n  --bg: #0e1116;\n  --ink: #f4f1ea;\n  --accent: #e8553d;\n"
                         "  --cap-bg: rgba(10, 12, 16, 0.72);\n  --cap-ink: #ffffff;\n}\n", encoding="utf-8")

    vv = {s["id"]: {"start": s["start"], "end": s["end"], "anchors": s["anchors"]} for s in tl["scenes"]}
    hosts = []
    if (comp / "_nen.html").exists():
        # Optional shared background (board, paper, grid) under every scene for the whole video.
        hosts.append(f'      <div id="host-nen" data-composition-id="_nen" data-composition-src="compositions/_nen.html"'
                     f' data-start="0" data-duration="{dur}" data-track-index="0" data-width="{w}" data-height="{h}"></div>')
    for i, s in enumerate(tl["scenes"]):
        f = comp / f"{s['id']}.html"
        if not f.exists():
            f.write_text(placeholder(s["id"], w, h, notes.get(s["id"], "")), encoding="utf-8")
        hosts.append(
            f'      <div id="host-{s["id"]}" data-composition-id="{s["id"]}" data-composition-src="compositions/{s["id"]}.html"'
            f' data-start="{s["start"]}" data-duration="{round(s["end"] - s["start"], 3)}" data-track-index="{1 + i % 2}"'
            f' data-width="{w}" data-height="{h}"></div>')
    caps = [
        f'        <div id="cap-{i}" class="clip cap" data-start="{c["start"]}" data-duration="{round(c["end"] - c["start"], 3)}"'
        f' data-track-index="8"><span>{html.escape(c["text"])}</span></div>'
        for i, c in enumerate(tl["captions"])]
    cap_size = 46 if h > w else 40
    audio_tag = (f'      <audio id="mix" src="mix.wav" data-start="0" data-duration="{dur}" data-track-index="10"></audio>'
                 if audio else "      <!-- audio omitted for render; mix.py final muxes mix.wav -->")
    kit_tags = "\n".join(f'    <script src="kit/{f.name}"></script>' for f in sorted(KIT.glob("*.js")))
    page = f"""<!doctype html>
<html lang="vi">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={w}, height={h}" />
    <title>{html.escape(sb.get("title", project.name))}</title>
    <script src="{GSAP}"></script>
{kit_tags}
    <link rel="stylesheet" href="theme.css" />
    <style>
{font_faces()}
      body {{ margin: 0; background: var(--bg, #0e1116); font-family: "Be Vietnam Pro", sans-serif; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      #captions {{ position: absolute; left: 0; right: 0; bottom: 0; height: 100%; pointer-events: none; }}
      .cap {{ position: absolute; left: 6%; right: 6%; bottom: 7%; display: flex; justify-content: center; }}
      .cap span {{ max-width: 100%; padding: 14px 28px; border-radius: 18px; background: var(--cap-bg);
        color: var(--cap-ink); font-size: {cap_size}px; font-weight: 600; line-height: 1.3; text-align: center; }}
    </style>
    <script>
      window.__vv = {{
        scenes: {json.dumps(vv, ensure_ascii=False)},
        local(id, key) {{
          const s = this.scenes[id];
          if (!s || !(key in s.anchors)) {{ console.error("KW miss: " + id + "." + key); return 0; }}
          return s.anchors[key] - s.start;
        }},
      }};
    </script>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{w}" data-height="{h}" data-duration="{dur}">
{chr(10).join(hosts)}
      <div id="captions">
{chr(10).join(caps)}
      </div>
{audio_tag}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    out = project / "index.html"
    out.write_text(page, encoding="utf-8")
    return out


if __name__ == "__main__":
    p = build(Path(sys.argv[1]).resolve(), audio="--no-audio" not in sys.argv)
    print(f"ASSEMBLED {p}{' (no audio)' if '--no-audio' in sys.argv else ''}")
