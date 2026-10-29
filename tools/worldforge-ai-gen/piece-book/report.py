#!/usr/bin/env python3
"""Write placement-stats.md and README.md from placement-stats.json."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, 'placement-stats.json')))
wc = json.load(open(os.path.join(HERE, 'wall-classes.json')))

decos = [r for k, r in d.items() if not k.startswith('door_')]
doors = [r for k, r in d.items() if k.startswith('door_')]
decos.sort(key=lambda r: -r['n'])
doors.sort(key=lambda r: -r['n'])

DEFS = """## Definitions

Corpus: 6 segments (Blackburrow, Leng, axe_glacier, oakvael, underkingdom, Praetoseba), 93 regions.
Decoration components counted: StaticComponent, LockersComponent, TrashComponent (id = `<static>`),
TreeComponent (`<tree>`), ObstructionComponent (`<obstruction>`), AltarComponent (`<altar>`),
CounterComponent (`<counter>`). One placement = one such component on one tile. Ids are the shared
sprite-id space, so the same id can appear under different component types (`component_types` says which).
DoorComponent placements are keyed `door_<closedId>` and get the same measures.

Wall classes per WallComponent wall id (from the piece book `placement`, then the palette name):
H = draws along its tile's south edge; V = draws along its tile's east edge; C = corner post, pillar,
column, stalagmite, portal pillar (point-like block); mass = solid block ids 31, 446, 447, 448, 1221.
A tile can carry several WallComponents; its class set is the union. `wall-classes.json` lists the mapping.

Wall adjacency for tile t=(x,y), defined by the drawn pieces:
- wallN: tile (x,y-1) has H or mass or C
- wallW: tile (x-1,y) has V or mass or C
- wallS: t itself has H (an H on the tile draws on its south edge) or (x,y+1) has mass
- wallE: t itself has V or (x+1,y) has mass
- corner: two adjacent sides (N&W, N&E, S&W, S&E)
- free: no WallComponent of any class on t or any of its 8 neighbours
- wall_within_2: any WallComponent in the 5x5 window around t
- on_wall_tile: t itself carries a WallComponent
- walls_both_N_and_S / walls_both_W_and_E: both neighbours on that axis carry any WallComponent
  (useful for doors: a door in a vertical wall run has walls N and S)

Doors: near_door = a door on t or any of its 8 neighbours (for a door id: another door on a neighbour).
door_approach = t is a tile directly in front of a door on either side: if the door's W and E
neighbours are walled the approach tiles are N and S of the door; if N and S are walled, W and E;
otherwise every unwalled orthogonal neighbour.

Same-id clustering: same_id_neighbour = at least one orthogonal neighbour carries the same id;
same_id_3plus = three or more; cluster size = 4-connected same-id component, reported as mean over
placements and mean over clusters (placements / clusters). spaced_two_apart = a same-id placement at
exactly distance 2 in a straight line with no decoration or door on the tile between.

Stacking: the tile carries another decoration component (any other id). top_costacked = those ids.
Co-occurrence: other decoration ids on the other 24 tiles of the 5x5 window, counted per
(placement, neighbour) pair.

Interior: 4-connected flood fill from t through passable tiles (present, non-empty, no WallComponent;
doors pass) for up to 40 steps; interior if the fill never touches a void tile (absent from the
region or an empty `<tile/>`). Approximate: open sky, water etc. are not treated as void.

All shares are percentages of n for that id.

