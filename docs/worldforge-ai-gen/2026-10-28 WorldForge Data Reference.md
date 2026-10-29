# WorldForge / Stormhalter data reference for a .mapproj generator + HTML renderer

Generated 2026-10-29 from the `jkachhad/stormhalter` repo (read-only analysis, Python `xml.etree`).
Source files:

- `Content/WorldForge/Components.xml` — the component palette (what WorldForge offers in its tree; the legend for generated tiles)
- `Content/Data/Terrain-External.xml` — terrain id → sprite definitions for the open-source art
- `Documentation/Content/AddingArt.md` — art conventions
- `Segments/Praetoseba.mapproj` — real example segment
- `Source/Kesmai.WorldForge/**` — the editor source (used to confirm serialization and render rules)

Companion machine-readable files (same folder as this document):

- `components-legend.json` — list of `{type, category, name, props{}}` for all 1,137 palette entries
- `terrain-index.json` — `{id: {action, cost, average?, label?, sprites:[{order, underpile?, resolution?, texture, source, offset?, frames?, palette?}]}}` for all 882 External terrains (`label` is the XML comment next to the terrain, present for 872 of 882)
- `id-crosscheck.json` — which palette ids resolve to External terrains, which are bin-only, which External ids no palette entry uses
- `map-used-ids.json` — every id value Praetoseba uses, per tag

---

## 0. The ten things a generator must know (read this first)

1. **A tile is a list of components; every component is just a `type` plus a handful of terrain ids.** The ids are global sprite ids (one number space shared by floors, walls, doors, statics...). The component type says *what the tile does* (blocks, teleports, burns); the ids say *what it looks like*.
2. **Only 735 of the 1,207 ids in Components.xml have a sprite in the repo.** The other 472 (all ids below 622, plus 1001–1007) are defined only in the closed client's `Data/Terrain.xml` inside `Stormhalter.bin`. That includes the most used ids in the game (Solid Rock wall 31, Forest 23, Dirt 12, Water 22, Dungeon/Town/Temple walls and doors, every counter, altar, egress, and all secretIds). **An HTML renderer using only repo PNGs can draw the Tenser/n099y/Fireal-era art (ids 622–1599) but must substitute placeholders for anything under 622.** In Praetoseba, 98 of the 111 distinct ids used are bin-only.
3. **Cell size is 100×100 px for the whole legacy set.** The editor draws each tile's sprites into a 100×100 box whose top-left is at `tileOrigin − (45,45)`, with the logical tile grid at 55 px per unit (`UnitSize = 55` in `ApplicationPresenter.cs`). So sprites overhang their tile by 45 px up/left; the `offset` element shifts the sprite further (in px at 1× zoom). `resolution="2"` sprites (n099y set, ids 1500–1599, and 1412) are 200×200 cells drawn at half scale, i.e. still 100×100 on screen.
4. **Draw order inside a tile = the `order` attribute of the terrain's sprite (0 floors → 7 closed H doors), stable-sorted.** Component order in the `<tile>` element only breaks ties. Floor first in the XML is the convention, but not required.
5. **Walls are per-tile, not per-edge.** A wall tile is a tile holding a `WallComponent`; "(H)" sprites are the face seen on an east-west run, "(V)" on a north-south run, "(C)" is a corner post. Praetoseba's wall runs are one tile thick and nearly always carry a floor under the wall (`FloorComponent` + `WallComponent`, 1,624 tiles) except for bulk "Solid Rock" (id 31) fill which is wall-only (3,552 tiles).
6. **Doors sit in the gap of a wall run, on their own tile, with a floor under them and no WallComponent.** 51 of 55 doors are `Floor + Door`. The door's H/V variant matches the run it plugs: the typical neighbor pattern is wall N/S + floor E/W for a (V) door and the reverse for (H).
7. **Region coordinates can be negative** (Praetoseba Surface spans x −56..127, y −3..86). WorldForge writes a `<bounds left top right bottom>` element on save in the current source, but the committed Praetoseba file has none, and loaders tolerate both. Tiles are written row-major (y outer, x inner), and empty tiles are written as `<tile x y />`.
8. **Movement cost is omitted when it equals 1** (`FloorComponent` serializer). Water always writes `movementCost` (3). `indestructible` is written only when true. `color` is written only when not white: `<color r g b a/>` as attributes (the palette file has a few empty `<color>` placeholders, which the loader will reject with a cast error — do not copy them).
9. **The palette's component type is not binding on ids.** Praetoseba uses id 105 (palette: StaticComponent "Tall Grass") as a `FloorComponent` ground 820 times, and id 313 (palette: ObstructionComponent "Sandstone Pillar") as a `WallComponent` wall. The id just picks the sprite; the type picks the behavior. A generator may do the same, but a renderer must not assume an id's type from the palette.
10. **Segment file layout:** `<segment name version>` → `<script name="Internal">` → `<regions>` → `<locations>` → `<subregions>` → `<entities>` → `<spawns>` → `<treasures>` → `<hoards>` (and the loader also accepts `<brushes>` and `<templates>`, absent in Praetoseba). Praetoseba is version `0.102.2.0`.

---

## 1. Components.xml — palette inventory

File: `Content/WorldForge/Components.xml`, root `<data>`, 1,137 `<component type="..." name="..." category="...">` children. Each child element is a property. There are 31 component types in 18 categories.

### 1.1 Count per type

| type | count | categories used |
|---|---|---|
| StaticComponent | 357 | Decorations 225, Wall Doodads (H) 53, Vegetation 51, lighting and shade 25, Grove 2, Misc. 1 |
| WallComponent | 233 | Structural 204, Customizable 27, Grove 2 |
| RuinsComponent | 158 | Ruins |
| FloorComponent | 103 | Floors 98, Grove 3, Customizable 2 |
| StaircaseComponent | 68 | Stairs |
| DoorComponent | 49 | Doors |
| ObstructionComponent | 31 | Obstructions |
| RopeComponent | 30 | Ropes |
| TreeComponent | 29 | Vegetation |
| EgressComponent | 12 | Teleport |
| CounterComponent | 12 | Counters and Altars |
| AltarComponent | 12 | Counters and Altars |
| WaterComponent | 11 | Water |
| ShaftComponent | 7 | Stairs |
| IceComponent | 5 | Floors |
| SkyComponent | 4 | Teleport |
| LockersComponent | 2 | Misc. |
| PoisonedWaterComponent, HiddenTeleporterComponent, TrashComponent | 1 each | Water / Teleport / Misc. |
| WhirlwindTrap, PoisonCloudTrap, BonfireTrap, FirestormTrap, ConcussionTrap, LightningBoltTrap, BlindTrap, FearTrap, StunTrap, DamageTrap, ActionTrap | 1 each | Traps |

Categories (count): Decorations 225, Structural 204, Ruins 158, Floors 103, Vegetation 80, Stairs 75, Wall Doodads (H) 53, Doors 49, Obstructions 31, Ropes 30, Customizable 29, lighting and shade 25, Counters and Altars 24, Teleport 17, Water 12, Traps 11, Grove 7, Misc. 4. (`category` may be a `/`-path in the loader, but the file uses flat names.)

### 1.2 Child elements per type (schema), with example values

| type | children seen | notes / examples |
|---|---|---|
| FloorComponent | `ground` (100 distinct), `movementCost` {0,1,2}, `color` (empty placeholder, 1×) | `<ground>23</ground><movementCost>1</movementCost>`; cost 2 = Sand/Reef, cost 0 appears on the two Customizable entries |
| IceComponent | `ground` {17,20,992,1349,1357}, `movementCost` 1 | slippery floors |
| WaterComponent | `ground` (10), `depth` 3, `movementCost` 3, `color` | `depth` is editor-only in the palette; the map writes `ground` + `movementCost` only |
| PoisonedWaterComponent | `ground` 180, `movementCost` 3, `color` | |
| WallComponent | `wall` (231), `destroyed` (115, often 0), `ruins` (60, often 0), `indestructible` {true,false}, `color` | map serializer always writes wall/destroyed/ruins, writes `indestructible` only if true |
| RuinsComponent | `ruins` (152) | rubble-only tile (no wall) |
| DoorComponent | `openId`, `closedId`, `destroyedId`, `secretId`, `isSecret` false, `isOpen` false | in maps `isSecret` written only when true; `indestructible` also accepted |
| StaircaseComponent | `teleporterId` (68), `descends` {true,false}, `destinationX/Y/Region` 0 | `teleporterId` is the sprite id; destination is filled in per placement |
| ShaftComponent | `teleporterId` (7), `descends` true, destination 0s | holes / trapdoors; serializer also knows `slipChance` |
| SkyComponent | `teleporterId` {9,1016,1017,1330}, destination 0s | "Air"/clouds: fall-through tiles (Praetoseba uses 9 "Air" 1,257×) |
| EgressComponent | `egress` (11), `destinationSegment` 1–5 | exits between segments |
| HiddenTeleporterComponent | destination 0s | map adds `<lightphases select="all"/>`, `<moonphases>`, `<professions>`, `<alignments>`, optional `message`, `level`, `allowNPC` |
| RopeComponent | `teleporterId` (30), `isSecret` false, destination 0s | serializer also knows `slipChance` |
| StaticComponent | `static` (357), `color` | pure decoration, no behavior |
| TreeComponent | `tree` (29), `canGrow` {true,false} | |
| ObstructionComponent | `obstruction` (31), `blockVision` {true,false} | impassable thing on a floor |
| CounterComponent | `counter` (12) | shop counters |
| AltarComponent | `altar` (12) | |
| LockersComponent | `static` {119,120} | |
| TrashComponent | `static` 88 | |
| *Trap types | `skill` 3, `direction` 5 (Whirlwind/PoisonCloud), `damage` 3 (DamageTrap) | serializer also knows `cooldown`, `trapCreatures`, `trapPlayer`, `interruptMovement` |

Component types that exist in the editor source but are not in the palette (they appear in maps): `Darkness` and `Fire` (child `allowDispel` true/false — Praetoseba has 866 Darkness and 36 Fire tiles), `Web`, `Whirlwind`, `ItemTeleporter` (`destinationX/Y`, phase/profession/alignment selectors, `type`, `fail`), `SpeechTeleporter` (`teleporterId`, `phrase`), `ItemActionComponent`. Note the magical ones serialize with the bare class name (`type="Darkness"`, not `DarknessComponent`).

Base (all components): optional `<color r="" g="" b="" a=""/>` (tint, omitted when white) and optional `<comment>` text, plus the `name` attribute is accepted on load.

### 1.3 Floors (FloorComponent + IceComponent) — name → ground → movementCost

See Appendix A for the full table of all 103 + 5 entries. Highlights for a generator: the "classic" floors are bin-only ids 1–24 (Light 1, Tile 2, Hardwood H/V 3/4, Temple 5, Burnt Stone 6, Lava 10, Dirt 12, Short Grass 13, Wood H/V 14/15, Beaten Path 16, Snow 17 (Ice type), Sand 18 cost 2, Ice 20, Bog 21, Forest 23, Honeycomb Flagstone 24) and 89–91 (Jungle), 115/116 (bridges), 175–196, 239, 252, 264/265/277 (Gravel Road / Sandstone Slabs / Sandstone Cobblestones), 289, 301, 325, 341, 369, 375, 387, 388, 393, 406, 419, 445, 492, 493, 602–621 ([Zrikz]/[Fireal] sets). Floors that *do* have repo sprites: Tenser rock/light-stone/cave floors in 661–696 and 1258–1329 (dungeondreary), palace 1116–1187, swamp 1090–1115, mines 1213–1224, glacial/icy 1348–1363, snow 1409–1411, and the n099y grass/dirt/water set 1500–1579 (not in the palette at all — see §4).

### 1.4 Walls — name → wall / destroyed / ruins

233 entries; naming is `<Style> (H)`, `(V)`, `(C)`. The classic sets (bin-only): Dungeon 25/26/32, Town 27/28/33, Temple 29/30/34, Solid Rock 31 (the universal "void" fill), Dirty Marble 139–144, Heavy Logs 145–150, Dragon 151–156, Cave 157–162 (ruins 170), Thicket 223–228, Egyptian 258–262 (destroyed 260/261), Egyptian Osiris 285–288, Dirt 333/334/355, Granite 335/336/357, Sandstone 346/347/359 (destroyed 338/339), Red Shoji 362–367, Undead 381/382/407, Blue Marble 383/384/409, Mines 413–418, Dragon(2) 428–444, Highmountain 459–465, Pagoda 470–485. Repo-sprited wall sets: Tenser light stone / rock / cave (661–696), BigCity (699–1257 range), dungeondreary purple/green/etc. (1258–1329), palace (1116–1187), newdungeonwalls 1225–1232, redbrickwalls 1340–1347, nidavellir 1364–1381, swamp, mines, tents. `ruins` ids 44/45/46/170/380/398/432/465/669 are the shared rubble sprites. Full table in Appendix A.

### 1.5 Doors — 49 entries

Each door is 4 ids: `closedId`, `openId`, `destroyedId`, `secretId`. Classic (bin-only): Marble 35/47/37 (V 36/48/49), Dungeon 62/74/80 (V 63/75/81), Town 64/76/82 (V 65/77/83), Temple 66/78/84 (V 67/79/85), Runic 229–234, Egyptian 311/307/309 (V 312/308/310), Red Shoji 378/391/404, Jail 420/433/435, Steel 453/455/457, Dirty Marble 494–499, Dragon 504–509, TrapCellar 972/973 (External). Repo-sprited: the nine Tenser door sheets 1040–1087 and 1382–1387 (each sheet = 6 cells: closed H, open H, ruin H, closed V, open V, ruin V, in that order left→right), plus BigCity windows/gates 858–861, 941–944, 948–951, 961–964. All Tenser doors reuse secretId 152 (Dragon V wall) as their "looks like a wall" state; classic doors use their matching wall id. Full table in Appendix A.

### 1.6 Decorations and the rest — name → id

Full lists in Appendix A: StaticComponent (357; Decorations / Wall Doodads (H) / Vegetation / lighting and shade / Grove / Misc.), TreeComponent (29), ObstructionComponent (31), CounterComponent (12), AltarComponent (12), RuinsComponent (158), StaircaseComponent (68 — eight Tenser stair sheets of 8 cells: down S/E/W/N then up N/W/E/S), ShaftComponent (7), SkyComponent (4), EgressComponent (12), RopeComponent (30), LockersComponent (2), TrashComponent (1), traps (11).

---

## 2. Terrain-External.xml — schema and inventory

File: `Content/Data/Terrain-External.xml`, root `<data>`, **882 `<terrain>` elements**, ids **622–998, 1008–1412, 1500–1599** (three contiguous runs; no duplicates). Ids 1–621 and 999–1007 are not here: they are in the client's internal `Data/Terrain.xml` (in `Stormhalter.bin`), which `TerrainManager.cs` loads first; External entries override internal ones by id.

### 2.1 Schema (from the header comment + `Editor/Terrain.cs` + `Game/GameSprite.cs`)

```xml
<terrain id="N" action="A" [cost="C"] [lom="..."] [tif="a,b,c"]>
  <sprite order="0..7" [underpile="true|false"] [resolution="1|2"]>
    <texture>Artist\Folder\sheet</texture>        <!-- path under Content/, no extension, case-sensitive, \ or / -->
    <source>(x,y,w,h)</source>                    <!-- rect in the sheet -->
    [<offset>(dx,dy)</offset>]                    <!-- px shift at 1x zoom -->
    [<frames step="ms" keys="0-19">               <!-- animation; source then spans the whole strip -->
       <frame>(x,y,w,h)</frame>...</frames>]
    [<palette step="ms" keys="0-7"><color source="(r,g,b,a)" [target="(r,g,b,a)"]/>...</palette>]
  </sprite>
  [<average>(r,g,b,a)</average>]                  <!-- heat-map color; 773 of 882 have it -->
</terrain>
```

- `action`: 0 none (422), 1 climb down (16), 2 climb up (13), 3 close door (27), 4 open door (43), 5 stairs up (53), 6 stairs down (53), 13 search (254 — walls use this), 31 open locker, 33 look, 37 portal (1). Values seen here: {0,1,2,3,4,5,6,13,37}.
- `cost`: pathing cost; absent on 767, `1` on 80, `0` on 22, `6` on 13 (water). The tile takes the max over its terrains.
- `order` seen: 0 (203), 1 (200), 2 (12), 3 (49), 4 (206), 5 (184), 6 (12), 7 (16). Meaning per header: 0 floors/water, 1 open H doors + decorations, 2 open V doors, 3 rubble/ruins/bridges/effects, 4 V walls/V wall decor/corner posts/counters/obstructions, 5 H walls/H wall decor, 6 closed V doors, 7 closed H doors.
- `underpile`: whether the sprite draws under dropped items. In the editor anything with `order <= 3` is treated as underpile regardless.
- A sprite has either `frames` or `palette`, never both. 37 terrains are animated (water waves, fire, braziers, portal, traps). Frame `keys` like `0-19` or `0-5,5-0`.
- Every terrain in this file has exactly **one** `<sprite>` (multi-sprite is allowed by the schema but unused).
- `offset` present on 70 sprites; common values `(0,0)`, `(0,9)` (tent walls), `(2,1)`, `(-10,-10)` (110×110 cells), `(0,-40)`/`(-40,0)` (torchdecal/doorjam alignment).
- `resolution="2"` on 101 sprites (ids 1412 and 1500–1599): the source cell is 200×200 and is drawn at 0.5 scale.

### 2.2 Cell size convention

**100×100 is the standard cell.** 773 of 882 sprites use a 100×100 source (or 100×100 frames). The others: 101 are 200×200 at resolution 2 (equivalent to 100×100), 4 are 110×110 with offset (-10,-10) (summoning circles, firebowl), and a handful are odd sizes (lectern 55×55, spider spit 45×45, portal 60×60 strip, traps-concept 500×500). Sheets are laid out on a 100 px grid, e.g. `BigCity.png` 900×900 = 9×9 cells, door sheets 600×100 = 6 cells, stair sheets 800×100 = 8 cells, `terrain001.png` 2000×2200 = 10×11 cells of 200 px.

On screen (WorldForge, `WorldGraphicsScreen.cs`): tile grid unit = 55 px; a tile's 100×100 sprite box is placed at `(tileX*55 − 45, tileY*55 − 45)` + `offset`, scaled by `zoom / resolution`. So the sprite's bottom-right 55×55 is the tile proper and the top/left 45 px overhang gives the isometric "height". Walls drawn later (higher order) cover the floor of the tile above/left. A faithful HTML renderer should reproduce exactly this: draw tiles in y-then-x order, each tile's sprites sorted by `order`, at those coordinates.

### 2.3 Texture sheets referenced (110 paths), existence and pixel sizes

All paths resolve under `Content/` after `\`→`/` and `.png` appended. **109 of 110 exist; 1 is missing: `Bitmaps\004-05` (terrain 1412 "climbable pole") — this lives in the closed client archive.** Case matches in every existing path. Sizes from PIL (all RGBA except `traps/fire4-Sheet.png` which is palettized):

| sheet (Content/…) | px | terrain ids |
|---|---|---|
| Tenser/Terrain/BigCity.png | 900×900 | 81 ids in 699–1257 |
| Tenser/Terrain/dungeondreary.png | 800×900 | 1258–1329 (72) |
| Tenser/Terrain/palacetileset.png | 800×900 | 1116–1187 (72) |
| Tenser/Terrain/rocktiles.png | 900×400 | 661–696 (36) |
| Tenser/Terrain/tents.png | 600×600 | 731–761 (31) |
| Tenser/Terrain/swamp_tileset.png | 600×600 | 1090–1115 (26) |
| Tenser/Terrain/millwork.png | 600×600 | 644–658, 707–730 (30) |
| Tenser/Terrain/ropeandvine.png | 600×300 | 1388–1408 (21) |
| Tenser/Terrain/market.png | 500×500 | 873–892 (20) |
| Tenser/Terrain/furniture.png | 400×500 | 1193–1212 (20) |
| Tenser/Terrain/nidavellir.png | 900×200 | 1364–1381 (18) |
| Tenser/Terrain/deciduoustree-expansion.png | 500×300 | 893–906 (14) |
| Tenser/Terrain/Sewers.png | 500×300 | 628–639 (12) |
| Tenser/Terrain/mines.png | 600×200 | 1213–1224 (12) |
| Tenser/Terrain/Pottery.png | 300×300 | 649–657 (9) |
| Tenser/Terrain/banners.png, shielddeco.png | 300×300 | 775–782, 767–774 |
| Tenser/Terrain/newdungeonwalls.png | 600×200 | 1225–1232 |
| Tenser/Terrain/redbrickwalls.png, volcanic.png, ice.png, glacial.png, icycavetiles.png, ladders.png | 800×100 | 1340–1347, 1008–1015, 991–998, 1356–1363, 1348–1355, 983–990 |
| Tenser/Terrain/{bwmarble,bluemarble,roughwood,finewood,finestairscarpet,ricketywood,decrepitwood,snowicey,bloodied,mossy,grassy,flower}stairs.png | 800×100 each | 785–856, 907–930 (8 each) |
| Tenser/Terrain/Doors/{4paneldoors,bluesteeldoor,peepholedoor,plaindoors,steeldoornoise,steeldoorsrustpatina,thinslatdoors,wideslatdoors,thinchamberdoor}.png | 600×100 each | 1040–1087, 1382–1387 |
| Tenser/Terrain/Trees.png | 200×200 | 624–627 |
| Tenser/Terrain/Water-Wave-Horizontal.png, Water-Wave-Vertical.png, EastWave-Sheet.png, SouthWave-Sheet.png | 2000×100 (20 frames) | 622, 623, 1018, 1019 |
| Tenser/Terrain/fire-Sheet.png, stormcloud-Sheet.png | 500×100 | 766, 1017 |
| Tenser/Terrain/firebowl-Sheet.png 440×110, firebowl-Sheet_ns.png 400×100 | | 975, 1037 |
| Tenser/Terrain/fireplace_animH/V.png, candelabra-DARKSheet.png, candelabraLight.png | 300×100 | 697, 698, 982, 1025 |
| Tenser/Terrain/torchdecals.png 1100×100, torches.png 600×100, wall brazier*.png / wallbrazier*_ns.png 600×100 | | 931–1039 (7), 1029–1030, 976–981, 1031–1036 |
| Tenser/Terrain/portal-Sheet.png | 3900×60 | 1330 |
| Tenser/Terrain/traps/Ltest5-Sheet.png 2100×100, fire4-Sheet.png 2100×100, electric_hex-Sheet.png 1100×100, traps-concept.png 500×500 | | 1334, 1333, 1332, 1335–1339 |
| Tenser/Terrain/summoningcircle{1,2,3}.png | 110×110 | 1190, 1189, 1188 |
| Tenser/Terrain/snowdriftedges.png, kesbrokenpillars.png, logfortification.png | 200×100 | 659–660, 783–784, 1088–1089 |
| Tenser/Terrain/lectern.png, lecternv.png | 55×55 | 1191, 1192 |
| Tenser/Terrain/spiderspit.png | 45×45 | 1331 |
| 25 single-cell 100×100 PNGs (BrokenPortalPillar[-2], BrokenStalagmite[-2], bookshelf[2], darkcloud, dirthole, drywell, grassyhole, sandhole, tunnelentrance, trapdoor, trapdooropen, flatstonebridge[2], icyrockfloor, icysnowfloor, snowfloor, snowdrift[2], spiralstaircase_blank, rubble_{bluemarble,egyptian,pagoda,sandstone,thicket}) | 100×100 | 640–643, 764–765, 1016, 969, 968, 970, 974, 971, 972, 973, 1027, 1028, 1409, 1410, 1411, 762, 763, 1026, 1020–1024 |
| **n099y/terrain/terrain001.png** | **2000×2200** (10×11 cells of 200) | **1500–1599 (100 ids; res 2)** |
| Bitmaps/004-05 | **MISSING** | 1412 |

Unused files in `Content/Tenser/Terrain/`: `TilesColumns.png`, `doorjams.png`, `rubble_dragonblue.png`, `tunnelentrancegrass.png` (not referenced by any terrain).

### 2.4 Id ranges by content set (External)

| ids | set / sheet | what |
|---|---|---|
| 622–623, 1018–1019 | water waves | animated water (cost 6) |
| 624–627 | Trees.png | 4 trees |
| 628–639 | Sewers | sewer floor/walls/drains |
| 640–643 | broken pillar / stalagmite | obstruction ruins |
| 644–658, 707–730 | millwork | wainscoting, mouldings, trim, web/skeleton decor |
| 649–657 | Pottery | vases |
| 661–696 | rocktiles | light stone / rock / cave / etc. wall-floor-column-ruin sets (4 styles × 9) |
| 697–698 | fireplaces (anim) | |
| 699–1257 (81 ids, scattered) | BigCity | city walls, windows, gates, roofs, signs |
| 731–761 | tents | tent walls/flaps (offset 0,9) |
| 762–763, 1409–1411 | snow | drifts, snow/ice floors |
| 764–765 | bookshelves | |
| 766, 975, 982, 1025, 1037 | fire, braziers, candelabra | animated light |
| 767–782 | shields, banners | wall doodads (H) |
| 783–784 | kesbrokenpillars | |
| 785–856, 907–930 | stairs | 12 styles × 8 directions |
| 873–892 | market | stalls, goods |
| 893–906 | deciduous trees | |
| 931–1039 (7) , 1029–1036, 976–981 | torches, braziers | wall lighting |
| 968–974 | holes, well, tunnel entrance, trapdoor | shaft sprites |
| 983–990 | ladders | 8 directions |
| 991–998, 1008–1015, 1348–1363 | ice, volcanic, icycave, glacial | floor/wall strips |
| 1016–1017 | clouds | sky sprites |
| 1020–1024 | rubble_* | ruins |
| 1026–1028 | spiral stair, flat stone bridges | |
| 1040–1087, 1382–1387 | door sheets | 9 door styles × (closed H, open H, ruin H, closed V, open V, ruin V) |
| 1088–1089 | log fortification | |
| 1090–1115 | swamp | |
| 1116–1187 | palace | 72-cell tileset |
| 1188–1190 | summoning circles | 110×110 |
| 1191–1192 | lecterns | |
| 1193–1212 | furniture | |
| 1213–1224 | mines | |
| 1225–1232 | newdungeonwalls | |
| 1258–1329 | dungeondreary | 9 colour-themed dungeon wall/floor/column/ruin/niche sets (8 cells each) |
| 1330 | portal (anim 65 frames) | |
| 1331–1339 | traps | |
| 1340–1347 | redbrickwalls | |
| 1364–1381 | nidavellir | dwarven set |
| 1388–1408 | ropeandvine | ropes, vines |
| 1412 | climbable pole | missing texture |
| 1500–1579 | n099y floors | grass000–019 (1500–1519), dirt000–019 (1520–1539), water000–039 (1540–1579); all order 0, underpile, cost 1 |
| 1580–1599 | n099y decorations | tree000–019; order 1 |

---

## 3. Praetoseba.mapproj — structure of a real segment

Root: `<segment name="Praetoseba" version="0.102.2.0">`. Top-level children in order: `script`, `regions`, `locations`, `subregions`, `entities`, `spawns`, `treasures`, `hoards`. 3.2 MB, 21,000 `<tile>` elements, 18,739 components.

### 3.1 Regions

| id | name | height | tiles written | x range | y range |
|---|---|---|---|---|---|
| 3 | hells gate | 30 | 2,438 | 0–45 | 0–52 |
| 1 | temple | 10 | 868 | 0–30 | 0–27 |
| 129 | karma | 0 | 323 | 0–16 | 0–18 |
| 10 | tower top | 0 | 196 | 0–13 | 0–13 |
| 0 | Praetoseba Surface | 0 | 12,000 | −56–127 | −3–86 |
| 2 | upper temple | 0 | 570 | −5–25 | −7–18 |
| 5 | tower lvl2 | 0 | 196 | 0–13 | 0–13 |
| 255 | sekhmet | 0 | 97 | 0–9 | 0–9 |
| 251 | lower UW | 0 | 4,312 | 0–97 | 0–43 |

Region element = `<id>`, `<name>`, `<height>` (elevation), then `<tile x y>`s. The current serializer can also emit `experienceMultiplier`, `healthMultiplier`, `level`, `showTreasureInWater` (only when non-default) and a `<bounds left top right bottom/>`. Region ids are arbitrary ints and need not be contiguous; ids are not in sorted order in the file. 7,543 tiles are written empty (`<tile x="23" y="0" />`), i.e. the writer emits the whole bounding rectangle.

### 3.2 Global component counts

FloorComponent 7,128 · WallComponent 6,085 · SkyComponent 1,257 · WaterComponent 1,147 · ObstructionComponent 969 · Darkness 866 · TreeComponent 633 · StaticComponent 394 · IceComponent 69 · DoorComponent 55 · AltarComponent 49 · Fire 36 · StaircaseComponent 20 · RopeComponent 17 · HiddenTeleporterComponent 8 · TrashComponent 4 · EgressComponent 1 · ItemTeleporter 1.

Components per tile: 0 → 7,543; 1 → 8,771; 2 → 4,122; 3 → 533; 4 → 30; 5 → 1.

Child elements actually written per type in the map: Wall `wall,destroyed,ruins[,indestructible]` (2,594 indestructible); Floor `ground[,movementCost]` (movementCost on 1,121, only when ≠1); Water `ground,movementCost`; Obstruction `obstruction[,blockVision]`; Static `static`; Door `openId,closedId,secretId,destroyedId[,isSecret][,indestructible]`; Tree `tree,canGrow`; Sky/Staircase/Rope `teleporterId[,destinationX,destinationY,destinationRegion]` (destinationRegion omitted when 0 = same region); HiddenTeleporter/ItemTeleporter `destinationX,destinationY[,destinationRegion],lightphases,moonphases,professions,alignments[,fail]` with `<lightphases select="all"/>` style selectors; Darkness/Fire `allowDispel`; Egress `egress,destinationSegment`.

### 3.3 Top 30 component combos (type + key ids), with palette names

| n | component | palette name |
|---|---|---|
| 3,527 | Wall 31/0/0 | Solid Rock (bin) — the void fill |
| 1,771 | Floor 23 | Forest |
| 1,257 | Sky teleporterId 9 | Air |
| 1,245 | Floor 12 | Dirt |
| 1,196 | Floor 265 | Sandstone Slabs |
| 1,147 | Water 22 | Water |
| 838 | Darkness allowDispel=true | — |
| 820 | Floor 105 | (palette: Static "Tall Grass" — used as a floor) |
| 769 | Obstruction 266 | Heavy Oak |
| 661 | Wall 346/338/0 | Sandstone (H) |
| 633 | Tree 98 | Large Tree |
| 493 | Wall 347/339/0 | Sandstone (V) |
| 490 | Floor 301 | Rosey Viens Granite |
| 429 | Floor 264 | Gravel Road |
| 363 | Wall 258/260/0 | Egyptian (H) |
| 356 | Wall 259/261/0 | Egyptian (V) |
| 301 | Floor 18 | Sand |
| 212 | Static 326 | Fig Tree |
| 201 | Floor 277 | Sandstone Cobblestones |
| 192 | Obstruction 19 | Reef |
| 167 | Floor 611 | Egypt (2) [Fireal] |
| 153 | Floor 325 | Yellow Brick Road |
| 113 | Wall 286/0/0 | Egyptian Osiris (V) |
| 109 | Wall 262/0/0 | Egyptian (C) |
| 105 | Wall 285/0/0 | Egyptian Osiris (H) |
| 103 | Floor 16 | Beaten Path |
| 93 | Wall 359/0/0 | Sandstone (C) |
| 69 | Ice 20 | Ice |
| 66 | Wall 313/0/0 | (palette: Obstruction "Sandstone Pillar" — used as a wall) |
| 65 | Static 111 | (not in palette) |

Distinct ids used: 23 wall ids, 24 floor ids, 111 ids in total; only 13 are External-defined (the Fireal floors 610/611 and a few Tenser ids); ids 7, 111, 112, 323 appear in the map but in no palette entry.

### 3.4 Tile composition patterns (component type sequence as written)

| count | pattern |
|---|---|
| 7,543 | (empty) |
| 3,552 | Wall only — almost all Solid Rock 31 fill |
| 2,724 | Floor only |
| 1,624 | Floor + Wall — the normal built wall tile |
| 1,228 | Sky only |
| 1,024 | Water only |
| 769 | Floor + Obstruction |
| 631 | Floor + Tree |
| 355 | Floor + Static |
| 274 | Floor + Darkness |
| 269 | Floor + Wall + Wall — corner tiles carrying both an (H)/(V) wall and a (C) post, or two faces |
| 205 | Floor + Wall + Darkness |
| 134 | Obstruction + Darkness |
| 94 | Water + Darkness |
| 69 | Ice only; 58 Obstruction only; 48 Altar only; 20 Staircase only; 20 Static only |
| 51 | Floor + Door |
| 36 | Floor + Fire |
| 23 | Water + Wall; 19 Sky + Wall; 18 Wall + Floor (reversed order); 9 Floor + Floor; 6 Sky + Rope; 2 Floor + Door + Wall |

Observations for a generator:

- **Floor+Wall on the same tile is the norm** for built walls (sandstone, Egyptian, cave). The floor is there so the tile reads correctly when the wall is destroyed. Solid-rock void is wall-only.
- **Wall-only tiles** are fine (3,552 of them). Sky-only, Water-only, Ice-only, Altar-only and Staircase-only tiles are also normal: those components carry their own ground sprite.
- **Two walls on one tile** (269 + 23): typically an (H) or (V) face plus the (C) corner post, e.g. `Floor 265 + Wall 259/261 + Wall 262` (Egyptian V + Egyptian C), or H + V at an L-corner (`259/261 + 258/260`). Both are marked indestructible in those spots.
- **Order of components in XML**: Floor is written first in about 97% of the multi-component tiles that contain a floor; walls after floors; Darkness/teleporters last. Reversed cases exist (`Wall, Floor`; `Darkness, Floor`) and render identically because the editor sorts by sprite `order`. A generator should write Floor → Wall(s) → Door/Obstruction/Static/Tree → magical/teleport for readability.
- **Multiple ids per sprite slot**: `destroyed`/`ruins` are 0 when the wall has no broken state (Solid Rock, Osiris, corner posts).

### 3.5 How doors are placed

55 doors: 51 are `Floor + Door`, 2 are `Floor + Door + Wall`, 2 are Door with other. The door tile is the **gap in the wall run** — it has no WallComponent of its own; the wall run stops on either side. Neighbor check (N,E,S,W): 17 doors with closedId 312 "Egyptian (V)" have walls N and S and floor E and W; 14 with closedId 311 "Egyptian (H)" have walls E and W and floor N and S (the remainder are at corners or in open rooms). So: **(H) door ⇔ wall run continues east-west through the door tile; (V) door ⇔ wall run continues north-south.** Secret doors (`isSecret true`, 20 of them) use the same placement with `secretId` set to the matching wall id (e.g. Dungeon H door 62/74/80 with secretId 258 Egyptian H wall).

Example door tile (region 3, x=11 y=33):

```xml
<tile x="11" y="33">
  <component type="FloorComponent"><ground>265</ground></component>
  <component type="DoorComponent">
    <openId>307</openId><closedId>311</closedId><secretId>299</secretId><destroyedId>309</destroyedId>
  </component>
