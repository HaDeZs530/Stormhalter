#!/usr/bin/env python3
"""Measure how the game developers place each decoration id across their maps.

Inputs (read-only): the six .mapproj segments, the components legend and the piece book.
Outputs: placement-stats.json, placement-stats.md, README.md in this directory.
"""
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque

HERE = os.path.dirname(os.path.abspath(__file__))
SEGMENTS = sorted(glob.glob('/home/claude/corpus/*.mapproj')) + [
    '/home/claude/jkachhad/stormhalter/Segments/Praetoseba.mapproj']
LEGEND = '/home/claude/out/components-legend.json'
PIECEBOOK = '/home/claude/out/2026-10-29 piece-book-draft.json'

DECO_TYPES = {
    'StaticComponent': 'static',
    'LockersComponent': 'static',
    'TrashComponent': 'static',
    'TreeComponent': 'tree',
    'ObstructionComponent': 'obstruction',
    'AltarComponent': 'altar',
    'CounterComponent': 'counter',
}
MASS_IDS = {31, 446, 447, 448, 1221}

# ---------------------------------------------------------------- palette
legend = json.load(open(LEGEND))
piece = json.load(open(PIECEBOOK))
piece_by_id = {e['id']: e for e in piece if isinstance(e.get('id'), int)}
legend_wall_name = {}
for e in legend:
    if e['type'] == 'WallComponent':
        legend_wall_name[int(e['props']['wall'])] = e.get('name') or ''


def wall_class(wid):
    """H / V / C / mass / other for a WallComponent wall id."""
    if wid in MASS_IDS:
        return 'mass'
    pb = piece_by_id.get(wid)
    pl = pb.get('placement') if pb else None
    if pl == 'wall-H':
        return 'H'
    if pl == 'wall-V':
        return 'V'
    if pl in ('wall-corner', 'free-standing'):
        return 'C'
    if pl == 'wall-mass':
        return 'mass'
    name = (legend_wall_name.get(wid) or (pb.get('name') if pb else '') or '').strip().lower()
    if re.search(r'\((h)\)', name) or re.search(r'(^|\s)h(\s|$)', name) or name.endswith(' h'):
        return 'H'
    if re.search(r'\((v)\)', name) or re.search(r'(^|\s)v(\s|$)', name) or name.endswith(' v'):
        return 'V'
    if re.search(r'\((c)\)', name) or any(k in name for k in ('post', 'pillar', 'column', 'corner', 'stalagmite')):
        return 'C'
    if 'solid' in name:
        return 'mass'
    if pb and pb.get('type') == 'ObstructionComponent':
        return 'C'  # pillar-type obstruction sprites used as wall ids (168, 313)
    return 'other'


def name_of(i):
    pb = piece_by_id.get(i)
    if pb and pb.get('name'):
        return pb['name']
    if pb and pb.get('kind'):
        return '(' + pb['kind'] + ')'
    return ''


# ---------------------------------------------------------------- parse
class Tile:
    __slots__ = ('floors', 'walls', 'door', 'decos', 'empty', 'wclasses')

    def __init__(self):
        self.floors = []
        self.walls = []      # wall ids
        self.door = None     # closedId
        self.decos = []      # (id, type)
        self.empty = True
        self.wclasses = set()


def parse_segment(path):
    tree = ET.parse(path)
    root = tree.getroot()
    segname = root.get('name') or os.path.basename(path)
    regions = []
    for reg in root.iter('region'):
        rid = reg.findtext('id')
        rname = reg.findtext('name')
        tiles = {}
        for t in reg.findall('tile'):
            x, y = int(t.get('x')), int(t.get('y'))
            tile = Tile()
            for c in t.findall('component'):
                ct = c.get('type')
                tile.empty = False
                if ct == 'FloorComponent':
                    g = c.findtext('ground')
                    if g is not None:
                        tile.floors.append(int(g))
                elif ct == 'WallComponent':
                    w = c.findtext('wall')
                    if w is not None:
                        wid = int(w)
                        tile.walls.append(wid)
                        tile.wclasses.add(wall_class(wid))
                elif ct == 'DoorComponent':
                    cid = c.findtext('closedId')
                    tile.door = int(cid) if cid is not None else -1
                elif ct in DECO_TYPES:
                    v = c.findtext(DECO_TYPES[ct])
                    if v is not None:
                        tile.decos.append((int(v), ct))
            tiles[(x, y)] = tile
        regions.append((segname, rid, rname, tiles))
    return regions


# ---------------------------------------------------------------- analysis
def has_class(tiles, xy, classes):
    t = tiles.get(xy)
    return bool(t) and bool(t.wclasses & classes)


def any_wall(tiles, xy):
    t = tiles.get(xy)
    return bool(t) and bool(t.walls)