Note on `on_wall_tile`: many of the most-used StaticComponent ids (12 Dirt, 179 Dusty Cave, 23, 1 Light,
182 Slate Flagstone, 20 Ice, 18 Sand, 387 Skulls ...) are floor-texture sprites that the developers put
as a StaticComponent on the same tile as a wall piece (99-100% on_wall_tile). They are wall under-fill,
not free decorations; their wall-side shares describe the wall tile they sit on, not an adjacency choice.
Wall-mounted furniture (bookshelves 243/244/764, storage shelf 439, Fuji 491, hanging skeleton 221,
wall darkened 933/934, waterfall 1006, hedge strips 226/227) is likewise placed ON the wall tile.
"""


def row(r):
    return '| %s | %s | %d | %d | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %.0f | %s |' % (
        r['id'], (r['name'] or '')[:28].replace('|', '/'), r['n'], r['regions'], r['floor_pct'], r['on_wall_tile_pct'],
        r['wall_N_pct'], r['wall_W_pct'], r['wall_S_pct'], r['wall_E_pct'], r['corner_pct'], r['free_pct'],
        r['near_door_pct'], r['door_approach_pct'], r['same_id_neighbour_pct'], r['same_id_3plus_neighbours_pct'],
        r['spaced_two_apart_pct'], r['stacked_pct'], str(r['interior_pct']) + (' | ' + ','.join(str(x[0]) for x in r['top_costacked'][:3]) if True else ''))


HDR = ('| id | name | n | regions | floor% | on-wall-tile% | N% | W% | S% | E% | corner% | free% | near-door% | '
       'approach% | same-nb% | same-3+% | spaced-2% | stacked% | interior% | top co-stacked |\n'
       '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')

lines = ['# Decoration placement statistics (developer maps)', '',
         'Generated by measure.py / report.py from the six developer segments. Counts only; no judgement.', '',
         DEFS, '', '## 60 most-used decoration ids', '', HDR]
for r in decos[:60]:
    lines.append(row(r))

lines += ['', '## Door ids (closedId)', '', HDR]
for r in doors:
    lines.append(row(r))

# ------------------------------------------------------------ rules
MIN = 20
rules = []


def fmt(r, field):
    return '%s %s (n=%d, %s %.0f%%)' % (r['id'], r['name'], r['n'], field, r[field])


def section(title, items):
    if items:
        rules.append('### ' + title)
        rules.extend('- ' + i for i in items)
        rules.append('')


big = [r for r in decos if r['n'] >= MIN]
for side in ('N', 'W', 'S', 'E'):
    f = 'wall_%s_pct' % side
    section('>=80%% with a wall on the %s side' % side, [fmt(r, f) for r in big if r[f] >= 80])
section('>=60% in a corner (two adjacent walled sides)', [fmt(r, 'corner_pct') for r in big if r['corner_pct'] >= 60])
section('>=70% free (no wall within 1 tile)', [fmt(r, 'free_pct') for r in big if r['free_pct'] >= 70])
floor_ids = [r for r in big if r['on_wall_tile_pct'] < 50]
section('>=60% with a wall on at least one side, N/W/S/E split (ids not sitting on wall tiles)',
        ['%s %s (n=%d): any side %.0f%%, N %.0f%% W %.0f%% S %.0f%% E %.0f%%, corner %.0f%%' % (
            r['id'], r['name'], r['n'], r['any_wall_side_pct'], r['wall_N_pct'], r['wall_W_pct'], r['wall_S_pct'], r['wall_E_pct'], r['corner_pct'])
         for r in floor_ids if r['any_wall_side_pct'] >= 60])
section('>=95% within 2 tiles of a wall (ids not sitting on wall tiles)',
        [fmt(r, 'wall_within_2_pct') for r in floor_ids if r['wall_within_2_pct'] >= 95])
section('>=90% on a tile that itself carries a wall piece (under-wall fill sprites)',
        [fmt(r, 'on_wall_tile_pct') for r in big if r['on_wall_tile_pct'] >= 90])
section('>=90% with a same-id orthogonal neighbour (always runs or masses)',
        [fmt(r, 'same_id_neighbour_pct') for r in big if r['same_id_neighbour_pct'] >= 90])
section('>=50% with 3+ same-id neighbours (massing)',
        [fmt(r, 'same_id_3plus_neighbours_pct') for r in big if r['same_id_3plus_neighbours_pct'] >= 50])
section('<=10% with a same-id neighbour (always placed singly)',
        [fmt(r, 'same_id_neighbour_pct') for r in big if r['same_id_neighbour_pct'] <= 10])
section('>=30% spaced two apart in a line', [fmt(r, 'spaced_two_apart_pct') for r in big if r['spaced_two_apart_pct'] >= 30])
section('>=50% stacked on another decoration',
        ['%s; top co-stacked: %s' % (fmt(r, 'stacked_pct'), ', '.join('%s %s x%d' % (c[0], c[2], c[1]) for c in r['top_costacked'][:3]))
         for r in big if r['stacked_pct'] >= 50])
section('>=30% within 1 tile of a door', [fmt(r, 'near_door_pct') for r in big if r['near_door_pct'] >= 30])
section('>=20% on a door approach tile', [fmt(r, 'door_approach_pct') for r in big if r['door_approach_pct'] >= 20])
section('>=95% interior (enclosed)', [fmt(r, 'interior_pct') for r in big if r['interior_pct'] >= 95])
section('<=5% interior (always exterior / open)', [fmt(r, 'interior_pct') for r in big if r['interior_pct'] <= 5])
section('100% on a floor tile and used in >=10 regions',
        [fmt(r, 'floor_pct') for r in big if r['floor_pct'] >= 99.5 and r['regions'] >= 10])
section('Doors: wall-run axis (n>=20)',
        ['%s %s (n=%d): walls both N&S %.0f%%, walls both W&E %.0f%%, another door adjacent %.0f%%' % (
            r['id'], r['name'], r['n'], r['walls_both_N_and_S_pct'], r['walls_both_W_and_E_pct'], r['near_door_pct'])
         for r in doors if r['n'] >= MIN])

lines += ['', '## Strong rules the numbers support (ids with n >= %d)' % MIN, ''] + rules
open(os.path.join(HERE, 'placement-stats.md'), 'w').write('\n'.join(lines) + '\n')

readme = ['# placement-stats', '',
          'Measured placement behaviour of every decoration id (and door closedId) across the six developer segments.',
          '', 'Files:', '- measure.py: parses the .mapproj files and writes placement-stats.json + wall-classes.json',
          '- report.py: writes placement-stats.md (definitions, top-60 table, door table, strong rules) and this README',
          '- placement-stats.json: {id: {...}} for decorations, {"door_<closedId>": {...}} for doors',
          '- wall-classes.json: wall id -> H / V / C / mass class used for adjacency',
          '', 'Run: `python3 -I measure.py && python3 -I report.py`', '', DEFS]
open(os.path.join(HERE, 'README.md'), 'w').write('\n'.join(readme) + '\n')
print('decorations', len(decos), 'doors', len(doors), 'placements', sum(r['n'] for r in decos), sum(r['n'] for r in doors))
