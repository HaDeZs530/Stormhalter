#!/usr/bin/env python3
"""Dry-run kit for the ChatGPT visual loop (2026-10-29).

Takes one developer room (Praetoseba region 1, the Egyptian temple hall), and writes:
  shell.xml / shell_clean.png / shell_diag.png   the room with every decoration removed
  scene.xml / scene_clean.png / scene_diag.png   the room as the developers decorated it
  scene_key.json                                 pin -> tile, id, type, piece-book facts
  pieces_sheet_A.png, pieces_sheet_B.png ...     contact sheets of the pilot subset
  pieces.json                                    the subset with the piece-book text
Clean renders carry no labels at all. Diagnostic renders carry the grid, tile coordinates on
every edge, door tiles, and (scene only) numbered pins. Both are cropped from the same render of
the same XML that WorldForge imports.
"""
import sys, json, copy, collections, xml.etree.ElementTree as ET
sys.path.insert(0, '/home/claude/tools')
from PIL import Image, ImageDraw, ImageFont
from wf_render import render_region, Sprites, UNIT, ID_FIELDS, tint

PROJ = '/home/claude/jkachhad/stormhalter/Segments/Praetoseba.mapproj'
RID = 1
WIN = (10, 6, 27, 21)          # x0,y0,x1,y1 inclusive, in region tile coordinates
MARGIN = 1
OUT = '/home/claude/pilot/dry-run'
BOOK = '/home/claude/out/2026-10-29 piece-book-draft.json'
FLOOR_TYPES = {'FloorComponent', 'WaterComponent', 'IceComponent', 'PoisonedWaterComponent'}
KEEP = FLOOR_TYPES | {'WallComponent', 'DoorComponent'}
DECO = {'StaticComponent': 'static', 'LockersComponent': 'static', 'TrashComponent': 'static',
        'TreeComponent': 'tree', 'ObstructionComponent': 'obstruction', 'AltarComponent': 'altar',
        'CounterComponent': 'counter'}
F = lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', s)

import os
os.makedirs(OUT, exist_ok=True)
book = json.load(open(BOOK))
byid = collections.defaultdict(list)
for e in book:
    byid[e['id']].append(e)
floor_only = {i for i, es in byid.items() if all(e['category'] == 'Floors' or e['type'] in FLOOR_TYPES for e in es)}


def entry(i, typ=None):
    es = byid.get(i, [])
    for e in es:
        if typ and e['type'] == typ:
            return e
    return es[0] if es else None


root = ET.parse(PROJ).getroot()
region = [r for r in root.iter('region') if int(r.findtext('id')) == RID][0]

# --- shell: strip decorations -------------------------------------------------------------
shell = copy.deepcopy(region)
removed = collections.Counter()
for t in shell.findall('tile'):
    for c in list(t.findall('component')):
        typ = c.get('type')
        if typ in KEEP:
            continue
        if typ == 'StaticComponent' and int(c.findtext('static') or 0) in floor_only:
            continue
        t.remove(c)
        removed[typ] += 1
print('removed', dict(removed))

# region XML files (what WorldForge imports)
for name, reg in (('scene', region), ('shell', shell)):
    ET.ElementTree(reg).write(f'{OUT}/{name}.xml', encoding='utf-8', xml_declaration=True)

sprites = Sprites()
tiles = region.findall('tile')
xs = [int(t.get('x')) for t in tiles]; ys = [int(t.get('y')) for t in tiles]
minx, miny = min(xs), min(ys)
x0, y0, x1, y1 = WIN
pad = 1  # render_region pad
cx0 = (x0 - MARGIN - minx + pad) * UNIT; cy0 = (y0 - MARGIN - miny + pad) * UNIT
cx1 = (x1 + MARGIN - minx + pad + 1) * UNIT; cy1 = (y1 + MARGIN - miny + pad + 1) * UNIT


def tile_px(x, y):
    """top-left pixel of tile (x,y) inside the crop"""
    return (x - minx + pad) * UNIT - cx0, (y - miny + pad) * UNIT - cy0


