#!/usr/bin/env python3
"""Execute a ChatGPT placement plan against a base region, validate it, render before/after.

  python3 run_plan.py <base.xml> <plan.json> <pieces.json> <outdir> --window x0 y0 x1 y1 --rev N
          [--reserve x0 y0 x1 y1 ...] [--route-from DOOR] [--route-to X Y] [--label "text"]

Writes into <outdir>:
  region.xml          base + accepted placements (what WorldForge imports)
  clean.png           render of region.xml, no labels
  diag.png            same framing: grid, coordinates, door tiles, pins, reserved rects, flagged tiles
  before_after.png    base render | new render, side by side
  validation.json     every placement with status and reasons, route checks, summary
  plan.resolved.json  the plan as executed (accepted placements only, with resolved fields)
Rejected placements are NOT written into region.xml; they appear in red on diag.png.
"""
import sys, json, copy, collections, argparse, os, xml.etree.ElementTree as ET
sys.path.insert(0, '/home/claude/tools')
from PIL import Image, ImageDraw, ImageFont
from wf_render import render_region, Sprites, UNIT

FLOOR_TYPES = {'FloorComponent', 'WaterComponent', 'IceComponent', 'PoisonedWaterComponent'}
FIELD = {'StaticComponent': 'static', 'LockersComponent': 'static', 'TrashComponent': 'static',
         'TreeComponent': 'tree', 'ObstructionComponent': 'obstruction', 'AltarComponent': 'altar',
         'CounterComponent': 'counter'}
BLOCKING = {'WallComponent', 'AltarComponent', 'CounterComponent', 'ObstructionComponent', 'TreeComponent'}
WALL_OK_CLASSES = {'against-wall', 'wall-H', 'wall-V', 'wall-corner', 'wall-mass'}
F = lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', s)


def tiles_of(region):
    return {(int(t.get('x')), int(t.get('y'))): t for t in region.findall('tile')}


def has(t, typ):
    return t is not None and t.find(f"component[@type='{typ}']") is not None


def has_floor(t):
    return t is not None and any(has(t, f) for f in FLOOR_TYPES)


def passable(t):
    if not has_floor(t):
        return False
    for c in t.findall('component'):
        if c.get('type') in BLOCKING:
            return False
        if c.get('type') == 'DoorComponent':
            return True  # doors open; they interrupt but do not block
    return True


