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


def show(el, a_, b_):
    TW.append(f"gsap.set('#{el}',{{autoAlpha:0}});")
    TW.append(f"tl.set('#{el}',{{autoAlpha:1}},{a_:.3f});")
    if b_ < DUR - .01:
        TW.append(f"tl.set('#{el}',{{autoAlpha:0}},{b_:.3f});")


# ------------------------------------------------------------------ speech captions: small, plain, static
ALL = [w for lines, _ in blocks for _, ln in lines for w in ln]
chunks, cur = [], []
for w in ALL:
    if cur and len(' '.join(x[2] for x in cur + [w])) > 30:
        chunks.append(cur); cur = []
    cur.append(w)
    if w[2][-1] in ',.?!':
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)
# fold one-word leftovers into a neighbour so nothing flashes alone
out = []
for ch in chunks:
    if len(ch) == 1 and out and len(' '.join(x[2] for x in out[-1] + ch)) <= 40 and out[-1][-1][2][-1] not in '.?!':
        out[-1] = out[-1] + ch
    else:
        out.append(ch)
chunks = out
END_CARD = 55.60          # "crashed out" -> good night card
for c, ch in enumerate(chunks):
    a_ = max(0.0, ch[0][0] - .05)
    nstart = chunks[c + 1][0][0] - .05 if c + 1 < len(chunks) else DUR
    end = min(nstart, ch[-1][1] + .7, END_CARD if a_ < END_CARD else DUR)
    if a_ >= END_CARD:
        continue
    txt = ' '.join(x[2] for x in ch).rstrip(',.')
    C_HTML.append(f'<div id="cap{c}" class="cap">{txt}</div>')
    show(f'cap{c}', a_, end)

# ------------------------------------------------------------------ time | activity labels (reference style)
LABELS = [  # start, end, time, activity   (times of day are guesses: check with Cailey)
    (10.667, 15.733, '12:00 PM', 'Class &#9999;&#65039;'),
    (15.733, 27.333, '1:30 PM', 'OTW'),
    (27.333, 35.000, '3:00 PM', 'West Philly &#127795;'),
    (35.000, 44.200, '5:00 PM', 'DJ Sesh &#127911;'),
    (44.200, 48.767, '8:30 PM', 'OTW'),
    (48.767, 51.733, '9:00 PM', 'Gym &#127947;&#65039;&#8205;&#9792;&#65039;'),
    (51.733, END_CARD, '10:30 PM', 'Consulting &#128187;'),
]
for k, (a_, b_, tm, act) in enumerate(LABELS):
    C_HTML.append(f'<div id="lab{k}" class="lab"><span>{tm}</span><span>{act}</span></div>')
    show(f'lab{k}', a_, b_)

# ------------------------------------------------------------------ good night end card
C_HTML.append('<div id="gn"><div class="g1">Good</div><div class="g2">Night</div>'
              '<div class="ty">[thanks for watching!]</div><div class="star">&#9733;</div></div>')
show('gn', END_CARD, DUR)

# ------------------------------------------------------------------ sound effects (from the creator 101 pack)
SFX = [
    ('click', 10.667, .55), ('click', 15.733, .55), ('click', 27.333, .55), ('click', 35.0, .55),
    ('click', 44.2, .55), ('click', 48.767, .55), ('click', 51.733, .55),     # each new time label
    ('pencil', 12.55, 1.0),            # notebook shot
    ('tada', 12.86, .45),              # "wharton student"
    ('embarrassing', 27.0, .5),        # "struggling with my 10:15s"
    ('fairy-dust', 29.80, .5),         # "beautiful day"
    ('hit', 49.70, .5),                # "the gym"
    ('typing', 51.80, .45),            # laptop
    ('flop', 55.70, .6),               # "crashed out"
    ('fairy-dust', 55.95, .45),        # good night card
]
SFX_LEN = {n: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                    f'assets/sfxpack/{n}.wav'], capture_output=True, text=True).stdout)
           for n in {x[0] for x in SFX}}


def audio():
    out, lanes = [], []
    for k, (name, t, vol) in enumerate(sorted(SFX, key=lambda x: x[1])):
        d = min(SFX_LEN[name], DUR - t)
        lane = next((i for i, e in enumerate(lanes) if e <= t), None)
        if lane is None:
            lanes.append(0)
            lane = len(lanes) - 1
        lanes[lane] = t + d
        out.append(f'<audio id="sfx{k}" src="assets/sfxpack/{name}.wav" data-start="{t:.3f}" data-duration="{d:.3f}" '
                   f'data-track-index="{10 + lane}" data-volume="{vol:.3f}"></audio>')
    return out


CSS = f"""
@font-face{{font-family:'Inter Tight';font-weight:400;src:url(assets/fonts/inter-tight-latin-400-normal.woff2) format('woff2');font-display:block}}
@font-face{{font-family:'Inter Tight';font-weight:500;src:url(assets/fonts/inter-tight-latin-500-normal.woff2) format('woff2');font-display:block}}
@font-face{{font-family:'Pinyon Script';src:url(assets/fonts/pinyon-script-latin-400-normal.woff2) format('woff2');font-display:block}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#000}}
#stage{{position:absolute;inset:0}}
.full{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.lab{{position:absolute;left:60px;right:60px;top:915px;z-index:8;display:flex;justify-content:space-between;align-items:center;
  color:#fff;font:500 50px 'Inter Tight','Noto Color Emoji';letter-spacing:-.055em;text-shadow:0 1px 6px rgba(0,0,0,.35)}}
.cap{{position:absolute;left:90px;right:130px;top:1330px;z-index:8;text-align:center;color:#fff;
  font:500 44px/1.15 'Inter Tight';letter-spacing:-.03em;text-shadow:0 1px 6px rgba(0,0,0,.5),0 0 2px rgba(0,0,0,.45)}}
#gn{{position:absolute;left:0;right:0;top:760px;height:520px;z-index:8;color:#fff;text-shadow:0 2px 14px rgba(0,0,0,.35)}}
#gn .g1{{position:absolute;left:180px;top:0;font:400 250px/1 'Pinyon Script'}}
#gn .g2{{position:absolute;left:330px;top:170px;font:400 250px/1 'Pinyon Script'}}
#gn .ty{{position:absolute;left:250px;top:420px;font:400 40px 'Inter Tight';letter-spacing:-.04em}}
#gn .star{{position:absolute;left:800px;top:375px;font-size:110px;line-height:1}}
"""

SAFE_GUIDE = ('<div style="position:absolute;inset:0;z-index:99;pointer-events:none">'
              '<div style="position:absolute;left:0;right:0;top:0;height:220px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;right:0;top:1470px;bottom:0;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;left:0;width:35px;top:220px;height:1250px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:35px;top:220px;height:935px;background:rgba(255,0,0,.28)"></div>'
              '<div style="position:absolute;right:0;width:100px;top:1155px;height:315px;background:rgba(255,0,0,.28)"></div></div>')

nl = '\n'
tweens = TW
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
print(f'wrote index.html {DUR:.3f}s  {len(chunks)} captions  {len(LABELS)} labels  {len(SFX)} sfx')