def wall_sides(tiles, x, y):
    n = has_class(tiles, (x, y - 1), {'H', 'mass', 'C'})
    w = has_class(tiles, (x - 1, y), {'V', 'mass', 'C'})
    s = has_class(tiles, (x, y), {'H'}) or has_class(tiles, (x, y + 1), {'mass'})
    e = has_class(tiles, (x, y), {'V'}) or has_class(tiles, (x + 1, y), {'mass'})
    return n, w, s, e


def wall_within(tiles, x, y, r):
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if any_wall(tiles, (x + dx, y + dy)):
                return True
    return False


def is_void(tiles, xy):
    t = tiles.get(xy)
    return t is None or t.empty


def passable(tiles, xy):
    t = tiles.get(xy)
    return t is not None and not t.empty and not t.walls


def enclosed(tiles, x, y, limit=40):
    """Flood fill through passable tiles; True if no void reached within `limit` steps."""
    start = (x, y)
    seen = {start}
    q = deque([(start, 0)])
    while q:
        (cx, cy), d = q.popleft()
        if d >= limit:
            continue
        for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
            p = (nx, ny)
            if p in seen:
                continue
            seen.add(p)
            if is_void(tiles, p):
                return False
            if passable(tiles, p):
                q.append((p, d + 1))
    return True


def door_approach_tiles(tiles, x, y):
    ew_walled = any_wall(tiles, (x - 1, y)) and any_wall(tiles, (x + 1, y))
    ns_walled = any_wall(tiles, (x, y - 1)) and any_wall(tiles, (x, y + 1))
    out = []
    if ew_walled and not ns_walled:
        out = [(x, y - 1), (x, y + 1)]
    elif ns_walled and not ew_walled:
        out = [(x - 1, y), (x + 1, y)]
    else:
        out = [p for p in ((x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)) if not any_wall(tiles, p)]
    return out