</tile>
```

### 3.6 The other sections (real examples, abbreviated)

```xml
<locations>
  <location name="Entrance" x="11" y="11" region="3" />
  <location name="Resurrect" x="8" y="15" region="1" />
</locations>

<subregions />          <!-- empty here; schema: <subregion name type="None|Town|Lair" region="N"><rectangles><rectangle left top right bottom/>…</rectangles></subregion> -->

<entities>
  <entity name="spawn">
    <script name="OnSpawn" enabled="true"><block /><block>
      var ani = new Restel(){ Name = "ani", MaxHealth = 10299, Health = 10299, BaseDodge = 21,
        Alignment = Alignment.Lawful, BasePenetration = ShieldPenetration.Medium, Body = 211 };
      return ani;
    </block><block /></script>
    <script name="OnDeath" enabled="false"><block /><block></block><block /></script>
    <script name="OnIncomingPlayer" enabled="true"><block /><block> if (spokeRecently(source)) return; … source.Say($"…{player.Name}"); </block><block /></script>
  </entity>
</entities>

<spawns>
  <spawn type="LocationSpawner" name="EntranceSpawn" enabled="true">
    <minimumDelay>900</minimumDelay><maximumDelay>900</maximumDelay><maximum>1</maximum>
    <script name="OnAfterSpawn" enabled="false">…</script>
    <script name="OnBeforeSpawn" enabled="false">…</script>
    <entry entity="spawn" size="1" minimum="1" maximum="1" />
    <location x="11" y="11" region="3" />
  </spawn>
</spawns>
<!-- RegionSpawner variant writes <bounds region="N"><inclusion left top right bottom/><exclusion …/></bounds> instead of <location> -->

<treasures><treasure name="Testing" /></treasures>   <!-- full form: <treasure name><notes/>…<entry weight="N"><notes/>…script…</entry></treasure> -->
<hoards />
```

Scripts are C# bodies in three `<block>` CDATA sections (before / body / after). The segment-level `<script name="Internal">` holds shared helpers.

`<brushes>` and `<templates>` are not present in Praetoseba. From `SegmentBrush.cs` / `SegmentTemplate.cs` the shapes are:

```xml
<brushes>
  <brush name="Forest mix">
    <entry weight="3"><component type="FloorComponent"><ground>23</ground></component></entry>
    <entry weight="1"><component type="FloorComponent"><ground>13</ground></component></entry>
  </brush>
</brushes>
<templates>
  <template name="Sandstone wall H">
    <component type="FloorComponent"><ground>265</ground></component>
    <component type="WallComponent"><wall>346</wall><destroyed>338</destroyed><ruins>0</ruins></component>
  </template>
