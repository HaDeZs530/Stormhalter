# placement-stats

Measured placement behaviour of every decoration id (and door closedId) across the six developer segments.

Files:
- measure.py: parses the .mapproj files and writes placement-stats.json + wall-classes.json
- report.py: writes placement-stats.md (definitions, top-60 table, door table, strong rules) and this README
- placement-stats.json: {id: {...}} for decorations, {"door_<closedId>": {...}} for doors
- wall-classes.json: wall id -> H / V / C / mass class used for adjacency

Run: `python3 -I measure.py && python3 -I report.py`

## Definitions

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