def analyse(regions):
    stats = {}

    def S(key):
        if key not in stats:
            stats[key] = dict(
                n=0, regions=set(), segments=set(), types=Counter(),
                floor=0, ground=Counter(),
                wallN=0, wallW=0, wallS=0, wallE=0, any_side=0, corner=0,
                free=0, wall_within_2=0,
                near_door=0, door_approach=0, on_wall_tile=0, walls_NS=0, walls_WE=0,
                same_nb1=0, same_nb3=0, cluster_sizes=[],
                stacked=0, costack=Counter(), cooc=Counter(),
                spaced2=0, interior=0,
            )
        return stats[key]

    for segname, rid, rname, tiles in regions:
        # door tiles and approach tiles
        doors = [(xy, t.door) for xy, t in tiles.items() if t.door is not None]
        door_set = {xy for xy, _ in doors}
        approach = set()
        for (x, y), _ in doors:
            approach.update(door_approach_tiles(tiles, x, y))
        near_door = set()
        for (x, y) in door_set:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    near_door.add((x + dx, y + dy))

        # same-id clusters (4-connected) per id
        id_tiles = defaultdict(set)
        for xy, t in tiles.items():
            for did, ct in t.decos:
                id_tiles[did].add(xy)
        cluster_of = {}
        for did, pts in id_tiles.items():
            seen = set()
            for p in pts:
                if p in seen:
                    continue
                comp = []
                q = [p]
                seen.add(p)
                while q:
                    c = q.pop()
                    comp.append(c)
                    for nb in ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)):
                        if nb in pts and nb not in seen:
                            seen.add(nb)
                            q.append(nb)
                for c in comp:
                    cluster_of[(did, c)] = len(comp)

        # placements: decorations and doors
        placements = []
        for xy, t in tiles.items():
            for did, ct in t.decos:
                placements.append((did, ct, xy))
            if t.door is not None:
                placements.append((('door', t.door), 'DoorComponent', xy))

        for key, ct, (x, y) in placements:
            s = S(key)
            t = tiles[(x, y)]
            s['n'] += 1
            s['regions'].add((segname, rid))
            s['segments'].add(segname)
            s['types'][ct] += 1
            if t.floors:
                s['floor'] += 1
                for g in t.floors:
                    s['ground'][g] += 1
            if t.walls:
                s['on_wall_tile'] += 1
            n, w, sd, e = wall_sides(tiles, x, y)
            s['wallN'] += n; s['wallW'] += w; s['wallS'] += sd; s['wallE'] += e
            if n or w or sd or e:
                s['any_side'] += 1
            if (n and w) or (n and e) or (sd and w) or (sd and e):
                s['corner'] += 1
            if any_wall(tiles, (x, y - 1)) and any_wall(tiles, (x, y + 1)):
                s['walls_NS'] += 1
            if any_wall(tiles, (x - 1, y)) and any_wall(tiles, (x + 1, y)):
                s['walls_WE'] += 1
            if not wall_within(tiles, x, y, 1):
                s['free'] += 1
            if wall_within(tiles, x, y, 2):
                s['wall_within_2'] += 1
            if (x, y) in near_door and ct != 'DoorComponent':
                s['near_door'] += 1
            elif ct == 'DoorComponent':
                # for doors: another door within 1 tile
                if any(p in door_set for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1),(x+1,y+1),(x-1,y-1),(x+1,y-1),(x-1,y+1))):
                    s['near_door'] += 1
            if (x, y) in approach:
                s['door_approach'] += 1
            # same-id neighbours
            if ct == 'DoorComponent':
                same = lambda p: p in tiles and tiles[p].door == key[1]
                others_here = [(d, c) for d, c in t.decos]
            else:
                same = lambda p: p in tiles and any(d == key for d, _ in tiles[p].decos)
                others_here = [(d, c) for d, c in t.decos if d != key]
            orth = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            k = sum(1 for p in orth if same(p))
            if k >= 1:
                s['same_nb1'] += 1
            if k >= 3:
                s['same_nb3'] += 1
            if ct != 'DoorComponent':
                s['cluster_sizes'].append(cluster_of[(key, (x, y))])
            # stacking
            if others_here:
                s['stacked'] += 1
                for d, _ in others_here:
                    s['costack'][d] += 1
            # co-occurrence within 2 tiles (other tiles)
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx == 0 and dy == 0:
                        continue
                    nt = tiles.get((x + dx, y + dy))
                    if not nt:
                        continue
                    for d, _ in nt.decos:
                        if d != key:
                            s['cooc'][d] += 1
            # spaced two apart in a straight line with empty in-between
            sp = False
            for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                far = (x + dx, y + dy)
                mid = (x + dx // 2, y + dy // 2)
                if same(far):
                    mt = tiles.get(mid)
                    if mt is None or (not mt.decos and mt.door is None):
                        sp = True
                        break
            if sp:
                s['spaced2'] += 1
            if enclosed(tiles, x, y):
                s['interior'] += 1
    return stats


def finalize(stats):
    out = {}
    for key, s in stats.items():
        n = s['n']
        pct = lambda v: round(100.0 * v / n, 1) if n else 0.0
        if isinstance(key, tuple):
            okey = 'door_%d' % key[1]
            did = key[1]
        else:
            okey = str(key)
            did = key
        cs = s['cluster_sizes']
        rec = {
            'id': did,
            'name': name_of(did),
            'component_types': dict(s['types']),
            'n': n,
            'regions': len(s['regions']),
            'segments': len(s['segments']),
            'floor_pct': pct(s['floor']),
            'top_ground': [[g, c] for g, c in s['ground'].most_common(3)],
            'on_wall_tile_pct': pct(s['on_wall_tile']),
            'wall_N_pct': pct(s['wallN']),
            'wall_W_pct': pct(s['wallW']),
            'wall_S_pct': pct(s['wallS']),
            'wall_E_pct': pct(s['wallE']),
            'any_wall_side_pct': pct(s['any_side']),
            'corner_pct': pct(s['corner']),
            'free_pct': pct(s['free']),
            'wall_within_2_pct': pct(s['wall_within_2']),
            'walls_both_N_and_S_pct': pct(s['walls_NS']),
            'walls_both_W_and_E_pct': pct(s['walls_WE']),
            'near_door_pct': pct(s['near_door']),
            'door_approach_pct': pct(s['door_approach']),
            'same_id_neighbour_pct': pct(s['same_nb1']),
            'same_id_3plus_neighbours_pct': pct(s['same_nb3']),
            'mean_cluster_size_per_placement': round(sum(cs) / len(cs), 2) if cs else None,
            'spaced_two_apart_pct': pct(s['spaced2']),
            'stacked_pct': pct(s['stacked']),
            'top_costacked': [[d, c, name_of(d)] for d, c in s['costack'].most_common(5)],
            'top_cooccurring_within_2': [[d, c, name_of(d)] for d, c in s['cooc'].most_common(8)],
            'interior_pct': pct(s['interior']),
        }
        if cs:
            # mean over distinct clusters = placements / clusters
            clusters = sum(1.0 / c for c in cs)
            rec['mean_cluster_size_per_cluster'] = round(len(cs) / clusters, 2)
        out[okey] = rec
    return out


def main():
    regions = []
    for p in SEGMENTS:
        r = parse_segment(p)
        print('parsed', os.path.basename(p), len(r), 'regions', file=sys.stderr)
        regions.extend(r)
    stats = analyse(regions)
    out = finalize(stats)
    # wall classification table for the README
    wc = {}
    for _, _, _, tiles in regions:
        for t in tiles.values():
            for w in t.walls:
                wc[w] = wall_class(w)
    with open(os.path.join(HERE, 'placement-stats.json'), 'w') as f:
        json.dump(out, f, indent=1)
    with open(os.path.join(HERE, 'wall-classes.json'), 'w') as f:
        json.dump({str(k): {'class': v, 'name': legend_wall_name.get(k) or name_of(k)} for k, v in sorted(wc.items())}, f, indent=1)
    print('ids:', len(out), file=sys.stderr)


if __name__ == '__main__':
    main()