</templates>
```

A brush picks one weighted entry per tile; a template is a fixed stack of components (its entries are "referencing elements", i.e. full component XML or a `<brush name=…/>`/`<template name=…/>` reference). Tiles may reference a template/brush by name instead of inlining components, but Praetoseba inlines everything, which is the safest output for a generator.

---

## 4. Cross-check: palette ids vs External terrain ids

- Components.xml references **1,207 distinct non-zero ids** (1–1411).
- **735 resolve** to `Terrain-External.xml` (sprite PNG in repo): runs 622–643, 649–657, 659–718, 726, 729, 731–736, 738–757, 762–958, 961–998, 1008–1047, 1049–1050, 1052–1065, 1067–1068, 1070–1071, 1073–1074, 1076–1222, 1225–1271, 1274–1295, 1298–1319, 1322–1330, 1340–1411.
- **472 do not** (closed-source client bin only): 1–6, 8–49, 62–67, 74–110, 113–130, 137–186, 189–239, 241–278, 283–290, 295–302, 305–319, 324–336, 338–339, 341–349, 355–375, 378–388, 391–401, 403–425, 428–450, 453–465, 470–499, 504–509, 512–514, 601–621, 1001–1007. Per property: ground 114 ids / 34 External; wall 231 / 142; destroyed 114 / 53; ruins 163 / 106; closedId & openId 49 / 27; destroyedId 46 / 23; **secretId 17 / 0; counter 12 / 0; altar 12 / 0; egress 11 / 0**; teleporterId 109 / 87; static 360 / 267; tree 29 / 17; obstruction 31 / 21.
- **147 External ids are not used by any palette entry**: 644–648, 658 (millwork wainscoting), 719–725, 727–728, 730, 737, 758–761, 959–960, the six door "ruin"/odd cells 1048, 1051, 1066, 1069, 1072, 1075, 1223–1224, 1272–1273, 1296–1297, 1320–1321, 1331–1339 (traps, spider spit), 1412 (missing texture) and **the entire n099y set 1500–1599**. A generator that wants n099y grass/dirt/water/trees must emit `FloorComponent ground=1500..1579` / `StaticComponent static=1580..1599` directly; there is no palette entry to copy.
- Ids 999–1000 and 1413–1499 are defined nowhere.
- In Praetoseba, of 111 distinct ids used, 98 are bin-only.

**Practical consequence for the HTML renderer:** keep a placeholder strategy for ids < 622 (and 1001–1007). Reasonable fallbacks: flat colour tiles keyed by component type (floor/wall/water/door) with the id printed, or use the `average` colour when a bin-only id has a palette sibling in the same family. If the closed client's `Stormhalter.bin` can be unzipped on the user's machine, its `Data/Terrain.xml` has the same schema as External and would fill the gap completely (WorldForge itself reads `Data\Terrain.xml` from the bin first, then overlays External).



## Appendix A. Components.xml full legend

Id suffix: ᴱ = terrain id defined in `Content/Data/Terrain-External.xml` (sprite available in repo); ᴮ = not in External, lives only in the closed client `Stormhalter.bin` `Data/Terrain.xml` (no sprite in repo). `0` = none.


### Floors — `FloorComponent` (103 entries)

| # | category | name | ground | movementCost | color |
|---|---|---|---|---|---|
| 1 | Floors | Light | 1ᴮ | 1 |  |
| 2 | Floors | Tile | 2ᴮ | 1 |  |
| 3 | Floors | Hardwood (H) | 3ᴮ | 1 |  |
| 4 | Floors | Hardwood (V) | 4ᴮ | 1 |  |
| 5 | Floors | Temple | 5ᴮ | 1 |  |
| 6 | Floors | Burnt Stone | 6ᴮ | 1 |  |
| 7 | Floors | (Lava) | 10ᴮ | 1 |  |
| 8 | Floors | (PH) | 11ᴮ | 1 |  |
| 9 | Floors | Dirt | 12ᴮ | 1 |  |
| 10 | Floors | Short Grass | 13ᴮ | 1 |  |
| 11 | Floors | Wood (H) | 14ᴮ | 1 |  |
| 12 | Floors | Wood (V) | 15ᴮ | 1 |  |
| 13 | Floors | Beaten Path | 16ᴮ | 1 |  |
| 14 | Floors | Sand | 18ᴮ | 2 |  |
| 15 | Floors | Bog | 21ᴮ | 1 |  |
| 16 | Floors | Forest | 23ᴮ | 1 |  |
| 17 | Floors | Honeycomb Flagstone | 24ᴮ | 1 |  |
| 18 | Floors | Jungle | 89ᴮ | 1 |  |
| 19 | Floors | Jungle (Moss) | 90ᴮ | 1 |  |
| 20 | Floors | Jungle (Foliage) | 91ᴮ | 1 |  |
| 21 | Floors | Bridge (H) | 115ᴮ | 1 |  |
| 22 | Floors | Bridge (V) | 116ᴮ | 1 |  |
| 23 | Floors | Flat Stone Bridge (H) | 1027ᴱ | 1 |  |
| 24 | Floors | Flat Stone Bridge (V) | 1028ᴱ | 1 |  |
| 25 | Floors | Rope Bridge (H) | 239ᴮ | 1 |  |
| 26 | Floors | Giant Logs | 175ᴮ | 1 |  |
| 27 | Floors | Worn Marble | 176ᴮ | 1 |  |
| 28 | Floors | Gray Tile | 178ᴮ | 1 |  |
| 29 | Floors | Dusty Cave | 179ᴮ | 1 |  |
| 30 | Floors | Slate Flagstone | 182ᴮ | 1 |  |
| 31 | Floors | Mossy Granite | 183ᴮ | 1 |  |
| 32 | Floors | Worn Cobblestone | 184ᴮ | 1 |  |
| 33 | Floors | Tidal Mud | 185ᴮ | 1 |  |
| 34 | Floors | Fine Marble | 186ᴮ | 1 |  |
| 35 | Floors | Oriental Rug | 196ᴮ | 1 |  |
| 36 | Floors | Stone Bridge (H) | 252ᴮ | 1 |  |
| 37 | Floors | Gravel Road | 264ᴮ | 1 |  |
| 38 | Floors | Sandstone Slabs | 265ᴮ | 1 |  |
| 39 | Floors | Sandstone Cobblestones | 277ᴮ | 1 |  |
| 40 | Floors | Green Alfalfa | 289ᴮ | 1 |  |
| 41 | Floors | Rosey Viens Granite | 301ᴮ | 1 |  |
| 42 | Floors | Yellow Brick Road | 325ᴮ | 1 |  |
| 43 | Floors | Jade Bricks | 341ᴮ | 1 |  |
| 44 | Floors | Mossy Cave Floor | 369ᴮ | 1 |  |
| 45 | Floors | Torn Cobblestones | 375ᴮ | 1 |  |
| 46 | Floors | Skulls | 387ᴮ | 1 |  |
| 47 | Floors | Blue Marble | 388ᴮ | 1 |  |
| 48 | Floors | Sandstone Cobblestones | 393ᴮ | 1 |  |
| 49 | Floors | (PH) | 406ᴮ | 1 |  |
| 50 | Floors | Ash | 419ᴮ | 1 |  |
| 51 | Floors | Blue Brick Road | 445ᴮ | 1 |  |
| 52 | Floors | Dark Wood | 492ᴮ | 1 |  |
| 53 | Floors | Bamboo | 493ᴮ | 1 |  |
| 54 | Floors | Sand [Zrikz] | 602ᴮ | 2 |  |
| 55 | Floors | Sand [Zrikz] | 603ᴮ | 2 |  |
| 56 | Floors | Sandflats [Zrikz] | 604ᴮ | 2 |  |
| 57 | Floors | Reef [Zrikz] | 605ᴮ | 2 |  |
| 58 | Floors | Aqua [Fireal] | 606ᴮ | 1 |  |
| 59 | Floors | Cobblestone [Fireal] | 607ᴮ | 1 |  |
| 60 | Floors | Cut Wood [Fireal] | 608ᴮ | 1 |  |
| 61 | Floors | Druid Cove [Fireal] | 609ᴮ | 1 |  |
| 62 | Floors | Egypt (1) [Fireal] | 610ᴮ | 1 |  |
| 63 | Floors | Egypt (2) [Fireal] | 611ᴮ | 1 |  |
| 64 | Floors | Fantasy Flower [Fireal] | 612ᴮ | 1 |  |
| 65 | Floors | Glass Lava [Fireal] | 613ᴮ | 1 |  |
| 66 | Floors | Grass [Fireal] | 614ᴮ | 1 |  |
| 67 | Floors | Ice [Fireal] | 615ᴮ | 1 |  |
| 68 | Floors | Labyrinth [Fireal] | 616ᴮ | 1 |  |
| 69 | Floors | Ornate [Fireal] | 617ᴮ | 1 |  |
| 70 | Floors | Paving Slabs [Fireal] | 618ᴮ | 1 |  |
| 71 | Floors | Skulls [Fireal] | 619ᴮ | 1 |  |
| 72 | Floors | Cobble Puzzle [Fireal] | 620ᴮ | 1 |  |
| 73 | Floors | Cobbles [Fireal] | 621ᴮ | 1 |  |
| 74 | Floors | Bedrock [Lux] | 1003ᴮ | 1 |  |
| 75 | Floors | Roots [Lux] | 1004ᴮ | 1 |  |
| 76 | Floors | Sewer Drain [Tenser] | 628ᴱ | 1 |  |
| 77 | Floors | Sewer Floor [Tenser] | 629ᴱ | 1 |  |
| 78 | Floors | Lava Tube Floor | 1009ᴱ | 1 |  |
| 79 | Floors | Swamp cave floor | 1091ᴱ | 1 |  |
| 80 | Floors | Swamp mossy floor | 1098ᴱ | 1 |  |
| 81 | Floors | Swamp rock floor | 1099ᴱ | 1 |  |
| 82 | Floors | mine floor | 1214ᴱ | 1 |  |
| 83 | Floors | new dungeon floor | 1226ᴱ | 1 |  |
| 84 | Floors | light stone floor | 671ᴱ | 1 |  |
| 85 | Floors | rock floor | 680ᴱ | 1 |  |
| 86 | Floors | cave floor | 689ᴱ | 1 |  |
| 87 | Floors | dark wood floor | 700ᴱ | 1 |  |
| 88 | Floors | light wood floor | 945ᴱ | 1 |  |
| 89 | Floors | rustic wood floor | 1237ᴱ | 1 |  |
| 90 | Floors | purple floor texture | 1259ᴱ | 1 |  |
| 91 | Floors | desat-blue floor texture | 1283ᴱ | 1 |  |
| 92 | Floors | dbl desat-green floor texture | 1307ᴱ | 1 |  |
| 93 | Floors | red brick floor | 1341ᴱ | 1 |  |
| 94 | Floors | nidavellir dark floor | 1365ᴱ | 1 |  |
| 95 | Floors | nidavellir light floor | 1372ᴱ | 1 |  |
| 96 | Floors | icy rock floor | 1409ᴱ | 1 |  |
| 97 | Floors | icy snow floor | 1410ᴱ | 1 |  |
| 98 | Floors | snow floor | 1411ᴱ | 1 |  |
| 99 | Customizable | palace flagstone floor | 1125ᴱ | 1 |  |
| 100 | Customizable | palace flagstone floor grout (alt color) | 1133ᴱ | 0 |  |
| 101 | Grove | None | 23ᴮ |  |  |
| 102 | Grove | None | 23ᴮ |  |  |
| 103 | Grove | None | 23ᴮ |  |  |

### Ice floors — `IceComponent` (5 entries)

| # | category | name | ground | movementCost |
|---|---|---|---|---|
| 1 | Floors | Snow | 17ᴮ | 1 |
| 2 | Floors | Ice | 20ᴮ | 1 |
| 3 | Floors | Ice Labyrinth Floor | 992ᴱ | 1 |
| 4 | Floors | Icy cave Floor | 1349ᴱ | 1 |
| 5 | Floors | glacier Floor | 1357ᴱ | 1 |

### Water — `WaterComponent` (11 entries)

| # | category | name | ground | depth | movementCost | color |
|---|---|---|---|---|---|---|
| 1 | Water | Water | 22ᴮ | 3 | 3 |  |
| 2 | Water | Fresh Water | 177ᴮ | 3 | 3 |  |
| 3 | Water | Dark and Cloudy Water | 180ᴮ | 3 | 3 |  |
| 4 | Water | Dark Red Liquid | 374ᴮ | 3 | 3 |  |
| 5 | Water | Shoreline (Shallow) [Zrikz] | 601ᴮ | 3 | 3 |  |
| 6 | Water | Shoreline [Zrikz] | 601ᴮ | 3 | 3 |  |
| 7 | Water | Sewer [Zrikz] | 602ᴮ | 3 | 3 |  |
| 8 | Water | Waves (H) [Tenser] | 622ᴱ | 3 | 3 |  |
| 9 | Water | Waves (V) [Tenser] | 623ᴱ | 3 | 3 |  |
| 10 | Water | Waves (E) [Tenser] | 1018ᴱ | 3 | 3 |  |
| 11 | Water | Waves (S) [Tenser] | 1019ᴱ | 3 | 3 |  |

### Poisoned water — `PoisonedWaterComponent` (1 entries)

| # | category | name | ground | movementCost | color |
|---|---|---|---|---|---|
| 1 | Water | Poisoned Water | 180ᴮ | 3 |  |

### Walls — `WallComponent` (233 entries)

Naming: (H) = horizontal wall sprite (draw order 5), (V) = vertical (order 4), (C) = corner post (order 4). `destroyed` = sprite shown when the wall is broken, `ruins` = rubble sprite drawn under the destroyed sprite (0 = none).

| # | category | name | wall | destroyed | ruins | indestructible | color |
|---|---|---|---|---|---|---|---|
| 1 | Structural | Town (H) | 27ᴮ | 40ᴮ | 45ᴮ | false |  |
| 2 | Structural | Town (C) | 33ᴮ | 784ᴱ | 45ᴮ | false |  |
| 3 | Structural | Town (V) | 28ᴮ | 41ᴮ | 45ᴮ | false |  |
| 4 | Structural | Temple (V) | 30ᴮ | 43ᴮ | 46ᴮ | false |  |
| 5 | Structural | Temple (H) | 29ᴮ | 42ᴮ | 46ᴮ | false |  |
| 6 | Structural | Temple (C) | 34ᴮ | 144ᴮ | 46ᴮ | false |  |
| 7 | Structural | Dirty Marble (V) | 140ᴮ | 142ᴮ | 46ᴮ | false |  |
| 8 | Structural | Dirty Marble (H) | 139ᴮ | 141ᴮ | 46ᴮ | false |  |
| 9 | Structural | Dirty Marble (C) | 143ᴮ | 144ᴮ | 46ᴮ | false |  |
| 10 | Structural | Heavy Logs (V) | 146ᴮ | 148ᴮ | 44ᴮ | false |  |
| 11 | Structural | Heavy Logs (H) | 145ᴮ | 147ᴮ | 44ᴮ | false |  |
| 12 | Structural | Heavy Logs (C) | 149ᴮ | 150ᴮ | 44ᴮ | false |  |
| 13 | Structural | Dragon (H) | 151ᴮ | 153ᴮ | 46ᴮ | true |  |
| 14 | Structural | Dragon (V) | 152ᴮ | 154ᴮ | 46ᴮ | true |  |
| 15 | Structural | Dragon (C) | 155ᴮ | 156ᴮ | 46ᴮ | false |  |
| 16 | Structural | Cave (V) | 158ᴮ | 161ᴮ | 170ᴮ | false |  |
| 17 | Structural | Cave (H) | 157ᴮ | 160ᴮ | 170ᴮ | false |  |
| 18 | Structural | Cave (C) | 159ᴮ | 162ᴮ | 170ᴮ | false |  |
| 19 | Structural | Dungeon (V) | 26ᴮ | 39ᴮ | 44ᴮ | false |  |
| 20 | Structural | Dungeon (H) | 25ᴮ | 38ᴮ | 44ᴮ | false |  |
| 21 | Structural | Dungeon (C) | 32ᴮ | 783ᴱ | 44ᴮ | false |  |
| 22 | Structural | Granite (V) | 336ᴮ | 345ᴮ | 44ᴮ | false |  |
| 23 | Structural | Granite (H) | 335ᴮ | 344ᴮ | 44ᴮ | false |  |
| 24 | Structural | Granite (C) | 357ᴮ | 358ᴮ | 44ᴮ | false |  |
| 25 | Structural | Sandstone (V) | 347ᴮ | 339ᴮ | 44ᴮ | false |  |
| 26 | Structural | Sandstone (H) | 346ᴮ | 338ᴮ | 44ᴮ | false |  |
| 27 | Structural | Sandstone (C) | 359ᴮ | 360ᴮ | 44ᴮ | false |  |
| 28 | Structural | Dirt (V) | 334ᴮ | 343ᴮ | 669ᴱ | false |  |
| 29 | Structural | Dirt (H) | 333ᴮ | 342ᴮ | 669ᴱ | false |  |
| 30 | Structural | Dirt (C) | 355ᴮ | 356ᴮ | 669ᴱ | false |  |
| 31 | Structural | Undead (V) | 382ᴮ | 395ᴮ | 44ᴮ | false |  |
| 32 | Structural | Undead (H) | 381ᴮ | 394ᴮ | 44ᴮ | false |  |
| 33 | Structural | Undead (C) | 407ᴮ | 408ᴮ | 44ᴮ | false |  |
| 34 | Structural | Blue Marble (V) | 384ᴮ | 397ᴮ | 44ᴮ | false |  |
| 35 | Structural | Blue Marble (H) | 383ᴮ | 396ᴮ | 44ᴮ | false |  |
| 36 | Structural | Blue Marble (C) | 409ᴮ | 410ᴮ | 44ᴮ | false |  |
| 37 | Structural | Mines (V) | 414ᴮ | 416ᴮ | 398ᴮ | false |  |
| 38 | Structural | Mines (H) | 413ᴮ | 415ᴮ | 398ᴮ | false |  |
| 39 | Structural | Mines (C) | 417ᴮ | 418ᴮ | 398ᴮ | false |  |
| 40 | Structural | Thicket (V) | 224ᴮ | 227ᴮ | 44ᴮ | false |  |
| 41 | Structural | Thicket (H) | 223ᴮ | 226ᴮ | 44ᴮ | false |  |
| 42 | Structural | Thicket (C) | 225ᴮ | 228ᴮ | 44ᴮ | false |  |
| 43 | Structural | Red Shoji (V) | 363ᴮ | 365ᴮ | 380ᴮ | false |  |
| 44 | Structural | Red Shoji (H) | 362ᴮ | 364ᴮ | 380ᴮ | false |  |
| 45 | Structural | Red Shoji (C) | 366ᴮ | 367ᴮ | 380ᴮ | false |  |
| 46 | Structural | Dragon (V) | 429ᴮ | 442ᴮ | 432ᴮ | false |  |
| 47 | Structural | Dragon (H) | 428ᴮ | 441ᴮ | 432ᴮ | false |  |
| 48 | Structural | Dragon Window (V) | 431ᴮ | 442ᴮ | 432ᴮ | false |  |
| 49 | Structural | Dragon Window (H) | 430ᴮ | 441ᴮ | 432ᴮ | false |  |
| 50 | Structural | Dragon (C) | 443ᴮ | 444ᴮ | 432ᴮ | false |  |
| 51 | Structural | Highmountain (V) | 460ᴮ | 462ᴮ | 465ᴮ | false |  |
| 52 | Structural | Highmountain (H) | 459ᴮ | 461ᴮ | 465ᴮ | false |  |
| 53 | Structural | Highmountain (C) | 463ᴮ | 464ᴮ | 465ᴮ | false |  |
| 54 | Structural | Pagoda Shoji (V) | 471ᴮ | 473ᴮ | 45ᴮ | false |  |
| 55 | Structural | Pagoda Shoji (H) | 470ᴮ | 472ᴮ | 45ᴮ | false |  |
| 56 | Structural | Pagoda Framed (V) | 475ᴮ | 477ᴮ | 45ᴮ | false |  |
| 57 | Structural | Pagoda Framed (H) | 474ᴮ | 476ᴮ | 45ᴮ | false |  |
| 58 | Structural | Pagoda Framed (V) | 483ᴮ | 485ᴮ | 45ᴮ | false |  |
| 59 | Structural | Pagoda Framed (H) | 482ᴮ | 484ᴮ | 45ᴮ | false |  |
| 60 | Structural | Pagoda (V) | 487ᴮ | 489ᴮ | 45ᴮ | false |  |
| 61 | Structural | Pagoda (H) | 486ᴮ | 488ᴮ | 45ᴮ | false |  |
| 62 | Structural | Pagoda (C) | 480ᴮ | 481ᴮ | 45ᴮ | false |  |
| 63 | Structural | Egyptian (V) | 259ᴮ | 261ᴮ | 44ᴮ | false |  |
| 64 | Structural | Egyptian (H) | 258ᴮ | 260ᴮ | 44ᴮ | false |  |
| 65 | Structural | Egyptian Life (V) | 272ᴮ | 261ᴮ | 44ᴮ | false |  |
| 66 | Structural | Egyptian Life (H) | 271ᴮ | 260ᴮ | 44ᴮ | false |  |
| 67 | Structural | Egyptian Life (V) | 274ᴮ | 261ᴮ | 44ᴮ | false |  |
| 68 | Structural | Egyptian Life (H) | 273ᴮ | 260ᴮ | 44ᴮ | false |  |
| 69 | Structural | Egyptian Sobet (V) | 276ᴮ | 261ᴮ | 44ᴮ | false |  |
| 70 | Structural | Egyptian Sobet (H) | 275ᴮ | 260ᴮ | 44ᴮ | false |  |
| 71 | Structural | Egyptian Horus (V) | 284ᴮ | 261ᴮ | 44ᴮ | false |  |
| 72 | Structural | Egyptian Horus (H) | 283ᴮ | 260ᴮ | 44ᴮ | false |  |
| 73 | Structural | Egyptian Osiris (V) | 286ᴮ | 261ᴮ | 44ᴮ | false |  |
| 74 | Structural | Egyptian Osiris (H) | 285ᴮ | 260ᴮ | 44ᴮ | false |  |
| 75 | Structural | Egyptian Sekhmet (V) | 288ᴮ | 261ᴮ | 44ᴮ | false |  |
| 76 | Structural | Egyptian Sekhmet (H) | 287ᴮ | 260ᴮ | 44ᴮ | false |  |
| 77 | Structural | Egyptian Re.Harakhti (V) | 296ᴮ | 261ᴮ | 44ᴮ | false |  |
| 78 | Structural | Egyptian Re.Harakhti (H) | 295ᴮ | 260ᴮ | 44ᴮ | false |  |
| 79 | Structural | Egyptian Anubis (V) | 297ᴮ | 261ᴮ | 44ᴮ | false |  |
| 80 | Structural | Egyptian Anubis (H) | 298ᴮ | 260ᴮ | 44ᴮ | false |  |
| 81 | Structural | Egyptian Iris (V) | 300ᴮ | 261ᴮ | 44ᴮ | false |  |
| 82 | Structural | Egyptian Iris (H) | 299ᴮ | 260ᴮ | 44ᴮ | false |  |
| 83 | Structural | Egyptian (C) | 262ᴮ | 263ᴮ | 44ᴮ | false |  |
| 84 | Structural | Solid Rock | 31ᴮ | 0 | 44ᴮ | true |  |
| 85 | Structural | Solid Granite | 447ᴮ | 0 | 44ᴮ | true |  |
| 86 | Structural | Solid Sandstone | 448ᴮ | 0 | 44ᴮ | true |  |
| 87 | Structural | Solid Dirt | 446ᴮ | 0 | 44ᴮ | true |  |
| 88 | Structural | Portal Pillar | 104ᴮ | 640ᴱ | 46ᴮ | true |  |
| 89 | Structural | Stalagmite | 371ᴮ | 641ᴱ | 170ᴮ | true |  |
| 90 | Structural |  panel wall (H)  | 707ᴱ | 710ᴱ | 711ᴱ | false |  |
| 91 | Structural |  panel wall (V)  | 709ᴱ | 712ᴱ | 711ᴱ | false |  |
| 92 | Structural |  panel corner post  | 708ᴱ | 0 | 711ᴱ | false |  |
| 93 | Structural |  Lodge wall (H)  | 713ᴱ | 716ᴱ | 717ᴱ | false |  |
| 94 | Structural |  Lodge wall (V)  | 715ᴱ | 718ᴱ | 717ᴱ | false |  |
| 95 | Structural |  Lodge corner post  | 714ᴱ | 0 | 717ᴱ | false |  |
| 96 | Structural |  front wall (H)  | 731ᴱ | 735ᴱ | 0 | false |  |
| 97 | Structural |  inside back wall (H)  | 732ᴱ | 735ᴱ | 0 | false |  |
| 98 | Structural |  inside left wall (V)  | 733ᴱ | 736ᴱ | 0 | false |  |
| 99 | Structural |  outside right wall (V)  | 734ᴱ | 736ᴱ | 0 | false |  |
| 100 | Structural | Ice Labyrinth(H) | 991ᴱ | 994ᴱ | 995ᴱ | false |  |
| 101 | Structural | Ice Labyrinth (V) | 993ᴱ | 996ᴱ | 995ᴱ | false |  |
| 102 | Structural | Ice Labyrinth Corner Pillar | 997ᴱ | 998ᴱ | 995ᴱ | false |  |
| 103 | Structural | Lava Tube Wall (H) | 1008ᴱ | 1011ᴱ | 1012ᴱ | false |  |
| 104 | Structural | Lava Tube Wall (V) | 1010ᴱ | 1013ᴱ | 1012ᴱ | false |  |
| 105 | Structural | Lava Tube Corner Pillar | 1014ᴱ | 1015ᴱ | 1012ᴱ | false |  |
| 106 | Structural | Log Fortification (H) | 1088ᴱ | 147ᴮ | 717ᴱ | false |  |
| 107 | Structural | Log Fortification (V) | 1089ᴱ | 148ᴮ | 717ᴱ | false |  |
| 108 | Structural | Swamp cave wall (V) | 1092ᴱ | 1095ᴱ | 1094ᴱ | false |  |
| 109 | Structural | Swamp cave wall (h) | 1090ᴱ | 1093ᴱ | 1094ᴱ | false |  |
| 110 | Structural | Swamp cave pillar | 1096ᴱ | 1097ᴱ | 1094ᴱ | false |  |
| 111 | Structural | Swamp tree pillar | 1108ᴱ | 1097ᴱ | 1094ᴱ | false |  |
| 112 | Structural | Swamp cave wall vine (V) | 1115ᴱ | 1095ᴱ | 1094ᴱ | false |  |
| 113 | Structural | Swamp cave wall vine (H) | 1114ᴱ | 1093ᴱ | 1094ᴱ | false |  |
| 114 | Structural | grey stone dragon - column wrap | 1128ᴱ | 1170ᴱ | 1170ᴱ | false |  |
| 115 | Structural | gold dragon - column wrap | 1129ᴱ | 1170ᴱ | 1170ᴱ | false |  |
| 116 | Structural | gold serpent - column wrap | 1130ᴱ | 1170ᴱ | 1170ᴱ | false |  |
| 117 | Structural | marble dragon column | 1131ᴱ | 1169ᴱ | 1170ᴱ | false |  |
| 118 | Structural | bull head column | 1132ᴱ | 1169ᴱ | 1170ᴱ | false |  |
| 119 | Structural | lion head column | 1140ᴱ | 1169ᴱ | 1170ᴱ | false |  |
| 120 | Structural | mine solid | 1221ᴱ | 1221ᴱ | 1221ᴱ | true |  |
| 121 | Structural | mine wall (h) | 1213ᴱ | 1217ᴱ | 1216ᴱ | true |  |
| 122 | Structural | mine wall (v) | 1215ᴱ | 1217ᴱ | 1218ᴱ | true |  |
| 123 | Structural | mine pillar | 1219ᴱ | 1217ᴱ | 1220ᴱ | true |  |
| 124 | Structural | mine wood post | 1222ᴱ | 1217ᴱ | 1220ᴱ | true |  |
| 125 | Structural | irr wall (h) | 1225ᴱ | 1229ᴱ | 1228ᴱ | false |  |
| 126 | Structural | irr wall (v) | 1227ᴱ | 1229ᴱ | 1230ᴱ | false |  |
| 127 | Structural | irr post | 1231ᴱ | 1229ᴱ | 1232ᴱ | false |  |
| 128 | Structural | stacked box obstruction | 666ᴱ | 667ᴱ | 667ᴱ | false |  |
| 129 | Structural | light stone wall (H) | 670ᴱ | 676ᴱ | 674ᴱ | false |  |
| 130 | Structural | light stone wall (V) | 672ᴱ | 675ᴱ | 674ᴱ | false |  |
| 131 | Structural | light stone column | 673ᴱ | 677ᴱ | 674ᴱ | false |  |
| 132 | Structural | rock wall (H) | 679ᴱ | 685ᴱ | 683ᴱ | false |  |
| 133 | Structural | rock wall (V) | 681ᴱ | 684ᴱ | 683ᴱ | false |  |
| 134 | Structural | rock wall column | 682ᴱ | 686ᴱ | 683ᴱ | false |  |
| 135 | Structural | cave wall (H) | 688ᴱ | 694ᴱ | 692ᴱ | false |  |
| 136 | Structural | cave wall (V) | 690ᴱ | 693ᴱ | 692ᴱ | false |  |
| 137 | Structural | cave wall column | 691ᴱ | 1229ᴱ | 692ᴱ | false |  |
| 138 | Structural | animated fireplace H | 697ᴱ | 1229ᴱ | 938ᴱ | false |  |
| 139 | Structural | animated fireplace V | 698ᴱ | 1229ᴱ | 947ᴱ | false |  |
| 140 | Structural | Big City wall H | 699ᴱ | 703ᴱ | 705ᴱ | false |  |
| 141 | Structural | Big City wall V | 701ᴱ | 703ᴱ | 704ᴱ | false |  |
| 142 | Structural | Big City wall corner column | 702ᴱ | 703ᴱ | 706ᴱ | false |  |
| 143 | Structural | Big City wall alt 1 H | 862ᴱ | 703ᴱ | 705ᴱ | false |  |
| 144 | Structural | Big City wall alt 1 V | 863ᴱ | 703ᴱ | 704ᴱ | false |  |
| 145 | Structural | Big City wall alt 2 H | 864ᴱ | 703ᴱ | 705ᴱ | false |  |
| 146 | Structural | Big City wall alt 2 V | 865ᴱ | 703ᴱ | 704ᴱ | false |  |
| 147 | Structural | Big City stained glass H | 867ᴱ | 703ᴱ | 705ᴱ | false |  |
| 148 | Structural | Big City stained glass V | 868ᴱ | 703ᴱ | 704ᴱ | false |  |
| 149 | Structural | Big City wall plain H | 869ᴱ | 703ᴱ | 705ᴱ | false |  |
| 150 | Structural | Big City wall plain V | 870ᴱ | 703ᴱ | 704ᴱ | false |  |
| 151 | Structural | fireplace H | 871ᴱ | 1229ᴱ | 938ᴱ | false |  |
| 152 | Structural | fireplace v | 872ᴱ | 1229ᴱ | 947ᴱ | false |  |
| 153 | Structural | stone wall H | 936ᴱ | 1229ᴱ | 938ᴱ | false |  |
| 154 | Structural | stone wall V | 937ᴱ | 1229ᴱ | 947ᴱ | false |  |
| 155 | Structural | wood siding wall H | 939ᴱ | 1239ᴱ | 965ᴱ | false |  |
| 156 | Structural | wood siding wall V | 940ᴱ | 1239ᴱ | 956ᴱ | false |  |
| 157 | Structural | wood post | 946ᴱ | 1239ᴱ | 408ᴮ | false |  |
| 158 | Structural | fence H | 952ᴱ | 1239ᴱ | 408ᴮ | true |  |
| 159 | Structural | fence v | 953ᴱ | 1239ᴱ | 408ᴮ | true |  |
| 160 | Structural | rustic log wall H | 957ᴱ | 1236ᴱ | 1236ᴱ | false |  |
| 161 | Structural | rustic log wall V | 958ᴱ | 1236ᴱ | 1236ᴱ | false |  |
| 162 | Structural | rustic log wall post | 1235ᴱ | 1236ᴱ | 1238ᴱ | false |  |
| 163 | Structural | temple stained glass H | 966ᴱ | 46ᴮ | 42ᴮ | false |  |
| 164 | Structural | temple stained glass V | 967ᴱ | 46ᴮ | 43ᴮ | false |  |
| 165 | Structural | temple niche H | 1240ᴱ | 46ᴮ | 42ᴮ | false |  |
| 166 | Structural | temple niche V | 1241ᴱ | 46ᴮ | 43ᴮ | false |  |
| 167 | Structural | dungeon dreary purple wall H | 1258ᴱ | 1262ᴱ | 1264ᴱ | false |  |
| 168 | Structural | dungeon dreary purple wall V | 1260ᴱ | 1262ᴱ | 1263ᴱ | false |  |
| 169 | Structural | dungeon dreary purple corner post | 1261ᴱ | 1262ᴱ | 1265ᴱ | false |  |
| 170 | Structural | dungeon dreary purple arch wall H | 1266ᴱ | 1262ᴱ | 1264ᴱ | false |  |
| 171 | Structural | dungeon dreary purple arch wall V | 1267ᴱ | 1262ᴱ | 1263ᴱ | false |  |
| 172 | Structural | dungeon dreary purple plain wall H | 1268ᴱ | 1262ᴱ | 1264ᴱ | false |  |
| 173 | Structural | dungeon dreary purple plain wall V | 1269ᴱ | 1262ᴱ | 1263ᴱ | false |  |
| 174 | Structural | dungeon dreary purple demon head wall H | 1270ᴱ | 1262ᴱ | 1264ᴱ | false |  |
| 175 | Structural | dungeon dreary desaturated blue wall H | 1282ᴱ | 1286ᴱ | 1288ᴱ | false |  |
| 176 | Structural | dungeon dreary desaturated blue wall V | 1284ᴱ | 1286ᴱ | 1287ᴱ | false |  |
| 177 | Structural | dungeon dreary desaturated blue column | 1285ᴱ | 1286ᴱ | 1289ᴱ | false |  |
| 178 | Structural | dungeon dreary desaturated blue arch wall H | 1290ᴱ | 1286ᴱ | 1288ᴱ | false |  |
| 179 | Structural | dungeon dreary desaturated blue arch wall V | 1291ᴱ | 1286ᴱ | 1287ᴱ | false |  |
| 180 | Structural | dungeon dreary desaturated blue bare wall H | 1292ᴱ | 1286ᴱ | 1288ᴱ | false |  |
| 181 | Structural | dungeon dreary desaturated blue bare wall V | 1293ᴱ | 1286ᴱ | 1287ᴱ | false |  |
| 182 | Structural | dungeon dreary desaturated blue demonhead wall V | 1294ᴱ | 1286ᴱ | 1288ᴱ | false |  |
| 183 | Structural | dungeon dreary 2x desaturated green wall H | 1306ᴱ | 1310ᴱ | 1312ᴱ | false |  |
| 184 | Structural | dungeon dreary 2x desaturated green wall V | 1308ᴱ | 1310ᴱ | 1311ᴱ | false |  |
| 185 | Structural | dungeon dreary 2x desaturated green column | 1309ᴱ | 1310ᴱ | 1313ᴱ | false |  |
| 186 | Structural | dungeon dreary 2x desaturated green arch wall H | 1314ᴱ | 1310ᴱ | 1312ᴱ | false |  |
| 187 | Structural | dungeon dreary 2x desaturated green arch wall V | 1315ᴱ | 1310ᴱ | 1311ᴱ | false |  |
| 188 | Structural | dungeon dreary 2x desaturated green bare wall H | 1316ᴱ | 1310ᴱ | 1312ᴱ | false |  |
| 189 | Structural | dungeon dreary 2x desaturated green bare wall V | 1317ᴱ | 1310ᴱ | 1311ᴱ | false |  |
| 190 | Structural | dungeon dreary 2x desaturated green demonhead wall H | 1318ᴱ | 1310ᴱ | 1312ᴱ | false |  |
| 191 | Structural | red brick wall (h) | 1340ᴱ | 1344ᴱ | 1346ᴱ | false |  |
| 192 | Structural | red brick wall (v) | 1342ᴱ | 1344ᴱ | 1345ᴱ | false |  |
| 193 | Structural | red brick post | 1343ᴱ | 1344ᴱ | 1347ᴱ | false |  |
| 194 | Structural | icy cave wall (h) | 1348ᴱ | 1352ᴱ | 1354ᴱ | false |  |
| 195 | Structural | icy cave wall (v) | 1350ᴱ | 1352ᴱ | 1353ᴱ | false |  |
| 196 | Structural | icy cave post | 1351ᴱ | 1352ᴱ | 1355ᴱ | false |  |
| 197 | Structural | glacier wall (H) | 1356ᴱ | 1360ᴱ | 1359ᴱ | false |  |
| 198 | Structural | glacier wall (v) | 1358ᴱ | 1360ᴱ | 1361ᴱ | false |  |
| 199 | Structural | glacier post | 1362ᴱ | 1360ᴱ | 1363ᴱ | false |  |
| 200 | Structural | nidavellir wall (h) | 1364ᴱ | 1368ᴱ | 1370ᴱ | false |  |
| 201 | Structural | nidavellir wall (v) | 1366ᴱ | 1368ᴱ | 1369ᴱ | false |  |
| 202 | Structural | nidavellir post | 1367ᴱ | 1368ᴱ | 1371ᴱ | false |  |
| 203 | Structural | nidavellir mythril wall (h) | 1380ᴱ | 1368ᴱ | 1371ᴱ | true |  |
| 204 | Structural | nidavellir mythril wall (v) | 1381ᴱ | 1368ᴱ | 1371ᴱ | true |  |
| 205 | Customizable | palace pillar right wall (H) | 1116ᴱ | 1161ᴱ | 1170ᴱ | false |  |
| 206 | Customizable | palace pillar right wall grout (H) (alt color) | 1147ᴱ | 1161ᴱ | 1170ᴱ | false |  |
| 207 | Customizable | palace pillar right wall highlights (H) (alt color) | 1156ᴱ | 1161ᴱ | 1170ᴱ | false |  |
| 208 | Customizable | palace wall (H) | 1117ᴱ | 1166ᴱ | 1170ᴱ | false |  |
| 209 | Customizable | palace wall grout (H) (alt color) | 1135ᴱ | 1166ᴱ | 1170ᴱ | false |  |
| 210 | Customizable | palace wall highlights (H) (alt color) | 1152ᴱ | 1166ᴱ | 1170ᴱ | false |  |
| 211 | Customizable | palace pillar left wall (H) | 1118ᴱ | 1163ᴱ | 1170ᴱ | false |  |
| 212 | Customizable | palace pillar left wall grout (H) (alt color) | 1149ᴱ | 1163ᴱ | 1170ᴱ | false |  |
| 213 | Customizable | palace pillar left wall highlights (H) (alt color) | 1154ᴱ | 1163ᴱ | 1170ᴱ | false |  |
| 214 | Customizable | palace pillar left wall (v) | 1119ᴱ | 1164ᴱ | 1170ᴱ | false |  |
| 215 | Customizable | palace pillar left wall grout (v) (alt color) | 1148ᴱ | 1164ᴱ | 1170ᴱ | false |  |
| 216 | Customizable | palace pillar left wall highlights (v) (alt color) | 1153ᴱ | 1164ᴱ | 1170ᴱ | false |  |
| 217 | Customizable | palace wall (v) | 1120ᴱ | 1165ᴱ | 1170ᴱ | false |  |
| 218 | Customizable | palace wall grout(v) (Alt color) | 1134ᴱ | 1165ᴱ | 1170ᴱ | false |  |
| 219 | Customizable | palace wall highlights (v) (Alt color) | 1151ᴱ | 1165ᴱ | 1170ᴱ | false |  |
| 220 | Customizable | palace pillar right wall (v) | 1121ᴱ | 1162ᴱ | 1170ᴱ | false |  |
| 221 | Customizable | palace pillar right wall grout (v) (alt color) | 1150ᴱ | 1162ᴱ | 1170ᴱ | false |  |
| 222 | Customizable | palace pillar right wall highlights (v) (alt color) | 1155ᴱ | 1162ᴱ | 1170ᴱ | false |  |
| 223 | Customizable | art niche wall (v) | 1122ᴱ | 1167ᴱ | 1170ᴱ | false |  |
| 224 | Customizable | art niche wall grout (v) (alt color) | 1145ᴱ | 1167ᴱ | 1170ᴱ | false |  |
| 225 | Customizable | art niche wall highlights (v) (alt color) | 1157ᴱ | 1167ᴱ | 1170ᴱ | false |  |
| 226 | Customizable | arch (v) | 1123ᴱ | 1186ᴱ | 1170ᴱ | false |  |
| 227 | Customizable | column | 1124ᴱ | 1169ᴱ | 1170ᴱ | false |  |
| 228 | Customizable | art niche wall (h) | 1126ᴱ | 1168ᴱ | 1170ᴱ | false |  |
| 229 | Customizable | art niche wall grout (h) (alt color) | 1146ᴱ | 1168ᴱ | 1170ᴱ | false |  |
| 230 | Customizable | art niche wall highlights (h) (alt color) | 1158ᴱ | 1168ᴱ | 1170ᴱ | false |  |
| 231 | Customizable | arch (h) | 1127ᴱ | 1185ᴱ | 1170ᴱ | false |  |
| 232 | Grove | None | 157ᴮ | 160ᴮ | 170ᴮ |  |  |
| 233 | Grove | None | 158ᴮ | 161ᴮ | 170ᴮ |  |  |

### Ruins — `RuinsComponent` (158 entries)

| # | category | name | ruins |
|---|---|---|---|
| 1 | Ruins | Dungeon | 44ᴮ |
| 2 | Ruins | Town | 45ᴮ |
| 3 | Ruins | Temple | 46ᴮ |
| 4 | Ruins | Heavy Logs Rubble | 717ᴱ |
| 5 | Ruins | Cave | 170ᴮ |
| 6 | Ruins | Red Shoji | 380ᴮ |
| 7 | Ruins | Mines | 398ᴮ |
| 8 | Ruins | Dragon | 432ᴮ |
| 9 | Ruins | Highmountain | 465ᴮ |
| 10 | Ruins | Sandstone Rubble | 1020ᴱ |
| 11 | Ruins | Blue Marble Rubble | 1021ᴱ |
| 12 | Ruins | Egyptian Rubble | 1022ᴱ |
| 13 | Ruins | Pagoda Rubble | 1023ᴱ |
| 14 | Ruins | Thicket Rubbish | 1024ᴱ |
| 15 | Ruins | Ice Wall Rubble | 995ᴱ |
| 16 | Ruins | Lava Tube Rubble | 1012ᴱ |
| 17 | Ruins |  Broken Portal Pillar | 642ᴱ |
| 18 | Ruins |  Broken Portal Pillar (Clean) | 640ᴱ |
| 19 | Ruins | Broken Stalagmite | 643ᴱ |
| 20 | Ruins | Broken Stalagmite (Clean) | 641ᴱ |
| 21 | Ruins | Town Wall Ruins (H) | 40ᴮ |
| 22 | Ruins | Town Wall Ruins (V) | 41ᴮ |
| 23 | Ruins | Town Wall Ruins (C) | 784ᴱ |
| 24 | Ruins | Temple Wall Ruins (H) | 42ᴮ |
| 25 | Ruins | Temple Wall Ruins (V) | 43ᴮ |
| 26 | Ruins | Temple Wall Ruins (C) | 144ᴮ |
| 27 | Ruins | Dungeon Wall Ruins (H) | 38ᴮ |
| 28 | Ruins | Dungeon Wall Ruins (V) | 39ᴮ |
| 29 | Ruins | Dungeon Wall Ruins (C) | 783ᴱ |
| 30 | Ruins | Sandstone Wall Ruins (H) | 338ᴮ |
| 31 | Ruins | Sandstone Wall Ruins (V) | 339ᴮ |
| 32 | Ruins | Sandstone Wall Ruins (C) | 360ᴮ |
| 33 | Ruins | Dirt Wall Ruins (H) | 342ᴮ |
| 34 | Ruins | Dirt Wall Ruins (V) | 343ᴮ |
| 35 | Ruins | Dirt Wall Ruins (C) | 356ᴮ |
| 36 | Ruins | Dirty Marble Ruins (H) | 141ᴮ |
| 37 | Ruins | Dirty Marble Ruins (V) | 142ᴮ |
| 38 | Ruins | Dirty Marble Ruins (C) | 144ᴮ |
| 39 | Ruins | Dragon Ruins (H) | 153ᴮ |
| 40 | Ruins | Dragon Ruins (V) | 154ᴮ |
| 41 | Ruins | Dragon Ruins (C) | 156ᴮ |
| 42 | Ruins | Dragon Ruins Blue (H) | 441ᴮ |
| 43 | Ruins | Dragon Ruins Blue (V) | 442ᴮ |
| 44 | Ruins | Dragon Ruins Blue (C) | 444ᴮ |
| 45 | Ruins | High Mountain Ruins (H) | 461ᴮ |
| 46 | Ruins | High Mountain Ruins (V) | 462ᴮ |
| 47 | Ruins | High Mountain Ruins (C) | 464ᴮ |
| 48 | Ruins | Red Shoji Ruins (H) | 364ᴮ |
| 49 | Ruins | Red Shoji Ruins (V) | 365ᴮ |
| 50 | Ruins | Red Shoji Ruins (C) | 367ᴮ |
| 51 | Ruins | Pagoda Shoji Ruins (H) | 472ᴮ |
| 52 | Ruins | Pagoda Shoji Ruins (V) | 473ᴮ |
| 53 | Ruins | Pagoda Shoji Ruins (C) | 481ᴮ |
| 54 | Ruins | Pagoda Framed Ruins (H) | 476ᴮ |
| 55 | Ruins | Pagoda Framed Ruins (V) | 477ᴮ |
| 56 | Ruins | Pagoda Framed Ruins (C) | 481ᴮ |
| 57 | Ruins | Pagoda Framed Ruins (H) | 484ᴮ |
| 58 | Ruins | Pagoda Framed Ruins (V) | 485ᴮ |
| 59 | Ruins | Pagoda Framed Ruins (C) | 481ᴮ |
| 60 | Ruins | Pagoda Ruins (H) | 488ᴮ |
| 61 | Ruins | Pagoda Ruins (V) | 489ᴮ |
| 62 | Ruins | Pagoda Ruins (C) | 481ᴮ |
| 63 | Ruins | Blue Marble Ruins (H) | 396ᴮ |
| 64 | Ruins | Blue Marble Ruins (V) | 397ᴮ |
| 65 | Ruins | Blue Marble Ruins (C) | 410ᴮ |
| 66 | Ruins | Egyptian Ruins (H) | 260ᴮ |
| 67 | Ruins | Egyptian Ruins (V) | 261ᴮ |
| 68 | Ruins | Egyptian Ruins (C) | 263ᴮ |
| 69 | Ruins | Heavy Log Ruins (H) | 147ᴮ |
| 70 | Ruins | Heavy Log Ruins (V) | 148ᴮ |
| 71 | Ruins | Heavy Log Ruins (C) | 150ᴮ |
| 72 | Ruins | Thicket Ruins (H) | 226ᴮ |
| 73 | Ruins | Thicket Ruins (V) | 227ᴮ |
| 74 | Ruins | Thicket Ruins (C) | 228ᴮ |
| 75 | Ruins |  Sewer Wall Ruins (H)  | 638ᴱ |
| 76 | Ruins |  Sewer Wall Ruins (V)  | 639ᴱ |
| 77 | Ruins |  Panel Wall Ruins (H)  | 710ᴱ |
| 78 | Ruins |  Panel wall ruins (V)  | 712ᴱ |
| 79 | Ruins |  Lodge Wall Ruins (H)  | 716ᴱ |
| 80 | Ruins |  Lodge wall ruins (V)  | 718ᴱ |
| 81 | Ruins | Ice Labyrinth Wall ruins(H) | 994ᴱ |
| 82 | Ruins | Ice Labyrinth Wall ruins (V) | 996ᴱ |
| 83 | Ruins | Ice Labyrinth Corner pillar ruins | 998ᴱ |
| 84 | Ruins | Lava Tube Wall ruins (H) | 1011ᴱ |
| 85 | Ruins | Lava Tube Wall ruins (V) | 1013ᴱ |
| 86 | Ruins | Lava Tube Corner pillar ruins | 1015ᴱ |
| 87 | Ruins | Lodge Wall Ruins (h) | 716ᴱ |
| 88 | Ruins | Lodge Wall Ruins (v) | 718ᴱ |
| 89 | Ruins | swamp cave rubble | 1094ᴱ |
| 90 | Ruins | swamp cave wall ruin (h) | 1093ᴱ |
| 91 | Ruins | swamp cave wall ruin (v) | 1095ᴱ |
| 92 | Ruins | swamp cave column ruin | 1097ᴱ |
| 93 | Ruins | palace right pillar ruins (h) | 1161ᴱ |
| 94 | Ruins | palace right pillar ruins (v) | 1162ᴱ |
| 95 | Ruins | palace left pillar ruins (h) | 1163ᴱ |
| 96 | Ruins | palace left pillar ruins (v) | 1164ᴱ |
| 97 | Ruins | palace wall ruins (v) | 1165ᴱ |
| 98 | Ruins | palace wall ruins (h) | 1166ᴱ |
| 99 | Ruins | art niche wall ruin (v) | 1167ᴱ |
| 100 | Ruins | art niche wall ruin (h) | 1168ᴱ |
| 101 | Ruins | palace column ruin | 1169ᴱ |
| 102 | Ruins | palace arch ruins (h) | 1185ᴱ |
| 103 | Ruins | palace arch ruins (v) | 1186ᴱ |
| 104 | Ruins | mine rubble | 1217ᴱ |
| 105 | Ruins | irr wall ruin (h) | 1228ᴱ |
| 106 | Ruins | irr wall rubble | 1229ᴱ |
| 107 | Ruins | irr wall ruin (v) | 1230ᴱ |
| 108 | Ruins | irr post ruin | 1232ᴱ |
| 109 | Ruins | light stone wall ruin (H) | 676ᴱ |
| 110 | Ruins | light stone wall ruin (V) | 675ᴱ |
| 111 | Ruins | light stone column ruin | 677ᴱ |
| 112 | Ruins | light stone rubble | 674ᴱ |
| 113 | Ruins | rock wall ruin (H) | 685ᴱ |
| 114 | Ruins | rock wall ruin (V) | 684ᴱ |
| 115 | Ruins | rock wall column ruin | 686ᴱ |
| 116 | Ruins | rock rubble | 683ᴱ |
| 117 | Ruins | cave wall ruin (H) | 694ᴱ |
| 118 | Ruins | cave wall ruin (V) | 693ᴱ |
| 119 | Ruins | cave wall column ruin | 695ᴱ |
| 120 | Ruins | cave rubble | 692ᴱ |
| 121 | Ruins | Big City wood and stone rubble | 703ᴱ |
| 122 | Ruins | Big City wood and stone V | 704ᴱ |
| 123 | Ruins | Big City wood and stone H | 705ᴱ |
| 124 | Ruins | Big City wood and stone column ruin | 706ᴱ |
| 125 | Ruins | Big City stone wall ruin H | 938ᴱ |
| 126 | Ruins | Big City stone wall ruin V | 947ᴱ |
| 127 | Ruins | Big City wood sided wall ruin H | 965ᴱ |
| 128 | Ruins | Big City wood sided wall rubble | 1239ᴱ |
| 129 | Ruins | Big City log wall ruin | 1236ᴱ |
| 130 | Ruins | Big City log column ruin | 1238ᴱ |
| 131 | Ruins | dungeon dreary purple wall rubble | 1262ᴱ |
| 132 | Ruins | dungeon dreary purple wall ruin V | 1263ᴱ |
| 133 | Ruins | dungeon dreary purple wall ruin H | 1264ᴱ |
| 134 | Ruins | dungeon dreary purple column ruin | 1265ᴱ |
| 135 | Ruins | dungeon dreary desaturated blue rubble | 1286ᴱ |
| 136 | Ruins | dungeon dreary desaturated blue wall V | 1287ᴱ |
| 137 | Ruins | dungeon dreary desaturated blue wall H | 1288ᴱ |
| 138 | Ruins | dungeon dreary desaturated blue column | 1289ᴱ |
| 139 | Ruins | dungeon dreary 2x desaturated green rubble | 1310ᴱ |
| 140 | Ruins | dungeon dreary 2x desaturated green wall V | 1311ᴱ |
| 141 | Ruins | dungeon dreary 2x desaturated green wall H | 1312ᴱ |
| 142 | Ruins | dungeon dreary 2x desaturated green column | 1313ᴱ |
| 143 | Ruins | red brick rubble | 1344ᴱ |
| 144 | Ruins | red brick wall ruin (h) | 1346ᴱ |
| 145 | Ruins | red brick wall ruin (v) | 1345ᴱ |
| 146 | Ruins | red brick post ruin | 1343ᴱ |
| 147 | Ruins | icy cave rubble | 1352ᴱ |
| 148 | Ruins | icy cave wall ruin (h) | 1354ᴱ |
| 149 | Ruins | icy cave wall ruin (v) | 1353ᴱ |
| 150 | Ruins | icy cave post ruin | 1355ᴱ |
| 151 | Ruins | glacier rubble | 1360ᴱ |
| 152 | Ruins | glacier wall ruin (h) | 1359ᴱ |
| 153 | Ruins | glacier wall ruin (v) | 1361ᴱ |
| 154 | Ruins | glacier post ruin | 1363ᴱ |
| 155 | Ruins | nidavellir rubble | 1368ᴱ |
| 156 | Ruins | nidavellir wall ruin (h) | 1370ᴱ |
| 157 | Ruins | nidavellir wall ruin (v) | 1369ᴱ |
| 158 | Ruins | nidavellir post ruin | 1371ᴱ |

### Doors — `DoorComponent` (49 entries)

A door tile renders exactly one of these ids: closedId by default, openId when open, secretId when isSecret (looks like a wall), destroyedId when broken. Doors are placed ON the gap tile in a wall run, not on a wall tile (see §3.5).

| # | category | name | closedId | openId | destroyedId | secretId | isSecret | isOpen |
|---|---|---|---|---|---|---|---|---|
| 1 | Doors | Town (V) | 65ᴮ | 77ᴮ | 83ᴮ | 28ᴮ | false | false |
| 2 | Doors | Town (H) | 64ᴮ | 76ᴮ | 82ᴮ | 27ᴮ | false | false |
| 3 | Doors | TrapCellar Door | 972ᴱ | 973ᴱ | 8ᴮ | 15ᴮ | false | false |
| 4 | Doors | Temple (V) | 67ᴮ | 79ᴮ | 85ᴮ | 152ᴮ | false | false |
| 5 | Doors | Temple (H) | 66ᴮ | 78ᴮ | 84ᴮ | 151ᴮ | false | false |
| 6 | Doors | Marble (V) | 36ᴮ | 48ᴮ | 49ᴮ | 140ᴮ | false | false |
| 7 | Doors | Marble (H) | 35ᴮ | 47ᴮ | 37ᴮ | 139ᴮ | false | false |
| 8 | Doors | Dungeon (V) | 63ᴮ | 75ᴮ | 81ᴮ | 26ᴮ | false | false |
| 9 | Doors | Dungeon (H) | 62ᴮ | 74ᴮ | 80ᴮ | 25ᴮ | false | false |
| 10 | Doors | Runic (V) | 230ᴮ | 232ᴮ | 234ᴮ | 28ᴮ | false | false |
| 11 | Doors | Runic (H) | 229ᴮ | 231ᴮ | 233ᴮ | 27ᴮ | false | false |
| 12 | Doors | Egyptian (V) | 312ᴮ | 308ᴮ | 310ᴮ | 300ᴮ | false | false |
| 13 | Doors | Egyptian (H) | 311ᴮ | 307ᴮ | 309ᴮ | 299ᴮ | false | false |
| 14 | Doors | Red Shoji (V) | 379ᴮ | 392ᴮ | 405ᴮ | 363ᴮ | false | false |
| 15 | Doors | Red Shoji (H) | 378ᴮ | 391ᴮ | 404ᴮ | 362ᴮ | false | false |
| 16 | Doors | Jail (V) | 421ᴮ | 434ᴮ | 436ᴮ | 450ᴮ | false | false |
| 17 | Doors | Jail (H) | 420ᴮ | 433ᴮ | 435ᴮ | 449ᴮ | false | false |
| 18 | Doors | Steel (V) | 454ᴮ | 456ᴮ | 458ᴮ | 429ᴮ | false | false |
| 19 | Doors | Steel (H) | 453ᴮ | 455ᴮ | 457ᴮ | 428ᴮ | false | false |
| 20 | Doors | Dirty Marble (V) | 495ᴮ | 497ᴮ | 499ᴮ | 140ᴮ | false | false |
| 21 | Doors | Dirty Marble (H) | 494ᴮ | 496ᴮ | 498ᴮ | 139ᴮ | false | false |
| 22 | Doors | Dragon (H) | 504ᴮ | 506ᴮ | 508ᴮ | 151ᴮ | false | false |
| 23 | Doors | Dragon (V) | 505ᴮ | 507ᴮ | 509ᴮ | 152ᴮ | false | false |
| 24 | Doors | 4 panel door (H) | 1040ᴱ | 1041ᴱ | 1042ᴱ | 152ᴮ | false | false |
| 25 | Doors | 4 panel door (v) | 1043ᴱ | 1044ᴱ | 1045ᴱ | 152ᴮ | false | false |
| 26 | Doors | blue steel door (h) | 1046ᴱ | 1047ᴱ | 1047ᴱ | 152ᴮ | false | false |
| 27 | Doors | blue steel door (v) | 1049ᴱ | 1050ᴱ | 1050ᴱ | 152ᴮ | false | false |
| 28 | Doors | peephole door (h) | 1052ᴱ | 1053ᴱ | 1054ᴱ | 152ᴮ | false | false |
| 29 | Doors | peephole door (v) | 1055ᴱ | 1056ᴱ | 1057ᴱ | 152ᴮ | false | false |
| 30 | Doors | plain door (h) | 1058ᴱ | 1059ᴱ | 1060ᴱ | 152ᴮ | false | false |
| 31 | Doors | plain door (v) | 1061ᴱ | 1062ᴱ | 1063ᴱ | 152ᴮ | false | false |
| 32 | Doors | steel door (h) | 1064ᴱ | 1065ᴱ | 1065ᴱ | 152ᴮ | false | false |
| 33 | Doors | steel door (v) | 1067ᴱ | 1068ᴱ | 1068ᴱ | 152ᴮ | false | false |
| 34 | Doors | steel door rusted (h) | 1070ᴱ | 1071ᴱ | 1071ᴱ | 152ᴮ | false | false |
| 35 | Doors | steel door rusted (v) | 1073ᴱ | 1074ᴱ | 1074ᴱ | 152ᴮ | false | false |
| 36 | Doors | thin slat door (h) | 1076ᴱ | 1077ᴱ | 1078ᴱ | 152ᴮ | false | false |
| 37 | Doors | thin slat door (v) | 1079ᴱ | 1080ᴱ | 1081ᴱ | 152ᴮ | false | false |
| 38 | Doors | wide slat door (h) | 1082ᴱ | 1083ᴱ | 1084ᴱ | 152ᴮ | false | false |
| 39 | Doors | wide slat door (v) | 1085ᴱ | 1086ᴱ | 1087ᴱ | 152ᴮ | false | false |
| 40 | Doors | Big City Window H | 858ᴱ | 859ᴱ | 703ᴱ | 152ᴮ | false | false |
| 41 | Doors | Big City Window V | 860ᴱ | 861ᴱ | 703ᴱ | 152ᴮ | false | false |
| 42 | Doors | Big City wood-sided window H | 941ᴱ | 942ᴱ | 1239ᴱ | 152ᴮ | false | false |
| 43 | Doors | Big City wood-sided window V | 943ᴱ | 944ᴱ | 1239ᴱ | 152ᴮ | false | false |
| 44 | Doors | Big City L cemetary gate H | 948ᴱ | 949ᴱ | 949ᴱ | 152ᴮ | false | false |
| 45 | Doors | Big City R cemetary gate H | 950ᴱ | 951ᴱ | 951ᴱ | 152ᴮ | false | false |
| 46 | Doors | Big City log cabin window H | 962ᴱ | 961ᴱ | 1236ᴱ | 152ᴮ | false | false |
| 47 | Doors | Big City log cabin window V | 964ᴱ | 963ᴱ | 1236ᴱ | 152ᴮ | false | false |
| 48 | Doors | thin chamber door (h) | 1382ᴱ | 1383ᴱ | 1384ᴱ | 152ᴮ | false | false |
| 49 | Doors | thin chamber door (v) | 1385ᴱ | 1386ᴱ | 1387ᴱ | 152ᴮ | false | false |

### Staircases — `StaircaseComponent` (68 entries)

| # | category | name | teleporterId | descends | destinationRegion | destinationX | destinationY |
|---|---|---|---|---|---|---|---|
| 1 | Stairs | Down (NS) | 123ᴮ | true | 0 | 0 | 0 |
| 2 | Stairs | Down (WE) | 124ᴮ | true | 0 | 0 | 0 |
| 3 | Stairs | Down (EW) | 125ᴮ | true | 0 | 0 | 0 |
| 4 | Stairs | Down (SN) | 126ᴮ | true | 0 | 0 | 0 |
| 5 | Stairs | Up (NS) | 127ᴮ | false | 0 | 0 | 0 |
| 6 | Stairs | Up (WE) | 128ᴮ | false | 0 | 0 | 0 |
| 7 | Stairs | Up (EW) | 129ᴮ | false | 0 | 0 | 0 |
| 8 | Stairs | Up (SN) | 130ᴮ | false | 0 | 0 | 0 |
| 9 | Stairs | Down (Spiral) | 254ᴮ | true | 0 | 0 | 0 |
| 10 | Stairs | Up (Spiral) | 253ᴮ | false | 0 | 0 | 0 |
| 11 | Stairs | Blank Down (Spiral) | 1026ᴱ | true | 0 | 0 | 0 |
| 12 | Stairs | BW Marble Stairs Down South | 785ᴱ | true | 0 | 0 | 0 |
| 13 | Stairs | BW Marble Stairs Down East | 786ᴱ | true | 0 | 0 | 0 |
| 14 | Stairs | BW Marble Stairs Down West | 787ᴱ | true | 0 | 0 | 0 |
| 15 | Stairs | BW Marble Stairs Down North | 788ᴱ | true | 0 | 0 | 0 |
| 16 | Stairs | BW Marble Stairs Up North | 789ᴱ | false | 0 | 0 | 0 |
| 17 | Stairs | BW Marble Stairs Up West | 790ᴱ | false | 0 | 0 | 0 |
| 18 | Stairs | BW Marble Stairs Up East | 791ᴱ | false | 0 | 0 | 0 |
| 19 | Stairs | BW Marble Stairs Up South | 792ᴱ | false | 0 | 0 | 0 |
| 20 | Stairs | Blue Marble Stairs Down South | 793ᴱ | true | 0 | 0 | 0 |
| 21 | Stairs | Blue Marble Stairs Down East | 794ᴱ | true | 0 | 0 | 0 |
| 22 | Stairs | Blue Marble Stairs Down West | 795ᴱ | true | 0 | 0 | 0 |
| 23 | Stairs | Blue Marble Stairs Down North | 796ᴱ | true | 0 | 0 | 0 |
| 24 | Stairs | Blue Marble Stairs Up North | 797ᴱ | false | 0 | 0 | 0 |
| 25 | Stairs | Blue Marble Stairs Up West | 798ᴱ | false | 0 | 0 | 0 |
| 26 | Stairs | Blue Marble Stairs Up East | 799ᴱ | false | 0 | 0 | 0 |
| 27 | Stairs | Blue Marble Stairs Up South | 800ᴱ | false | 0 | 0 | 0 |
| 28 | Stairs | Rough Wood Stairs Down South | 801ᴱ | true | 0 | 0 | 0 |
| 29 | Stairs | Rough Wood Stairs Down East | 802ᴱ | true | 0 | 0 | 0 |
| 30 | Stairs | Rough Wood Stairs Down West | 803ᴱ | true | 0 | 0 | 0 |
| 31 | Stairs | Rough Wood Stairs Down South | 804ᴱ | true | 0 | 0 | 0 |
| 32 | Stairs | Rough Wood Stairs Up North | 805ᴱ | false | 0 | 0 | 0 |
| 33 | Stairs | Rough Wood Stairs Up West | 806ᴱ | false | 0 | 0 | 0 |
| 34 | Stairs | Rough Wood Stairs Up East | 807ᴱ | false | 0 | 0 | 0 |
| 35 | Stairs | Rough Wood Stairs Up South | 808ᴱ | false | 0 | 0 | 0 |
| 36 | Stairs | Fine Wood Stairs Down South | 809ᴱ | true | 0 | 0 | 0 |
| 37 | Stairs | Fine Wood Stairs Down East | 810ᴱ | true | 0 | 0 | 0 |
| 38 | Stairs | Fine Wood Stairs Down West | 811ᴱ | true | 0 | 0 | 0 |
| 39 | Stairs | Fine Wood Stairs Down North | 812ᴱ | true | 0 | 0 | 0 |
| 40 | Stairs | Fine Wood Stairs Up North | 813ᴱ | false | 0 | 0 | 0 |
| 41 | Stairs | Fine Wood Stairs Up West | 814ᴱ | false | 0 | 0 | 0 |
| 42 | Stairs | Fine Wood Stairs Up East | 815ᴱ | false | 0 | 0 | 0 |
| 43 | Stairs | Fine Wood Stairs Up South | 816ᴱ | false | 0 | 0 | 0 |
| 44 | Stairs | Rickety Wood Stairs Down South | 825ᴱ | true | 0 | 0 | 0 |
| 45 | Stairs | Rickety Wood Stairs Down East | 826ᴱ | true | 0 | 0 | 0 |
| 46 | Stairs | Rickety Wood Stairs Down West | 827ᴱ | true | 0 | 0 | 0 |
| 47 | Stairs | Rickety Wood Stairs Down North | 828ᴱ | true | 0 | 0 | 0 |
| 48 | Stairs | Rickety Wood Stairs Up North | 829ᴱ | false | 0 | 0 | 0 |
| 49 | Stairs | Rickety Wood Stairs Up West | 830ᴱ | false | 0 | 0 | 0 |
| 50 | Stairs | Rickety Wood Stairs Up East | 831ᴱ | false | 0 | 0 | 0 |
| 51 | Stairs | Rickety Wood Stairs Up South | 832ᴱ | false | 0 | 0 | 0 |
| 52 | Stairs | Decrepit Wood Stairs Down South | 833ᴱ | true | 0 | 0 | 0 |
| 53 | Stairs | Decrepit Wood Stairs Down East | 834ᴱ | true | 0 | 0 | 0 |
| 54 | Stairs | Decrepit Wood Stairs Down West | 835ᴱ | true | 0 | 0 | 0 |
| 55 | Stairs | Decrepit Wood Stairs Down North | 836ᴱ | true | 0 | 0 | 0 |
| 56 | Stairs | Decrepit Wood Stairs Up North | 837ᴱ | false | 0 | 0 | 0 |
| 57 | Stairs | Decrepit Wood Stairs Up West | 838ᴱ | false | 0 | 0 | 0 |
| 58 | Stairs | Decrepit Wood Stairs Up East | 839ᴱ | false | 0 | 0 | 0 |
| 59 | Stairs | Decrepit Wood Stairs Up South | 840ᴱ | false | 0 | 0 | 0 |
| 60 | Stairs | Dry Well | 968ᴱ | true | 0 | 0 | 0 |
| 61 | Stairs | Ladder Down South | 983ᴱ | true | 0 | 0 | 0 |
| 62 | Stairs | Ladder Down East | 984ᴱ | true | 0 | 0 | 0 |
| 63 | Stairs | Ladder Down West | 985ᴱ | true | 0 | 0 | 0 |
| 64 | Stairs | Ladder Down North | 986ᴱ | true | 0 | 0 | 0 |
| 65 | Stairs | Ladder Up North | 987ᴱ | false | 0 | 0 | 0 |
| 66 | Stairs | Ladder Up West | 988ᴱ | false | 0 | 0 | 0 |
| 67 | Stairs | Ladder Up East | 989ᴱ | false | 0 | 0 | 0 |
| 68 | Stairs | Ladder Up South | 990ᴱ | false | 0 | 0 | 0 |

### Shafts — `ShaftComponent` (7 entries)

| # | category | name | teleporterId | descends |
|---|---|---|---|---|
| 1 | Stairs | Pit | 8ᴮ | true |
| 2 | Stairs | Pit (Caved) | 181ᴮ | true |
| 3 | Stairs | Tunnel Entrance | 971ᴱ | true |
| 4 | Stairs | Dirt Hole | 969ᴱ | true |
| 5 | Stairs | Grassy Hole | 970ᴱ | true |
| 6 | Stairs | TrapCellar Door Down | 973ᴱ | true |
| 7 | Stairs | Sand Hole | 974ᴱ | true |

### Sky (fall-through) — `SkyComponent` (4 entries)

| # | category | name | teleporterId |
|---|---|---|---|
| 1 | Teleport | Air | 9ᴮ |
| 2 | Teleport | Dark Air | 1016ᴱ |
| 3 | Teleport | Dark Air Animated | 1017ᴱ |
| 4 | Teleport | Animated Portal | 1330ᴱ |

### Egress (segment exits) — `EgressComponent` (12 entries)

| # | category | name | egress | destinationSegment |
|---|---|---|---|---|
| 1 | Teleport | Leng | 315ᴮ | 2 |
| 2 | Teleport | Kesmai | 316ᴮ | 1 |
| 3 | Teleport | Oakvael | 328ᴮ | 4 |
| 4 | Teleport | Axe Glacier | 329ᴮ | 3 |
| 5 | Teleport | Underkingdom | 330ᴮ | 5 |
| 6 | Teleport | Torii | 332ᴮ |  |
| 7 | Teleport | Rift Glacier | 319ᴮ |  |
| 8 | Teleport | Shukumei | 331ᴮ |  |
| 9 | Teleport | Annwn | 318ᴮ |  |
| 10 | Teleport | Generic | 318ᴮ |  |
| 11 | Teleport | Moongate | 189ᴮ |  |
| 12 | Teleport | Moongate | 190ᴮ |  |

### Hidden teleporter — `HiddenTeleporterComponent` (1 entries)

| # | category | name | destinationRegion | destinationX | destinationY |
|---|---|---|---|---|---|
| 1 | Teleport | Hidden | 0 | 0 | 0 |

### Ropes — `RopeComponent` (30 entries)

| # | category | name | teleporterId | isSecret |
|---|---|---|---|---|
| 1 | Ropes | Climb Up (X South) | 237ᴮ | false |
| 2 | Ropes | Climb Up (X East) | 238ᴮ | false |
| 3 | Ropes | Climb Down (X West) | 241ᴮ | false |
| 4 | Ropes | Climb Up (X West) | 255ᴮ | false |
| 5 | Ropes | Down (South) | 256ᴮ | false |
| 6 | Ropes | Up (South) | 257ᴮ | false |
| 7 | Ropes | Climb Down (X West) | 512ᴮ | false |
| 8 | Ropes | Rope | 513ᴮ | false |
| 9 | Ropes | Rope | 514ᴮ | false |
| 10 | Ropes | Rope North and Up | 1388ᴱ | false |
| 11 | Ropes | Rope West and Up | 1389ᴱ | false |
| 12 | Ropes | Rope East and Up | 1390ᴱ | false |
| 13 | Ropes | Rope West and Down | 1391ᴱ | false |
| 14 | Ropes | Rope North and Down | 1392ᴱ | false |
| 15 | Ropes | Rope South and Up | 1393ᴱ | false |
| 16 | Ropes | Rope East/South and Down | 1394ᴱ | false |
| 17 | Ropes | Root North and Up | 1395ᴱ | false |
| 18 | Ropes | Root West and Up | 1396ᴱ | false |
| 19 | Ropes | Root East and Up | 1397ᴱ | false |
| 20 | Ropes | Root West and Down | 1398ᴱ | false |
| 21 | Ropes | Root South and Up | 1399ᴱ | false |
| 22 | Ropes | Root North and Down | 1400ᴱ | false |
| 23 | Ropes | Root East/South and Down | 1401ᴱ | false |
| 24 | Ropes | Vine North and Up | 1402ᴱ | false |
| 25 | Ropes | Vine West and Up | 1403ᴱ | false |
| 26 | Ropes | Vine East and Up | 1404ᴱ | false |
| 27 | Ropes | Vine West and Down | 1405ᴱ | false |
| 28 | Ropes | Vine North and Down | 1406ᴱ | false |
| 29 | Ropes | Vine South and Up | 1407ᴱ | false |
| 30 | Ropes | Vine East/South and Down | 1408ᴱ | false |

### Statics (decorations) — `StaticComponent` (357 entries)

| # | category | name | static | color |
|---|---|---|---|---|
| 1 | Vegetation | Jungle Foliage | 92ᴮ |  |
| 2 | Vegetation | Jungle Foliage | 93ᴮ |  |
| 3 | Vegetation | Jungle Foliage | 94ᴮ |  |
| 4 | Vegetation | Jungle Foliage | 95ᴮ |  |
| 5 | Vegetation | Tall Grass | 105ᴮ |  |
| 6 | Vegetation | Tall Reeds | 106ᴮ |  |
| 7 | Vegetation | Tall Grass | 107ᴮ |  |
| 8 | Vegetation | Wheat | 875ᴱ |  |
| 9 | Vegetation | Burnt Wheat | 876ᴱ |  |
| 10 | Vegetation | Corn | 873ᴱ |  |
| 11 | Vegetation | Burnt Corn | 874ᴱ |  |
| 12 | Vegetation | Grapevines | 877ᴱ |  |
| 13 | Vegetation | Burnt Grapevines | 878ᴱ |  |
| 14 | Vegetation | Tall Reeds | 108ᴮ |  |
| 15 | Vegetation | Tall Bamboo | 109ᴮ |  |
| 16 | Vegetation | Tall Bamboo | 110ᴮ |  |
| 17 | Vegetation | Heavy Snow | 121ᴮ |  |
| 18 | Vegetation | Heavy Snow | 122ᴮ |  |
| 19 | Vegetation | Creosote Bush | 205ᴮ |  |
| 20 | Vegetation | Red Flowers | 206ᴮ |  |
| 21 | Vegetation | Yellow Flowers | 207ᴮ |  |
| 22 | Vegetation | Large Oak Trunk | 208ᴮ |  |
| 23 | Vegetation | Fig Tree | 326ᴮ |  |
| 24 | Vegetation | Burnt Tree (L) | 101ᴮ |  |
| 25 | Vegetation | Burnt Tree (M) | 102ᴮ |  |
| 26 | Vegetation | Burnt Tree (S) | 103ᴮ |  |
| 27 | Vegetation | Burnt Wierd Tree | 372ᴮ |  |
| 28 | Vegetation | Burnt Fruit Tree | 897ᴱ |  |
| 29 | Vegetation | Dead Shrubs | 1002ᴮ |  |
| 30 | Vegetation | Dead Tree | 1005ᴮ |  |
| 31 | Vegetation | lilly pads | 1100ᴱ |  |
| 32 | Vegetation | swamp assorted | 1101ᴱ |  |
| 33 | Vegetation | reeds and cattails | 1102ᴱ |  |
| 34 | Vegetation | swamp flower purple | 1103ᴱ |  |
| 35 | Vegetation | swamp flower white | 1104ᴱ |  |
| 36 | Vegetation | lilly pad cluster | 1105ᴱ |  |
| 37 | Vegetation | cattail cluster | 1106ᴱ |  |
| 38 | Vegetation | tall reeds | 1107ᴱ |  |
| 39 | Vegetation | Swamp Cypress | 1112ᴱ |  |
| 40 | Vegetation | Swamp Cypress dead | 1113ᴱ |  |
| 41 | Vegetation | short hedge V | 1233ᴱ |  |
| 42 | Vegetation | short hedge H | 1234ᴱ |  |
| 43 | Vegetation | round topiari | 1243ᴱ |  |
| 44 | Vegetation | fir topiari | 1245ᴱ |  |
| 45 | Vegetation | med blooming mushroom | 1373ᴱ |  |
| 46 | Vegetation | large and med mushroom | 1374ᴱ |  |
| 47 | Vegetation | 2 med mushrooms | 1375ᴱ |  |
| 48 | Vegetation | large mushroom | 1376ᴱ |  |
| 49 | Vegetation | med mushroom | 1377ᴱ |  |
| 50 | Vegetation | small mushroom cluster (right) | 1378ᴱ |  |
| 51 | Vegetation | small mushroom cluster (left) | 1379ᴱ |  |
| 52 | Decorations | Boxing Ring | 114ᴮ |  |
| 53 | Decorations | Small Spring | 242ᴮ |  |
| 54 | Decorations | Fountain Pool | 209ᴮ |  |
| 55 | Decorations | Fountain Center | 210ᴮ |  |
| 56 | Decorations | Blood over Altar | 236ᴮ |  |
| 57 | Decorations | Blood Stains | 167ᴮ |  |
| 58 | Decorations | Gravestone (1) | 213ᴮ |  |
| 59 | Decorations | Gravestone (2) | 214ᴮ |  |
| 60 | Decorations | Gravestone (3) | 215ᴮ |  |
| 61 | Decorations | Grave (1) | 216ᴮ |  |
| 62 | Decorations | Grave (2) | 217ᴮ |  |
| 63 | Decorations | Mirror (H) | 117ᴮ |  |
| 64 | Decorations | Mirror (V) | 118ᴮ |  |
| 65 | Decorations | Torn Tapestry (H) | 171ᴮ |  |
| 66 | Decorations | Torn Tapestry (V) | 172ᴮ |  |
| 67 | Decorations | Oriental Tapestry (H) | 197ᴮ |  |
| 68 | Decorations | Oriental Tapestry (V) | 198ᴮ |  |
| 69 | Decorations | Red Carpet | 317ᴮ |  |
| 70 | Decorations | Crushed Bones | 173ᴮ |  |
| 71 | Decorations | Sordid Remains (H) | 211ᴮ |  |
| 72 | Decorations | Sordid Remains (V) | 212ᴮ |  |
| 73 | Decorations | Hanging Skeleton (H) | 220ᴮ |  |
| 74 | Decorations | Hanging Skeleton (V) | 221ᴮ |  |
| 75 | Decorations | Bookshelf (H) | 243ᴮ |  |
| 76 | Decorations | Bookshelf (V) | 244ᴮ |  |
| 77 | Decorations | librarybookshelf (H) | 764ᴱ |  |
| 78 | Decorations | librarybookshelf2 (V) | 765ᴱ |  |
| 79 | Decorations | Storage Shelf (H) | 439ᴮ |  |
| 80 | Decorations | Storage Shelf (V) | 440ᴮ |  |
| 81 | Decorations | Wizard Emblems (H) | 245ᴮ |  |
| 82 | Decorations | Wizard Emblems (V) | 246ᴮ |  |
| 83 | Decorations | Tailor Scraps | 250ᴮ |  |
| 84 | Decorations | Iron Throne | 219ᴮ |  |
| 85 | Decorations | Dragon Throne | 222ᴮ |  |
| 86 | Decorations | Oak Throne | 251ᴮ |  |
| 87 | Decorations | Treasure | 349ᴮ |  |
| 88 | Decorations | Campfire | 373ᴮ |  |
| 89 | Decorations | Crated Fruits | 880ᴱ |  |
| 90 | Decorations | Crated Veggies and Grains | 881ᴱ |  |
| 91 | Decorations | Sealed Crate (L) | 879ᴱ |  |
| 92 | Decorations | Open Crate (L) | 888ᴱ |  |
| 93 | Decorations | Destroyed Crate (L) | 889ᴱ |  |
| 94 | Decorations | Sealed Crate (S) | 886ᴱ |  |
| 95 | Decorations | Open Crate (S) | 890ᴱ |  |
| 96 | Decorations | Destroyed Crate (S) | 891ᴱ |  |
| 97 | Decorations | Price List (H) | 348ᴮ |  |
| 98 | Decorations | Price List (V) | 361ᴮ |  |
| 99 | Decorations | Dagger (H) | 385ᴮ |  |
| 100 | Decorations | Dagger (V) | 386ᴮ |  |
| 101 | Decorations | Mace (H) | 305ᴮ |  |
| 102 | Decorations | Mace (V) | 306ᴮ |  |
| 103 | Decorations | Jail Cot (H) | 411ᴮ |  |
| 104 | Decorations | Jail Cot (V) | 412ᴮ |  |
| 105 | Decorations | Crane (H) | 478ᴮ |  |
| 106 | Decorations | Crane (V) | 479ᴮ |  |
| 107 | Decorations | Fuji (H) | 490ᴮ |  |
| 108 | Decorations | Fuji (V) | 491ᴮ |  |
| 109 | Decorations | Wine Cask (V) | 401ᴮ |  |
| 110 | Decorations | Shimmering Wall (H) | 194ᴮ |  |
| 111 | Decorations | Shimmering Wall (V) | 195ᴮ |  |
| 112 | Decorations | Waterfall (H) | 191ᴮ |  |
| 113 | Decorations | Waterfall (V) | 192ᴮ |  |
| 114 | Decorations | Waterfall Animated (H) | 1006ᴮ |  |
| 115 | Decorations | Waterfall Animated (V) | 1007ᴮ |  |
| 116 | Decorations | snowdrift (H) | 762ᴱ |  |
| 117 | Decorations | snowdrift edge (H) | 660ᴱ |  |
| 118 | Decorations | snowdrift2 (V) | 763ᴱ |  |
| 119 | Decorations | snowdrift edge (V) | 659ᴱ |  |
| 120 | Decorations | webbed soul (H) | 661ᴱ |  |
| 121 | Decorations | webbed soul (V) | 662ᴱ |  |
| 122 | Decorations | web(H) | 663ᴱ |  |
| 123 | Decorations | web(V) | 664ᴱ |  |
| 124 | Decorations | crushed skeleton | 665ᴱ |  |
| 125 | Decorations | skeleton 1 | 668ᴱ |  |
| 126 | Decorations | skeleton 2 | 669ᴱ |  |
| 127 | Decorations | skeleton 3 | 678ᴱ |  |
| 128 | Decorations | skeleton 4 | 687ᴱ |  |
| 129 | Decorations | armored skeleton | 696ᴱ |  |
| 130 | Decorations | Closed Sarcophagus (H) | 424ᴮ |  |
| 131 | Decorations | Closed Sarcophagus (V) | 425ᴮ |  |
| 132 | Decorations | Open Sarcophagus (H) | 437ᴮ |  |
| 133 | Decorations | Open Sarcophagus (V) | 438ᴮ |  |
| 134 | Decorations | Torii (H) | 422ᴮ |  |
| 135 | Decorations | Torii (V) | 423ᴮ |  |
| 136 | Decorations | Congealed Lava | 137ᴮ |  |
| 137 | Decorations | Fog | 193ᴮ |  |
| 138 | Decorations | Barrel Water | 235ᴮ |  |
| 139 | Decorations | Mossy Pillar | 1001ᴮ |  |
| 140 | Decorations | Open Stones | 218ᴮ |  |
| 141 | Decorations | Sewer Wall Drain (1) | 632ᴱ |  |
| 142 | Decorations | Sewer Wall Drain (2) | 633ᴱ |  |
| 143 | Decorations | Sewer Wall Drain (3) | 634ᴱ |  |
| 144 | Decorations | Sewer Wall Drain (4) | 635ᴱ |  |
| 145 | Decorations | Sewer Wall (V) | 630ᴱ |  |
| 146 | Decorations | Sewer Wall (H) | 631ᴱ |  |
| 147 | Decorations | Sewer Wall Full (V) | 636ᴱ |  |
| 148 | Decorations | Sewer Wall Full (H) | 637ᴱ |  |
| 149 | Decorations | Collapsed Portal Pillar | 642ᴱ |  |
| 150 | Decorations | Shattered Stalagmite | 643ᴱ |  |
| 151 | Decorations | Vase (Base) | 649ᴱ |  |
| 152 | Decorations | Vase (Single Ring) | 650ᴱ |  |
| 153 | Decorations | Vase (Double Ring) | 651ᴱ |  |
| 154 | Decorations | Vase (Pattern 1) | 652ᴱ |  |
| 155 | Decorations | Vase (Pattern 2) | 653ᴱ |  |
| 156 | Decorations | Vase (Pattern 3) | 654ᴱ |  |
| 157 | Decorations | Vase (Shadow) | 655ᴱ |  |
| 158 | Decorations | Vase (Broken) | 656ᴱ |  |
| 159 | Decorations | Vases | 657ᴱ |  |
| 160 | Decorations |  Plaster-set Back-board (H)  | 726ᴱ |  |
| 161 | Decorations |  Plaster-set Back-board (V) | 729ᴱ |  |
| 162 | Decorations |  inside-back rope (H)  | 738ᴱ |  |
| 163 | Decorations |  left-inside rope (V)  | 739ᴱ |  |
| 164 | Decorations |  right flap-1 (V)  | 740ᴱ |  |
| 165 | Decorations |  red rug  | 741ᴱ |  |
| 166 | Decorations |  gray rug  | 742ᴱ |  |
| 167 | Decorations |  front flap-2 (H)  | 743ᴱ |  |
| 168 | Decorations |  inside back rope accent (H)  | 744ᴱ |  |
| 169 | Decorations |  inside-left rope accent (V)  | 745ᴱ |  |
| 170 | Decorations |  right flap-2 (V)  | 746ᴱ |  |
| 171 | Decorations |  square fur rug  | 747ᴱ |  |
| 172 | Decorations |  bear rug (V)  | 748ᴱ |  |
| 173 | Decorations |  front flap-1 accent (H)  | 749ᴱ |  |
| 174 | Decorations |  inside-back shade-screen (H)  | 750ᴱ |  |
| 175 | Decorations |  inside left shade screen (V)  | 751ᴱ |  |
| 176 | Decorations |  right flap-1 accent (V)  | 752ᴱ |  |
| 177 | Decorations |  bear rug (H)  | 753ᴱ |  |
| 178 | Decorations |  front flap-2 accent (H)  | 754ᴱ |  |
| 179 | Decorations |  inside back stripe accent (H)  | 755ᴱ |  |
| 180 | Decorations |  inside left stripe accent (V)  | 756ᴱ |  |
| 181 | Decorations |  right flap-2 accent (V)  | 757ᴱ |  |
| 182 | Decorations | Stair Rug Down South | 817ᴱ |  |
| 183 | Decorations | Stair Rug Down East | 818ᴱ |  |
| 184 | Decorations | Stair Rug Down West | 819ᴱ |  |
| 185 | Decorations | Stair Rug Down North | 820ᴱ |  |
| 186 | Decorations | Stair Rug Up North | 821ᴱ |  |
| 187 | Decorations | Stair Rug Up West | 822ᴱ |  |
| 188 | Decorations | Stair Rug Up East | 823ᴱ |  |
| 189 | Decorations | Stair Rug Up South | 824ᴱ |  |
| 190 | Decorations | Snow and Icey Stair Down South | 841ᴱ |  |
| 191 | Decorations | Snow and Icey Stair Down East | 842ᴱ |  |
| 192 | Decorations | Snow and Icey Stair Down West | 843ᴱ |  |
| 193 | Decorations | Snow and Icey Stair Down North | 844ᴱ |  |
| 194 | Decorations | Snow and Icey Stair Up North | 845ᴱ |  |
| 195 | Decorations | Snow and Icey Stair Up West | 846ᴱ |  |
| 196 | Decorations | Snow and Icey Stair Up East | 847ᴱ |  |
| 197 | Decorations | Snow and Icey Stair Up South | 848ᴱ |  |
| 198 | Decorations | Bloodied Stair Down South | 849ᴱ |  |
| 199 | Decorations | Bloodied Stair Down East | 850ᴱ |  |
| 200 | Decorations | Bloodied Stair Down West | 851ᴱ |  |
| 201 | Decorations | Bloodied Stair Down North | 852ᴱ |  |
| 202 | Decorations | Bloodied Stair Up North | 853ᴱ |  |
| 203 | Decorations | Bloodied Stair Up West | 854ᴱ |  |
| 204 | Decorations | Bloodied Stair Up East | 855ᴱ |  |
| 205 | Decorations | Bloodied Stair Up South | 856ᴱ |  |
| 206 | Decorations | Mossy Stairs Down South | 907ᴱ |  |
| 207 | Decorations | Mossy Stairs Down East | 908ᴱ |  |
| 208 | Decorations | Mossy Stairs Down West | 909ᴱ |  |
| 209 | Decorations | Mossy Stairs Down North | 910ᴱ |  |
| 210 | Decorations | Mossy Stairs Up North | 911ᴱ |  |
| 211 | Decorations | Mossy Stairs Up West | 912ᴱ |  |
| 212 | Decorations | Mossy Stairs Up East | 913ᴱ |  |
| 213 | Decorations | Mossy Stairs Up South | 914ᴱ |  |
| 214 | Decorations | Grassy Stairs Down South | 915ᴱ |  |
| 215 | Decorations | Grassy Stairs Down East | 916ᴱ |  |
| 216 | Decorations | Grassy Stairs Down West | 917ᴱ |  |
| 217 | Decorations | Grassy Stairs Down North | 918ᴱ |  |
| 218 | Decorations | Grassy Stairs Up North | 919ᴱ |  |
| 219 | Decorations | Grassy Stairs Up West | 920ᴱ |  |
| 220 | Decorations | Grassy Stairs Up East | 921ᴱ |  |
| 221 | Decorations | Grassy Stairs Up South | 922ᴱ |  |
| 222 | Decorations | Floral Stair Accent Down South | 923ᴱ |  |
| 223 | Decorations | Floral Stair Accent Down East | 924ᴱ |  |
| 224 | Decorations | Floral Stair Accent Down West | 925ᴱ |  |
| 225 | Decorations | Floral Stair Accent Down North | 926ᴱ |  |
| 226 | Decorations | Floral Stair Accent Up North | 927ᴱ |  |
| 227 | Decorations | Floral Stair Accent Up West | 928ᴱ |  |
| 228 | Decorations | Floral Stair Accent Up East | 929ᴱ |  |
| 229 | Decorations | Floral Stair Accent Up South | 930ᴱ |  |
| 230 | Decorations | swamp vines for tree column | 1109ᴱ |  |
| 231 | Decorations | swamp vines wrap for tree column | 1110ᴱ |  |
| 232 | Decorations | swamp vines floral for tree column | 1111ᴱ |  |
| 233 | Decorations | Magic circle 3 | 1188ᴱ |  |
| 234 | Decorations | Magic circle 2 | 1189ᴱ |  |
| 235 | Decorations | Magic circle 1 | 1190ᴱ |  |
| 236 | Decorations | lectern (h) | 1191ᴱ |  |
| 237 | Decorations | lectern (v) | 1192ᴱ |  |
| 238 | Decorations | desk (h) | 1193ᴱ |  |
| 239 | Decorations | desk (v) | 1194ᴱ |  |
| 240 | Decorations | single bed (v) | 1195ᴱ |  |
| 241 | Decorations | single bed (h) | 1205ᴱ |  |
| 242 | Decorations | double bed (v) | 1196ᴱ |  |
| 243 | Decorations | double bed (h) | 1206ᴱ |  |
| 244 | Decorations | rightfacing chair (h) | 1197ᴱ |  |
| 245 | Decorations | southfacing chair (v) | 1198ᴱ |  |
| 246 | Decorations | leftfacing chair (h) | 1199ᴱ |  |
| 247 | Decorations | northfacing chair (v) | 1200ᴱ |  |
| 248 | Decorations | wardrobe (v) | 1201ᴱ |  |
| 249 | Decorations | wardrobe (h) | 1202ᴱ |  |
| 250 | Decorations | nightstand (h) | 1203ᴱ |  |
| 251 | Decorations | nightstand (v) | 1204ᴱ |  |
| 252 | Decorations | bunk (v) | 1207ᴱ |  |
| 253 | Decorations | bunk (h) | 1208ᴱ |  |
| 254 | Decorations | big chest (h) | 1209ᴱ |  |
| 255 | Decorations | big chest (v) | 1210ᴱ |  |
| 256 | Decorations | nightstand (h) chamber pot,wash basin, candle | 1211ᴱ |  |
| 257 | Decorations | nightstand (v) candle | 1212ᴱ |  |
| 258 | Decorations | cauldron | 1242ᴱ |  |
| 259 | Decorations | headstone 1 | 1244ᴱ |  |
| 260 | Decorations | small headstone 1 | 1247ᴱ |  |
| 261 | Decorations | cross headstone 1 | 1248ᴱ |  |
| 262 | Decorations | sleeping woman sarcophagus V | 1249ᴱ |  |
| 263 | Decorations | blank sarcophagus V | 1250ᴱ |  |
| 264 | Decorations | rejuvinated sarcophagus V | 1251ᴱ |  |
| 265 | Decorations | headstone 1 V | 1252ᴱ |  |
| 266 | Decorations | small headstone 1 V | 1253ᴱ |  |
| 267 | Decorations | cross headstone 1 V | 1254ᴱ |  |
| 268 | Decorations | rejuvinated sarcophagus H | 1255ᴱ |  |
| 269 | Decorations | sleeping woman sarophagus H | 1256ᴱ |  |
| 270 | Decorations | blank sarcophagus H | 1257ᴱ |  |
| 271 | Decorations | purple cultist statue | 1274ᴱ |  |
| 272 | Decorations | blue cultist statue | 1298ᴱ |  |
| 273 | Decorations | green cultist statue | 1322ᴱ |  |
| 274 | Decorations | purple maiden statue | 1275ᴱ |  |
| 275 | Decorations | blue maiden statue | 1299ᴱ |  |
| 276 | Decorations | green maiden statue | 1323ᴱ |  |
| 277 | lighting and shade | Torchlight (H) | 931ᴱ |  |
| 278 | lighting and shade | Torchlight (V) | 932ᴱ |  |
| 279 | lighting and shade | Wall Brazier (H) | 976ᴱ |  |
| 280 | lighting and shade | Wall Brazier (V) | 977ᴱ |  |
| 281 | lighting and shade | Wall Brazier Greenfire(H) | 978ᴱ |  |
| 282 | lighting and shade | Wall Brazier Greenfire(V) | 979ᴱ |  |
| 283 | lighting and shade | Wall Brazier Bluefire(H) | 980ᴱ |  |
| 284 | lighting and shade | Wall Brazier Bluefire(V) | 981ᴱ |  |
| 285 | lighting and shade | Wall Darkened (H) | 933ᴱ |  |
| 286 | lighting and shade | Wall Darkened (V) | 934ᴱ |  |
| 287 | lighting and shade | Floor Darkened | 935ᴱ |  |
| 288 | lighting and shade | Floor Brazier | 975ᴱ |  |
| 289 | lighting and shade | Sidewall Darkened (V) | 1038ᴱ |  |
| 290 | lighting and shade | Sidewall Darkened (H) | 1039ᴱ |  |
| 291 | lighting and shade | Candelabra | 982ᴱ |  |
| 292 | lighting and shade | Candelabra without Shade | 1025ᴱ |  |
| 293 | lighting and shade | torches (H) no shade | 1029ᴱ |  |
| 294 | lighting and shade | torches (v) no shade | 1030ᴱ |  |
| 295 | lighting and shade | floor brazier without shade | 1037ᴱ |  |
| 296 | lighting and shade | wall brazier without shade (H) | 1035ᴱ |  |
| 297 | lighting and shade | wall brazier without shade (V) | 1036ᴱ |  |
| 298 | lighting and shade | blue wall brazier without shade (H) | 1031ᴱ |  |
| 299 | lighting and shade | blue wall brazier without shade (V) | 1032ᴱ |  |
| 300 | lighting and shade | green wall brazier without shade (H) | 1033ᴱ |  |
| 301 | lighting and shade | green wall brazier without shade (V) | 1034ᴱ |  |
| 302 | Misc. | Animated campfire | 766ᴱ |  |
| 303 | Grove | None | 226ᴮ |  |
| 304 | Grove | None | 227ᴮ |  |
| 305 | Wall Doodads (H) | Shield Ornamental (for the shadow) (H) | 767ᴱ |  |
| 306 | Wall Doodads (H) | Crossed swords (H) | 768ᴱ |  |
| 307 | Wall Doodads (H) | Shiny Shield Ornamental (H) | 769ᴱ |  |
| 308 | Wall Doodads (H) | Shield Ornamental Trim 1 (H) | 770ᴱ |  |
| 309 | Wall Doodads (H) | Shield Ornamental Trim 2 (H) | 771ᴱ |  |
| 310 | Wall Doodads (H) | Shield Ornamental Matte Shield (H) | 772ᴱ |  |
| 311 | Wall Doodads (H) | Shield Ornamental Chevron (H) | 773ᴱ |  |
| 312 | Wall Doodads (H) | Shield Ornamental inverted Chevron (H) | 774ᴱ |  |
| 313 | Wall Doodads (H) | Banner Low Contrast (H) | 775ᴱ |  |
| 314 | Wall Doodads (H) | Banner trim 1 (H) | 776ᴱ |  |
| 315 | Wall Doodads (H) | Banner Yasnaki symbol (H) | 777ᴱ |  |
| 316 | Wall Doodads (H) | Banner High contrast (H) | 778ᴱ |  |
| 317 | Wall Doodads (H) | Banner Mu Symbol (H) | 779ᴱ |  |
| 318 | Wall Doodads (H) | Banner pole (H) | 780ᴱ |  |
| 319 | Wall Doodads (H) | Banner trim 2 (H) | 781ᴱ |  |
| 320 | Wall Doodads (H) | Banner Kesmai Dragon symbol (H) | 782ᴱ |  |
| 321 | Wall Doodads (H) | dragon head mount (v) | 1136ᴱ |  |
| 322 | Wall Doodads (H) | dragon head mount (h) | 1137ᴱ |  |
| 323 | Wall Doodads (H) | vampire portrait (v) | 1138ᴱ |  |
| 324 | Wall Doodads (H) | vampire portrait (h) | 1139ᴱ |  |
| 325 | Wall Doodads (H) | dragon head arch topper (h) | 1141ᴱ |  |
| 326 | Wall Doodads (H) | dragon head arch topper (v) | 1142ᴱ |  |
| 327 | Wall Doodads (H) | bull head arch topper (h) | 1143ᴱ |  |
| 328 | Wall Doodads (H) | bull head arch topper (v) | 1144ᴱ |  |
| 329 | Wall Doodads (H) | lion head arch topper (v) | 1159ᴱ |  |
| 330 | Wall Doodads (H) | lion head arch topper (h) | 1160ᴱ |  |
| 331 | Wall Doodads (H) | stained glass - dragon (v) | 1171ᴱ |  |
| 332 | Wall Doodads (H) | stained glass - dragon (h) | 1172ᴱ |  |
| 333 | Wall Doodads (H) | red dragon banner (v) | 1173ᴱ |  |
| 334 | Wall Doodads (H) | red dragon banner (h) | 1174ᴱ |  |
| 335 | Wall Doodads (H) | dragon mural (v) | 1175ᴱ |  |
| 336 | Wall Doodads (H) | dragon mural (h) | 1176ᴱ |  |
| 337 | Wall Doodads (H) | stained glass - priest (v) | 1177ᴱ |  |
| 338 | Wall Doodads (H) | stained glass - priest (h) | 1178ᴱ |  |
| 339 | Wall Doodads (H) | stained glass - court (v) | 1179ᴱ |  |
| 340 | Wall Doodads (H) | stained glass - court (h) | 1180ᴱ |  |
| 341 | Wall Doodads (H) | purple Mu banner (v) | 1181ᴱ |  |
| 342 | Wall Doodads (H) | purple Mu banner (h) | 1182ᴱ |  |
| 343 | Wall Doodads (H) | green banner (v) | 1183ᴱ |  |
| 344 | Wall Doodads (H) | green banner (h) | 1184ᴱ |  |
| 345 | Wall Doodads (H) | black banner (h) | 1187ᴱ |  |
| 346 | Wall Doodads (H) | purple bat ornament (h) | 1276ᴱ |  |
| 347 | Wall Doodads (H) | purple bat ornament (v) | 1277ᴱ |  |
| 348 | Wall Doodads (H) | blue bat ornament (h) | 1300ᴱ |  |
| 349 | Wall Doodads (H) | blue bat ornament (v) | 1301ᴱ |  |
| 350 | Wall Doodads (H) | green bat ornament (h) | 1324ᴱ |  |
| 351 | Wall Doodads (H) | green bat ornament (v) | 1325ᴱ |  |
| 352 | Wall Doodads (H) | purple wall carving (h) | 1278ᴱ |  |
| 353 | Wall Doodads (H) | purple wall carving (v) | 1279ᴱ |  |
| 354 | Wall Doodads (H) | blue wall carving (h) | 1302ᴱ |  |
| 355 | Wall Doodads (H) | blue wall carving (v) | 1303ᴱ |  |
| 356 | Wall Doodads (H) | green wall carving (h) | 1326ᴱ |  |
| 357 | Wall Doodads (H) | green wall carving (v) | 1327ᴱ |  |

### Trees — `TreeComponent` (29 entries)

| # | category | name | tree | canGrow |
|---|---|---|---|---|
| 1 | Vegetation | Large Tree | 98ᴮ | true |
| 2 | Vegetation | Medium Tree | 99ᴮ | true |
| 3 | Vegetation | Small Tree | 100ᴮ | true |
| 4 | Vegetation | Large Pine Tree | 199ᴮ | true |
| 5 | Vegetation | Medium Pine Tree | 200ᴮ | true |
| 6 | Vegetation | Small Pine Tree | 201ᴮ | true |
| 7 | Vegetation | Large Pine Tree (Snow) | 202ᴮ | true |
| 8 | Vegetation | Medium Pine Tree (Snow) | 203ᴮ | true |
| 9 | Vegetation | Small Pine Tree (Snow) | 204ᴮ | true |
| 10 | Vegetation | Small Jungle Tree | 247ᴮ | true |
| 11 | Vegetation | Wierd Tree | 370ᴮ | true |
| 12 | Vegetation | Bamboo | 403ᴮ | true |
| 13 | Vegetation | Palm Tree [Tenser] | 624ᴱ | false |
| 14 | Vegetation | Large Palm Tree (1) [Tenser] | 625ᴱ | false |
| 15 | Vegetation | Large Palm Tree (2) [Tenser] | 626ᴱ | false |
| 16 | Vegetation | Banana Tree [Tenser] | 627ᴱ | false |
| 17 | Vegetation | Pear Tree | 893ᴱ | false |
| 18 | Vegetation | Peach Tree | 894ᴱ | false |
| 19 | Vegetation | Apple Tree | 895ᴱ | false |
| 20 | Vegetation | Orange Tree | 896ᴱ | false |
| 21 | Vegetation | Cherry Tree | 905ᴱ | false |
| 22 | Vegetation | Cherry Tree (Blossoms) | 906ᴱ | false |
| 23 | Vegetation | Autumn Brown Tree | 898ᴱ | false |
| 24 | Vegetation | Autumn Orange Tree | 899ᴱ | false |
| 25 | Vegetation | Autumn Light Red Tree | 901ᴱ | false |
| 26 | Vegetation | Autumn Dark Red Tree | 900ᴱ | false |
| 27 | Vegetation | Autumn Yellow Tree | 902ᴱ | false |
| 28 | Vegetation | Dormant Deciduous Tree | 903ᴱ | false |
| 29 | Vegetation | Frozen Deciduous Tree | 904ᴱ | false |

### Obstructions — `ObstructionComponent` (31 entries)

| # | category | name | obstruction | blockVision |
|---|---|---|---|---|
| 1 | Obstructions | Reef | 19ᴮ | false |
| 2 | Obstructions | Reef [Zrikz] | 605ᴮ | false |
| 3 | Obstructions | Iron Porticullus (H) | 165ᴮ | false |
| 4 | Obstructions | Iron Porticullus (V) | 166ᴮ | false |
| 5 | Obstructions | Jail (H) | 449ᴮ | false |
| 6 | Obstructions | Jail (V) | 450ᴮ | false |
| 7 | Obstructions | Massive Anvil | 164ᴮ | false |
| 8 | Obstructions | Cart (H) | 892ᴱ | false |
| 9 | Obstructions | Cart (V) | 887ᴱ | false |
| 10 | Obstructions | Crate (L) | 879ᴱ | false |
| 11 | Obstructions | Crate of Grains | 882ᴱ | false |
| 12 | Obstructions | Mace Display Crate | 883ᴱ | false |
| 13 | Obstructions | Greataxe Display Crate | 884ᴱ | false |
| 14 | Obstructions | Sword Display Crate | 885ᴱ | false |
| 15 | Obstructions | Heavy Oak | 266ᴮ | true |
| 16 | Obstructions | Dirty Marble Pillar | 168ᴮ | true |
| 17 | Obstructions | Sandstone Pillar | 313ᴮ | true |
| 18 | Obstructions | Large dragonscale pillar | 857ᴱ | true |
| 19 | Obstructions | small dragonscale pillar | 866ᴱ | true |
| 20 | Obstructions | Big City cemetary fence post | 954ᴱ | true |
| 21 | Obstructions | Big City gargoyle Gate post | 955ᴱ | true |
| 22 | Obstructions | Big City knight memorial | 1246ᴱ | true |
| 23 | Obstructions | dungeon dreary plain king statue | 1280ᴱ | true |
| 24 | Obstructions | dungeon dreary blue king statue | 1304ᴱ | true |
| 25 | Obstructions | dungeon dreary green king statue | 1328ᴱ | true |
| 26 | Obstructions | dungeon dreary plain dragon statue | 1281ᴱ | true |
| 27 | Obstructions | dungeon dreary blue dragon statue | 1305ᴱ | true |
| 28 | Obstructions | dungeon dreary green dragon statue | 1329ᴱ | true |
| 29 | Obstructions | dungeon dreary purple column | 1271ᴱ | true |
| 30 | Obstructions | dungeon dreary blue column | 1295ᴱ | true |
| 31 | Obstructions | dungeon dreary green column | 1319ᴱ | true |

### Counters — `CounterComponent` (12 entries)

| # | category | name | counter |
|---|---|---|---|
| 1 | Counters and Altars | Wood (H) | 86ᴮ |
| 2 | Counters and Altars | Wood (V) | 87ᴮ |
| 3 | Counters and Altars | Slate (H) | 96ᴮ |
| 4 | Counters and Altars | Slate (V) | 97ᴮ |
| 5 | Counters and Altars | Gilded (H) | 248ᴮ |
| 6 | Counters and Altars | Gilded (V) | 249ᴮ |
| 7 | Counters and Altars | Table (H) | 267ᴮ |
| 8 | Counters and Altars | Table (V) | 268ᴮ |
| 9 | Counters and Altars | Alchemy Table (H) | 269ᴮ |
| 10 | Counters and Altars | Alchemy Table (V) | 270ᴮ |
| 11 | Counters and Altars | Stone Table (H) | 399ᴮ |
| 12 | Counters and Altars | Stone Table (V) | 400ᴮ |

### Altars — `AltarComponent` (12 entries)

| # | category | name | altar |
|---|---|---|---|
| 1 | Counters and Altars | Temple Altar | 113ᴮ |
| 2 | Counters and Altars | Granite Altar (1) | 138ᴮ |
| 3 | Counters and Altars | Granite Altar (2) | 163ᴮ |
| 4 | Counters and Altars | Skull Altar | 169ᴮ |
| 5 | Counters and Altars | Carved Wood Altar | 174ᴮ |
| 6 | Counters and Altars | Egyptian Altar (1) | 278ᴮ |
| 7 | Counters and Altars | Egyptian Altar (2) | 290ᴮ |
| 8 | Counters and Altars | Egyptian Altar (3) | 302ᴮ |
| 9 | Counters and Altars | Egyptian Altar (4) | 314ᴮ |
| 10 | Counters and Altars | Egyptian Altar (5) | 324ᴮ |
| 11 | Counters and Altars | Egyptian Altar (6) | 327ᴮ |
| 12 | Counters and Altars | Blue Marble (6) | 368ᴮ |

### Lockers — `LockersComponent` (2 entries)

| # | category | name | static |
|---|---|---|---|
| 1 | Misc. | Lockers (H) | 119ᴮ |
| 2 | Misc. | Lockers (V) | 120ᴮ |

### Trash — `TrashComponent` (1 entries)

| # | category | name | static |
|---|---|---|---|
| 1 | Misc. | Trash Barrel | 88ᴮ |

### Traps (one palette entry each)

| type | category | name | props |
|---|---|---|---|
| WhirlwindTrap | Traps | Whirlwind | {'direction': '5', 'skill': '3'} |
| PoisonCloudTrap | Traps | Poison Cloud | {'direction': '5', 'skill': '3'} |
| BonfireTrap | Traps | Bonfire | {'skill': '3'} |
| FirestormTrap | Traps | Firestorm | {'skill': '3'} |
| ConcussionTrap | Traps | Concussion | {'skill': '3'} |
| LightningBoltTrap | Traps | Lightning Bolt | {'skill': '3'} |
| BlindTrap | Traps | Blind | {'skill': '3'} |
| FearTrap | Traps | Fear | {'skill': '3'} |
| StunTrap | Traps | Stun | {'skill': '3'} |
| DamageTrap | Traps | Damage | {'damage': '3'} |
| ActionTrap | Traps | Action | {} |


## Appendix B. Terrain-External.xml index (882 terrains)

Columns: id, label (from the XML comment next to the terrain), action, cost, draw order, underpile, texture (path under `Content/`, no extension), source rect `(x,y,w,h)`, offset, anim/res flags.

| id | label | act | cost | ord | up | texture | source | offset | notes |
|---|---|---|---|---|---|---|---|---|---|
| 622 |  | 0 | 6 | 0 |  | Tenser/Terrain/Water-Wave-Horizontal | (0,0,2000,100) |  | anim 20f step150 |
| 623 |  | 0 | 6 | 0 |  | Tenser/Terrain/Water-Wave-Vertical | (0,0,2000,100) |  | anim 20f step150 |
| 624 |  | 0 |  | 1 | true | Tenser/Terrain/Trees | (0,0,100,100) |  |  |
| 625 |  | 0 |  | 1 | true | Tenser/Terrain/Trees | (0,100,100,100) |  |  |
| 626 |  | 0 |  | 1 | true | Tenser/Terrain/Trees | (100,100,100,100) |  |  |
| 627 |  | 0 |  | 1 | true | Tenser/Terrain/Trees | (100,0,100,100) |  |  |
| 628 | Sewer Drain | 0 |  | 0 |  | Tenser/Terrain/Sewers | (0,0,100,100) |  |  |
| 629 | Sewer Floor | 0 |  | 0 |  | Tenser/Terrain/Sewers | (0,100,100,100) |  |  |
| 630 | Sewer Half-Wall (V) | 0 |  | 4 |  | Tenser/Terrain/Sewers | (100,0,100,100) |  |  |
| 631 | Sewer Half-Wall (H) | 0 |  | 5 |  | Tenser/Terrain/Sewers | (200,0,100,100) |  |  |
| 632 | Sewer Drain Round (V) | 0 |  | 4 |  | Tenser/Terrain/Sewers | (100,100,100,100) |  |  |
| 633 | Sewer Drain Round (H) | 0 |  | 5 |  | Tenser/Terrain/Sewers | (300,100,100,100) |  |  |
| 634 | Sewer Drain Floor (H) | 0 |  | 5 |  | Tenser/Terrain/Sewers | (300,0,100,100) |  |  |
| 635 | Sewer Drain Floor (V) | 0 |  | 4 |  | Tenser/Terrain/Sewers | (200,100,100,100) |  |  |
| 636 | Sewer Wall Full (V) | 0 |  | 4 |  | Tenser/Terrain/Sewers | (400,0,100,100) |  |  |
| 637 | Sewer Wall Full (H) | 13 |  | 5 |  | Tenser/Terrain/Sewers | (400,100,100,100) |  |  |
| 638 | Sewer Wall Ruins (H) | 0 | 6 | 5 |  | Tenser/Terrain/Sewers | (0,200,100,100) |  |  |
| 639 | Sewer Wall Ruins (V) | 0 | 6 | 3 |  | Tenser/Terrain/Sewers | (100,200,100,100) |  |  |
| 640 |  | 0 |  | 4 |  | Tenser/Terrain/BrokenPortalPillar | (0,0,100,100) |  |  |
| 641 |  | 0 |  | 4 |  | Tenser/Terrain/BrokenStalagmite | (0,0,100,100) |  |  |
| 642 |  | 0 |  | 4 |  | Tenser/Terrain/BrokenPortalPillar-2 | (0,0,100,100) |  |  |
| 643 |  | 0 |  | 4 |  | Tenser/Terrain/BrokenStalagmite-2 | (0,0,100,100) |  |  |
| 644 | wainscotting side V | 0 |  | 4 |  | Tenser/Terrain/millwork | (0,400,100,100) |  |  |
| 645 | wainscotting side white V | 0 |  | 4 |  | Tenser/Terrain/millwork | (100,400,100,100) |  |  |
| 646 | crown and foot moulding V | 0 |  | 4 |  | Tenser/Terrain/millwork | (200,400,100,100) |  |  |
| 647 | wainscotting side H | 0 |  | 5 |  | Tenser/Terrain/millwork | (300,400,100,100) |  |  |
| 648 | wainscotting side white H | 0 |  | 5 |  | Tenser/Terrain/millwork | (400,400,100,100) |  |  |
| 649 | Vase (base) | 0 |  | 1 |  | Tenser/Terrain/Pottery | (0,0,100,100) |  |  |
| 650 | Vase (Single Ring) | 0 |  | 1 |  | Tenser/Terrain/Pottery | (0,100,100,100) |  |  |
| 651 | Vase (Double Ring) | 0 |  | 1 |  | Tenser/Terrain/Pottery | (100,0,100,100) |  |  |
| 652 | Vase (Pattern 1) | 0 |  | 1 |  | Tenser/Terrain/Pottery | (200,0,100,100) |  |  |
| 653 | Vase (Pattern 2) | 0 |  | 1 |  | Tenser/Terrain/Pottery | (200,100,100,100) |  |  |
| 654 | Vase (Pattern 3) | 0 |  | 1 |  | Tenser/Terrain/Pottery | (200,200,100,100) |  |  |
| 655 | Vase (Shadow) | 0 |  | 1 |  | Tenser/Terrain/Pottery | (100,200,100,100) |  |  |
| 656 | Vase (Broken) | 0 |  | 1 |  | Tenser/Terrain/Pottery | (0,200,100,100) |  |  |
| 657 | Vases | 0 |  | 1 |  | Tenser/Terrain/Pottery | (100,100,100,100) |  |  |
| 658 | crown and foot moulding H | 0 |  | 5 |  | Tenser/Terrain/millwork | (500,400,100,100) |  |  |
| 659 | snowdrift edge v | 0 |  | 4 |  | Tenser/Terrain/snowdriftedges | (0,0,100,100) |  |  |
| 660 | snowdrift edge h | 0 |  | 5 |  | Tenser/Terrain/snowdriftedges | (100,0,100,100) |  |  |
| 661 | webbed soul H | 0 |  | 5 |  | Tenser/Terrain/rocktiles | (0,0,100,100) |  |  |
| 662 | webbed soul V | 0 |  | 4 |  | Tenser/Terrain/rocktiles | (100,0,100,100) |  |  |
| 663 | web H | 0 |  | 5 |  | Tenser/Terrain/rocktiles | (200,0,100,100) |  |  |
| 664 | web V | 0 |  | 4 |  | Tenser/Terrain/rocktiles | (300,0,100,100) |  |  |
| 665 | crushed skellie | 0 |  | 1 |  | Tenser/Terrain/rocktiles | (400,0,100,100) |  |  |
| 666 | stacked boxes | 5 |  | 1 |  | Tenser/Terrain/rocktiles | (500,0,100,100) |  |  |
| 667 | stacked boxes blownup | 1 |  | 1 |  | Tenser/Terrain/rocktiles | (600,0,100,100) |  |  |
| 668 | skeleton 1 | 0 |  | 1 |  | Tenser/Terrain/rocktiles | (700,0,100,100) |  |  |
| 669 | skeleton 2 | 0 |  | 1 |  | Tenser/Terrain/rocktiles | (800,0,100,100) |  |  |
| 670 | light stone wall H | 13 |  | 5 |  | Tenser/Terrain/rocktiles | (0,100,100,100) |  |  |
| 671 | light stone floor | 0 |  | 0 |  | Tenser/Terrain/rocktiles | (100,100,100,100) |  |  |
| 672 | light stone wall V | 13 |  | 4 |  | Tenser/Terrain/rocktiles | (200,100,100,100) |  |  |
| 673 | light stone column | 0 |  | 4 |  | Tenser/Terrain/rocktiles | (300,100,100,100) |  |  |
| 674 | light stone rubble | 0 |  | 3 |  | Tenser/Terrain/rocktiles | (400,100,100,100) |  |  |
| 675 | light stone V wall ruin | 0 |  | 4 |  | Tenser/Terrain/rocktiles | (500,100,100,100) |  |  |
| 676 | light stone H wall ruin | 0 |  | 5 |  | Tenser/Terrain/rocktiles | (600,100,100,100) |  |  |
| 677 | light stone column ruin | 0 |  | 4 |  | Tenser/Terrain/rocktiles | (700,100,100,100) |  |  |
| 678 | skeleton 3 | 0 |  | 1 |  | Tenser/Terrain/rocktiles | (800,100,100,100) |  |  |
| 679 | rock wall H | 13 |  | 5 |  | Tenser/Terrain/rocktiles | (0,200,100,100) |  |  |
| 680 | rock floor | 0 |  | 0 |  | Tenser/Terrain/rocktiles | (100,200,100,100) |  |  |
| 681 | rock wall V | 13 |  | 4 |  | Tenser/Terrain/rocktiles | (200,200,100,100) |  |  |
| 682 | rock column | 0 |  | 4 |  | Tenser/Terrain/rocktiles | (300,200,100,100) |  |  |
| 683 | rock rubble | 0 |  | 3 |  | Tenser/Terrain/rocktiles | (400,200,100,100) |  |  |
| 684 | rock wall ruin V | 0 |  | 4 |  | Tenser/Terrain/rocktiles | (500,200,100,100) |  |  |
| 685 | rock wall ruin H | 0 |  | 5 |  | Tenser/Terrain/rocktiles | (600,200,100,100) |  |  |
| 686 | rock column ruin | 0 |  | 4 |  | Tenser/Terrain/rocktiles | (700,200,100,100) |  |  |
| 687 | skeleton 4 | 0 |  | 1 |  | Tenser/Terrain/rocktiles | (800,200,100,100) |  |  |
| 688 | cave wall H | 13 |  | 5 |  | Tenser/Terrain/rocktiles | (0,300,100,100) |  |  |
| 689 | cave floor | 0 |  | 1 |  | Tenser/Terrain/rocktiles | (100,300,100,100) |  |  |
| 690 | cave wall V | 13 |  | 4 |  | Tenser/Terrain/rocktiles | (200,300,100,100) |  |  |
| 691 | cave column | 0 |  | 4 |  | Tenser/Terrain/rocktiles | (300,300,100,100) |  |  |
| 692 | cave rubble | 0 |  | 3 |  | Tenser/Terrain/rocktiles | (400,300,100,100) |  |  |
| 693 | cave wall V ruin | 0 |  | 4 |  | Tenser/Terrain/rocktiles | (500,300,100,100) |  |  |
| 694 | cave wall H ruin | 0 |  | 5 |  | Tenser/Terrain/rocktiles | (600,300,100,100) |  |  |
| 695 | cave column ruin | 0 |  | 4 |  | Tenser/Terrain/rocktiles | (700,300,100,100) |  |  |
| 696 | armored skeleton | 0 |  | 1 |  | Tenser/Terrain/rocktiles | (800,300,100,100) |  |  |
| 697 | Animated Fireplace (H) | 13 | 0 | 5 |  | Tenser/Terrain/fireplace_animH | (0,0,300,100) |  | anim 3f step100 |
| 698 | Animated Fireplace (V) | 13 | 0 | 4 |  | Tenser/Terrain/fireplace_animV | (0,0,300,100) |  | anim 3f step100 |
| 699 | Big city stone and wood wall (H) | 13 |  | 5 |  | Tenser/Terrain/BigCity | (0,0,100,100) |  |  |
| 700 | Big city dark wood floor | 0 |  | 0 |  | Tenser/Terrain/BigCity | (100,0,100,100) |  |  |
| 701 | Big city stone and wood wall (V) | 13 |  | 4 |  | Tenser/Terrain/BigCity | (200,0,100,100) |  |  |
| 702 | Big city stone and wood post | 13 |  | 4 |  | Tenser/Terrain/BigCity | (300,0,100,100) |  |  |
| 703 | Big city stone and wood rubble | 13 |  | 3 |  | Tenser/Terrain/BigCity | (400,0,100,100) |  |  |
| 704 | Big city stone and wood wall ruin (V) | 13 |  | 4 |  | Tenser/Terrain/BigCity | (500,0,100,100) |  |  |
| 705 | Big city stone and wood wall ruin (H) | 13 |  | 5 |  | Tenser/Terrain/BigCity | (600,0,100,100) |  |  |
| 706 | Big city stone and wood wall ruin cornerpost | 13 |  | 4 |  | Tenser/Terrain/BigCity | (700,0,100,100) |  |  |
| 707 | panel wall (H) | 13 |  | 5 |  | Tenser/Terrain/millwork | (0,0,100,100) |  |  |
| 708 | panel corner post | 0 |  | 4 |  | Tenser/Terrain/millwork | (100,0,100,100) |  |  |
| 709 | panel wall (V) | 13 |  | 4 |  | Tenser/Terrain/millwork | (200,0,100,100) |  |  |
| 710 | Panel Wall Ruins (H) | 0 | 6 | 5 |  | Tenser/Terrain/millwork | (300,0,100,100) |  |  |
| 711 | Panel wall Rubble | 0 | 6 | 3 |  | Tenser/Terrain/millwork | (400,0,100,100) |  |  |
| 712 | Panel wall ruins (V) | 0 | 6 | 4 |  | Tenser/Terrain/millwork | (500,0,100,100) |  |  |
| 713 | Lodge wall (H) | 13 |  | 5 |  | Tenser/Terrain/millwork | (0,100,100,100) |  |  |
| 714 | Lodge Corner post | 0 |  | 4 |  | Tenser/Terrain/millwork | (100,100,100,100) |  |  |
| 715 | Lodge wall (V) | 13 |  | 4 |  | Tenser/Terrain/millwork | (200,100,100,100) |  |  |
| 716 | Lodge Wall Ruins (H) | 0 | 6 | 5 |  | Tenser/Terrain/millwork | (300,100,100,100) |  |  |
| 717 | Lodge wall Rubble | 0 | 6 | 3 |  | Tenser/Terrain/millwork | (400,100,100,100) |  |  |
| 718 | Lodge wall ruins (V) | 0 | 6 | 4 |  | Tenser/Terrain/millwork | (500,100,100,100) |  |  |
| 719 | wainscoting wood wall (H) | 13 |  | 5 |  | Tenser/Terrain/millwork | (0,200,100,100) |  |  |
| 720 | wainscoting stone wall (H) | 13 |  | 5 |  | Tenser/Terrain/millwork | (100,200,100,100) |  |  |
| 721 | wall moulding (H) | 0 |  | 5 |  | Tenser/Terrain/millwork | (200,200,100,100) |  |  |
| 722 | Wainscoting wood Wall (V) | 13 |  | 4 |  | Tenser/Terrain/millwork | (300,200,100,100) |  |  |
| 723 | Wainscoting stone wall (V) | 13 |  | 4 |  | Tenser/Terrain/millwork | (400,200,100,100) |  |  |
| 724 | Wall moulding (V) | 0 |  | 4 |  | Tenser/Terrain/millwork | (500,200,100,100) |  |  |
| 725 | Plaster-Sand wall (H) | 13 |  | 5 |  | Tenser/Terrain/millwork | (0,300,100,100) |  |  |
| 726 | Plaster-set Back-board (H) | 13 |  | 5 |  | Tenser/Terrain/millwork | (100,300,100,100) |  |  |
| 727 | Plaster-gypsum wall (H) | 13 |  | 5 |  | Tenser/Terrain/millwork | (200,300,100,100) |  |  |
| 728 | Plaster-sand Wall (V) | 13 |  | 4 |  | Tenser/Terrain/millwork | (300,300,100,100) |  |  |
| 729 | Plaster-set Back-board (V) | 13 |  | 4 |  | Tenser/Terrain/millwork | (400,300,100,100) |  |  |
| 730 | Plaster-gypsum wall (V) | 13 |  | 4 |  | Tenser/Terrain/millwork | (500,300,100,100) |  |  |
| 731 | front wall (H) | 13 |  | 5 |  | Tenser/Terrain/tents | (0,0,100,100) | (0,9) |  |
| 732 | inside back wall (H) | 13 |  | 5 |  | Tenser/Terrain/tents | (100,0,100,100) |  |  |
| 733 | inside left wall (V) | 13 |  | 4 |  | Tenser/Terrain/tents | (200,0,100,100) |  |  |
| 734 | outside right wall (V) | 13 |  | 4 |  | Tenser/Terrain/tents | (300,0,100,100) |  |  |
| 735 | burnt tent wall - ash pile (H) | 0 |  | 5 |  | Tenser/Terrain/tents | (400,0,100,100) |  |  |
| 736 | burnt tent wall - ash pile (V) | 0 |  | 4 |  | Tenser/Terrain/tents | (500,0,100,100) |  |  |
| 737 | front wall flap-1 (H) | 0 |  | 5 |  | Tenser/Terrain/tents | (0,100,100,100) | (0,9) |  |
| 738 | inside-back rope (H) | 0 |  | 5 |  | Tenser/Terrain/tents | (100,100,100,100) |  |  |
| 739 | left-inside rope (V) | 0 |  | 4 |  | Tenser/Terrain/tents | (200,100,100,100) |  |  |
| 740 | right flap-1 (V) | 0 |  | 4 |  | Tenser/Terrain/tents | (300,100,100,100) |  |  |
| 741 | red rug | 0 |  | 0 |  | Tenser/Terrain/tents | (400,100,100,100) |  |  |
| 742 | gray rug | 0 |  | 0 |  | Tenser/Terrain/tents | (500,100,100,100) |  |  |
| 743 | front flap-2 (H) | 0 |  | 5 |  | Tenser/Terrain/tents | (0,200,100,100) | (0,9) |  |
| 744 | inside back rope accent (H) | 0 |  | 5 |  | Tenser/Terrain/tents | (100,200,100,100) |  |  |
| 745 | inside-left rope accent (V) | 0 |  | 4 |  | Tenser/Terrain/tents | (200,200,100,100) |  |  |
| 746 | right flap-2 (V) | 0 |  | 4 |  | Tenser/Terrain/tents | (300,200,100,100) |  |  |
| 747 | square fur rug | 0 |  | 0 |  | Tenser/Terrain/tents | (400,200,100,100) |  |  |
| 748 | bear rug (V) | 0 |  | 0 |  | Tenser/Terrain/tents | (500,200,100,100) |  |  |
| 749 | front flap-1 accent (H) | 0 |  | 5 |  | Tenser/Terrain/tents | (0,300,100,100) | (0,9) |  |
| 750 | inside-back shade-screen (H) | 0 |  | 5 |  | Tenser/Terrain/tents | (100,300,100,100) |  |  |
| 751 | inside left shade screen (V) | 0 |  | 4 |  | Tenser/Terrain/tents | (200,300,100,100) |  |  |
| 752 | right flap-1 accent (V) | 0 |  | 4 |  | Tenser/Terrain/tents | (300,300,100,100) |  |  |
| 753 | bear rug (H) | 0 |  | 0 |  | Tenser/Terrain/tents | (400,300,100,100) |  |  |
| 754 | front flap-2 accent (H) | 0 |  | 5 |  | Tenser/Terrain/tents | (0,400,100,100) | (0,9) |  |
| 755 | inside back stripe accent (H) | 0 |  | 5 |  | Tenser/Terrain/tents | (100,400,100,100) |  |  |
| 756 | inside left stripe accent (V) | 0 |  | 4 |  | Tenser/Terrain/tents | (200,400,100,100) |  |  |
| 757 | right flap-2 accent (V) | 0 |  | 4 |  | Tenser/Terrain/tents | (300,400,100,100) |  |  |
| 758 | front wall accent (H) | 0 |  | 5 |  | Tenser/Terrain/tents | (0,500,100,100) | (0,9) |  |
| 759 | back wall accent (H) | 0 |  | 5 |  | Tenser/Terrain/tents | (100,500,100,100) |  |  |
| 760 | left wall accent (V) | 0 |  | 4 |  | Tenser/Terrain/tents | (200,500,100,100) |  |  |
| 761 | right wall accent (V) | 0 |  | 4 |  | Tenser/Terrain/tents | (300,500,100,100) |  |  |
| 762 | snowdrift (H) | 0 |  | 5 |  | Tenser/Terrain/snowdrift | (0,0,100,100) |  |  |
| 763 | snowdrift2 (V) | 0 |  | 4 |  | Tenser/Terrain/snowdrift2 | (0,0,100,100) |  |  |
| 764 | librarybookshelf (H) | 0 |  | 5 |  | Tenser/Terrain/bookshelf | (0,0,100,100) |  |  |
| 765 | librarybookshelf2 (V) | 0 |  | 4 |  | Tenser/Terrain/bookshelf2 | (0,0,100,100) |  |  |
| 766 | animated campfire | 0 | 6 | 0 |  | Tenser/Terrain/fire-Sheet | (0,0,500,100) |  | anim 5f step100 |
| 767 | Shield Ornamental (for the shadow) (H) | 0 |  | 5 |  | Tenser/Terrain/shielddeco | (0,0,100,100) |  |  |
| 768 | Crossed swords (H) | 0 |  | 5 |  | Tenser/Terrain/shielddeco | (100,0,100,100) |  |  |
| 769 | Shiny Shield Ornamental (H) | 0 |  | 5 |  | Tenser/Terrain/shielddeco | (200,0,100,100) |  |  |
| 770 | Shield Ornamental Trim 1 (H) | 0 |  | 5 |  | Tenser/Terrain/shielddeco | (0,100,100,100) |  |  |
| 771 | Shield Ornamental Trim 2 (H) | 0 |  | 5 |  | Tenser/Terrain/shielddeco | (200,100,100,100) |  |  |
| 772 | Shield Ornamental Matte Shield (H) | 0 |  | 5 |  | Tenser/Terrain/shielddeco | (0,200,100,100) |  |  |
| 773 | Shield Ornamental Chevron (H) | 0 |  | 5 |  | Tenser/Terrain/shielddeco | (100,200,100,100) |  |  |
| 774 | Shield Ornamental inverted Chevron (H) | 0 |  | 5 |  | Tenser/Terrain/shielddeco | (200,200,100,100) |  |  |
| 775 | Banner Low Contrast (H) | 0 |  | 5 |  | Tenser/Terrain/banners | (0,0,100,100) |  |  |
| 776 | Banner trim 1 (H) | 0 |  | 5 |  | Tenser/Terrain/banners | (100,0,100,100) |  |  |
| 777 | Banner Yasnaki symbol (H) | 0 |  | 5 |  | Tenser/Terrain/banners | (200,0,100,100) |  |  |
| 778 | Banner High contrast (H) | 0 |  | 5 |  | Tenser/Terrain/banners | (0,100,100,100) |  |  |
| 779 | Banner Mu Symbol (H) | 0 |  | 5 |  | Tenser/Terrain/banners | (200,100,100,100) |  |  |
| 780 | Banner pole (H) | 0 |  | 5 |  | Tenser/Terrain/banners | (0,200,100,100) |  |  |
| 781 | Banner trim 2 (H) | 0 |  | 5 |  | Tenser/Terrain/banners | (100,200,100,100) |  |  |
| 782 | Banner Kesmai Dragon symbol (H) | 0 |  | 5 |  | Tenser/Terrain/banners | (200,200,100,100) |  |  |
| 783 | Dungeon (C) | 0 |  | 4 |  | Tenser/Terrain/kesbrokenpillars | (0,0,100,100) |  |  |
| 784 | Town (C) | 0 |  | 4 |  | Tenser/Terrain/kesbrokenpillars | (100,0,100,100) |  |  |
| 785 | B&W Marble Stairs down and south | 6 |  | 0 |  | Tenser/Terrain/bwmarblestairs | (0,0,100,100) |  |  |
| 786 | B&W Marble Stairs down and east | 6 |  | 0 |  | Tenser/Terrain/bwmarblestairs | (100,0,100,100) |  |  |
| 787 | B&W Marble Stairs down and west | 6 |  | 0 |  | Tenser/Terrain/bwmarblestairs | (200,0,100,100) |  |  |
| 788 | B&W Marble Stairs down and north | 6 |  | 0 |  | Tenser/Terrain/bwmarblestairs | (300,0,100,100) |  |  |
| 789 | B&W Marble Stairs up and north | 5 |  | 0 |  | Tenser/Terrain/bwmarblestairs | (400,0,100,100) |  |  |
| 790 | B&W Marble Stairs up and west | 5 |  | 0 |  | Tenser/Terrain/bwmarblestairs | (500,0,100,100) |  |  |
| 791 | B&W Marble Stairs up and east | 5 |  | 0 |  | Tenser/Terrain/bwmarblestairs | (600,0,100,100) |  |  |
| 792 | B&W Marble Stairs up and south | 5 |  | 0 |  | Tenser/Terrain/bwmarblestairs | (700,0,100,100) |  |  |
| 793 | Blue Marble Stairs down and south | 6 |  | 0 |  | Tenser/Terrain/bluemarblestairs | (0,0,100,100) |  |  |
| 794 | Blue Marble Stairs down and east | 6 |  | 0 |  | Tenser/Terrain/bluemarblestairs | (100,0,100,100) |  |  |
| 795 | Blue Marble Stairs down and west | 6 |  | 0 |  | Tenser/Terrain/bluemarblestairs | (200,0,100,100) |  |  |
| 796 | Blue Marble Stairs down and north | 6 |  | 0 |  | Tenser/Terrain/bluemarblestairs | (300,0,100,100) |  |  |
| 797 | Blue Marble Stairs up and north | 5 |  | 0 |  | Tenser/Terrain/bluemarblestairs | (400,0,100,100) |  |  |
| 798 | Blue Marble Stairs up and west | 5 |  | 0 |  | Tenser/Terrain/bluemarblestairs | (500,0,100,100) |  |  |
| 799 | Blue Marble Stairs up and east | 5 |  | 0 |  | Tenser/Terrain/bluemarblestairs | (600,0,100,100) |  |  |
| 800 | Blue Marble Stairs up and south | 5 |  | 0 |  | Tenser/Terrain/bluemarblestairs | (700,0,100,100) |  |  |
| 801 | Rough Wood Stairs down and south | 6 |  | 0 |  | Tenser/Terrain/roughwoodstairs | (0,0,100,100) |  |  |
| 802 | Rough Wood Stairs down and east | 6 |  | 0 |  | Tenser/Terrain/roughwoodstairs | (100,0,100,100) |  |  |
| 803 | Rough Wood Stairs down and west | 6 |  | 0 |  | Tenser/Terrain/roughwoodstairs | (200,0,100,100) |  |  |
| 804 | Rough Wood Stairs down and north | 6 |  | 0 |  | Tenser/Terrain/roughwoodstairs | (300,0,100,100) |  |  |
| 805 | Rough Wood Stairs up and north | 5 |  | 0 |  | Tenser/Terrain/roughwoodstairs | (400,0,100,100) |  |  |
| 806 | Rough Wood Stairs up and west | 5 |  | 0 |  | Tenser/Terrain/roughwoodstairs | (500,0,100,100) |  |  |
| 807 | Rough Wood Stairs up and east | 5 |  | 0 |  | Tenser/Terrain/roughwoodstairs | (600,0,100,100) |  |  |
| 808 | Rough Wood Stairs up and south | 5 |  | 0 |  | Tenser/Terrain/roughwoodstairs | (700,0,100,100) |  |  |
| 809 | Fine Wood Stairs down and south | 6 |  | 0 |  | Tenser/Terrain/finewoodstairs | (0,0,100,100) |  |  |
| 810 | Fine Wood Stairs down and east | 6 |  | 0 |  | Tenser/Terrain/finewoodstairs | (100,0,100,100) |  |  |
| 811 | Fine Wood Stairs down and west | 6 |  | 0 |  | Tenser/Terrain/finewoodstairs | (200,0,100,100) |  |  |
| 812 | Fine Wood Stairs down and north | 6 |  | 0 |  | Tenser/Terrain/finewoodstairs | (300,0,100,100) |  |  |
| 813 | Fine Wood Stairs up and north | 5 |  | 0 |  | Tenser/Terrain/finewoodstairs | (400,0,100,100) |  |  |
| 814 | Fine Wood Stairs up and west | 5 |  | 0 |  | Tenser/Terrain/finewoodstairs | (500,0,100,100) |  |  |
| 815 | Fine Wood Stairs up and east | 5 |  | 0 |  | Tenser/Terrain/finewoodstairs | (600,0,100,100) |  |  |
| 816 | Fine Wood Stairs up and south | 5 |  | 0 |  | Tenser/Terrain/finewoodstairs | (700,0,100,100) |  |  |
| 817 | Fine Stairs Carpet down and south | 6 |  | 1 |  | Tenser/Terrain/finestairscarpet | (0,0,100,100) |  |  |
| 818 | Fine Stairs Carpet down and east | 6 |  | 1 |  | Tenser/Terrain/finestairscarpet | (100,0,100,100) |  |  |
| 819 | Fine Stairs Carpet down and west | 6 |  | 1 |  | Tenser/Terrain/finestairscarpet | (200,0,100,100) |  |  |
| 820 | Fine Stairs Carpet down and north | 6 |  | 1 |  | Tenser/Terrain/finestairscarpet | (300,0,100,100) |  |  |
| 821 | Fine Stairs Carpet up and north | 5 |  | 1 |  | Tenser/Terrain/finestairscarpet | (400,0,100,100) |  |  |
| 822 | Fine Stairs Carpet up and west | 5 |  | 1 |  | Tenser/Terrain/finestairscarpet | (500,0,100,100) |  |  |
| 823 | Fine Stairs Carpet up and east | 5 |  | 1 |  | Tenser/Terrain/finestairscarpet | (600,0,100,100) |  |  |
| 824 | Fine Stairs Carpet up and south | 5 |  | 1 |  | Tenser/Terrain/finestairscarpet | (700,0,100,100) |  |  |
| 825 | Rickety Wood Stairs down and south | 6 |  | 0 |  | Tenser/Terrain/ricketywoodstairs | (0,0,100,100) |  |  |
| 826 | Rickety Wood Stairs down and east | 6 |  | 0 |  | Tenser/Terrain/ricketywoodstairs | (100,0,100,100) |  |  |
| 827 | Rickety Wood Stairs down and west | 6 |  | 0 |  | Tenser/Terrain/ricketywoodstairs | (200,0,100,100) |  |  |
| 828 | Rickety Wood Stairs down and north | 6 |  | 0 |  | Tenser/Terrain/ricketywoodstairs | (300,0,100,100) |  |  |
| 829 | Rickety Wood Stairs up and north | 5 |  | 0 |  | Tenser/Terrain/ricketywoodstairs | (400,0,100,100) |  |  |
| 830 | Rickety Wood Stairs up and west | 5 |  | 0 |  | Tenser/Terrain/ricketywoodstairs | (500,0,100,100) |  |  |
| 831 | Rickety Wood Stairs up and east | 5 |  | 0 |  | Tenser/Terrain/ricketywoodstairs | (600,0,100,100) |  |  |
| 832 | Rickety Wood Stairs up and south | 5 |  | 0 |  | Tenser/Terrain/ricketywoodstairs | (700,0,100,100) |  |  |
| 833 | Decrepit Wood Stairs down and south | 6 |  | 0 |  | Tenser/Terrain/decrepitwoodstairs | (0,0,100,100) |  |  |
| 834 | Decrepit Wood Stairs down and east | 6 |  | 0 |  | Tenser/Terrain/decrepitwoodstairs | (100,0,100,100) |  |  |
| 835 | Decrepit Wood Stairs down and west | 6 |  | 0 |  | Tenser/Terrain/decrepitwoodstairs | (200,0,100,100) |  |  |
| 836 | Decrepit Wood Stairs down and north | 6 |  | 0 |  | Tenser/Terrain/decrepitwoodstairs | (300,0,100,100) |  |  |
| 837 | Decrepit Wood Stairs up and north | 5 |  | 0 |  | Tenser/Terrain/decrepitwoodstairs | (400,0,100,100) |  |  |
| 838 | Decrepit Wood Stairs up and west | 5 |  | 0 |  | Tenser/Terrain/decrepitwoodstairs | (500,0,100,100) |  |  |
| 839 | Decrepit Wood Stairs up and east | 5 |  | 0 |  | Tenser/Terrain/decrepitwoodstairs | (600,0,100,100) |  |  |
| 840 | Decrepit Wood Stairs up and south | 5 |  | 0 |  | Tenser/Terrain/decrepitwoodstairs | (700,0,100,100) |  |  |
| 841 | Snow & Icey Stairs down and south | 6 |  | 1 |  | Tenser/Terrain/snowiceystairs | (0,0,100,100) |  |  |
| 842 | Snow & Icey Stairs down and east | 6 |  | 1 |  | Tenser/Terrain/snowiceystairs | (100,0,100,100) |  |  |
| 843 | Snow & Icey Stairs down and west | 6 |  | 1 |  | Tenser/Terrain/snowiceystairs | (200,0,100,100) |  |  |
| 844 | Snow & Icey Stairs down and north | 6 |  | 1 |  | Tenser/Terrain/snowiceystairs | (300,0,100,100) |  |  |
| 845 | Snow & Icey Stairs up and north | 5 |  | 1 |  | Tenser/Terrain/snowiceystairs | (400,0,100,100) |  |  |
| 846 | Snow & Icey Stairs up and west | 5 |  | 1 |  | Tenser/Terrain/snowiceystairs | (500,0,100,100) |  |  |
| 847 | Snow & Icey Stairs up and east | 5 |  | 1 |  | Tenser/Terrain/snowiceystairs | (600,0,100,100) |  |  |
| 848 | Snow & Icey Stairs up and south | 5 |  | 1 |  | Tenser/Terrain/snowiceystairs | (700,0,100,100) |  |  |
| 849 | Bloodied Stairs down and south | 6 |  | 1 |  | Tenser/Terrain/bloodiedstairs | (0,0,100,100) |  |  |
| 850 | Bloodied Stairs down and east | 6 |  | 1 |  | Tenser/Terrain/bloodiedstairs | (100,0,100,100) |  |  |
| 851 | Bloodied Stairs down and west | 6 |  | 1 |  | Tenser/Terrain/bloodiedstairs | (200,0,100,100) |  |  |
| 852 | Bloodied Stairs down and north | 6 |  | 1 |  | Tenser/Terrain/bloodiedstairs | (300,0,100,100) |  |  |
| 853 | Bloodied Stairs up and north | 5 |  | 1 |  | Tenser/Terrain/bloodiedstairs | (400,0,100,100) |  |  |
| 854 | Bloodied Stairs up and west | 5 |  | 1 |  | Tenser/Terrain/bloodiedstairs | (500,0,100,100) |  |  |
| 855 | Bloodied Stairs up and east | 5 |  | 1 |  | Tenser/Terrain/bloodiedstairs | (600,0,100,100) |  |  |
| 856 | Bloodied Stairs up and south | 5 |  | 1 |  | Tenser/Terrain/bloodiedstairs | (700,0,100,100) |  |  |
| 857 | Big city stone Dragonscale pillar | 13 |  | 4 |  | Tenser/Terrain/BigCity | (800,0,100,100) |  |  |
| 858 | Big city stone window closed H | 4 |  | 7 |  | Tenser/Terrain/BigCity | (0,100,100,100) |  |  |
| 859 | Big city stone window open (H) | 3 |  | 1 |  | Tenser/Terrain/BigCity | (100,100,100,100) |  |  |
| 860 | Big city stone window closed V | 4 |  | 6 |  | Tenser/Terrain/BigCity | (200,100,100,100) |  |  |
| 861 | Big city stone window open V | 3 |  | 2 |  | Tenser/Terrain/BigCity | (300,100,100,100) |  |  |
| 862 | Big city stone alt wall H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (400,100,100,100) |  |  |
| 863 | Big city stone alt wall V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (500,100,100,100) |  |  |
| 864 | Big city stone alt wall 2 H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (600,100,100,100) |  |  |
| 865 | Big city stone alt wall 2 V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (700,100,100,100) |  |  |
| 866 | Big city stone small Dragonscale pillar | 13 |  | 4 |  | Tenser/Terrain/BigCity | (800,100,100,100) |  |  |
| 867 | Big city stone Stained Glass window wall H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (0,200,100,100) |  |  |
| 868 | Big city stone Stained Glass window wall V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (100,200,100,100) |  |  |
| 869 | Big city stone plain wall H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (200,200,100,100) |  |  |
| 870 | Big city stone plain wall V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (300,200,100,100) |  |  |
| 871 | Big city stone fireplace H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (400,200,100,100) |  |  |
| 872 | Big city stone fireplace V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (500,200,100,100) |  |  |
| 873 | Cornfield | 0 |  | 1 |  | Tenser/Terrain/market | (0,0,100,100) |  |  |
| 874 | Cornfield Burned | 0 |  | 1 |  | Tenser/Terrain/market | (100,0,100,100) |  |  |
| 875 | Wheatfield | 0 |  | 1 |  | Tenser/Terrain/market | (200,0,100,100) |  |  |
| 876 | Wheatfield Burned | 0 |  | 1 |  | Tenser/Terrain/market | (300,0,100,100) |  |  |
| 877 | Grapevines | 0 |  | 1 |  | Tenser/Terrain/market | (400,0,100,100) |  |  |
| 878 | Grapevines Burned | 0 |  | 1 |  | Tenser/Terrain/market | (0,100,100,100) |  |  |
| 879 | Large Crate | 0 |  | 1 |  | Tenser/Terrain/market | (100,100,100,100) |  |  |
| 880 | Fruit crate - Apples, Pears and Oranges. | 0 |  | 1 |  | Tenser/Terrain/market | (200,100,100,100) |  |  |
| 881 | Veggie crate - Lettuce, tomatoe, corn, and bags of grain | 0 |  | 1 |  | Tenser/Terrain/market | (300,100,100,100) |  |  |
| 882 | Crate of grain w Scoop | 0 |  | 1 |  | Tenser/Terrain/market | (400,100,100,100) |  |  |
| 883 | Axe Display | 0 |  | 1 |  | Tenser/Terrain/market | (0,200,100,100) |  |  |
| 884 | Greataxe Display | 0 |  | 1 |  | Tenser/Terrain/market | (100,200,100,100) |  |  |
| 885 | Sword Display | 0 |  | 1 |  | Tenser/Terrain/market | (200,200,100,100) |  |  |
| 886 | Small Crate | 0 |  | 1 |  | Tenser/Terrain/market | (300,200,100,100) |  |  |
| 887 | Cart (v) | 0 |  | 1 |  | Tenser/Terrain/market | (400,200,100,100) |  |  |
| 888 | Large Crate Open | 0 |  | 1 |  | Tenser/Terrain/market | (0,300,100,100) |  |  |
| 889 | Large Crate Ruined | 0 |  | 1 |  | Tenser/Terrain/market | (100,300,100,100) |  |  |
| 890 | Small Crate Open | 0 |  | 1 |  | Tenser/Terrain/market | (200,300,100,100) |  |  |
| 891 | Small Crate Ruined | 0 |  | 1 |  | Tenser/Terrain/market | (300,300,100,100) |  |  |
| 892 | Cart (H) | 0 |  | 1 |  | Tenser/Terrain/market | (400,300,100,100) |  |  |
| 893 | Pear tree | 0 |  | 1 |  | Tenser/Terrain/deciduoustree-expansion | (0,0,100,100) |  |  |
| 894 | Peach tree | 0 |  | 1 |  | Tenser/Terrain/deciduoustree-expansion | (100,0,100,100) |  |  |
| 895 | Apple tree | 0 |  | 1 |  | Tenser/Terrain/deciduoustree-expansion | (200,0,100,100) |  |  |
| 896 | Orange tree | 0 |  | 1 |  | Tenser/Terrain/deciduoustree-expansion | (300,0,100,100) |  |  |
| 897 | Burned Fruit tree (all) | 0 |  | 1 |  | Tenser/Terrain/deciduoustree-expansion | (400,0,100,100) |  |  |
| 898 | Brown Fall tree | 0 |  | 1 |  | Tenser/Terrain/deciduoustree-expansion | (0,100,100,100) |  |  |
| 899 | Orange Fall tree | 0 |  | 1 |  | Tenser/Terrain/deciduoustree-expansion | (100,100,100,100) |  |  |
| 900 | Deep Red Fall tree | 0 |  | 1 |  | Tenser/Terrain/deciduoustree-expansion | (200,100,100,100) |  |  |
| 901 | Red Fall tree | 0 |  | 1 |  | Tenser/Terrain/deciduoustree-expansion | (300,100,100,100) |  |  |
| 902 | Yellow Fall tree | 0 |  | 1 |  | Tenser/Terrain/deciduoustree-expansion | (400,100,100,100) |  |  |
| 903 | Dormant tree | 0 |  | 1 |  | Tenser/Terrain/deciduoustree-expansion | (0,200,100,100) |  |  |
| 904 | Icey Dormant tree | 0 |  | 1 |  | Tenser/Terrain/deciduoustree-expansion | (100,200,100,100) |  |  |
| 905 | Cherry tree | 0 |  | 1 |  | Tenser/Terrain/deciduoustree-expansion | (200,200,100,100) |  |  |
| 906 | Cherry tree blossom | 0 |  | 1 |  | Tenser/Terrain/deciduoustree-expansion | (300,200,100,100) |  |  |
| 907 | Mossy Stair Down South | 6 |  | 1 |  | Tenser/Terrain/mossystairs | (0,0,100,100) |  |  |
| 908 | Mossy Stair Down East | 6 |  | 1 |  | Tenser/Terrain/mossystairs | (100,0,100,100) |  |  |
| 909 | Mossy Stair Down West | 6 |  | 1 |  | Tenser/Terrain/mossystairs | (200,0,100,100) |  |  |
| 910 | Mossy Stair Down North | 6 |  | 1 |  | Tenser/Terrain/mossystairs | (300,0,100,100) |  |  |
| 911 | Mossy Stair Up North | 5 |  | 1 |  | Tenser/Terrain/mossystairs | (400,0,100,100) |  |  |
| 912 | Mossy Stair Up West | 5 |  | 1 |  | Tenser/Terrain/mossystairs | (500,0,100,100) |  |  |
| 913 | Mossy Stair Up East | 5 |  | 1 |  | Tenser/Terrain/mossystairs | (600,0,100,100) |  |  |
| 914 | Mossy Stair Up South | 5 |  | 1 |  | Tenser/Terrain/mossystairs | (700,0,100,100) |  |  |
| 915 | Grassy Stair Down South | 6 |  | 1 |  | Tenser/Terrain/grassystairs | (0,0,100,100) |  |  |
| 916 | Grassy Stair Down East | 6 |  | 1 |  | Tenser/Terrain/grassystairs | (100,0,100,100) |  |  |
| 917 | Grassy Stair Down West | 6 |  | 1 |  | Tenser/Terrain/grassystairs | (200,0,100,100) |  |  |
| 918 | Grassy Stair Down North | 6 |  | 1 |  | Tenser/Terrain/grassystairs | (300,0,100,100) |  |  |
| 919 | Grassy Stair Up North | 5 |  | 1 |  | Tenser/Terrain/grassystairs | (400,0,100,100) |  |  |
| 920 | Grassy Stair Up West | 5 |  | 1 |  | Tenser/Terrain/grassystairs | (500,0,100,100) |  |  |
| 921 | Grassy Stair Up East | 5 |  | 1 |  | Tenser/Terrain/grassystairs | (600,0,100,100) |  |  |
| 922 | Grassy Stair Up South | 5 |  | 1 |  | Tenser/Terrain/grassystairs | (700,0,100,100) |  |  |
| 923 | Flower Stair Down South | 6 |  | 1 |  | Tenser/Terrain/flowerstairs | (0,0,100,100) |  |  |
| 924 | Flower Stair Down East | 6 |  | 1 |  | Tenser/Terrain/flowerstairs | (100,0,100,100) |  |  |
| 925 | Flower Stair Down West | 6 |  | 1 |  | Tenser/Terrain/flowerstairs | (200,0,100,100) |  |  |
| 926 | Flower Stair Down North | 6 |  | 1 |  | Tenser/Terrain/flowerstairs | (300,0,100,100) |  |  |
| 927 | Flower Stair Up North | 5 |  | 1 |  | Tenser/Terrain/flowerstairs | (400,0,100,100) |  |  |
| 928 | Flower Stair Up West | 5 |  | 1 |  | Tenser/Terrain/flowerstairs | (500,0,100,100) |  |  |
| 929 | Flower Stair Up East | 5 |  | 1 |  | Tenser/Terrain/flowerstairs | (600,0,100,100) |  |  |
| 930 | Flower Stair Up South | 5 |  | 1 |  | Tenser/Terrain/flowerstairs | (700,0,100,100) |  |  |
| 931 | Torch Wall Decal (H) | 0 |  | 5 |  | Tenser/Terrain/torchdecals | (0,0,900,100) |  | anim 3f step200 |
| 932 | Torch Wall Decal (V) | 0 |  | 4 |  | Tenser/Terrain/torchdecals | (0,0,900,100) | (1,1) | anim 3f step200 |
| 933 | Darkened Wall Decal (H) | 0 |  | 5 |  | Tenser/Terrain/torchdecals | (600,0,100,100) | (0,0) |  |
| 934 | Darkened Wall Decal (V) | 0 |  | 4 |  | Tenser/Terrain/torchdecals | (700,0,100,100) | (0,0) |  |
| 935 | Darkened Floor Decal | 0 |  | 0 |  | Tenser/Terrain/torchdecals | (800,0,100,100) |  |  |
| 936 | Big city stone plain stone wall H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (600,200,100,100) |  |  |
| 937 | Big city stone plain stone wall V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (700,200,100,100) |  |  |
| 938 | Big city stone ruined stone wall H | 0 |  | 5 |  | Tenser/Terrain/BigCity | (800,200,100,100) |  |  |
| 939 | Big city wood siding wall H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (0,300,100,100) |  |  |
| 940 | Big city wood siding wall V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (100,300,100,100) |  |  |
| 941 | Big city wood siding window closed H | 4 |  | 7 |  | Tenser/Terrain/BigCity | (200,300,100,100) |  |  |
| 942 | Big city wood siding window open H | 3 |  | 1 |  | Tenser/Terrain/BigCity | (300,300,100,100) |  |  |
| 943 | Big city wood siding window closed V | 4 |  | 6 |  | Tenser/Terrain/BigCity | (400,300,100,100) |  |  |
| 944 | Big city wood siding window open V | 3 |  | 2 |  | Tenser/Terrain/BigCity | (500,300,100,100) |  |  |
| 945 | Big city light wood floor | 0 |  | 0 |  | Tenser/Terrain/BigCity | (600,300,100,100) |  |  |
| 946 | Big city wood siding post | 13 |  | 4 |  | Tenser/Terrain/BigCity | (700,300,100,100) |  |  |
| 947 | Big city stone wall ruin V | 0 |  | 4 |  | Tenser/Terrain/BigCity | (800,300,100,100) |  |  |
| 948 | Big city cemetary gate H closed | 4 |  | 7 |  | Tenser/Terrain/BigCity | (0,400,100,100) | (-5,0) |  |
| 949 | Big city cemetary gate H open | 3 |  | 1 |  | Tenser/Terrain/BigCity | (100,400,100,100) | (-5,0) |  |
| 950 | Big city cemetary gate Right H closed | 4 |  | 7 |  | Tenser/Terrain/BigCity | (200,400,100,100) | (-10,0) |  |
| 951 | Big city cemetary gate Right H open | 3 |  | 1 |  | Tenser/Terrain/BigCity | (300,400,100,100) | (-10,0) |  |
| 952 | Big city cemetary fence H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (400,400,100,100) |  |  |
| 953 | Big city cemetary fence V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (500,400,100,100) |  |  |
| 954 | Big city cemetary fence post | 13 |  | 7 |  | Tenser/Terrain/BigCity | (600,400,100,100) | (0,0) |  |
| 955 | Big city cemetary fence post w gargoyle | 13 |  | 7 |  | Tenser/Terrain/BigCity | (700,400,100,100) | (0,0) |  |
| 956 | Big city wood siding ruin V | 0 |  | 4 |  | Tenser/Terrain/BigCity | (800,400,100,100) |  |  |
| 957 | log cabin wall H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (0,500,100,100) |  |  |
| 958 | log cabin wall V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (100,500,100,100) |  |  |
| 959 | log cabin wall ends H | 13 |  | 4 |  | Tenser/Terrain/BigCity | (200,500,100,100) |  |  |
| 960 | log cabin wall ends V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (300,500,100,100) |  |  |
| 961 | log cabin window open H | 3 |  | 1 |  | Tenser/Terrain/BigCity | (400,500,100,100) |  |  |
| 962 | log cabin window closed H | 4 |  | 7 |  | Tenser/Terrain/BigCity | (500,500,100,100) |  |  |
| 963 | log cabin window open V | 3 |  | 2 |  | Tenser/Terrain/BigCity | (600,500,100,100) |  |  |
| 964 | log cabin window closed V | 4 |  | 6 |  | Tenser/Terrain/BigCity | (700,500,100,100) |  |  |
| 965 | wood siding ruin H | 0 |  | 5 |  | Tenser/Terrain/BigCity | (800,500,100,100) |  |  |
| 966 | temple stained glass wall H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (0,600,100,100) |  |  |
| 967 | temple stained glass wall V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (100,600,100,100) |  |  |
| 968 | Dry Well | 1 |  | 0 |  | Tenser/Terrain/drywell | (0,0,100,100) |  |  |
| 969 | Dirt Hole | 1 |  | 0 |  | Tenser/Terrain/dirthole | (0,0,100,100) |  |  |
| 970 | Grassy Hole | 1 |  | 0 |  | Tenser/Terrain/grassyhole | (0,0,100,100) |  |  |
| 971 | Tunnel Entrance | 1 |  | 0 |  | Tenser/Terrain/tunnelentrance | (0,0,100,100) |  |  |
| 972 | Trap Door Closed | 4 |  | 0 |  | Tenser/Terrain/trapdoor | (0,0,100,100) |  |  |
| 973 | Trap Door Open | 1 |  | 0 |  | Tenser/Terrain/trapdooropen | (0,0,100,100) |  |  |
| 974 | Sand Hole | 1 |  | 0 |  | Tenser/Terrain/sandhole | (0,0,100,100) |  |  |
| 975 | Floor Brazier (H) | 0 |  | 0 |  | Tenser/Terrain/firebowl-Sheet | (0,0,440,110) | (-10,-10) | anim 4f step200 |
| 976 | Wall Brazier (H) | 0 |  | 5 |  | Tenser/Terrain/wall brazier | (0,0,600,100) | (0,0) | anim 3f step200 |
| 977 | Wall Brazier (V) | 0 |  | 4 |  | Tenser/Terrain/wall brazier | (0,0,600,100) | (2,1) | anim 3f step200 |
| 978 | Wall Brazier - green fire (H) | 0 |  | 5 |  | Tenser/Terrain/wall brazier-greenfire | (0,0,600,100) |  | anim 3f step200 |
| 979 | Wall Brazier - green fire (V) | 0 |  | 4 |  | Tenser/Terrain/wall brazier-greenfire | (0,0,600,100) | (2,1) | anim 3f step200 |
| 980 | Wall Brazier - blue fire (H) | 0 |  | 5 |  | Tenser/Terrain/wall brazier-bluefire | (0,0,600,100) |  | anim 3f step200 |
| 981 | Wall Brazier - blue fire (V) | 0 |  | 4 |  | Tenser/Terrain/wall brazier-bluefire | (0,0,600,100) | (2,1) | anim 3f step200 |
| 982 | Candelabra | 0 |  | 0 |  | Tenser/Terrain/candelabra-DARKSheet | (0,0,300,100) | (0,0) | anim 3f step200 |
| 983 | Ladder Down South | 6 |  | 5 |  | Tenser/Terrain/ladders | (0,0,100,100) |  |  |
| 984 | Ladder Down East | 6 |  | 5 |  | Tenser/Terrain/ladders | (100,0,100,100) |  |  |
| 985 | Ladder Down West | 6 |  | 5 |  | Tenser/Terrain/ladders | (200,0,100,100) |  |  |
| 986 | Ladder Down North | 6 |  | 5 |  | Tenser/Terrain/ladders | (300,0,100,100) |  |  |
| 987 | Ladder Up North | 5 |  | 5 |  | Tenser/Terrain/ladders | (400,0,100,100) |  |  |
| 988 | Ladder Up West | 5 |  | 5 |  | Tenser/Terrain/ladders | (500,0,100,100) |  |  |
| 989 | Ladder Up East | 5 |  | 5 |  | Tenser/Terrain/ladders | (600,0,100,100) |  |  |
| 990 | Ladder Up South | 5 |  | 5 |  | Tenser/Terrain/ladders | (700,0,100,100) |  |  |
| 991 | Ice Labyrinth Wall (H) | 13 |  | 5 |  | Tenser/Terrain/ice | (0,0,100,100) |  |  |
| 992 | Ice Labyrinth Floor | 0 |  | 0 |  | Tenser/Terrain/ice | (100,0,100,100) |  |  |
| 993 | Ice Labyrinth Wall (V) | 13 |  | 4 |  | Tenser/Terrain/ice | (200,0,100,100) |  |  |
| 994 | Ice Labyrinth Wall ruin (H) | 0 |  | 5 |  | Tenser/Terrain/ice | (300,0,100,100) |  |  |
| 995 | Ice Labyrinth rubble | 0 |  | 3 |  | Tenser/Terrain/ice | (400,0,100,100) |  |  |
| 996 | Ice Labyrinth Wall ruin (V) | 0 |  | 4 |  | Tenser/Terrain/ice | (500,0,100,100) |  |  |
| 997 | Ice Labyrinth Wall Corner Pillar | 0 |  | 4 |  | Tenser/Terrain/ice | (600,0,100,100) |  |  |
| 998 | Ice Labyrinth Corner Pillar ruin | 0 |  | 4 |  | Tenser/Terrain/ice | (700,0,100,100) |  |  |
| 1008 | Lava Tube Wall (H) | 13 |  | 5 |  | Tenser/Terrain/volcanic | (0,0,100,100) |  |  |
| 1009 | Lava Tube Floor | 0 |  | 0 |  | Tenser/Terrain/volcanic | (100,0,100,100) |  |  |
| 1010 | Lava Tube Wall (V) | 13 |  | 4 |  | Tenser/Terrain/volcanic | (200,0,100,100) |  |  |
| 1011 | Lava Tube Wall ruin (H) | 0 |  | 5 |  | Tenser/Terrain/volcanic | (300,0,100,100) |  |  |
| 1012 | Lava Tube rubble | 0 |  | 3 |  | Tenser/Terrain/volcanic | (400,0,100,100) |  |  |
| 1013 | Lava Tube Wall ruin (V) | 0 |  | 4 |  | Tenser/Terrain/volcanic | (500,0,100,100) |  |  |
| 1014 | Lava Tube Wall Corner Pillar | 0 |  | 4 |  | Tenser/Terrain/volcanic | (600,0,100,100) |  |  |
| 1015 | Lava Tube Corner Pillar ruin | 0 |  | 4 |  | Tenser/Terrain/volcanic | (700,0,100,100) |  |  |
| 1016 | Dark Cloud Skyhex | 0 |  | 0 |  | Tenser/Terrain/darkcloud | (0,0,100,100) |  |  |
| 1017 | Dark Cloud Animated Skyhex | 0 |  | 0 |  | Tenser/Terrain/stormcloud-Sheet | (0,0,500,100) |  | anim 5f step200 |
| 1018 | Animated Wave East | 0 | 6 | 0 |  | Tenser/Terrain/EastWave-Sheet | (0,0,2000,100) |  | anim 20f step150 |
| 1019 | Animated Wave South | 0 | 6 | 0 |  | Tenser/Terrain/SouthWave-Sheet | (0,0,2000,100) |  | anim 20f step150 |
| 1020 | Sandstone Rubble | 0 |  | 3 |  | Tenser/Terrain/rubble_sandstone | (0,0,100,100) |  |  |
| 1021 | Blue Marble Rubble | 0 |  | 3 |  | Tenser/Terrain/rubble_bluemarble | (0,0,100,100) |  |  |
| 1022 | Egyptian Rubble | 0 |  | 3 |  | Tenser/Terrain/rubble_egyptian | (0,0,100,100) |  |  |
| 1023 | Pagoda Rubble | 0 |  | 3 |  | Tenser/Terrain/rubble_pagoda | (0,0,100,100) |  |  |
| 1024 | Thicket Rubbish | 0 |  | 3 |  | Tenser/Terrain/rubble_thicket | (0,0,100,100) |  |  |
| 1025 | Candelabra - no shade | 0 |  | 0 |  | Tenser/Terrain/candelabraLight | (0,0,300,100) |  | anim 3f step150 |
| 1026 | Blank Spiral Staircase | 6 |  | 5 |  | Tenser/Terrain/spiralstaircase_blank | (0,0,100,100) |  |  |
| 1027 | Flat Stone Bridge (H) | 0 |  | 3 |  | Tenser/Terrain/flatstonebridge | (0,0,100,100) |  |  |
| 1028 | Flat Stone Bridge (V) | 0 |  | 3 |  | Tenser/Terrain/flatstonebridge2 | (0,0,100,100) |  |  |
| 1029 | Torch Wall Decal (H) | 0 |  | 5 |  | Tenser/Terrain/torches | (0,0,600,100) |  | anim 3f step200 |
| 1030 | Torch Wall Decal (V) | 0 |  | 4 |  | Tenser/Terrain/torches | (0,0,600,100) | (1,1) | anim 3f step200 |
| 1031 | Wall Brazier - blue fire no shadow (H) | 0 |  | 5 |  | Tenser/Terrain/wallbrazierblue_ns | (0,0,600,100) |  | anim 3f step200 |
| 1032 | Wall Brazier - blue fire no shadow (V) | 0 |  | 4 |  | Tenser/Terrain/wallbrazierblue_ns | (0,0,600,100) | (2,1) | anim 3f step200 |
| 1033 | Wall Brazier - green fire no shadow (H) | 0 |  | 5 |  | Tenser/Terrain/wallbraziergreen_ns | (0,0,600,100) |  | anim 3f step200 |
| 1034 | Wall Brazier - green fire no shadow (V) | 0 |  | 4 |  | Tenser/Terrain/wallbraziergreen_ns | (0,0,600,100) | (2,1) | anim 3f step200 |
| 1035 | Wall Brazier - no shadow (H) | 0 |  | 5 |  | Tenser/Terrain/wallbrazier_ns | (0,0,600,100) |  | anim 3f step200 |
| 1036 | Wall Brazier - no shadow (V) | 0 |  | 4 |  | Tenser/Terrain/wallbrazier_ns | (0,0,600,100) | (2,1) | anim 3f step200 |
| 1037 | Floor Brazier no shadow | 0 |  | 0 |  | Tenser/Terrain/firebowl-Sheet_ns | (0,0,400,100) |  | anim 4f step200 |
| 1038 | Darkened Sidewall (V) Decal | 0 |  | 1 |  | Tenser/Terrain/torchdecals | (900,0,100,100) |  |  |
| 1039 | Darkened Sidewall (H) Decal | 0 |  | 1 |  | Tenser/Terrain/torchdecals | (1000,0,100,100) |  |  |
| 1040 | 4 panel door(H) | 4 |  | 7 |  | Tenser/Terrain/Doors/4paneldoors | (0,0,100,100) |  |  |
| 1041 | 4 panel door open(H) | 3 |  | 1 |  | Tenser/Terrain/Doors/4paneldoors | (100,0,100,100) |  |  |
| 1042 | 4 panel door ruin (H) | 4 |  | 3 |  | Tenser/Terrain/Doors/4paneldoors | (200,0,100,100) |  |  |
| 1043 | 4 panel door (v) | 4 |  | 6 |  | Tenser/Terrain/Doors/4paneldoors | (300,0,100,100) |  |  |
| 1044 | 4 panel door open (v) | 3 |  | 2 |  | Tenser/Terrain/Doors/4paneldoors | (400,0,100,100) |  |  |
| 1045 | 4 panel door ruin (v) | 4 |  | 3 |  | Tenser/Terrain/Doors/4paneldoors | (500,0,100,100) |  |  |
| 1046 | blue steel door (h) | 4 |  | 7 |  | Tenser/Terrain/Doors/bluesteeldoor | (0,0,100,100) |  |  |
| 1047 | blue steel door open (h) | 3 |  | 1 |  | Tenser/Terrain/Doors/bluesteeldoor | (100,0,100,100) |  |  |
| 1048 | blue steel door ruin (h) | 4 |  | 3 |  | Tenser/Terrain/Doors/bluesteeldoor | (200,0,100,100) |  |  |
| 1049 | blue steel door (v) | 4 |  | 6 |  | Tenser/Terrain/Doors/bluesteeldoor | (300,0,100,100) |  |  |
| 1050 | blue steel door open (v) | 3 |  | 2 |  | Tenser/Terrain/Doors/bluesteeldoor | (400,0,100,100) |  |  |
| 1051 | blue steel door ruin (v) | 4 |  | 3 |  | Tenser/Terrain/Doors/bluesteeldoor | (500,0,100,100) |  |  |
| 1052 | peephole door (h) | 4 |  | 7 |  | Tenser/Terrain/Doors/peepholedoor | (0,0,100,100) |  |  |
| 1053 | peephole door open (h) | 3 |  | 1 |  | Tenser/Terrain/Doors/peepholedoor | (100,0,100,100) |  |  |
| 1054 | peephole door ruin (h) | 4 |  | 3 |  | Tenser/Terrain/Doors/peepholedoor | (200,0,100,100) |  |  |
| 1055 | peephole door (v) | 4 |  | 6 |  | Tenser/Terrain/Doors/peepholedoor | (300,0,100,100) |  |  |
| 1056 | peephole door open (v) | 3 |  | 2 |  | Tenser/Terrain/Doors/peepholedoor | (400,0,100,100) |  |  |
| 1057 | peephole door ruin (v) | 4 |  | 3 |  | Tenser/Terrain/Doors/peepholedoor | (500,0,100,100) |  |  |
| 1058 | plain door (h) | 4 |  | 7 |  | Tenser/Terrain/Doors/plaindoors | (0,0,100,100) |  |  |
| 1059 | plain door open (h) | 3 |  | 1 |  | Tenser/Terrain/Doors/plaindoors | (100,0,100,100) |  |  |
| 1060 | plain door ruin (h) | 4 |  | 3 |  | Tenser/Terrain/Doors/plaindoors | (200,0,100,100) |  |  |
| 1061 | plain door (v) | 4 |  | 6 |  | Tenser/Terrain/Doors/plaindoors | (300,0,100,100) |  |  |
| 1062 | plain door open (v) | 3 |  | 2 |  | Tenser/Terrain/Doors/plaindoors | (400,0,100,100) |  |  |
| 1063 | plain door ruin (v) | 4 |  | 3 |  | Tenser/Terrain/Doors/plaindoors | (500,0,100,100) |  |  |
| 1064 | steel door (h) | 4 |  | 7 |  | Tenser/Terrain/Doors/steeldoornoise | (0,0,100,100) |  |  |
| 1065 | steel door open (h) | 3 |  | 1 |  | Tenser/Terrain/Doors/steeldoornoise | (100,0,100,100) |  |  |
| 1066 | steel door ruin (h) | 4 |  | 3 |  | Tenser/Terrain/Doors/steeldoornoise | (200,0,100,100) |  |  |
| 1067 | steel door (v) | 4 |  | 6 |  | Tenser/Terrain/Doors/steeldoornoise | (300,0,100,100) |  |  |
| 1068 | steel door open (v) | 3 |  | 2 |  | Tenser/Terrain/Doors/steeldoornoise | (400,0,100,100) |  |  |
| 1069 | steel door ruin (v) | 4 |  | 3 |  | Tenser/Terrain/Doors/steeldoornoise | (500,0,100,100) |  |  |
| 1070 | steel door rusted (h) | 4 |  | 7 |  | Tenser/Terrain/Doors/steeldoorsrustpatina | (0,0,100,100) |  |  |
| 1071 | steel door rusted open (h) | 3 |  | 1 |  | Tenser/Terrain/Doors/steeldoorsrustpatina | (100,0,100,100) |  |  |
| 1072 | steel door rusted ruin (h) | 4 |  | 3 |  | Tenser/Terrain/Doors/steeldoorsrustpatina | (200,0,100,100) |  |  |
| 1073 | steel door rusted (v) | 4 |  | 6 |  | Tenser/Terrain/Doors/steeldoorsrustpatina | (300,0,100,100) |  |  |
| 1074 | steel door rusted open (v) | 3 |  | 2 |  | Tenser/Terrain/Doors/steeldoorsrustpatina | (400,0,100,100) |  |  |
| 1075 | steel door rusted ruin (v) | 4 |  | 3 |  | Tenser/Terrain/Doors/steeldoorsrustpatina | (500,0,100,100) |  |  |
| 1076 | thin slat door (h) | 4 |  | 7 |  | Tenser/Terrain/Doors/thinslatdoors | (0,0,100,100) |  |  |
| 1077 | thin slat door open (h) | 3 |  | 1 |  | Tenser/Terrain/Doors/thinslatdoors | (100,0,100,100) |  |  |
| 1078 | thin slat door ruin (h) | 4 |  | 3 |  | Tenser/Terrain/Doors/thinslatdoors | (200,0,100,100) |  |  |
| 1079 | thin slat door (v) | 4 |  | 6 |  | Tenser/Terrain/Doors/thinslatdoors | (300,0,100,100) |  |  |
| 1080 | thin slat door open (v) | 3 |  | 2 |  | Tenser/Terrain/Doors/thinslatdoors | (400,0,100,100) |  |  |
| 1081 | thin slat door ruin (v) | 4 |  | 3 |  | Tenser/Terrain/Doors/thinslatdoors | (500,0,100,100) |  |  |
| 1082 | wide slat door (h) | 4 |  | 7 |  | Tenser/Terrain/Doors/wideslatdoors | (0,0,100,100) |  |  |
| 1083 | wide slat door open (h) | 3 |  | 1 |  | Tenser/Terrain/Doors/wideslatdoors | (100,0,100,100) |  |  |
| 1084 | wide slat door ruin (h) | 4 |  | 3 |  | Tenser/Terrain/Doors/wideslatdoors | (200,0,100,100) |  |  |
| 1085 | wide slat door (v) | 4 |  | 6 |  | Tenser/Terrain/Doors/wideslatdoors | (300,0,100,100) |  |  |
| 1086 | wide slat door open (v) | 3 |  | 2 |  | Tenser/Terrain/Doors/wideslatdoors | (400,0,100,100) |  |  |
| 1087 | wide slat door ruin (v) | 13 |  | 3 |  | Tenser/Terrain/Doors/wideslatdoors | (500,0,100,100) |  |  |
| 1088 | log fortification (h) | 13 |  | 5 |  | Tenser/Terrain/logfortification | (0,0,100,100) |  |  |
| 1089 | log fortification (v) | 13 |  | 4 |  | Tenser/Terrain/logfortification | (100,0,100,100) |  |  |
| 1090 | swamp cave wall (h) | 13 |  | 5 |  | Tenser/Terrain/swamp_tileset | (0,0,100,100) |  |  |
| 1091 | swamp cave floor | 0 |  | 0 |  | Tenser/Terrain/swamp_tileset | (100,0,100,100) |  |  |
| 1092 | swamp cave wall (v) | 13 |  | 4 |  | Tenser/Terrain/swamp_tileset | (200,0,100,100) |  |  |
| 1093 | swamp cave wall ruin (h) | 13 |  | 5 |  | Tenser/Terrain/swamp_tileset | (300,0,100,100) |  |  |
| 1094 | swamp cave rubble | 13 |  | 3 |  | Tenser/Terrain/swamp_tileset | (400,0,100,100) |  |  |
| 1095 | swamp cave wall ruin (v) | 13 |  | 4 |  | Tenser/Terrain/swamp_tileset | (500,0,100,100) |  |  |
| 1096 | swamp cave wall column | 13 |  | 4 |  | Tenser/Terrain/swamp_tileset | (0,100,100,100) |  |  |
| 1097 | swamp cave wall column ruin | 13 |  | 4 |  | Tenser/Terrain/swamp_tileset | (100,100,100,100) |  |  |
| 1098 | mossy swamp floor | 0 |  | 0 |  | Tenser/Terrain/swamp_tileset | (200,100,100,100) |  |  |
| 1099 | rocky swamp floor | 0 |  | 0 |  | Tenser/Terrain/swamp_tileset | (300,100,100,100) |  |  |
| 1100 | lilly pads | 0 |  | 1 |  | Tenser/Terrain/swamp_tileset | (400,100,100,100) |  |  |
| 1101 | swamp vegetation asstd | 0 |  | 1 |  | Tenser/Terrain/swamp_tileset | (500,100,100,100) |  |  |
| 1102 | reeds and cattails | 0 |  | 1 |  | Tenser/Terrain/swamp_tileset | (0,200,100,100) |  |  |
| 1103 | swamp flower purple | 0 |  | 1 |  | Tenser/Terrain/swamp_tileset | (100,200,100,100) |  |  |
| 1104 | swamp flower white | 0 |  | 1 |  | Tenser/Terrain/swamp_tileset | (200,200,100,100) |  |  |
| 1105 | lilly pad cluster | 0 |  | 1 |  | Tenser/Terrain/swamp_tileset | (300,200,100,100) |  |  |
| 1106 | cattail cluster | 0 |  | 1 |  | Tenser/Terrain/swamp_tileset | (400,200,100,100) |  |  |
| 1107 | tall reeds | 0 |  | 1 |  | Tenser/Terrain/swamp_tileset | (500,200,100,100) |  |  |
| 1108 | tree post column | 0 |  | 1 |  | Tenser/Terrain/swamp_tileset | (0,300,100,100) |  |  |
| 1109 | tree column vines (experimental) | 0 |  | 1 |  | Tenser/Terrain/swamp_tileset | (100,300,100,100) |  |  |
| 1110 | tree column vines wrap (experimental) | 0 |  | 1 |  | Tenser/Terrain/swamp_tileset | (200,300,100,100) |  |  |
| 1111 | tree column vines floral (experimental) | 0 |  | 1 |  | Tenser/Terrain/swamp_tileset | (300,300,100,100) |  |  |
| 1112 | swamp cypress tree | 0 |  | 1 |  | Tenser/Terrain/swamp_tileset | (400,300,100,100) |  |  |
| 1113 | swamp cypress tree dead | 0 |  | 1 |  | Tenser/Terrain/swamp_tileset | (500,300,100,100) |  |  |
| 1114 | swamp cav wall vine (h) | 13 |  | 5 |  | Tenser/Terrain/swamp_tileset | (0,400,100,100) |  |  |
| 1115 | swamp cav wall vine (v) | 13 |  | 4 |  | Tenser/Terrain/swamp_tileset | (100,400,100,100) |  |  |
| 1116 | palace pillar right wall (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (0,0,100,100) |  |  |
| 1117 | palace wall (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (100,0,100,100) |  |  |
| 1118 | palace pillar left wall (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (200,0,100,100) |  |  |
| 1119 | palace pillar left wall (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (300,0,100,100) |  |  |
| 1120 | palace wall (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (400,0,100,100) |  |  |
| 1121 | palace pillar right wall (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (500,0,100,100) |  |  |
| 1122 | palace art niche wall (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (600,0,100,100) |  |  |
| 1123 | palace arch (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (700,0,100,100) |  |  |
| 1124 | palace corner post/column | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (0,100,100,100) |  |  |
| 1125 | flagstone floor | 0 |  | 0 |  | Tenser/Terrain/palacetileset | (100,100,100,100) |  |  |
| 1126 | palace art niche (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (200,100,100,100) |  |  |
| 1127 | palace arch (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (300,100,100,100) |  |  |
| 1128 | stone-carved dragon column wrap | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (400,100,100,100) |  |  |
| 1129 | gold-jade dragon column wrap | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (500,100,100,100) |  |  |
| 1130 | gold serpent column wrap | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (600,100,100,100) |  |  |
| 1131 | marble dragon column | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (700,100,100,100) |  |  |
| 1132 | bull head column | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (0,200,100,100) |  |  |
| 1133 | Floor Grout (Alt color) | 0 |  | 0 |  | Tenser/Terrain/palacetileset | (100,200,100,100) |  |  |
| 1134 | palace wall Grout (V) (Alt color) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (200,200,100,100) |  |  |
| 1135 | palace wall Grout (H) (Alt color) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (300,200,100,100) |  |  |
| 1136 | dragonhead mount (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (400,200,100,100) |  |  |
| 1137 | dragonhead mount (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (500,200,100,100) |  |  |
| 1138 | Brick's Charlie portrait (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (600,200,100,100) |  |  |
| 1139 | Brick's Charlie portrait (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (700,200,100,100) |  |  |
| 1140 | Lion head pillar | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (0,300,100,100) |  |  |
| 1141 | Dragon head Arch-topper (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (100,300,100,100) |  |  |
| 1142 | Dragon head Arch-topper (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (200,300,100,100) |  |  |
| 1143 | Bull head Arch-topper (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (300,300,100,100) |  |  |
| 1144 | Bull head Arch-topper (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (400,300,100,100) |  |  |
| 1145 | art niche wall grout (v) (Alt Color) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (500,300,100,100) |  |  |
| 1146 | art niche wall grout (h) (Alt Color) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (600,300,100,100) |  |  |
| 1147 | palace right pillar wall grout (h) (Alt Color) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (700,300,100,100) |  |  |
| 1148 | palace left pillar wall grout (v) (Alt Color) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (0,400,100,100) |  |  |
| 1149 | palace left pillar wall grout (h) (Alt Color) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (100,400,100,100) |  |  |
| 1150 | palace right pillar wall grout (v) (Alt Color) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (200,400,100,100) |  |  |
| 1151 | palace wall highlights (v) (Alt Color) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (300,400,100,100) |  |  |
| 1152 | palace wall highlights (h) (Alt Color) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (400,400,100,100) |  |  |
| 1153 | palace left pillar wall highlights (v) (Alt Color) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (500,400,100,100) |  |  |
| 1154 | palace left pillar wall highlights (h) (Alt Color) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (600,400,100,100) |  |  |
| 1155 | palace right pillar wall highlights (v) (Alt Color) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (700,400,100,100) |  |  |
| 1156 | palace right pillar wall highlights (h) (Alt Color) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (0,500,100,100) |  |  |
| 1157 | art niche wall highlights (v) (Alt Color) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (100,500,100,100) |  |  |
| 1158 | art niche wall highlights (h) (Alt Color) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (200,500,100,100) |  |  |
| 1159 | Lion head arch-topper (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (300,500,100,100) |  |  |
| 1160 | Lion head arch-topper (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (400,500,100,100) |  |  |
| 1161 | palace right pillar wall ruin (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (500,500,100,100) |  |  |
| 1162 | palace right pillar wall ruin (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (600,500,100,100) |  |  |
| 1163 | palace left pillar wall ruin (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (700,500,100,100) |  |  |
| 1164 | palace left pillar wall ruin (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (0,600,100,100) |  |  |
| 1165 | palace wall ruin (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (100,600,100,100) |  |  |
| 1166 | palace wall ruin (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (200,600,100,100) |  |  |
| 1167 | art niche wall ruin (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (300,600,100,100) |  |  |
| 1168 | art niche wall ruin (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (400,600,100,100) |  |  |
| 1169 | column ruin | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (500,600,100,100) |  |  |
| 1170 | palace rubble | 13 |  | 3 |  | Tenser/Terrain/palacetileset | (600,600,100,100) |  |  |
| 1171 | stained glass - dragon (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (700,600,100,100) |  |  |
| 1172 | stained glass - dragon (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (0,700,100,100) |  |  |
| 1173 | red dragon banner (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (100,700,100,100) |  |  |
| 1174 | red dragon banner (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (200,700,100,100) |  |  |
| 1175 | dragon mural (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (300,700,100,100) |  |  |
| 1176 | dragon mural (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (400,700,100,100) |  |  |
| 1177 | stained glass - priest (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (500,700,100,100) |  |  |
| 1178 | stained glass - priest (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (600,700,100,100) |  |  |
| 1179 | stained glass - court (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (700,700,100,100) |  |  |
| 1180 | stained glass - court (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (0,800,100,100) |  |  |
| 1181 | purple Mu banner (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (100,800,100,100) |  |  |
| 1182 | purple Mu banner (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (200,800,100,100) |  |  |
| 1183 | green banner (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (300,800,100,100) |  |  |
| 1184 | green banner (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (400,800,100,100) |  |  |
| 1185 | Arch ruins (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (500,800,100,100) |  |  |
| 1186 | Arch ruins (v) | 13 |  | 4 |  | Tenser/Terrain/palacetileset | (600,800,100,100) |  |  |
| 1187 | black banner (h) | 13 |  | 5 |  | Tenser/Terrain/palacetileset | (700,800,100,100) |  |  |
| 1188 | magic circle 3 floor test | 0 |  | 0 |  | Tenser/Terrain/summoningcircle3 | (0,0,110,110) | (-10,-10) |  |
| 1189 | magic circle 2 floor test | 0 |  | 0 |  | Tenser/Terrain/summoningcircle2 | (0,0,110,110) | (-10,-10) |  |
| 1190 | magic circle 1 floor test | 0 |  | 0 |  | Tenser/Terrain/summoningcircle1 | (0,0,110,110) | (-10,-10) |  |
| 1191 | lectern (h) | 0 |  | 0 |  | Tenser/Terrain/lectern | (0,0,55,55) | (22,45) |  |
| 1192 | lectern (v) | 0 |  | 0 |  | Tenser/Terrain/lecternv | (0,0,55,55) | (45,23) |  |
| 1193 | Desk (h) | 0 |  | 0 |  | Tenser/Terrain/furniture | (0,0,100,100) | (0,0) |  |
| 1194 | Desk (v) | 0 |  | 0 |  | Tenser/Terrain/furniture | (100,0,100,100) | (0,0) |  |
| 1195 | Single bed (v) | 0 |  | 0 |  | Tenser/Terrain/furniture | (200,0,100,100) | (0,-40) |  |
| 1196 | Double bed (v) | 0 |  | 0 |  | Tenser/Terrain/furniture | (300,0,100,100) | (0,-40) |  |
| 1197 | Chair rightface (h) | 0 |  | 0 |  | Tenser/Terrain/furniture | (0,100,100,100) | (0,0) |  |
| 1198 | Chair southface (v) | 0 |  | 0 |  | Tenser/Terrain/furniture | (100,100,100,100) | (0,0) |  |
| 1199 | Chair leftface (h) | 0 |  | 0 |  | Tenser/Terrain/furniture | (200,100,100,100) | (0,0) |  |
| 1200 | Chair northface (v) | 0 |  | 0 |  | Tenser/Terrain/furniture | (300,100,100,100) | (0,0) |  |
| 1201 | Wardrobe (v) | 0 |  | 0 |  | Tenser/Terrain/furniture | (0,200,100,100) | (0,0) |  |
| 1202 | Wardrobe (h) | 0 |  | 0 |  | Tenser/Terrain/furniture | (100,200,100,100) | (0,0) |  |
| 1203 | Nightstand (h) | 0 |  | 0 |  | Tenser/Terrain/furniture | (200,200,100,100) | (0,0) |  |
| 1204 | Nightstand (v) | 0 |  | 0 |  | Tenser/Terrain/furniture | (300,200,100,100) | (0,0) |  |
| 1205 | Single bed (h) | 0 |  | 0 |  | Tenser/Terrain/furniture | (0,300,100,100) | (0,0) |  |
| 1206 | Double bed (h) | 0 |  | 0 |  | Tenser/Terrain/furniture | (100,300,100,100) | (-40,0) |  |
| 1207 | bunk bed (v) | 0 |  | 0 |  | Tenser/Terrain/furniture | (200,300,100,100) | (0,-40) |  |
| 1208 | bunk bed (h) | 0 |  | 0 |  | Tenser/Terrain/furniture | (300,300,100,100) | (-40,0) |  |
| 1209 | big chest(h) | 0 |  | 0 |  | Tenser/Terrain/furniture | (0,400,100,100) | (0,0) |  |
| 1210 | big chest(v) | 0 |  | 0 |  | Tenser/Terrain/furniture | (100,400,100,100) | (0,0) |  |
| 1211 | wash basin, Chamber pot and candle for Nightstand (h) | 0 |  | 0 |  | Tenser/Terrain/furniture | (200,400,100,100) | (0,0) |  |
| 1212 | candle for Nightstand (v) | 0 |  | 0 |  | Tenser/Terrain/furniture | (300,400,100,100) | (0,0) |  |
| 1213 | Mine wall (h) | 13 |  | 5 |  | Tenser/Terrain/mines | (0,0,100,100) | (0,0) |  |
| 1214 | Mine floor texture | 0 |  | 5 |  | Tenser/Terrain/mines | (100,0,100,100) | (0,0) |  |
| 1215 | Mine wall (v) | 13 |  | 5 |  | Tenser/Terrain/mines | (200,0,100,100) | (0,0) |  |
| 1216 | Mine wall ruin (h) | 13 |  | 5 |  | Tenser/Terrain/mines | (300,0,100,100) | (0,0) |  |
| 1217 | Mine rubble | 13 |  | 3 |  | Tenser/Terrain/mines | (400,0,100,100) | (0,0) |  |
| 1218 | Mine wall ruin (v) | 13 |  | 4 |  | Tenser/Terrain/mines | (500,0,100,100) | (0,0) |  |
| 1219 | Mine post | 13 |  | 4 |  | Tenser/Terrain/mines | (0,100,100,100) | (0,0) |  |
| 1220 | Mine post ruin | 0 |  | 4 |  | Tenser/Terrain/mines | (100,100,100,100) | (0,0) |  |
| 1221 | Mine obstruction | 13 |  | 4 |  | Tenser/Terrain/mines | (200,100,100,100) | (0,0) |  |
| 1222 | Mine support post | 0 |  | 4 |  | Tenser/Terrain/mines | (300,100,100,100) | (0,0) |  |
| 1223 | Mine rocks h | 0 |  | 4 |  | Tenser/Terrain/mines | (400,100,100,100) | (0,0) |  |
| 1224 | mine rocks v | 0 |  | 0 |  | Tenser/Terrain/mines | (500,100,100,100) | (0,0) |  |
| 1225 | irregular wall (h) | 13 |  | 5 |  | Tenser/Terrain/newdungeonwalls | (0,0,100,100) | (0,0) |  |
| 1226 | dungeon floor | 0 |  | 0 |  | Tenser/Terrain/newdungeonwalls | (100,0,100,100) | (0,0) |  |
| 1227 | irregular wall (v) | 13 |  | 4 |  | Tenser/Terrain/newdungeonwalls | (200,0,100,100) | (0,0) |  |
| 1228 | irregular wall ruin (h) | 13 |  | 5 |  | Tenser/Terrain/newdungeonwalls | (300,0,100,100) | (0,0) |  |
| 1229 | irregular wall rubble | 13 |  | 3 |  | Tenser/Terrain/newdungeonwalls | (400,0,100,100) | (0,0) |  |
| 1230 | irregular wall ruin (v) | 13 |  | 4 |  | Tenser/Terrain/newdungeonwalls | (500,0,100,100) | (0,0) |  |
| 1231 | irregular wall post | 13 |  | 4 |  | Tenser/Terrain/newdungeonwalls | (0,100,100,100) | (0,0) |  |
| 1232 | irregular wall post ruin | 13 |  | 4 |  | Tenser/Terrain/newdungeonwalls | (100,100,100,100) | (0,0) |  |
| 1233 | short hedge V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (200,600,100,100) |  |  |
| 1234 | short hedge H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (300,600,100,100) |  |  |
| 1235 | log cabin column | 13 |  | 4 |  | Tenser/Terrain/BigCity | (400,600,100,100) |  |  |
| 1236 | log cabin rubble | 0 |  | 3 |  | Tenser/Terrain/BigCity | (500,600,100,100) |  |  |
| 1237 | rustic wood floor | 0 |  | 0 |  | Tenser/Terrain/BigCity | (600,600,100,100) |  |  |
| 1238 | wood siding ruin column | 0 |  | 4 |  | Tenser/Terrain/BigCity | (700,600,100,100) |  |  |
| 1239 | wood refuse/rubble | 0 |  | 3 |  | Tenser/Terrain/BigCity | (800,600,100,100) |  |  |
| 1240 | temple skull niche H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (0,700,100,100) |  |  |
| 1241 | temple black rose niche V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (100,700,100,100) |  |  |
| 1242 | cauldron | 0 |  | 1 |  | Tenser/Terrain/BigCity | (200,700,100,100) |  |  |
| 1243 | potted topiari round | 0 |  | 1 |  | Tenser/Terrain/BigCity | (300,700,100,100) |  |  |
| 1244 | headstone H | 0 |  | 1 |  | Tenser/Terrain/BigCity | (400,700,100,100) |  |  |
| 1245 | potted fir topiari | 0 |  | 1 |  | Tenser/Terrain/BigCity | (500,700,100,100) |  |  |
| 1246 | knight statue/memorial | 0 |  | 1 |  | Tenser/Terrain/BigCity | (600,700,100,100) |  |  |
| 1247 | small headstone H | 0 |  | 1 |  | Tenser/Terrain/BigCity | (700,700,100,100) |  |  |
| 1248 | headstone w cross H | 0 |  | 1 |  | Tenser/Terrain/BigCity | (800,700,100,100) |  |  |
| 1249 | sleeping woman sarcophagus V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (0,800,100,100) |  |  |
| 1250 | sarcophagus V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (100,800,100,100) |  |  |
| 1251 | rejuvinated sarcophagus V | 13 |  | 4 |  | Tenser/Terrain/BigCity | (200,800,100,100) |  |  |
| 1252 | headstone V | 0 |  | 1 |  | Tenser/Terrain/BigCity | (300,800,100,100) |  |  |
| 1253 | small headstone v | 0 |  | 1 |  | Tenser/Terrain/BigCity | (400,800,100,100) |  |  |
| 1254 | headstone w cross V | 0 |  | 1 |  | Tenser/Terrain/BigCity | (500,800,100,100) |  |  |
| 1255 | rejuvinated sarcophagus H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (600,800,100,100) |  |  |
| 1256 | sleeping woman sarcophagus H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (700,800,100,100) |  |  |
| 1257 | blank sarcophagus H | 13 |  | 5 |  | Tenser/Terrain/BigCity | (800,800,100,100) |  |  |
| 1258 | purple wall H | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (0,0,100,100) |  |  |
| 1259 | purple texture/floor | 0 |  | 0 |  | Tenser/Terrain/dungeondreary | (100,0,100,100) |  |  |
| 1260 | purple wall V | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (200,0,100,100) |  |  |
| 1261 | purple column | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (300,0,100,100) |  |  |
| 1262 | purple rubble | 0 |  | 3 |  | Tenser/Terrain/dungeondreary | (400,0,100,100) |  |  |
| 1263 | purple wall ruin V | 0 |  | 4 |  | Tenser/Terrain/dungeondreary | (500,0,100,100) |  |  |
| 1264 | purple wall ruin H | 0 |  | 5 |  | Tenser/Terrain/dungeondreary | (600,0,100,100) |  |  |
| 1265 | purple column ruin | 0 |  | 4 |  | Tenser/Terrain/dungeondreary | (700,0,100,100) |  |  |
| 1266 | purple arched niche wall H | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (0,100,100,100) |  |  |
| 1267 | purple arched niche wall V | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (100,100,100,100) |  |  |
| 1268 | purple bare wall H | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (200,100,100,100) |  |  |
| 1269 | purple bare wall V | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (300,100,100,100) |  |  |
| 1270 | purple demonhead wall H | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (400,100,100,100) |  |  |
| 1271 | purple obstruction | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (500,100,100,100) |  |  |
| 1272 | purple pillar | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (600,100,100,100) |  |  |
| 1273 | purple tall pillar | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (700,100,100,100) |  |  |
| 1274 | purple cultist statue | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (0,200,100,100) |  |  |
| 1275 | purple maiden statue | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (100,200,100,100) |  |  |
| 1276 | purple bat wall ornament H | 0 |  | 5 |  | Tenser/Terrain/dungeondreary | (200,200,100,100) |  |  |
| 1277 | purple bat wall ornament V | 0 |  | 4 |  | Tenser/Terrain/dungeondreary | (300,200,100,100) |  |  |
| 1278 | purple wall ornament H | 0 |  | 5 |  | Tenser/Terrain/dungeondreary | (400,200,100,100) |  |  |
| 1279 | purple wall ornament V | 0 |  | 4 |  | Tenser/Terrain/dungeondreary | (500,200,100,100) |  |  |
| 1280 | king statue | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (600,200,100,100) |  |  |
| 1281 | dragon statue | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (700,200,100,100) |  |  |
| 1282 | desaturated blue wall H | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (0,300,100,100) |  |  |
| 1283 | desaturated blue texture/floor | 0 |  | 0 |  | Tenser/Terrain/dungeondreary | (100,300,100,100) |  |  |
| 1284 | desaturated blue wall V | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (200,300,100,100) |  |  |
| 1285 | desaturated blue column | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (300,300,100,100) |  |  |
| 1286 | desaturated blue rubble | 0 |  | 3 |  | Tenser/Terrain/dungeondreary | (400,300,100,100) |  |  |
| 1287 | desaturated blue wall ruin V | 0 |  | 4 |  | Tenser/Terrain/dungeondreary | (500,300,100,100) |  |  |
| 1288 | desaturated blue wall ruin H | 0 |  | 5 |  | Tenser/Terrain/dungeondreary | (600,300,100,100) |  |  |
| 1289 | desaturated blue column ruin | 0 |  | 4 |  | Tenser/Terrain/dungeondreary | (700,300,100,100) |  |  |
| 1290 | desaturated blue arched niche wall H | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (0,400,100,100) |  |  |
| 1291 | desaturated blue arched niche wall V | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (100,400,100,100) |  |  |
| 1292 | desaturated blue bare wall H | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (200,400,100,100) |  |  |
| 1293 | desaturated blue bare wall V | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (300,400,100,100) |  |  |
| 1294 | desaturated blue demonhead wall H | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (400,400,100,100) |  |  |
| 1295 | desaturated blue obstruction | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (500,400,100,100) |  |  |
| 1296 | desaturated blue pillar | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (600,400,100,100) |  |  |
| 1297 | desaturated blue tall pillar | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (700,400,100,100) |  |  |
| 1298 | desaturated blue cultist statue | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (0,500,100,100) |  |  |
| 1299 | desaturated blue maiden statue | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (100,500,100,100) |  |  |
| 1300 | desaturated blue bat wall ornament H | 0 |  | 5 |  | Tenser/Terrain/dungeondreary | (200,500,100,100) |  |  |
| 1301 | desaturated blue bat wall ornament V | 0 |  | 4 |  | Tenser/Terrain/dungeondreary | (300,500,100,100) |  |  |
| 1302 | desaturated blue wall ornament H | 0 |  | 5 |  | Tenser/Terrain/dungeondreary | (400,500,100,100) |  |  |
| 1303 | desaturated blue wall ornament V | 0 |  | 4 |  | Tenser/Terrain/dungeondreary | (500,500,100,100) |  |  |
| 1304 | desaturated blue king statue | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (600,500,100,100) |  |  |
| 1305 | desaturated blue dragon statue | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (700,500,100,100) |  |  |
| 1306 | double-desaturated green wall H | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (0,600,100,100) |  |  |
| 1307 | double-desaturated green texture/floor | 0 |  | 0 |  | Tenser/Terrain/dungeondreary | (100,600,100,100) |  |  |
| 1308 | double-desaturated green wall V | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (200,600,100,100) |  |  |
| 1309 | double-desaturated green column | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (300,600,100,100) |  |  |
| 1310 | double-desaturated green rubble | 0 |  | 3 |  | Tenser/Terrain/dungeondreary | (400,600,100,100) |  |  |
| 1311 | double-desaturated green wall ruin V | 0 |  | 4 |  | Tenser/Terrain/dungeondreary | (500,600,100,100) |  |  |
| 1312 | double-desaturated green wall ruin H | 0 |  | 5 |  | Tenser/Terrain/dungeondreary | (600,600,100,100) |  |  |
| 1313 | double-desaturated green column ruin | 0 |  | 4 |  | Tenser/Terrain/dungeondreary | (700,600,100,100) |  |  |
| 1314 | double-desaturated green arched niche wall H | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (0,700,100,100) |  |  |
| 1315 | double-desaturated green arched niche wall V | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (100,700,100,100) |  |  |
| 1316 | double-desaturated green bare wall H | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (200,700,100,100) |  |  |
| 1317 | double-desaturated green bare wall V | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (300,700,100,100) |  |  |
| 1318 | double-desaturated green demonhead wall H | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (400,700,100,100) |  |  |
| 1319 | double-desaturated green obstruction | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (500,700,100,100) |  |  |
| 1320 | double-desaturated green pillar | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (600,700,100,100) |  |  |
| 1321 | double-desaturated green tall pillar | 13 |  | 4 |  | Tenser/Terrain/dungeondreary | (700,700,100,100) |  |  |
| 1322 | double-desaturated green cultist statue | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (0,800,100,100) |  |  |
| 1323 | double-desaturated green maiden statue | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (100,800,100,100) |  |  |
| 1324 | double-desaturated green bat wall ornament H | 0 |  | 5 |  | Tenser/Terrain/dungeondreary | (200,800,100,100) |  |  |
| 1325 | double-desaturated green bat wall ornament V | 0 |  | 4 |  | Tenser/Terrain/dungeondreary | (300,800,100,100) |  |  |
| 1326 | double-desaturated green wall ornament H | 0 |  | 5 |  | Tenser/Terrain/dungeondreary | (400,800,100,100) |  |  |
| 1327 | double-desaturated green wall ornament V | 0 |  | 4 |  | Tenser/Terrain/dungeondreary | (500,800,100,100) |  |  |
| 1328 | double-desaturated green king statue | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (600,800,100,100) |  |  |
| 1329 | double-desaturated green dragon statue | 13 |  | 5 |  | Tenser/Terrain/dungeondreary | (700,800,100,100) |  |  |
| 1330 | Animated Portal | 37 |  | 3 |  | Tenser/Terrain/portal-Sheet | (0,0,3900,60) |  | anim 65f step100 |
| 1331 | Acid/Poison Spider Spitwad | 0 |  | 3 |  | Tenser/Terrain/spiderspit | (0,0,45,45) |  |  |
| 1332 | Electrified Hex trap | 0 |  | 1 |  | Tenser/Terrain/traps/electric_hex-Sheet | (0,0,1100,100) |  | anim 11f step100 |
| 1333 | Animated fire trap | 0 |  | 1 |  | Tenser/Terrain/traps/fire4-Sheet | (0,0,2100,100) |  | anim 21f step100 |
| 1334 | Animated lightning bolt trap | 0 |  | 1 |  | Tenser/Terrain/traps/Ltest5-Sheet | (0,0,2100,100) |  | anim 21f step100 |
| 1335 | Horizontal Wall blade trap | 0 |  | 1 |  | Tenser/Terrain/traps/traps-concept | (0,0,500,500) |  | anim 5f step100 |
| 1336 | Vertical Wall blade trap | 0 |  | 1 |  | Tenser/Terrain/traps/traps-concept | (0,0,500,500) |  | anim 5f step100 |
| 1337 | Floor Spike trap | 0 |  | 1 |  | Tenser/Terrain/traps/traps-concept | (0,0,500,500) |  | anim 5f step100 |
| 1338 | Horizontal arrow Trap | 0 |  | 1 |  | Tenser/Terrain/traps/traps-concept | (0,0,500,500) |  | anim 5f step100 |
| 1339 | Vertical arrow trap | 0 |  | 1 |  | Tenser/Terrain/traps/traps-concept | (0,0,500,500) |  | anim 5f step100 |
| 1340 | Red Brick Wall (H) | 13 |  | 5 |  | Tenser/Terrain/redbrickwalls | (0,0,100,100) |  |  |
| 1341 | Red Brick floor | 0 |  | 5 |  | Tenser/Terrain/redbrickwalls | (100,0,100,100) |  |  |
| 1342 | Red Brick Wall (V) | 13 |  | 4 |  | Tenser/Terrain/redbrickwalls | (200,0,100,100) |  |  |
| 1343 | Red Brick Post | 13 |  | 4 |  | Tenser/Terrain/redbrickwalls | (300,0,100,100) |  |  |
| 1344 | Red Brick rubble | 13 |  | 3 |  | Tenser/Terrain/redbrickwalls | (400,0,100,100) |  |  |
| 1345 | Red Brick Wall ruin (V) | 13 |  | 4 |  | Tenser/Terrain/redbrickwalls | (500,0,100,100) |  |  |
| 1346 | Red Brick Wall ruin (H) | 13 |  | 5 |  | Tenser/Terrain/redbrickwalls | (600,0,100,100) |  |  |
| 1347 | Red Brick post ruin | 13 |  | 4 |  | Tenser/Terrain/redbrickwalls | (700,0,100,100) |  |  |
| 1348 | icy caves wall (h) | 13 |  | 5 |  | Tenser/Terrain/icycavetiles | (0,0,100,100) |  |  |
| 1349 | icy caves floor | 0 |  | 0 |  | Tenser/Terrain/icycavetiles | (100,0,100,100) |  |  |
| 1350 | icy caves wall (v) | 13 |  | 4 |  | Tenser/Terrain/icycavetiles | (200,0,100,100) |  |  |
| 1351 | icy caves post | 13 |  | 4 |  | Tenser/Terrain/icycavetiles | (300,0,100,100) |  |  |
| 1352 | icy caves rubble | 13 |  | 3 |  | Tenser/Terrain/icycavetiles | (400,0,100,100) |  |  |
| 1353 | icy caves wall ruin (v) | 13 |  | 4 |  | Tenser/Terrain/icycavetiles | (500,0,100,100) |  |  |
| 1354 | icy caves wall ruin (h) | 13 |  | 5 |  | Tenser/Terrain/icycavetiles | (600,0,100,100) |  |  |
| 1355 | icy caves post ruin | 13 |  | 4 |  | Tenser/Terrain/icycavetiles | (700,0,100,100) |  |  |
| 1356 | glacial wall (h) | 13 |  | 5 |  | Tenser/Terrain/glacial | (0,0,100,100) |  |  |
| 1357 | glacial floor | 0 |  | 0 |  | Tenser/Terrain/glacial | (100,0,100,100) |  |  |
| 1358 | glacial wall (v) | 13 |  | 4 |  | Tenser/Terrain/glacial | (200,0,100,100) |  |  |
| 1359 | glacial wall ruin (h) | 13 |  | 5 |  | Tenser/Terrain/glacial | (300,0,100,100) |  |  |
| 1360 | glacial rubble | 13 |  | 3 |  | Tenser/Terrain/glacial | (400,0,100,100) |  |  |
| 1361 | glacial wall ruin (v) | 13 |  | 4 |  | Tenser/Terrain/glacial | (500,0,100,100) |  |  |
| 1362 | glacial post | 13 |  | 4 |  | Tenser/Terrain/glacial | (600,0,100,100) |  |  |
| 1363 | glacial post ruin | 13 |  | 4 |  | Tenser/Terrain/glacial | (700,0,100,100) |  |  |
| 1364 | nidavellir wall (h) | 13 |  | 5 |  | Tenser/Terrain/nidavellir | (0,0,100,100) |  |  |
| 1365 | nidavellir floor dark | 0 |  | 0 |  | Tenser/Terrain/nidavellir | (100,0,100,100) |  |  |
| 1366 | nidavellir wall (v) | 13 |  | 4 |  | Tenser/Terrain/nidavellir | (200,0,100,100) |  |  |
| 1367 | nidavellir post | 13 |  | 4 |  | Tenser/Terrain/nidavellir | (300,0,100,100) |  |  |
| 1368 | nidavellir rubble | 13 |  | 3 |  | Tenser/Terrain/nidavellir | (400,0,100,100) |  |  |
| 1369 | nidavellir wall ruin (v) | 13 |  | 4 |  | Tenser/Terrain/nidavellir | (500,0,100,100) |  |  |
| 1370 | nidavellir wall ruin (h) | 13 |  | 5 |  | Tenser/Terrain/nidavellir | (600,0,100,100) |  |  |
| 1371 | nidavellir post ruin | 13 |  | 4 |  | Tenser/Terrain/nidavellir | (700,0,100,100) |  |  |
| 1372 | nidavellir light floor | 0 |  | 0 |  | Tenser/Terrain/nidavellir | (800,0,100,100) |  |  |
| 1373 | nidavellir med mushroom | 13 |  | 1 |  | Tenser/Terrain/nidavellir | (0,100,100,100) |  |  |
| 1374 | nidavellir giant mushroom 1 | 13 |  | 1 |  | Tenser/Terrain/nidavellir | (100,100,100,100) |  |  |
| 1375 | nidavellir med mushroom 2 | 13 |  | 1 |  | Tenser/Terrain/nidavellir | (200,100,100,100) |  |  |
| 1376 | nidavellir giant mushroom 2 | 13 |  | 1 |  | Tenser/Terrain/nidavellir | (300,100,100,100) |  |  |
| 1377 | nidavellir med mushroom 3 | 13 |  | 1 |  | Tenser/Terrain/nidavellir | (400,100,100,100) |  |  |
| 1378 | nidavellir small mushroom cluster | 13 |  | 1 |  | Tenser/Terrain/nidavellir | (500,100,100,100) |  |  |
| 1379 | nidavellir small mush cluster 2 | 13 |  | 1 |  | Tenser/Terrain/nidavellir | (600,100,100,100) |  |  |
| 1380 | nidavellir mythril wall (h) | 13 |  | 5 |  | Tenser/Terrain/nidavellir | (700,100,100,100) |  |  |
| 1381 | nidavellir mythril wall (v) | 13 |  | 4 |  | Tenser/Terrain/nidavellir | (800,100,100,100) |  |  |
| 1382 | thin chamber door closed (h) | 4 |  | 7 |  | Tenser/Terrain/Doors/thinchamberdoor | (0,0,100,100) |  |  |
| 1383 | thin chamber door open (h) | 3 |  | 1 |  | Tenser/Terrain/Doors/thinchamberdoor | (100,0,100,100) |  |  |
| 1384 | thin chamber door ruin (h) | 3 |  | 3 |  | Tenser/Terrain/Doors/thinchamberdoor | (200,0,100,100) |  |  |
| 1385 | thin chamber door closed (v) | 4 |  | 6 |  | Tenser/Terrain/Doors/thinchamberdoor | (300,0,100,100) |  |  |
| 1386 | thin chamber door open (v) | 3 |  | 2 |  | Tenser/Terrain/Doors/thinchamberdoor | (400,0,100,100) |  |  |
| 1387 | thin chamber door ruin (v) | 4 |  | 3 |  | Tenser/Terrain/Doors/thinchamberdoor | (500,0,100,100) |  |  |
| 1388 | Rope North and up | 2 |  | 1 |  | Tenser/Terrain/ropeandvine | (0,0,100,100) |  |  |
| 1389 | Rope West and up | 2 |  | 1 |  | Tenser/Terrain/ropeandvine | (100,0,100,100) |  |  |
| 1390 | Rope East and up | 2 |  | 1 |  | Tenser/Terrain/ropeandvine | (200,0,100,100) |  |  |
| 1391 | Rope west and down | 1 |  | 1 |  | Tenser/Terrain/ropeandvine | (300,0,100,100) |  |  |
| 1392 | Rope North and down | 1 |  | 1 |  | Tenser/Terrain/ropeandvine | (400,0,100,100) |  |  |
| 1393 | Rope South and up | 2 |  | 1 |  | Tenser/Terrain/ropeandvine | (400,0,100,100) |  |  |
| 1394 | Rope East/South and down | 1 |  | 1 |  | Tenser/Terrain/ropeandvine | (500,0,100,100) |  |  |
| 1395 | Root North and up | 2 |  | 1 |  | Tenser/Terrain/ropeandvine | (0,100,100,100) |  |  |
| 1396 | Root West and up | 2 |  | 1 |  | Tenser/Terrain/ropeandvine | (100,100,100,100) |  |  |
| 1397 | Root East and up | 2 |  | 1 |  | Tenser/Terrain/ropeandvine | (200,100,100,100) |  |  |
| 1398 | Root West and down | 1 |  | 1 |  | Tenser/Terrain/ropeandvine | (300,100,100,100) |  |  |
| 1399 | Root South and up | 2 |  | 1 |  | Tenser/Terrain/ropeandvine | (400,100,100,100) |  |  |
| 1400 | Root North and down | 1 |  | 1 |  | Tenser/Terrain/ropeandvine | (400,100,100,100) |  |  |
| 1401 | Root East/south and down | 1 |  | 1 |  | Tenser/Terrain/ropeandvine | (500,100,100,100) |  |  |
| 1402 | vine North and up | 2 |  | 1 |  | Tenser/Terrain/ropeandvine | (0,200,100,100) |  |  |
| 1403 | vine west and up | 2 |  | 1 |  | Tenser/Terrain/ropeandvine | (100,200,100,100) |  |  |
| 1404 | vine East and up | 2 |  | 1 |  | Tenser/Terrain/ropeandvine | (200,200,100,100) |  |  |
| 1405 | vine West and down | 1 |  | 1 |  | Tenser/Terrain/ropeandvine | (300,200,100,100) |  |  |
| 1406 | vine North and down | 1 |  | 1 |  | Tenser/Terrain/ropeandvine | (400,200,100,100) |  |  |
| 1407 | vine South and up | 2 |  | 1 |  | Tenser/Terrain/ropeandvine | (400,200,100,100) |  |  |
| 1408 | vine East/South and down | 1 |  | 1 |  | Tenser/Terrain/ropeandvine | (500,200,100,100) |  |  |
| 1409 | icy rock floor | 0 |  | 0 |  | Tenser/Terrain/icyrockfloor | (0,0,100,100) |  |  |
| 1410 | icy snow floor | 0 |  | 0 |  | Tenser/Terrain/icysnowfloor | (0,0,100,100) |  |  |
| 1411 | snow floor | 0 |  | 0 |  | Tenser/Terrain/snowfloor | (0,0,100,100) |  |  |
| 1412 | climbable pole | 2 |  | 4 |  | Bitmaps/004-05 | (1200,1200,200,200) |  | res=2 |
| 1500 | n099y  floor  grass000 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (0,0,200,200) |  | res=2 |
| 1501 | n099y  floor  grass001 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (200,0,200,200) |  | res=2 |
| 1502 | n099y  floor  grass002 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (400,0,200,200) |  | res=2 |
| 1503 | n099y  floor  grass003 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (600,0,200,200) |  | res=2 |
| 1504 | n099y  floor  grass004 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (800,0,200,200) |  | res=2 |
| 1505 | n099y  floor  grass005 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1000,0,200,200) |  | res=2 |
| 1506 | n099y  floor  grass006 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1200,0,200,200) |  | res=2 |
| 1507 | n099y  floor  grass007 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1400,0,200,200) |  | res=2 |
| 1508 | n099y  floor  grass008 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1600,0,200,200) |  | res=2 |
| 1509 | n099y  floor  grass009 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1800,0,200,200) |  | res=2 |
| 1510 | n099y  floor  grass010 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (0,200,200,200) |  | res=2 |
| 1511 | n099y  floor  grass011 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (200,200,200,200) |  | res=2 |
| 1512 | n099y  floor  grass012 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (400,200,200,200) |  | res=2 |
| 1513 | n099y  floor  grass013 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (600,200,200,200) |  | res=2 |
| 1514 | n099y  floor  grass014 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (800,200,200,200) |  | res=2 |
| 1515 | n099y  floor  grass015 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1000,200,200,200) |  | res=2 |
| 1516 | n099y  floor  grass016 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1200,200,200,200) |  | res=2 |
| 1517 | n099y  floor  grass017 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1400,200,200,200) |  | res=2 |
| 1518 | n099y  floor  grass018 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1600,200,200,200) |  | res=2 |
| 1519 | n099y  floor  grass019 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1800,200,200,200) |  | res=2 |
| 1520 | n099y  floor  dirt000 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (0,400,200,200) |  | res=2 |
| 1521 | n099y  floor  dirt001 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (200,400,200,200) |  | res=2 |
| 1522 | n099y  floor  dirt002 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (400,400,200,200) |  | res=2 |
| 1523 | n099y  floor  dirt003 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (600,400,200,200) |  | res=2 |
| 1524 | n099y  floor  dirt004 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (800,400,200,200) |  | res=2 |
| 1525 | n099y  floor  sand005 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1000,400,200,200) |  | res=2 |
| 1526 | n099y  floor  sand006 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1200,400,200,200) |  | res=2 |
| 1527 | n099y  floor  sand007 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1400,400,200,200) |  | res=2 |
| 1528 | n099y  floor  gravel008 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1600,400,200,200) |  | res=2 |
| 1529 | n099y  floor  gravel009 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1800,400,200,200) |  | res=2 |
| 1530 | n099y  floor  water000 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (0,600,200,200) |  | res=2 |
| 1531 | n099y  floor  water001 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (200,600,200,200) |  | res=2 |
| 1532 | n099y  floor  water002 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (400,600,200,200) |  | res=2 |
| 1533 | n099y  floor  water003 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (600,600,200,200) |  | res=2 |
| 1534 | n099y  floor  water004 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (800,600,200,200) |  | res=2 |
| 1535 | n099y  floor  water005 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1000,600,200,200) |  | res=2 |
| 1536 | n099y  floor  portal006 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1200,600,200,200) |  | res=2 |
| 1537 | n099y  floor  portal007 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1400,600,200,200) |  | res=2 |
| 1538 | n099y  floor  portal008 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1600,600,200,200) |  | res=2 |
| 1539 | n099y  floor  portal009 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1800,600,200,200) |  | res=2 |
| 1540 | n099y  floor  water010 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (0,800,200,200) |  | res=2 |
| 1541 | n099y  floor  water011 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (200,800,200,200) |  | res=2 |
| 1542 | n099y  floor  water012 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (400,800,200,200) |  | res=2 |
| 1543 | n099y  floor  water013 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (600,800,200,200) |  | res=2 |
| 1544 | n099y  floor  water014 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (800,800,200,200) |  | res=2 |
| 1545 | n099y  floor  water015 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1000,800,200,200) |  | res=2 |
| 1546 | n099y  floor  portal016 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1200,800,200,200) |  | res=2 |
| 1547 | n099y  floor  portal017 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1400,800,200,200) |  | res=2 |
| 1548 | n099y  floor  portal018 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1600,800,200,200) |  | res=2 |
| 1549 | n099y  floor  portal019 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1800,800,200,200) |  | res=2 |
| 1550 | n099y  floor  water020 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (0,1000,200,200) |  | res=2 |
| 1551 | n099y  floor  water021 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (200,1000,200,200) |  | res=2 |
| 1552 | n099y  floor  water022 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (400,1000,200,200) |  | res=2 |
| 1553 | n099y  floor  water023 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (600,1000,200,200) |  | res=2 |
| 1554 | n099y  floor  water024 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (800,1000,200,200) |  | res=2 |
| 1555 | n099y  floor  water025 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1000,1000,200,200) |  | res=2 |
| 1556 | n099y  floor  water026 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1200,1000,200,200) |  | res=2 |
| 1557 | n099y  floor  water027 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1400,1000,200,200) |  | res=2 |
| 1558 | n099y  floor  water028 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1600,1000,200,200) |  | res=2 |
| 1559 | n099y  floor  water029 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1800,1000,200,200) |  | res=2 |
| 1560 | n099y  floor  water030 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (0,1200,200,200) |  | res=2 |
| 1561 | n099y  floor  water031 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (200,1200,200,200) |  | res=2 |
| 1562 | n099y  floor  water032 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (400,1200,200,200) |  | res=2 |
| 1563 | n099y  floor  water033 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (600,1200,200,200) |  | res=2 |
| 1564 | n099y  floor  water034 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (800,1200,200,200) |  | res=2 |
| 1565 | n099y  floor  water035 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1000,1200,200,200) |  | res=2 |
| 1566 | n099y  floor  portal036 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1200,1200,200,200) |  | res=2 |
| 1567 | n099y  floor  portal037 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1400,1200,200,200) |  | res=2 |
| 1568 | n099y  floor  portal038 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1600,1200,200,200) |  | res=2 |
| 1569 | n099y  floor  portal039 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1800,1200,200,200) |  | res=2 |
| 1570 | n099y  floor  water040 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (0,1400,200,200) |  | res=2 |
| 1571 | n099y  floor  water041 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (200,1400,200,200) |  | res=2 |
| 1572 | n099y  floor  water042 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (400,1400,200,200) |  | res=2 |
| 1573 | n099y  floor  water043 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (600,1400,200,200) |  | res=2 |
| 1574 | n099y  floor  water044 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (800,1400,200,200) |  | res=2 |
| 1575 | n099y  floor  water045 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1000,1400,200,200) |  | res=2 |
| 1576 | n099y  floor  water046 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1200,1400,200,200) |  | res=2 |
| 1577 | n099y  floor  water047 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1400,1400,200,200) |  | res=2 |
| 1578 | n099y  floor  water048 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1600,1400,200,200) |  | res=2 |
| 1579 | n099y  floor  water049 | 0 | 1 | 0 | true | n099y/terrain/terrain001 | (1800,1400,200,200) |  | res=2 |
| 1580 | n099y  decorations tree000 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (0,1600,200,200) |  | res=2 |
| 1581 | n099y  decorations tree001 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (200,1600,200,200) |  | res=2 |
| 1582 | n099y  decorations tree002 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (400,1600,200,200) |  | res=2 |
| 1583 | n099y  decorations tree003 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (600,1600,200,200) |  | res=2 |
| 1584 | n099y  decorations tree004 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (800,1600,200,200) |  | res=2 |
| 1585 | n099y  decorations tree005 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (1000,1600,200,200) |  | res=2 |
| 1586 | n099y  decorations tree006 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (1200,1600,200,200) |  | res=2 |
| 1587 | n099y  decorations tree007 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (1400,1600,200,200) |  | res=2 |
| 1588 | n099y  decorations tree008 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (1600,1600,200,200) |  | res=2 |
| 1589 | n099y  decorations tree009 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (1800,1600,200,200) |  | res=2 |
| 1590 | n099y  decorations tree010 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (0,1800,200,200) |  | res=2 |
| 1591 | n099y  decorations tree011 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (200,1800,200,200) |  | res=2 |
| 1592 | n099y  decorations tree012 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (400,1800,200,200) |  | res=2 |
| 1593 | n099y  decorations tree013 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (600,1800,200,200) |  | res=2 |
| 1594 | n099y  decorations tree014 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (800,1800,200,200) |  | res=2 |
| 1595 | n099y  decorations tree015 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (1000,1800,200,200) |  | res=2 |
| 1596 | n099y  decorations tree016 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (1200,1800,200,200) |  | res=2 |
| 1597 | n099y  decorations tree017 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (1400,1800,200,200) |  | res=2 |
| 1598 | n099y  decorations tree018 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (1600,1800,200,200) |  | res=2 |
| 1599 | n099y  decorations tree019 | 0 | 0 | 1 | false | n099y/terrain/terrain001 | (1800,1800,200,200) |  | res=2 |