def diag(crop, title, pins=None, doors=()):
    RUL = 26
    W, H = crop.width + 2 * RUL, crop.height + 2 * RUL + 40
    page = Image.new('RGB', (W, H), (0, 0, 0))
    page.paste(crop, (RUL, RUL + 40))
    d = ImageDraw.Draw(page, 'RGBA')
    d.rectangle([0, 0, W, 40], fill=(255, 220, 0))
    d.text((8, 20), title, fill=(0, 0, 0), font=F(20), anchor='lm')
    ox, oy = RUL, RUL + 40
    for x in range(x0 - MARGIN, x1 + MARGIN + 1):
        px, _ = tile_px(x, y0)
        d.line([(ox + px, oy), (ox + px, oy + crop.height)], fill=(255, 255, 255, 70))
        for yy in (oy - RUL // 2, oy + crop.height + RUL // 2):
            d.text((ox + px + UNIT // 2, yy), str(x), fill=(255, 255, 255), font=F(12), anchor='mm')
    for y in range(y0 - MARGIN, y1 + MARGIN + 1):
        _, py = tile_px(x0, y)
        d.line([(ox, oy + py), (ox + crop.width, oy + py)], fill=(255, 255, 255, 70))
        for xx in (ox - RUL // 2, ox + crop.width + RUL // 2):
            d.text((xx, oy + py + UNIT // 2), str(y), fill=(255, 255, 255), font=F(12), anchor='mm')
    # window outline
    wx, wy = tile_px(x0, y0)
    d.rectangle([ox + wx, oy + wy, ox + wx + (x1 - x0 + 1) * UNIT, oy + wy + (y1 - y0 + 1) * UNIT],
                outline=(255, 255, 0, 170), width=2)
    for (x, y) in doors:
        px, py = tile_px(x, y)
        d.rectangle([ox + px + 2, oy + py + 2, ox + px + UNIT - 2, oy + py + UNIT - 2], outline=(0, 200, 255, 230), width=3)
    if pins:
        stack = collections.Counter()
        for p in pins:
            px, py = tile_px(p['x'], p['y'])
            s = stack[(p['x'], p['y'])]; stack[(p['x'], p['y'])] += 1
            cx = ox + px + UNIT // 2 + (14 if s % 2 else 0) - (7 if s else 0)
            cy = oy + py + UNIT // 2 + (14 if s >= 2 else 0) - (7 if s else 0)
            r = 13
            d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], fill=(0, 0, 0))
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 230, 0))
            d.text((cx, cy), str(p['pin']), fill=(0, 0, 0), font=F(14), anchor='mm')
    return page


# doors in window
doors = []
for t in region.findall('tile'):
    x, y = int(t.get('x')), int(t.get('y'))
    if x0 <= x <= x1 and y0 <= y <= y1 and t.find("component[@type='DoorComponent']") is not None:
        doors.append((x, y))

# pins: every decoration in the window, in reading order, as the scene key
pins = []
for t in sorted(region.findall('tile'), key=lambda t: (int(t.get('y')), int(t.get('x')))):
    x, y = int(t.get('x')), int(t.get('y'))
    if not (x0 <= x <= x1 and y0 <= y <= y1):
        continue
    for c in t.findall('component'):
        typ = c.get('type')
        if typ in DECO:
            i = int(c.findtext(DECO[typ]) or 0)
            if typ == 'StaticComponent' and i in floor_only:
                continue
            e = entry(i, typ) or {}
            pins.append({'pin': len(pins) + 1, 'x': x, 'y': y, 'id': i, 'type': typ,
                         'name': e.get('name') or f'id{i}',
                         'book': {k: e.get(k) for k in ('look', 'kind', 'placement', 'setting', 'tone')}})
        elif typ == 'DoorComponent':
            i = int(c.findtext('closedId') or 0); e = entry(i, typ) or {}
            pins.append({'pin': len(pins) + 1, 'x': x, 'y': y, 'id': i, 'type': typ, 'name': e.get('name') or f'door{i}',
                         'book': {k: e.get(k) for k in ('look', 'kind', 'placement', 'setting', 'tone')}})

for name, reg, pn in (('shell', shell, None), ('scene', region, pins)):
    img, unk = render_region(reg, sprites, pad=pad)
    crop = img.crop((max(0, cx0), max(0, cy0), min(img.width, cx1), min(img.height, cy1))).convert('RGB')
    crop.save(f'{OUT}/{name}_clean.png')
    title = f"{name.upper()} rev 0 — Praetoseba region 1 'temple' — tiles x {x0}..{x1}, y {y0}..{y1} (yellow box); blue = door tiles"
    diag(crop, title, pn, doors).save(f'{OUT}/{name}_diag.png')
    print(name, crop.size, 'unknown', unk)

# floors / walls in window for the key
fl, wl = collections.Counter(), collections.Counter()
for t in region.findall('tile'):
    x, y = int(t.get('x')), int(t.get('y'))
    if not (x0 <= x <= x1 and y0 <= y <= y1):
        continue
    for c in t.findall('component'):
        if c.get('type') in FLOOR_TYPES:
            fl[int(c.findtext('ground') or 0)] += 1
        elif c.get('type') == 'WallComponent':
            wl[int(c.findtext('wall') or 0)] += 1
key = {'kit': 'dry-run', 'date': '2026-10-29', 'segment': 'Praetoseba', 'region': RID, 'name': 'temple',
       'window': list(WIN), 'margin_tiles': MARGIN, 'tile_px': UNIT,
       'doors': [{'x': x, 'y': y} for x, y in doors],
       'floors': [{'id': i, 'name': (entry(i) or {}).get('name'), 'count': n} for i, n in fl.most_common()],
       'walls': [{'id': i, 'name': (entry(i) or {}).get('name'), 'count': n} for i, n in wl.most_common()],
       'pins': pins}
json.dump(key, open(f'{OUT}/scene_key.json', 'w'), indent=1)

# --- pilot piece subset: temple setting + everything used in the room ----------------------
used = {(p['id'], p['type']) for p in pins}
sub = []
seen = set()
for e in book:
    k = (e['id'], e['type'])
    if k in seen:
        continue
    if 'temple' in (e.get('setting') or []) or k in used or e['id'] in fl or e['id'] in wl:
        if e['category'] in ('Structural', 'Ruins', 'Customizable', 'unlisted') and k not in used and e['id'] not in wl:
            continue  # keep the sheet to things ChatGPT can place in this room
        sub.append(e); seen.add(k)
print('subset', len(sub), collections.Counter(e['category'] for e in sub).most_common())

# contact sheets, 8x6 cards of 150 px, like the piece book
CARD, COLS, ROWS = 150, 8, 6
SPR = 100


def card_img(e):
    im = Image.new('RGBA', (SPR, SPR), (70, 70, 70, 255))
    layers = sorted(sprites.terrain.get(e['id'], []), key=lambda L: L['order'])
    for L in layers:
        s = sprites.img(L)
        im.alpha_composite(s, (L['off'][0], L['off'][1]))  # sprite cell == 100 px, tile at (45,45)
    return im


per = COLS * ROWS
letters = 'ABCDEFGH'
pieces_out = []
for si in range(0, len(sub), per):
    chunk = sub[si:si + per]
    sheet = Image.new('RGB', (COLS * CARD, ROWS * CARD + 44), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    label = f'PILOT SHEET {letters[si // per]} — temple subset — 2026-10-29'
    d.rectangle([0, 0, sheet.width, 44], fill=(255, 220, 0)); d.text((8, 22), label, fill=(0, 0, 0), font=F(22), anchor='lm')
    for j, e in enumerate(chunk):
        cx, cy = (j % COLS) * CARD, 44 + (j // COLS) * CARD
        d.rectangle([cx + 2, cy + 2, cx + CARD - 2, cy + CARD - 2], fill=(40, 40, 40), outline=(90, 90, 90))
        ci = card_img(e)
        sheet.paste(ci, (cx + 25, cy + 6), ci)
        d.text((cx + CARD // 2, cy + 112), f"#{e['n']}  id {e['id']}", fill=(255, 230, 0), font=F(12), anchor='mm')
        nm = (e.get('name') or '')[:22]
        d.text((cx + CARD // 2, cy + 126), nm, fill=(230, 230, 230), font=F(11), anchor='mm')
        d.text((cx + CARD // 2, cy + 140), e['type'].replace('Component', ''), fill=(160, 160, 160), font=F(10), anchor='mm')
        pieces_out.append({'sheet': letters[si // per], 'card': j + 1, **{k: e.get(k) for k in
                           ('n', 'id', 'name', 'type', 'category', 'look', 'kind', 'size', 'placement', 'setting', 'tone', 'pairs_with', 'notes', 'usage')}})
    sheet.save(f'{OUT}/pieces_sheet_{letters[si // per]}.png')
    print('sheet', letters[si // per], len(chunk))
json.dump(pieces_out, open(f'{OUT}/pieces.json', 'w'), indent=1)
