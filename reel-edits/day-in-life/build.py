#!/usr/bin/env python3
"""day-in-life reel, cool girl look end to end.

Voiceover over b-roll (one continuous segment). Calm cream Inter captions + one butter-yellow Instrument Serif
italic phrase per line, bottom-anchored in the safe zone, warm faded grade, sparkles on key lines, soft punches on
the source's own shot changes, subtle SFX.

PY build.py           writes index.html
PY build.py --safe    + red Instagram safe-zone guide (snapshots only)
"""
import json
import os
import re
import shutil
import subprocess
import sys

SAFE = '--safe' in sys.argv or bool(os.environ.get('SAFE'))
DUR = float(subprocess.run([shutil.which('ffprobe') or 'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                            'stream=duration', '-of', 'csv=p=0', 'assets/aroll.mp4'],
                           capture_output=True, encoding='utf-8', errors='replace').stdout.strip().split(',')[0])
YEL = '#FAE67A'
GIRL_F = 'sepia(.18) saturate(.9) contrast(.93) brightness(1.05) hue-rotate(-5deg)'

# ------------------------------------------------------------------ words (merge "3 a .m." -> "3am" etc.)
with open('words.json', encoding='utf-8') as f:
    raw = json.load(f)
W = []
i = 0
while i < len(raw):
    w = dict(raw[i])
    nxt = [r['text'] for r in raw[i + 1:i + 3]]
    if len(nxt) == 2 and nxt[0].lower() in ('a', 'p') and nxt[1].startswith('.m'):
        w['text'] = w['text'] + nxt[0].lower() + 'm' + nxt[1][3:]
        w['end'] = raw[i + 2]['end']
        i += 3
    elif nxt and nxt[0].startswith('-'):
        w['text'] = w['text'] + nxt[0][1:]
        w['end'] = raw[i + 1]['end']
        i += 2
    else:
        i += 1
    W.append(w)


def norm(s):
    return re.sub(r"[^a-z0-9']", '', s.lower().replace(':', ''))


# each block: "pre words | italic words | post words" -- every displayed word maps 1:1 onto a spoken word
BLOCKS = [
    ("i don't know if anybody else | has this problem, |", True),
    ("but in college, i always try to go to | sleep so early, |", False),
    ("i try to be on top of my | sleep schedule, |", False),
    ("and i always end up falling asleep at like | 2 or 3am |", False),
    ("and not being able to wake up for my | first class, |", False),
    ("so come spend the day of my life with me as a | wharton student. |", True),
    ("i woke up at | 12 today | for my 12pm class,", False),
    ("and the one thing that nobody talks about in college is the | 10am classes. |", False),
    ("i swear to god, everybody talks about | the 8:30s |", False),
    ("and how difficult it is to | wake up | for those,", False),
    ("but i'm personally struggling with | my 10:15s. |", False),
    ("thankfully for me, it was a | beautiful day | outside,", True),
    ("and i wanted to go meet up with my friends so we could go to | west philly, |", False),
    ("and i think that something people | don't talk about | enough", False),
    ("when going to | penn | is, yes,", True),
    ("you have so much | proximity | to the city,", False),
    ("but you're also so close to a | cute residential | and naturey area.", False),
    ("after that, i just did some | maintenance | work,", False),
    ("i went to | the gym, |", False),
    ("i did some work for a | consulting | project that i'm working on this semester,", False),
    ("i studied a bit, and then i | crashed out | on my bed.", True),
]

blocks, wi = [], 0
for spec, spark in BLOCKS:
    parts = [p.split() for p in spec.split('|')]
    lines = []
    for kind, toks in zip('ses', parts):
        line = []
        for tok in toks:
            src = W[wi]
            assert norm(tok) == norm(src['text']), f'caption {tok!r} != spoken {src["text"]!r} at {src["start"]}'
            line.append((src['start'], src['end'], tok))
            wi += 1
        lines.append((kind, line))
    blocks.append((lines, spark))
assert wi == len(W), f'{len(W) - wi} spoken words without a caption'

C_HTML, TW = [], []
for b, (lines, spark) in enumerate(blocks):
    flat = [w for _, ln in lines for w in ln]
    a = max(0.0, flat[0][0] - .06)
    nxt = blocks[b + 1][0] if b + 1 < len(blocks) else None
    nstart = min(w[0] for _, ln in nxt for w in ln) - .06 if nxt else DUR
    end = min(nstart, flat[-1][1] + 1.2, DUR)
    rows = []
    for li, (kind, ln) in enumerate(lines):
        if not ln:
            continue
        spans = []
        for k, (t, _, txt) in enumerate(ln):
            gid = f'b{b}-{li}-{k}'
            spans.append(f'<span id="{gid}" class="gw">{txt}</span>')
            if kind == 's':
                TW.append(f"tl.fromTo('#{gid}',{{autoAlpha:0,y:14}},{{autoAlpha:1,y:0,duration:.26,ease:'power2.out',immediateRender:false}},{max(a, t - .04):.3f});")
            else:
                TW.append(f"tl.fromTo('#{gid}',{{autoAlpha:0,y:22,scale:.92}},{{autoAlpha:1,y:0,scale:1,duration:.4,ease:'power2.out',immediateRender:false}},{max(a, t - .04):.3f});")
        rows.append(f'<div class="{kind}">{" ".join(spans)}</div>')
    C_HTML.append(f'<div id="blk{b}" class="gcap">{"".join(rows)}</div>')
    TW.append(f"gsap.set('#blk{b} .gw',{{autoAlpha:0}});")
    if end < DUR - .01:
        TW.append(f"tl.to('#blk{b}',{{autoAlpha:0,duration:.14}},{end - .14:.3f});")
        TW.append(f"tl.set('#blk{b}',{{autoAlpha:0}},{end:.3f});")
    if spark:   # twinkling sparkles beside the italic line
        it = [w for kind, ln in lines if kind == 'e' for w in ln]
        t0 = it[0][0]
        for k, (x, y, sz, dt) in enumerate([(120, 1190, 56, .08), (905, 1150, 40, .22), (880, 1290, 28, .4)]):
            if t0 + dt + .3 > end - .14:
                continue
            sid = f'sp{b}-{k}'
            C_HTML.append(f'<div id="{sid}" class="spark" style="left:{x}px;top:{y}px;font-size:{sz}px">&#10022;</div>')
            TW += [f"gsap.set('#{sid}',{{autoAlpha:0,scale:0}});",
                   f"tl.to('#{sid}',{{autoAlpha:1,scale:1,duration:.3,ease:'back.out(2.5)'}},{t0 + dt:.3f});"]
            if t0 + dt + 1.1 < end - .14:
                TW.append(f"tl.to('#{sid}',{{scale:.7,duration:.4,yoyo:true,repeat:1,ease:'sine.inOut'}},{t0 + dt + .3:.3f});")
            if end < DUR - .01:
                TW += [f"tl.to('#{sid}',{{autoAlpha:0,duration:.14}},{end - .14:.3f});", f"tl.set('#{sid}',{{autoAlpha:0}},{end:.3f});"]

# soft punch on the source's own shot changes (detected with ffmpeg scene filter)
SHOTS = [4.0, 10.667, 12.533, 15.733, 17.067, 20.367, 22.567, 24.967, 27.333, 32.767, 35.0, 40.5, 44.2, 46.467, 48.767, 51.733]
for t in SHOTS:
    TW.append(f"tl.fromTo('#stage',{{scale:1.04}},{{scale:1,duration:.32,ease:'power2.out',immediateRender:false}},{t:.3f});")

spark_t = [[w for kind, ln in lines if kind == 'e' for w in ln][0][0] for lines, s in blocks if s]
SFX = [('whoosh-short', .02, .2)] + [('sparkle', t, .22) for t in spark_t] + \
      [('whoosh-short', t - .1, .14) for t in (12.533, 27.333, 46.467)] + [('pop', 49.62, .14)]
SFX_LEN = {'whoosh-short': .57, 'pop': .72, 'sparkle': 1.8, 'click': .3, 'click-soft': .37}
SFX_GAIN = 0.75


def audio():
    out, lanes = [], []
    for k, (name, t, vol) in enumerate(sorted(SFX, key=lambda x: x[1])):
        d = min(SFX_LEN[name], DUR - t)
        lane = next((i for i, e in enumerate(lanes) if e <= t), None)
        if lane is None:
            lanes.append(0)
            lane = len(lanes) - 1
        lanes[lane] = t + d
        out.append(f'<audio id="sfx{k}" src="assets/sfx/{name}.mp3" data-start="{t:.3f}" data-duration="{d:.3f}" '
                   f'data-track-index="{10 + lane}" data-volume="{vol * SFX_GAIN:.3f}"></audio>')
    return out


CSS = f'''
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}}
#stage{{position:absolute;inset:0;transform-origin:50% 45%}}
.full{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.fx{{position:absolute;inset:0;pointer-events:none}}
#gwarm{{z-index:7;background:linear-gradient(180deg,rgba(255,226,200,.10),rgba(255,196,170,.16));mix-blend-mode:soft-light}}
#gvig{{z-index:7;background:radial-gradient(120% 70% at 50% 45%,rgba(255,255,255,0) 52%,rgba(60,35,25,.34) 100%)}}
#ggrad{{z-index:7;background:linear-gradient(180deg,rgba(60,35,25,.22) 0%,rgba(60,35,25,0) 26%,rgba(60,35,25,0) 44%,rgba(45,26,18,.42) 66%,rgba(40,24,18,.55) 100%)}}
.gcap{{position:absolute;left:70px;right:110px;bottom:470px;z-index:8;text-align:center;color:#FFF8EF;
  text-shadow:0 2px 26px rgba(60,30,20,.6),0 1px 4px rgba(40,20,10,.35)}}
.gcap .s{{font:500 58px/1.18 Inter;letter-spacing:-1px}}
.gcap .e{{font:italic 400 150px 'Instrument Serif';line-height:.95;color:{YEL};margin:2px 0 6px;white-space:nowrap}}
.gw{{display:inline-block}}
.spark{{position:absolute;z-index:8;color:{YEL};line-height:1;text-shadow:0 0 18px rgba(250,230,122,.5)}}
'''

SAFE_GUIDE = ('<div style="position:absolute;inset:0;z-index:99;pointer-events:none">'
              '<div style="position:absolute;left:0;right:0;top:0;height:220px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;right:0;top:1470px;bottom:0;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;width:35px;top:220px;height:1250px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:35px;top:220px;height:935px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:100px;top:1155px;height:315px;background:rgba(255,0,0,.28)"></div></div>')

nl = '\n'
tweens = [f"gsap.set('.g',{{filter:'{GIRL_F}'}});"] + TW
html = f'''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<link rel="stylesheet" href="assets/fonts/fonts.css" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR:.3f}" data-width="1080" data-height="1920">
  <audio id="bga" src="assets/aroll.mp4" data-start="0" data-media-start="0" data-duration="{DUR:.3f}" data-track-index="2" data-volume="1"></audio>
{nl.join(audio())}
  <div id="stage">
    <video id="bgv" class="full g" src="assets/aroll.mp4" muted playsinline data-start="0" data-media-start="0" data-duration="{DUR:.3f}" data-track-index="0"></video>
  </div>
  <div id="gwarm" class="fx"></div><div id="gvig" class="fx"></div><div id="ggrad" class="fx"></div>
{nl.join(C_HTML)}
{SAFE_GUIDE if SAFE else ''}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{nl.join(tweens)}
tl.set({{}}, {{}}, {DUR:.3f});
window.__timelines["main"] = tl;
</script>
</body>
</html>
'''
with open('index.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)
print(f'wrote index.html {DUR:.3f}s  {len(blocks)} caption blocks  {len(SFX)} sfx')
