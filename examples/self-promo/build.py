#!/usr/bin/env python3
"""The clip in this repo's README: 12 seconds, 1920x1080.

The tool demonstrates itself. Composition code on the left turns into a frame of
this very clip on the right, and the ending says so.

Fonts are expected in ./fonts (Oswald 500/700, JetBrains Mono 400/700 as woff2),
gsap.min.js next to index.html, audio in ./audio. Generate the bed with
scripts/score.py, then: hf check && hf render.
"""
import html
import os

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "kadr-promo", "index.html")

CODE = [
    '<div class="clip" data-start="0" data-duration="4">',
    '  <h1 id="title">Hello</h1>',
    '</div>',
    '',
    'tl.from("#title", { y: 80, opacity: 0 });',
]

BG = "#0a0a0c"
INK = "#ede4d3"
DIM = "#8c867c"
ACCENT = "#ee4e4e"
LINE = "#25252b"

def code_lines():
    out = []
    for i, line in enumerate(CODE):
        cls = "cl"
        out.append(
            f'<div id="code{i}" class="{cls} clip" data-start="{0.3 + i*0.38:.2f}" '
            f'data-duration="{7.7 - i*0.38:.2f}" data-track-index="{10+i}" '
            f'style="top: {i*62}px">{html.escape(line).replace(" ", "&nbsp;") or "&nbsp;"}</div>'
        )
    return "\n      ".join(out)