def flood(T, start, goal_set):
    seen = {start}; q = [start]
    while q:
        x, y = q.pop()
        if (x, y) in goal_set:
            return True
        for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if (nx, ny) not in seen and passable(T.get((nx, ny))):
                seen.add((nx, ny)); q.append((nx, ny))
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base'); ap.add_argument('plan'); ap.add_argument('pieces'); ap.add_argument('out')
    ap.add_argument('--window', nargs=4, type=int, required=True)
    ap.add_argument('--rev', type=int, default=1)
    ap.add_argument('--reserve', nargs='+', type=int, default=[], help='x0 y0 x1 y1 groups')
    ap.add_argument('--route-to', nargs=2, type=int, help='tile the doors must reach (its passable neighbours count)')
    ap.add_argument('--label', default='')
    ap.add_argument('--before', help='region xml to show on the left of before_after (default: base)')
    ap.add_argument('--allow-floors', action='store_true', help='let the plan change floor ids inside the window')
    ap.add_argument('--patch', help='patch json (ops against the plan given as <plan>, which must be the previous plan.resolved.json)')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    x0, y0, x1, y1 = a.window
    reserved = set()
    for i in range(0, len(a.reserve), 4):
        rx0, ry0, rx1, ry1 = a.reserve[i:i+4]
        reserved |= {(x, y) for x in range(rx0, rx1+1) for y in range(ry0, ry1+1)}

    pieces = json.load(open(a.pieces))
    pk = {(e['id'], e['type']): e for e in pieces}
    plan = json.load(open(a.plan))
    placements = plan['plan']['placements'] if 'plan' in plan else plan['placements']
    patch_log = []
    if a.patch:
        patch = json.load(open(a.patch))
        if int(patch.get('against_rev', -1)) != int(plan.get('rev', a.rev - 1)):
            sys.exit('STALE_PATCH: patch is against rev %s but the plan is rev %s' % (patch.get('against_rev'), plan.get('rev')))
        byp = {q['p']: q for q in placements}
        if patch.get('groups'):
            plan['groups'] = patch['groups']
        for op in patch['ops']:
            k, pid = op['op'], op['p']
            if k == 'add':
                if pid in byp:
                    patch_log.append({'op': op, 'status': 'rejected', 'why': 'id already exists'}); continue
                q = {kk: op[kk] for kk in ('p', 'id', 'type', 'x', 'y', 'group', 'why') if kk in op}
                placements.append(q); byp[pid] = q
            elif pid not in byp:
                patch_log.append({'op': op, 'status': 'rejected', 'why': 'no such placement'}); continue
            elif k == 'floor':
                placements.append({'p': pid, 'id': op['id'], 'type': 'FloorComponent', 'x': op['x'], 'y': op['y'], 'group': op.get('group'), 'why': op.get('why')})
                byp[pid] = placements[-1]
            elif k == 'remove':
                placements.remove(byp.pop(pid))
            elif k == 'move':
                byp[pid]['x'], byp[pid]['y'] = op['x'], op['y']; byp[pid]['why'] = op.get('why', byp[pid].get('why'))
            elif k == 'replace':
                byp[pid]['id'], byp[pid]['type'] = op['id'], op['type']; byp[pid]['why'] = op.get('why', byp[pid].get('why'))
            else:
                patch_log.append({'op': op, 'status': 'rejected', 'why': 'unknown op'}); continue
            patch_log.append({'op': op, 'status': 'applied'})

    base = ET.parse(a.base).getroot()
    region = copy.deepcopy(base)
    T = tiles_of(region)
    doors = [(x, y) for (x, y), t in T.items() if has(t, 'DoorComponent') and x0 <= x <= x1 and y0 <= y <= y1]

    issues, accepted, occupied = [], [], collections.Counter()
    results = []
    for p in placements:
        pid, i, typ, x, y = p['p'], int(p['id']), p['type'], int(p['x']), int(p['y'])
        errs, warns = [], []
        e = pk.get((i, typ))
        if e is None:
            errs.append('UNKNOWN_ID_OR_TYPE: %d %s not in pieces.json' % (i, typ))
        if typ not in FIELD and typ != 'FloorComponent':
            errs.append('UNSUPPORTED_TYPE: %s' % typ)
        t = T.get((x, y))
        if t is None:
            errs.append('NO_TILE: (%d,%d) does not exist in the region' % (x, y))
        else:
            if not (x0 <= x <= x1 and y0 <= y <= y1):
                errs.append('OUT_OF_WINDOW')
            if not has_floor(t):
                errs.append('NO_FLOOR: tile has no floor component')
            if has(t, 'WallComponent') and (e or {}).get('placement') not in WALL_OK_CLASSES and (e or {}).get('category') != 'Wall Doodads (H)':
                errs.append('ON_WALL_TILE: piece class %s may not sit on a wall tile' % (e or {}).get('placement'))
            if has(t, 'DoorComponent'):
                errs.append('ON_DOOR_TILE')
            if (x, y) in reserved:
                errs.append('IN_RESERVED_AREA')
            for c in t.findall('component'):
                if c.get('type') in FIELD and c.findtext(FIELD[c.get('type')]) == str(i):
                    errs.append('DUPLICATE: same id already on this tile')
            if typ == 'FloorComponent' and not a.allow_floors:
                errs.append('FLOOR_CHANGE_NOT_ALLOWED in this pass')
            if typ == 'FloorComponent' and has(t, 'WallComponent'):
                errs.append('FLOOR_UNDER_WALL: not changing floors under wall tiles')
            if occupied[(x, y)]:
                warns.append('STACKED: another planned piece already on this tile')
            # door approach: the tile directly west/east/north/south of a door should stay clear
            for dx, dy in doors:
                if abs(dx - x) + abs(dy - y) == 1:
                    warns.append('DOOR_APPROACH: adjacent to door (%d,%d)' % (dx, dy))
        status = 'error' if errs else ('warn' if warns else 'ok')
        results.append({'p': pid, 'id': i, 'type': typ, 'x': x, 'y': y, 'group': p.get('group'),
                        'status': status, 'errors': errs, 'warnings': warns,
                        'name': (e or {}).get('name'), 'placement_class': (e or {}).get('placement')})
        if not errs and typ == 'FloorComponent':
            fc = t.find("component[@type='FloorComponent']")
            if fc is None:
                fc = ET.SubElement(t, 'component', type='FloorComponent'); ET.SubElement(fc, 'ground')
            fc.find('ground').text = str(i)
            accepted.append(dict(p, name=(e or {}).get('name')))
        elif not errs:
            c = ET.SubElement(t, 'component', type=typ)
            ET.SubElement(c, FIELD[typ]).text = str(i)
            occupied[(x, y)] += 1
            accepted.append(dict(p, name=(e or {}).get('name')))

    # route checks: every door must reach the goal's passable neighbourhood
    routes = []
    if a.route_to:
        gx, gy = a.route_to
        goal = {(gx+dx, gy+dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
        T2 = tiles_of(region)
        for d in doors:
            # start from the tile west of the door (inside the hall) and east of it
            ok = any(flood(T2, s, goal) for s in ((d[0]-1, d[1]), (d[0]+1, d[1]), (d[0], d[1]-1), (d[0], d[1]+1)) if passable(T2.get(s)))
            routes.append({'from_door': list(d), 'to': [gx, gy], 'clear': ok})
            if not ok:
                issues.append({'code': 'REQUIRED_ROUTE_BLOCKED', 'severity': 'error', 'from': list(d), 'to': [gx, gy]})
    # reserved rectangles must still be passable
    for (x, y) in sorted(reserved):
        t = T.get((x, y))
        if t is not None and has_floor(t) and not passable(t) and not has(t, 'DoorComponent'):
            issues.append({'code': 'RESERVED_TILE_BLOCKED', 'severity': 'error', 'tile': [x, y]})

    corridor = {'status': 'not_run'}
    if reserved:
        blocked = [list(t) for t in sorted(reserved) if has_floor(T.get(t)) and not passable(T.get(t)) and not has(T.get(t), 'DoorComponent')]
        corridor = {'status': 'fail' if blocked else 'pass', 'tiles': len(reserved), 'blocked': blocked,
                    'note': 'every reserved tile must stay passable; the reserved rectangles define the corridor width'}
    # occlusion: does the visible part of a placed sprite cover a door tile or a reserved tile it is not anchored on?
    occl = []
    sprites_tmp = Sprites()
    for r in results:
        if r['status'] == 'error':
            continue
        layers = sprites_tmp.terrain.get(r['id'], [])
        if not layers:
            continue
        cov = set()
        for L in layers:
            im = sprites_tmp.img(L); bb = im.getbbox()
            if not bb:
                continue
            ox_, oy_ = -45 + L['off'][0], -45 + L['off'][1]
            for px_ in (bb[0], bb[2]-1):
                for py_ in (bb[1], bb[3]-1):
                    cov.add((r['x'] + (ox_+px_)//UNIT, r['y'] + (oy_+py_)//UNIT))
            # fill in between the corners
            xs_ = [c[0] for c in cov]; ys_ = [c[1] for c in cov]
            cov = {(cx_, cy_) for cx_ in range(min(xs_), max(xs_)+1) for cy_ in range(min(ys_), max(ys_)+1)}
        cov.discard((r['x'], r['y']))
        hit_doors = [list(d) for d in doors if d in cov]
        hit_res = [list(t) for t in sorted(reserved) if t in cov]
        if hit_doors or hit_res:
            occl.append({'p': r['p'], 'covers_doors': hit_doors, 'covers_reserved': hit_res})
            r['warnings'].append('OCCLUSION: sprite extends over door/reserved tiles %s' % (hit_doors + hit_res))
            if r['status'] == 'ok': r['status'] = 'warn'
    occlusion = {'status': 'pass' if not occl else 'warn', 'method': 'sprite alpha bounding box vs door and reserved tiles (warning only; tall pieces lean up-left by design)', 'hits': occl}

    n_err = sum(1 for r in results if r['status'] == 'error') + sum(1 for i in issues if i['severity'] == 'error') + (1 if corridor.get('status') == 'fail' else 0)
    validation = {'schema_version': '1', 'rev': a.rev, 'window': a.window, 'status': 'fail' if n_err else 'pass',
                  'checks': {'placements': 'run', 'route_connectivity': 'run' if a.route_to else 'not_run',
                             'corridor_width': corridor['status'] if corridor['status'] == 'not_run' else 'run',
                             'sprite_occlusion': 'run', 'wall_side_support': 'not_run', 'editor_import': 'not_run'},
                  'patch_log': patch_log, 'corridor': corridor, 'occlusion': occlusion,
                  'placements': results, 'routes': routes, 'issues': issues,
                  'metrics': {'planned': len(results), 'accepted': len(accepted),
                              'rejected': sum(1 for r in results if r['status'] == 'error'),
                              'warnings': sum(len(r['warnings']) for r in results),
                              'routes_clear': sum(1 for r in routes if r['clear']), 'routes_total': len(routes)}}
    json.dump(validation, open(f'{a.out}/validation.json', 'w'), indent=1)
    json.dump({'rev': a.rev, 'groups': plan.get('plan', plan).get('groups', []), 'placements': accepted},
              open(f'{a.out}/plan.resolved.json', 'w'), indent=1)
    ET.ElementTree(region).write(f'{a.out}/region.xml', encoding='utf-8', xml_declaration=True)

    # ---- renders ------------------------------------------------------------------------
    sprites = Sprites()
    alltiles = base.findall('tile')
    minx = min(int(t.get('x')) for t in alltiles); miny = min(int(t.get('y')) for t in alltiles)
    pad, M = 1, 1
    cx0 = (x0 - M - minx + pad) * UNIT; cy0 = (y0 - M - miny + pad) * UNIT
    cx1 = (x1 + M - minx + pad + 1) * UNIT; cy1 = (y1 + M - miny + pad + 1) * UNIT

    def crop_of(reg):
        img, _ = render_region(reg, sprites, pad=pad)
        return img.crop((max(0, cx0), max(0, cy0), min(img.width, cx1), min(img.height, cy1))).convert('RGB')

    def tile_px(x, y):
        return (x - minx + pad) * UNIT - cx0, (y - miny + pad) * UNIT - cy0

    before, after = crop_of(ET.parse(a.before).getroot() if a.before else base), crop_of(region)
    after.save(f'{a.out}/clean.png')
    ba = Image.new('RGB', (before.width * 2 + 20, before.height + 40), (0, 0, 0))
    ba.paste(before, (0, 40)); ba.paste(after, (before.width + 20, 40))
    d = ImageDraw.Draw(ba)
    d.text((8, 20), f'BEFORE (rev {a.rev-1})', fill=(255, 220, 0), font=F(20), anchor='lm')
    d.text((before.width + 28, 20), f'AFTER (rev {a.rev})', fill=(255, 220, 0), font=F(20), anchor='lm')
    ba.save(f'{a.out}/before_after.png')

    RUL = 26; HB = 64
    W, H = after.width + 2 * RUL, after.height + 2 * RUL + HB
    page = Image.new('RGB', (W, H), (0, 0, 0)); page.paste(after, (RUL, RUL + HB))
    d = ImageDraw.Draw(page, 'RGBA')
    d.rectangle([0, 0, W, HB], fill=(255, 220, 0))
    title = f'DIAG rev {a.rev} — {a.label}'
    fnt = F(18)
    while d.textlength(title, font=fnt) > W - 16 and fnt.size > 10: fnt = F(fnt.size - 1)
    d.text((8, 18), title, fill=(0, 0, 0), font=fnt, anchor='lm')
    legend = f'review window x {x0}..{x1}, y {y0}..{y1} = yellow box   |   cyan D = door   |   dark = reserved route   |   yellow tag = placed, orange = warning, red = rejected'
    fnt = F(13)
    while d.textlength(legend, font=fnt) > W - 16 and fnt.size > 8: fnt = F(fnt.size - 1)
    d.text((8, 46), legend, fill=(0, 0, 0), font=fnt, anchor='lm')
    ox, oy = RUL, RUL + HB
    wx, wy = tile_px(x0, y0)
    d.rectangle([ox+wx, oy+wy, ox+wx+(x1-x0+1)*UNIT, oy+wy+(y1-y0+1)*UNIT], outline=(255, 255, 0, 200), width=2)
    for x in range(x0 - M, x1 + M + 1):
        px, _ = tile_px(x, y0); d.line([(ox+px, oy), (ox+px, oy+after.height)], fill=(255, 255, 255, 70))
        for yy in (oy - RUL//2, oy + after.height + RUL//2):
            d.text((ox+px+UNIT//2, yy), str(x), fill=(255, 255, 255), font=F(12), anchor='mm')
    for y in range(y0 - M, y1 + M + 1):
        _, py = tile_px(x0, y); d.line([(ox, oy+py), (ox+after.width, oy+py)], fill=(255, 255, 255, 70))
        for xx in (ox - RUL//2, ox + after.width + RUL//2):
            d.text((xx, oy+py+UNIT//2), str(y), fill=(255, 255, 255), font=F(12), anchor='mm')
    for (x, y) in sorted(reserved):
        px, py = tile_px(x, y); d.rectangle([ox+px, oy+py, ox+px+UNIT, oy+py+UNIT], fill=(0, 0, 80, 110))
    for (x, y) in doors:
        px, py = tile_px(x, y)
        d.rectangle([ox+px+1, oy+py+1, ox+px+UNIT-1, oy+py+UNIT-1], outline=(0, 0, 0, 255), width=5)
        d.rectangle([ox+px+3, oy+py+3, ox+px+UNIT-3, oy+py+UNIT-3], outline=(0, 230, 255, 255), width=3)
        d.rectangle([ox+px+UNIT-22, oy+py+UNIT-16, ox+px+UNIT-3, oy+py+UNIT-3], fill=(0, 230, 255, 255))
        d.text((ox+px+UNIT-12, oy+py+UNIT-9), 'D', fill=(0, 0, 0), font=F(11), anchor='mm')
    stack = collections.Counter()
    for r in results:
        px, py = tile_px(r['x'], r['y'])
        s = stack[(r['x'], r['y'])]; stack[(r['x'], r['y'])] += 1
        ax, ay = ox+px+UNIT//2, oy+py+UNIT//2            # anchor: tile centre
        cx, cy = ax + 24, ay + 24 + s*18                    # label: off the sprite, down-right, with a leader line
        col = (255, 60, 60) if r['status'] == 'error' else ((255, 170, 0) if r['status'] == 'warn' else (255, 230, 0))
        if r['status'] == 'error':
            d.rectangle([ox+px+2, oy+py+2, ox+px+UNIT-2, oy+py+UNIT-2], outline=(255, 40, 40, 255), width=4)
        d.line([(ax, ay), (cx-14, cy-6)], fill=(0, 0, 0, 255), width=3); d.line([(ax, ay), (cx-14, cy-6)], fill=col, width=1)
        d.ellipse([ax-3, ay-3, ax+3, ay+3], fill=col, outline=(0, 0, 0, 255))
        d.rounded_rectangle([cx-18, cy-9, cx+18, cy+9], radius=6, fill=(0, 0, 0, 255))
        d.rounded_rectangle([cx-16, cy-7, cx+16, cy+7], radius=5, fill=col)
        d.text((cx, cy), r['p'], fill=(0, 0, 0), font=F(11), anchor='mm')
    page.save(f'{a.out}/diag.png')
    print(json.dumps(validation['metrics']), validation['status'])
    for r in results:
        if r['status'] != 'ok':
            print(r['p'], r['status'], r['errors'], r['warnings'])
    for i in issues:
        print(i)


if __name__ == '__main__':
    main()
