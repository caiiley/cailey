#!/usr/bin/env python3
"""day-in-life-2 reel (wharton marketing major, rainy friday)

Originally: day-in-life reel, cool girl look end to end.

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


blocks = []

C_HTML, TW = [], []


def show(el, a_, b_):
    TW.append(f"gsap.set('#{el}',{{autoAlpha:0}});")
    TW.append(f"tl.set('#{el}',{{autoAlpha:1}},{a_:.3f});")
    if b_ < DUR - .01:
        TW.append(f"tl.set('#{el}',{{autoAlpha:0}},{b_:.3f});")


# ------------------------------------------------------------------ speech captions: small, plain, static
FIX = {'brandy': 'brandy'}
ALL = [(w['start'], w['end'], FIX.get(w['text'].lower(), w['text'].lower())) for w in W if w['text'].lower().strip(',.') not in ('um', 'uh')]
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
END_CARD = 57.75          # "crashed out" -> good night card
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
LABELS = [  # start, end, time, activity   (times are made up for the vibe, except 2:35 PM from the SEPTA board)
    (0.0, 4.533, '10:00 AM', 'Center City &#127961;&#65039;'),
    (4.533, 11.0, '10:30 AM', 'Brandy Run &#128717;&#65039;'),
    (11.0, 12.033, '11:45 AM', 'Back to Campus'),
    (12.033, 17.367, '12:30 PM', 'Clouding Up &#9729;&#65039;'),
    (17.367, 18.567, '2:35 PM', 'SEPTA &#128647;'),
    (18.567, 22.267, '2:50 PM', 'OTW to Work'),
    (22.267, 27.233, '3:05 PM', 'Flash Flood &#9748;'),
    (27.233, 29.433, '3:30 PM', 'Work &#128188;'),
    (29.433, 33.5, '7:15 PM', 'Dinner &#127831;'),
    (33.5, 37.567, '8:00 PM', 'Sketching &#9999;&#65039;'),
    (37.567, 46.1, '9:30 PM', 'Portfolio &#128187;'),
    (46.1, 52.667, '11:00 PM', 'Final Touches &#10024;'),
    (52.667, 55.167, '12:00 AM', 'Wind Down &#128367;&#65039;'),
    (55.167, END_CARD, '12:15 AM', 'Reminder &#129293;'),
]
for k, (a_, b_, tm, act) in enumerate(LABELS):
    C_HTML.append(f'<div id="lab{k}" class="lab"><span>{tm}</span><span>{act}</span></div>')
    show(f'lab{k}', a_, b_)

# ------------------------------------------------------------------ good night end card
C_HTML.append('<div id="gn"><div class="g1">Good</div><div class="g2">Night</div>'
              '<div class="ty">[thanks for watching!]</div><div class="star">&#9733;</div></div>')
show('gn', END_CARD, DUR)

# ------------------------------------------------------------------ sound effects (from the creator 101 pack)
SFX = [('click', t, .55) for t, *_ in LABELS[1:]] + [
    ('flash', 0.0, .6),                # open
    ('tada', 2.25, .45),               # "wharton"
    ('cash-register', 9.95, .4),       # "brandy"
    ('fairy-dust', 11.25, .5),         # "beautiful outside"
    ('embarrassing', 16.45, .5),       # "volatile"
    ('hit', 22.70, .55),               # "flash flood"
    ('flop', 27.50, .55),              # "so awful"
    ('bite', 32.75, .7),               # "chicken"
    ('pencil', 35.90, 1.0),            # "sketching"
    ('typing', 37.70, .45),            # laptop
    ('button', 46.62, .5),             # "just chill"
    ('click2', 49.94, .5), ('click2', 50.38, .5), ('click2', 50.62, .5),   # "back to back to back"
    ('bubbles', 53.70, .4),            # "take a break"
    ('fairy-dust', 57.80, .45),        # good night card
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
  color:#fff;font:500 50px 'Inter Tight','Noto Color Emoji';letter-spacing:-.055em;text-shadow:0 1px 8px rgba(0,0,0,.55),0 0 2px rgba(0,0,0,.4)}}
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