HTML = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Oswald"; font-weight: 700; src: url("fonts/Oswald-700-latin.woff2") format("woff2"); }}
      @font-face {{ font-family: "Oswald"; font-weight: 500; src: url("fonts/Oswald-500-latin.woff2") format("woff2"); }}
      @font-face {{ font-family: "JB"; font-weight: 700; src: url("fonts/JetBrainsMono-700-latin.woff2") format("woff2"); }}
      @font-face {{ font-family: "JB"; font-weight: 400; src: url("fonts/JetBrainsMono-400-latin.woff2") format("woff2"); }}

      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: {BG}; }}
      #root {{ position: relative; width: 1920px; height: 1080px; }}

      .label {{
        position: absolute; font-family: "JB", monospace; font-size: 28px;
        letter-spacing: 8px; color: {DIM}; text-transform: uppercase;
      }}
      #lhs {{ left: 150px; top: 170px; }}
      #rhs {{ right: 150px; top: 170px; }}

      .rule {{ position: absolute; top: 250px; height: 4px; background: {LINE}; transform-origin: left center; }}
      #ruleL {{ left: 150px; width: 720px; }}
      #ruleR {{ left: 1050px; width: 720px; }}

      /* left half: the composition source */
      .cl {{
        position: absolute; left: 150px;
        font-family: "JB", monospace; font-weight: 400; font-size: 34px;
        color: {DIM}; white-space: pre;
      }}
      .cl:nth-child(2) {{ color: {INK}; }}

      /* right half: what it renders into */
      #frame {{
        position: absolute; left: 1050px; top: 330px; width: 720px; height: 405px;
        border: 2px solid {LINE}; background: #111;
      }}
      #shot, #shot2 {{
        position: absolute; left: 60px; top: 150px;
        font-family: "Oswald", sans-serif; font-weight: 700; font-size: 96px;
        color: {INK}; text-transform: uppercase; letter-spacing: -2px;
      }}
      #shot2 {{ color: {ACCENT}; }}
      #playhead {{ position: absolute; left: 0; bottom: 0; height: 5px; background: {ACCENT}; width: 720px; transform-origin: left center; }}

      /* ending */
      #brand {{
        position: absolute; left: 150px; top: 380px;
        font-family: "Oswald", sans-serif; font-weight: 700; font-size: 220px;
        letter-spacing: -8px; line-height: 0.9; color: {INK}; text-transform: uppercase;
      }}
      #brand em {{ font-style: normal; color: {ACCENT}; }}
      #claim {{
        position: absolute; left: 156px; top: 640px;
        font-family: "Oswald", sans-serif; font-weight: 500; font-size: 54px; color: {DIM};
      }}
      #repo {{
        position: absolute; left: 158px; top: 745px;
        font-family: "JB", monospace; font-size: 34px; letter-spacing: 3px; color: {ACCENT};
      }}
      #meta {{
        position: absolute; right: 150px; top: 745px;
        font-family: "JB", monospace; font-size: 26px; letter-spacing: 5px; color: {DIM};
        text-transform: uppercase;
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="12"
         data-width="1920" data-height="1080">

      <div id="lhs" class="label clip" data-start="0" data-duration="7.9" data-track-index="0">you write html</div>
      <div id="rhs" class="label clip" data-start="1.5" data-duration="6.4" data-track-index="1">it renders mp4</div>
      <div id="ruleL" class="rule clip" data-start="0" data-duration="7.9" data-track-index="2"></div>
      <div id="ruleR" class="rule clip" data-start="1.5" data-duration="6.4" data-track-index="3"></div>

      {code_lines()}

      <div id="frame" class="clip" data-start="1.7" data-duration="6.2" data-track-index="4">
        <div id="shot">Hello</div>
        <div id="shot2">frame 2</div>
        <div id="playhead"></div>
      </div>

      <div id="brand" class="clip" data-start="8.2" data-duration="3.8" data-track-index="5">Ka<em>dr</em></div>
      <div id="claim" class="clip" data-start="8.8" data-duration="3.2" data-track-index="6">this video was made with it</div>
      <div id="repo" class="clip" data-start="9.4" data-duration="2.6" data-track-index="7">github.com/Sanexxxx777/kadr</div>
      <div id="meta" class="clip" data-start="9.7" data-duration="2.3" data-track-index="8">mit + apache-2.0</div>

      <audio id="bgm" src="audio/score.wav" data-start="0" data-duration="12" data-track-index="30" data-volume="0.5"></audio>
      <audio id="sfx1" src="audio/typing.mp3" data-start="0.4" data-duration="1.6" data-track-index="31" data-volume="0.4"></audio>
      <audio id="sfx2" src="audio/whoosh-short.mp3" data-start="1.75" data-duration="0.57" data-track-index="32" data-volume="0.3"></audio>
      <audio id="sfx3" src="audio/impact-bass-2.mp3" data-start="8.1" data-duration="2.6" data-track-index="33" data-volume="0.28"></audio>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});

      tl.from("#lhs", {{ opacity: 0, duration: 0.4 }}, 0);
      tl.from("#ruleL", {{ scaleX: 0, duration: 0.6, ease: "power3.out" }}, 0.05);
      gsap.utils.toArray(".cl").forEach((el, i) => {{
        tl.from(el, {{ x: -24, opacity: 0, duration: 0.35, ease: "power3.out" }}, 0.35 + i * 0.38);
      }});

      tl.from("#rhs", {{ opacity: 0, duration: 0.4 }}, 1.55);
      tl.from("#ruleR", {{ scaleX: 0, duration: 0.6, ease: "power3.out" }}, 1.6);
      tl.from("#frame", {{ opacity: 0, x: 40, duration: 0.5, ease: "power3.out" }}, 1.75);
      tl.from("#shot", {{ y: 60, opacity: 0, duration: 0.7, ease: "power3.out" }}, 2.2);
      /* the playhead runs exactly as long as the frame is on screen */
      tl.from("#playhead", {{ scaleX: 0, duration: 5.9, ease: "none" }}, 1.9);

      tl.set("#shot2", {{ y: 60, opacity: 0 }}, 0);
      tl.to("#shot", {{ y: -60, opacity: 0, duration: 0.4, ease: "power3.in" }}, 4.6);
      tl.to("#shot2", {{ y: 0, opacity: 1, duration: 0.45, ease: "power3.out" }}, 4.75);

      tl.from("#brand", {{ y: 90, opacity: 0, duration: 0.7, ease: "power3.out" }}, 8.25);
      tl.from("#claim", {{ y: 30, opacity: 0, duration: 0.5, ease: "power3.out" }}, 8.85);
      tl.from("#repo", {{ opacity: 0, duration: 0.5 }}, 9.45);
      tl.from("#meta", {{ opacity: 0, duration: 0.5 }}, 9.75);

      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(HTML)
print(f"wrote: {OUT}")
