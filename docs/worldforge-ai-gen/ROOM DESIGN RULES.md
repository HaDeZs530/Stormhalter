# Room design rules — Stormhalter / WorldForge (2026-10-29)

You (ChatGPT) design a room or a small area completely: its shape, walls, doors, floors and every decoration. Claude builds it with LOK Studio's wall engine (which picks the exact wall pieces, corner posts, door orientation and mass edges), adds your decorations, validates everything and renders it exactly as WorldForge draws it. You never choose individual wall pieces; you draw where walls go.

## 1. The grid
- Flat square grid, 55 px per tile. x = column (left to right), y = row (top to bottom), (0,0) is the top-left of your map.
- Sprites are 100 px cells drawn up and to the left of their tile, so tall things lean up-left over the tiles above them. The viewer looks from the south-east: north and west walls face the viewer, south and east walls are seen from behind.
- One tile holds one floor plus any number of decorations stacked on it.

## 2. Drawing the map
You draw the map as rows of text, one character per tile, all rows the same length:

    #   wall (a thin wall; the engine picks the horizontal, vertical or corner piece)
    M   solid mass (solid rock or granite; impassable, fills the space between rooms)
    D   door (must sit inside a straight run of # walls: # on both sides left-right, or both sides up-down)
    .   room floor
    ,   hall / corridor floor
    1 2 3   accent floors (a second, third, fourth floor type you choose in the style)
    (space)  nothing (void, black)

### Two ways to make a room
A. **Wall ring** (buildings, free-standing structures, rooms with void around them): draw a ring of `#` around the floor. Nothing outside it.

    ##########
    #........#
    #........#
    #........#
    ####D#####
        ,

B. **Carved from mass** (dungeons, caves, rooms inside rock): fill everything solid with `M` and carve the floor out of it. The engine dresses every edge where mass meets floor with the proper wall faces. **Do not draw `#` between `M` and floor**: that makes a double wall.

    MMMMMMMMMMMM
    MM........MM
    MM........MM
    MM....#####M
    MM....D...MM
    MM....#...MM
    MMMMM,,MMMMM

Inside a carved area, use `#` for thin partitions that split it into rooms, with `D` doors in them. An opening without a door is just floor running through the mass.

### Wall rules the engine enforces (so draw this way)
- Walls are one tile thick. Never draw two `#` side by side to make a thick wall; use `M` for thickness.
- Rooms that touch share one wall.
- The walkable inside of a ring is the tiles inside it. A room with an 8 x 4 interior is drawn 10 x 6 including its ring.
- Every `D` needs a straight wall on both sides; never a door on a corner, never two doors side by side unless you want a double-wide entrance (a run of `D`s in one wall is fine).
- The north-west corner of every wall ring always gets a corner post; the engine does this.
- Keep the tile in front of and behind every door clear of anything that blocks.

### Sizes that read well in this game
- Small rooms (store room, cell, shrine): 3 x 3 to 6 x 6 interior.
- Normal rooms: 6 x 6 to 10 x 10.
- Halls and boss rooms: 12 x 10 and up; up to about 50 x 50 for a whole area.
- Corridors: 1 to 3 tiles wide; 2 reads as a main route.
- Give big rooms something structural inside: columns (C-type pillars as decorations), a raised sanctuary on an accent floor, partitions with doors.

## 3. The style
Pick one wall set, one door set, one mass, a mass style and floors. Use these known-good sets (H = horizontal, V = vertical, C = corner post):

| Wall set | H | V | C | Fits |
|---|---|---|---|---|
| Temple stone | 29 | 30 | 34 | temple, castle, general dungeon |
| Egyptian | 258 | 259 | 262 | desert temple, tomb |
| Sandstone | 346 | 347 | 359 | desert, hellish dungeon |
| Dirty Marble | 139 | 140 | 143 | old palace, ruined temple, forge |
| Grey block (irr) | 1225 | 1227 | 1231 | castle, tower, keep |

| Door set | H | V |
|---|---|---|
| Temple | 66 | 67 |
| Dungeon (wood/iron) | 62 | 63 |
| Egyptian stone | 311 | 312 |
| Marble | 35 | 36 |

Mass: 447 Solid Granite (default), 31 Solid Rock (caves, dungeons), 446 Solid Dirt (mines, earth).
Mass style: `faces` (default; wall faces dress the mass edges), `ring` (the developers' style: a ring of wall behind the walls), `bare` (raw rock against floor, for caves).
### Two or more wall types in one design
Name extra styles and paint which tiles use them with a second map of the same size, `zones`: a letter marks a tile as that style, a space means the main style. A wall shared between two zones takes the style of the zone you mark it with. Example: a temple-stone hall with an Egyptian tomb chamber on the east side, whose shared wall stays temple stone:

    "styles": {"B": {"wall_H": 258, "wall_V": 259, "wall_C": 262, "door_H": 311, "door_V": 312, "room": 265}},
    "map":   ["#################", "#.......#.......#", "#.......D.......#", "#####D###########"],
    "zones": ["         BBBBBBBB", "         BBBBBBBB", "         BBBBBBBB", "         BBBBBBBB"]

Anything a zone style leaves out is taken from the main style.

Floors: any FloorComponent id from the piece book. Common: 1 Light, 5 Temple (ornate red/gold), 12 Dirt, 14 Wood, 176 Worn Marble, 265 Sandstone Slabs, 301 Rosey Viens Granite, 388 Blue Marble.

## 4. Decoration rules
Pieces come from the piece book: `Dropbox\WorldForge AI Gen\piece-book\2026-10-29 piece-book-draft.json` (every piece: id, component type, name, look, placement class, setting, tone, usage counts) and the contact sheets in `passes\pass-01 2026-10-29 sheet descriptions\to-GPT\` (open them with vision to see what a piece looks like). Use ids only from the book and always give the component type with the id.

How the developers place things (measured across 93 of their regions):
- **Wall-mounted pieces sit ON the wall tile**, not beside it: tapestries, hanging skeletons, shelves, banners, mirrors, wall doodads. (H) versions go on north-wall tiles, (V) versions on west-wall tiles. South and east walls are seen from behind: put nothing on them.
- **Floor furniture backs onto the north or west wall** (beds, cots, chests, shelves on the floor, thrones): put it on the floor tile just inside a north or west wall. Almost never against south or east walls.
- **Door approaches stay clear**: the tile in front of and behind a door has a decoration less than 7 percent of the time.
- **Altars usually stand on a special floor** (about three times in four): give an altar an accent floor under it or around it.
- **Trees mass**: forest trees are planted touching each other in large clusters, not dotted. Orchard trees are spaced two apart in rows.
- **Scatter stacks**: bones, skulls, blood, dust, rubble, webs, food and small items are layered on top of each other and on furniture tiles. Dense rooms stack two or three pieces per tile in places.
- **Density**: finished developer rooms are dense. Aim for 35 to 50 percent of floor tiles carrying something in a lived-in or ruined room; a formal hall can be lower but needs strong groups.
- **What blocks movement**: walls, mass, altars, counters (tables), obstructions, trees. Statics (most decorations, scatter, overlays) do not block. Keep at least one clear route from every door to every part of the room that matters.

How to compose (do it in this order and name each group):
1. Floor zones: the main floor, then accent floors for the sanctuary, paths, recesses, damage.
2. Focal group: the one thing the room is about, at the end of the main approach.
3. Furniture and secondary groups: what the room is used for.
4. Scatter and story: what happened here.
5. Lighting: braziers, torches, candelabra, fire, so the room reads at night.

## 5. What you send back
Save one file, `design.json`, in the `from-GPT\` folder you are told:

    {
     "name": "Crypt of the Ninth Seal",
     "style": {"wall_H": 29, "wall_V": 30, "wall_C": 34, "door_H": 62, "door_V": 63,
               "mass": 31, "mass_style": "faces", "room": 176, "hall": 12,
               "accent1": 5, "accent2": 0, "accent3": 0},
     "map": ["MMMMMMMM", "MM....MM", "..."],
     "groups": [{"id": "g1", "layer": 2, "purpose": "..."}],
     "decor": [{"p": "p01", "id": 113, "type": "AltarComponent", "x": 5, "y": 3, "group": "g1", "why": "..."}],
     "route_to": [5, 4],
     "reserve": [[4, 6, 5, 12]],
     "notes": "..."
    }

- `map`: the rows as above. Accent floors in the map use the ids in `style.accent1..3`.
- `decor`: x,y are map column and row. Decorations go on floor tiles, or on wall tiles only for wall-mounted pieces. Never on door tiles or mass.
- `route_to`: the tile every door must be able to reach (usually in front of the focal group).
- `reserve`: optional rectangles [x0, y0, x1, y1] that must stay free of anything that blocks (the main approach).
- A revision is a patch: `{"against_rev": N, "ops": [{"op":"add"|"remove"|"move"|"replace"|"floor", ...}]}` — never a full rewrite once Claude has built rev 1.

Claude answers with: `clean.png` (exactly as WorldForge draws it), `diag.png` (grid, coordinates, your p-ids on leader lines, doors, reserved areas, rejected pieces in red), `validation.json` (every placement and route checked), and `region.xml` (the file Tony imports).
