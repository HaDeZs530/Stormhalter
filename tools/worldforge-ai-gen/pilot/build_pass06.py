#!/usr/bin/env python3
"""Pass 06 kit: the dense-decoration palette (temple/crypt/dungeon/undead) as wrapped-name sheets + pieces.json."""
import sys, json, collections, textwrap
sys.path.insert(0, '/home/claude/tools')
from PIL import Image, ImageDraw, ImageFont
from wf_render import Sprites

OUT = '/home/claude/pilot/pass06/out'
import os; os.makedirs(OUT, exist_ok=True)
book = json.load(open('/home/claude/out/2026-10-29 piece-book-draft.json'))
SET = {'temple', 'crypt', 'dungeon', 'ruins', 'palace', 'castle', 'wizard', 'sewer'}
TONE = {'undead', 'cursed', 'corrupted', 'dark', 'blessed', 'grand', 'hot'}
EXCL_CAT = {'Structural', 'Ruins', 'Customizable', 'unlisted', 'Stairs', 'Doors', 'Misc.', 'Teleport', 'Traps', 'Water', 'Vegetation'}
KEEP_TYPES = {'StaticComponent', 'FloorComponent', 'ObstructionComponent', 'CounterComponent', 'AltarComponent', 'TrashComponent', 'LockersComponent'}
sub, seen = [], set()
for e in book:
    k = (e['id'], e['type'])
    if k in seen or e['category'] in EXCL_CAT or e['type'] not in KEEP_TYPES:
        continue
    s = set(e.get('setting') or []); t = set(e.get('tone') or [])
    if (s & SET) or (t & TONE) or e['placement'] in ('scatter', 'cluster', 'overlay'):
        sub.append(e); seen.add(k)
# the pilot's own 86 as well, so every id used so far stays legal
for e in json.load(open('/home/claude/pilot/dry-run/pieces.json')):
    k = (e['id'], e['type'])
    if k not in seen and e['type'] in KEEP_TYPES:
        sub.append(e); seen.add(k)
order = {'Floors': 0, 'Decorations': 1, 'lighting and shade': 2, 'Counters and Altars': 3, 'Obstructions': 4, 'Wall Doodads (H)': 5}
sub.sort(key=lambda e: (order.get(e['category'], 9), e.get('placement') or '', e['id']))
print('palette', len(sub), collections.Counter(e['category'] for e in sub).most_common())

sprites = Sprites()
F = lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', s)
CARD, COLS, ROWS = 150, 8, 6


def card_img(e):
    im = Image.new('RGBA', (100, 100), (70, 70, 70, 255))
    for L in sorted(sprites.terrain.get(e['id'], []), key=lambda L: L['order']):
        im.alpha_composite(sprites.img(L), (L['off'][0], L['off'][1]))
    return im


per = COLS * ROWS
letters = 'ABCDEFGHIJKL'
out = []
for si in range(0, len(sub), per):
    chunk = sub[si:si + per]; L = letters[si // per]
    sheet = Image.new('RGB', (COLS * CARD, ROWS * CARD + 44), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    d.rectangle([0, 0, sheet.width, 44], fill=(255, 220, 0))
    d.text((8, 22), f'PASS 06 SHEET {L} — dense temple/crypt/dungeon palette — 2026-10-29', fill=(0, 0, 0), font=F(22), anchor='lm')
    for j, e in enumerate(chunk):
        cx, cy = (j % COLS) * CARD, 44 + (j // COLS) * CARD
        d.rectangle([cx + 2, cy + 2, cx + CARD - 2, cy + CARD - 2], fill=(40, 40, 40), outline=(90, 90, 90))
        ci = card_img(e); sheet.paste(ci, (cx + 25, cy + 4), ci)
        d.text((cx + CARD // 2, cy + 108), f"id {e['id']}  {e['type'].replace('Component', '')}", fill=(255, 230, 0), font=F(11), anchor='mm')
        lines = textwrap.wrap(e.get('name') or '', 24)[:2]
        for li, ln in enumerate(lines):
            d.text((cx + CARD // 2, cy + 121 + li * 11), ln, fill=(230, 230, 230), font=F(10), anchor='mm')
        d.text((cx + CARD // 2, cy + 143), (e.get('placement') or '')[:22], fill=(150, 200, 255), font=F(9), anchor='mm')
        out.append({'sheet': L, 'card': j + 1, **{k: e.get(k) for k in ('n', 'id', 'name', 'type', 'category', 'look', 'kind', 'size', 'placement', 'setting', 'tone', 'pairs_with', 'notes', 'usage')}})
    sheet.save(f'{OUT}/pieces_sheet_{L}.png'); print('sheet', L, len(chunk))
json.dump(out, open(f'{OUT}/pieces.json', 'w'), indent=1)
