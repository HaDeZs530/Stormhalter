# WorldForge analysis and map-tool design
Date: 2026-10-28. Sources: jkachhad/stormhalter (cloned 2026-10-28), Tony's client archives (Data.bin, Kesmai.bin, Stormhalter.bin, UI.bin), the eldrathor-maps skill rules.

Companion files: `WorldForge Source Reference` (what the editor code does), `WorldForge Data Reference` (palette, terrain, Praetoseba patterns), `components-legend.json`, `terrain-index-merged.json`, `tools/xnb2png.py`, `tools/wf_render.py`.

## 1. What we have access to, and what it unlocks

| Source | What it holds | Status |
|---|---|---|
| GitHub repo | WorldForge source (C#), Components.xml palette (1,137 entries), Terrain-External.xml (882 terrains, ids 622–1599), loose PNG art for those, Praetoseba.mapproj example (9 regions, 21,000 tiles) | cloned |
| Data.bin | the core `Data/Terrain.xml` (550 terrains, ids 1–621 + 1001–1007: Solid Rock, Forest, Dirt, Water, every classic wall/door/altar/counter), Items.xml, Body.xml, Audio.xml | unzipped |
| Kesmai.bin | the classic `Bitmaps/004-01..09` sprite sheets as XNB | decoded to PNG |
| Stormhalter.bin | 865 XNB textures: all Tenser/Fireal/n099y/Zrikz/Azimuth art, segment maps, bodies, items | 734 textures decoded to PNG (131 non-texture entries are sounds and a shader) |
| UI.bin | client UI | not needed |

Result: all 1,432 terrain ids in the game now resolve to a real PNG sprite. The GitHub repo alone covers only 735 of the 1,207 ids the palette uses, and in Praetoseba 98 of 111 ids used are bin-only, so the archives were the missing half.

The XNB format here is MonoGame 3.8 with LZ4 compression, SurfaceFormat Color (RGBA8). `tools/xnb2png.py` decodes them all.

## 2. How WorldForge actually works (facts from the source)

Editor version 0.117.0. The current editor does not save `.mapproj`. It saves a folder project: `Segment.xml` (name + version only), `Regions/{id}.xml` (one `<region>` per file, the `7.xml` style you work in), plus `Locations.xml`, `Subregions.xml`, `Entities.xml`, `Spawns.xml`, `Treasures.xml`, `Brushes.xml`, `Components.xml`, `Templates.xml`, and a generated `{Name}.csproj`. `.mapproj` is import-only ("Convert Segment"). The `<region>` element is identical in both.

### The grid is flat, the sprites lean
- Tile unit = 55 px. Coordinates: x east, y south, negatives allowed.
- Every sprite is a 100x100 cell drawn with its top-left at `tileOrigin - (45,45)`, plus the sprite's `<offset>`, scaled `zoom / resolution` (`resolution="2"` = 200x200 cells drawn at half size).
- So every sprite overhangs its tile 45 px up and 45 px left. That is the whole "isometric" effect: a wall sprite drawn on tile (x,y) covers most of tiles (x-1,y), (x,y-1), (x-1,y-1). Every rule in the eldrathor-maps skill (walls lean up-left, hidden floor row/col south and east of mass, columns spaced two apart) is a consequence of this one number.
- Tiles are drawn x outer, y inner: a tile paints over its north neighbor and over every tile in the columns to its west.
- Inside a tile, layers are stable-sorted by the sprite's `order` attribute (0 floors, 1-3 ground details, 4 walls V, 5 walls H, 6/7 closed doors). Component order in the XML only breaks ties, which is why a floor written after a wall still renders under it.
- `<color r g b a/>` on a component multiplies the sprite (tint). `underpile` is parsed but never used by the editor. Region `height` is elevation in feet, server-only (fall distance), no render effect.

### Components
Type = exact C# class name. Floor `ground[,movementCost]` (cost omitted when 1); Wall `wall,destroyed,ruins[,indestructible]` (all three ids mandatory, the loader throws on a missing one); Door `openId,closedId,secretId,destroyedId[,isSecret,isOpen]`; Water `ground,depth,movementCost`; Tree `tree,canGrow` (canGrow mandatory); Static/Lockers/Trash `static`; Obstruction `obstruction,blockVision`; Staircase/Shaft/Rope/Sky `teleporterId,destinationX,destinationY[,destinationRegion]`. Darkness/Fire/Whirlwind use hard-coded terrain ids (7/135/132). Full table with defaults is in the Source Reference. The id is just the sprite; the type is the behaviour. Praetoseba uses Static id 105 as a floor 820 times.

### Pathing (server code)
Wall blocks unless destroyed; closed door interrupts (secret door blocks like a wall); obstruction rejects; water interrupts unless flying/water-walking, cost `min(depth, movementCost)`; ruins cost 3; counter/altar block. Destructible walls should carry a floor beneath them; indestructible walls need not.

### What does NOT exist
No procedural generation. `GenerateRegionWindow` is a stub (the importer it needs was never written). Brushes are weighted random entries but nothing bakes them and the map view only shows the first entry. Templates are single-tile component stacks. So anything that generates layout has to live outside WorldForge; the editor is only the viewer/hand-editor.

## 3. What Praetoseba teaches (the dev's own map)
- Built wall = `Floor + Wall` on one tile (1,624 tiles). Void fill = Wall-only Solid Rock 31 (3,552 tiles). Corner = `Floor + Wall(H or V) + Wall(C)` (269 tiles), both indestructible.
- A door is the gap in the run: `Floor + Door`, no WallComponent (51 of 55 doors). (V) door has walls N and S; (H) door has walls E and W.
- Empty `<tile x y/>` is written for the whole bounding box. Floor first in ~97% of multi-component tiles.
- Spawns, entities (C# script bodies in three CDATA blocks), locations and treasures are separate sections; a layout tool can ignore them entirely and still produce a region the editor loads.

## 4. Proposed tool: "Forge Studio" (working name)

Goal: describe a space in parameters or words, get back (a) an HTML/PNG preview drawn exactly as WorldForge would draw it, with the real sprites, and (b) a `Regions/N.xml` you can drop into the project or replicate by hand.

Three layers, each usable on its own:

1. **Renderer** (built, prototype `wf_render.py`): region XML + merged terrain index + decoded art → image. Reproduces the editor's 55/45/order rules; Praetoseba regions 1 and 3 render correctly. Next step is the HTML version: one self-contained page with a sprite atlas, pan/zoom, coordinate grid, hover-to-inspect per tile, and a layer toggle (floors / walls / decoration / red structure view). This is the "see it before WorldForge" piece and the review surface for everything else.

2. **Layout engine** (exists as Stage A in `Claude Worldforge Testing\Generator\stage_a.py`): roles grid (floor-visible / floor-hidden / wall-NS / wall-EW / corner / structural / door) with the partition-first shell rules, ends rule, pierced-run rule. I would port it in unchanged as the structural core rather than re-derive it; the source analysis confirms its assumptions (45 px overhang, x-outer draw order).

3. **Palette and decoration layer** (new): a named palette block maps roles to real ids (`floor-visible: 265, wall-ns: 347/339/0, door-ns: 312/308/299/310 ...`), pulled from the legend by family name, so a "sandstone temple" and a "dirty marble crypt" are the same layout with a different block. Decoration uses the scatter/clump recipes from the skill plus Luxx's own caveat: placement constraints per sprite class (altars against the north wall, pews in rows two apart, braziers flanking doors, no statics on wall tiles).

Input modes, in order of build: parameter form (room list with sizes, connections, door sides, palette) → sketch intake (the markup-loop rule, diff not classify) → text description mapped onto the parameter form.

Output: `N.xml` with UTF-8 BOM, CRLF, 2-space indent, half-open bounds, full child sets on every wall, floor first, written as raw text not ElementTree.

## 5. Decisions needed before building
1. Scope of the first build: HTML renderer alone first (so every later step has a review surface), or renderer + parameter-form generator together.
2. Where the decoded art lives: 774 PNGs (~60 MB). Proposal: `OneDrive\Stormhalter Worlds\Claude Stuff\Stormhalter Maps\art\` beside the existing reference folder, and the tool reads from there. The sprite atlas baked into the HTML would hold only the ids a region uses.
3. Whether to port `stage_a.py` as-is or re-express the layout rules in the new tool. Port is my recommendation.
4. Fork: GitHub needs your account; click Fork on jkachhad/Stormhalter and I'll push the analysis docs and tools there as a `tools/` folder if you want them versioned beside the source.
