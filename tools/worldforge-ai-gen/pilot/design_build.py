#!/usr/bin/env python3
"""ChatGPT room design -> WorldForge region, rendered and validated.

  python3 design_build.py <design.json> <outdir> [--region-id 1]

design.json (written by ChatGPT):
{
 "name": "...",
 "style": {"wall_H": 29, "wall_V": 30, "wall_C": 34, "door_H": 66, "door_V": 67,
           "mass": 447, "mass_style": "faces", "room": 5, "hall": 1, "accent1": 0, "accent2": 0, "accent3": 0},
 "map": ["MMMMMMMMMM", "M########M", "M#......#M", ...],
 "groups": [{"id": "g1", "purpose": "..."}],
 "decor": [{"p": "p01", "id": 113, "type": "AltarComponent", "x": 5, "y": 3, "group": "g1", "why": "..."}]
}
Map legend:  # wall   M solid mass   D door   . room floor   , hall floor   1 2 3 accent floors
             (space) or _ nothing (void)
x = column, y = row, both 0-based, top-left of the map is (0,0).

Steps: map -> LOK Studio sketch -> sketch_build (the regression-tested wall engine picks every
H/V/C piece, corner post, door orientation and mass face) -> run_plan adds the decor and validates
-> clean.png, diag.png, validation.json, region.xml.
"""
import sys, json, subprocess, argparse, os
from pathlib import Path

GEN = Path('/home/claude/lok-studio/generator')
HERE = Path(__file__).resolve().parent
BOOK = '/home/claude/out/2026-10-29 piece-book-draft.json'
LEGEND = {'#': 'wall', 'M': 'structural', 'D': 'door', '.': 'room', ',': 'hall',
          '1': 'accent1', '2': 'accent2', '3': 'accent3'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('design'); ap.add_argument('out')
    ap.add_argument('--region-id', type=int, default=1)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    d = json.load(open(a.design))
    rows = d['map']
    W = max(len(r) for r in rows); H = len(rows)
    layers, bad = {}, []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in (' ', '_'):
                continue
            k = LEGEND.get(ch)
            if not k:
                bad.append((x, y, ch)); continue
            layers.setdefault(k, []).append([x, y])
    if bad:
        sys.exit('MAP_ERROR: unknown map characters %s' % bad[:10])
    sketch = {'app': 'lok-sketcher', 'version': 5, 'title': d.get('name', 'design'), 'region': a.region_id,
              'width': W, 'height': H, 'x0': 0, 'y0': 0, 'layers': layers, 'labels': []}
    json.dump(sketch, open(out / 'sketch.json', 'w'))

    st = d['style']
    pal = {'room': st['room'], 'hall': st.get('hall') or st['room'], 'floor': st['room'],
           'structural_floor': st.get('structural_floor') or st['room'],
           'wall-ns': st['wall_H'], 'wall-ew': st['wall_V'], 'corner': st['wall_C'],
           'structural': st.get('mass', 447), 'door-ns': st['door_H'], 'door-ew': st['door_V'],
           'mass_style': st.get('mass_style', 'faces')}
    for k in ('accent1', 'accent2', 'accent3'):
        if st.get(k):
            pal[k] = st[k]
    json.dump(pal, open(out / 'palette.json', 'w'), indent=1)
    extra = []
    # second, third ... style: "styles": {"B": {...}}, "zones": rows of the same size, letter = style, '.'/space = main
    if d.get('zones') and d.get('styles'):
        def to_pal(st2):
            q = {'wall-ns': st2.get('wall_H', st['wall_H']), 'wall-ew': st2.get('wall_V', st['wall_V']),
                 'corner': st2.get('wall_C', st['wall_C']), 'door-ns': st2.get('door_H', st['door_H']),
                 'door-ew': st2.get('door_V', st['door_V']), 'structural': st2.get('mass', st.get('mass', 447)),
                 'room': st2.get('room', st['room']), 'hall': st2.get('hall') or st2.get('room') or st.get('hall') or st['room']}
            q['floor'] = q['room']
            for k in ('accent1', 'accent2', 'accent3'):
                if st2.get(k): q[k] = st2[k]
            return q
        masks = {'kind': 'masks', 'styles': {}, 'masks': []}
        for name, st2 in d['styles'].items():
            masks['styles'][name] = to_pal(st2)
            tiles = [[x, y] for y, row in enumerate(d['zones']) for x, ch in enumerate(row) if ch == name]
            masks['masks'].append({'name': name, 'style': name, 'tiles': tiles})
        json.dump(masks, open(out / 'masks.json', 'w'))
        extra = ['--masks', str(out / 'masks.json')]
    r = subprocess.run([sys.executable, str(GEN / 'sketch_build.py'), str(out / 'sketch.json'), '--new',
                        str(a.region_id), d.get('name', 'design'), '--palette', str(out / 'palette.json'),
                        '-o', str(out / 'shell.xml')] + extra, capture_output=True, text=True)
    (out / 'build_report.txt').write_text(r.stdout + r.stderr)
    if r.returncode:
        sys.exit('BUILD_FAILED:\n' + (r.stderr or r.stdout)[-1500:])

    # decor on top: window = whole map, pieces = the whole piece book
    plan = {'rev': 1, 'groups': d.get('groups', []), 'placements': d.get('decor', [])}
    json.dump(plan, open(out / 'plan.json', 'w'), indent=1)
    cmd = [sys.executable, str(HERE / 'run_plan.py'), str(out / 'shell.xml'), str(out / 'plan.json'), BOOK, str(out),
           '--window', '0', '0', str(W - 1), str(H - 1), '--rev', '1', '--label', d.get('name', 'design')]
    if d.get('reserve'):
        cmd += ['--reserve'] + [str(v) for rect in d['reserve'] for v in rect]
    if d.get('route_to'):
        cmd += ['--route-to', str(d['route_to'][0]), str(d['route_to'][1])]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-2000:])


if __name__ == '__main__':
    main()
