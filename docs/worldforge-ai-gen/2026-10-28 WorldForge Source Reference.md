# WorldForge map format and rendering — source reference

Derived from the WorldForge editor source at `/home/claude/jkachhad/stormhalter/Source/Kesmai.WorldForge/` (assembly version `0.117.0`, `Properties/AssemblyInfo.cs:42`), the server component code under `Source/Kesmai.Server/Game/World/Maps/Components/`, the shipped art data `Content/Data/Terrain-External.xml`, the palette `Content/WorldForge/Components.xml`, and the sample legacy project `Segments/Praetoseba.mapproj` (version `0.102.2.0`). All element and attribute names below are quoted verbatim from code.

Written 2026-10-28.

---

## 0. Two on-disk formats: `.mapproj` (legacy) and the directory project (current)

This is the first surprise. The current editor **does not save `.mapproj` files**. It reads and writes a **directory-based project**; `.mapproj` is only an *import* ("Convert Segment") format.

### 0.1 Current format: directory project

`ApplicationPresenter.SaveSegment` (`Editor/MVP/Presenters/ApplicationPresenter.cs:346-469`) writes into a folder:

| File | Root element | Written by |
|---|---|---|
| `Segment.xml` | `<segment name="…" version="…"/>` (attributes only, no children) | line 400-403 |
| `Regions/{ID}.xml` | `<region>` (one file per region, named by numeric ID) | line 390-391; stale `Regions/*.xml` not matching a current region ID are **deleted** (line 384-388) |
| `Locations.xml` | `<locations>` | `SegmentLocations.Save` |
| `Subregions.xml` | `<subregions>` | `SegmentSubregions.Save` |
| `Entities.xml` | `<entities>` | `SegmentEntities.Save` |
| `Spawns.xml` | `<spawns>` | `SegmentSpawns.Save` |
| `Treasures.xml` | `<treasures>` | `SegmentTreasures.Save` |
| `Brushes.xml` | `<brushes>` | `SegmentBrushes.Save` |
| `Components.xml` | `<components>` | `SegmentComponents.Save` |
| `Templates.xml` | `<templates>` | `SegmentTemplates.Save` |
| `{SegmentName}.csproj` | MSBuild project (only created if missing) | line 415-461 |
| `Source/**/*.cs` | C# scripts compiled by the csproj (not written by Save) | |

The csproj it generates (line 419-435): `Sdk="Microsoft.NET.Sdk"`, `OutputType=Library`, `TargetFramework=net11.0`, `RootNamespace`/`AssemblyName` = segment name, `EnableDefaultItems=false`, `<Compile Include="Source/**/*.cs"/>`, `PackageReference`s to `Kesmai.Server.Reference` and `Kesmai.Server.Reference.Generator` (`Version="*"`), and an `<AdditionalFiles>` item for each of the nine XML files plus `Regions/*.xml`. The server-side source generator consumes those AdditionalFiles.

`OpenSegment` (line 241-344) opens a **folder**, uses the folder name as the segment name, reads the files above if present, and loads every `Regions/*.xml` as a `SegmentRegion`. Load order matters: Locations, Components, Brushes, Templates, then Regions, then Subregions, Entities, Spawns, Treasures. Components/Brushes/Templates must be loaded before regions because tiles may reference them by name (§4).

**Quirk:** OpenSegment reads `"Segments.xml"` (plural, line 295) while SaveSegment writes `"Segment.xml"` (singular, line 403). So on reopen the name attribute is never read; the folder name wins.

`Segment.OnSegmentFileChanged` (`Editor/MVP/Models/Segment.cs:107-144`) hot-reloads `locations/subregions/entities/spawns/treasures/components/brushes/templates.xml` when a FileSystemWatcher sees them change (but **not** region files).

### 0.2 Legacy format: `.mapproj` (single XML file)

`ConvertSegment` (`ApplicationPresenter.cs:525-712`) is the only code that reads `.mapproj`. It:

1. Loads the file; root must be `<segment>` with attributes `name` and `version` (both required, line 555-559).
2. Reads `<script>` and writes `Source/Internal.cs` from the **second** `<block>` of it as `public partial class {segmentName} { … }` in `namespace Kesmai.Server.Segments` (line 564-576).
3. Takes `<regions>/<region>` elements and saves each one verbatim to `Regions/{id}.xml` where `{id}` is the text of the region's `<id>` child (line 581-598).
4. Writes `Segment.xml` with `name` and the **editor's** `Core.Version`, not the file's version (line 619-621).
5. Copies `<locations>`, `<subregions>`, `<entities>`, `<spawns>`, `<treasures>` elements verbatim to their files (line 623-627); writes **empty** `<components/>`, `<brushes/>`, `<templates/>` (line 628-630).
6. Rewrites legacy 3-block `<script>` elements in spawns/entities/treasures into the current single-CDATA form (line 632-665): `<script name="…" enabled="…"><![CDATA[body]]></script>` where body = the second `<block>`'s text trimmed of leading/trailing `\r\n`.
7. There is a dead-code attempt to rename `LocationSpawner`→`LocationRegionSpawner` (line 610-617) that iterates `segmentRoot.Elements("spawns")` and switches on the *container's* name, so it never matches; the actual aliasing happens on load in `SegmentSpawns.Load` (§3.5).

The sample `Praetoseba.mapproj` has root children in this order: `script, regions, locations, subregions, entities, spawns, treasures, hoards`. `<hoards/>` is ignored by the converter.

**Bottom line for a generator:** the *region XML* is identical in both formats (a `<region>` element). To be loadable by the current editor you should emit a directory project; to be convertible you can emit a `.mapproj`. Everything below describes the region/tile/component element schema that both share.

---

## 1. Complete XML schema as WorldForge writes it

### 1.1 `Segment.xml` / `.mapproj` root

```xml
<segment name="MySegment" version="0.117.0.0" />
```

- `name` (string) — segment name; also the C# class name (spaces removed, `SegmentWorkspace.cs:118`).
- `version` (string) — `Core.Version.ToString()`, i.e. the editor's assembly version. On load the `Version` passed to every `Load(root, version)` is **always `Core.Version`**, never the file's; nothing in the editor branches on version (searched: no migration logic beyond the `.mapproj` converter).

In the legacy `.mapproj` the root additionally holds `<script name="Internal" enabled="true">` with three `<block>` CDATA children (prefix, body, suffix) and the collection elements described below as children.

### 1.2 `<region>` — `SegmentRegion.GetSerializingElement` (`Editor/MVP/Models/Game/SegmentRegion.cs:136-181`)

```xml
<region>
  <id>7</id>
  <name>Temple Forge</name>
  <height>0</height>
  <experienceMultiplier>1.5</experienceMultiplier>   <!-- omitted when == 1.0 -->
  <healthMultiplier>1.25</healthMultiplier>           <!-- omitted when == 1.0 -->
  <level>3</level>                                    <!-- omitted when == 0 -->
  <showTreasureInWater>true</showTreasureInWater>     <!-- omitted when false -->
  <bounds left="0" top="0" right="40" bottom="30" />  <!-- see note -->
  <tile x="0" y="0"> … </tile>
  …
</region>
```

| Element | C# | Type | Default | Omitted when default? | Notes |
|---|---|---|---|---|---|
| `id` | `ID` | int | — | never | file is named `{id}.xml`; CreateRegion picks the lowest free positive integer (`ApplicationPresenter.cs:476-485`) |
| `name` | `Name` | string | `"Region {id}"` | never | |
| `height` | `Elevation` | int | 0 | **never** (always written) | Elevation in feet. Only consumer is the server's `Teleporter.Initialize` (`Kesmai.Server/.../Teleporters/Teleporter.cs:51-54`): `_elevationDelta = destinationRegion.Elevation - region.Elevation`. Used by Sky ("It looks like a N foot drop", fall damage, death if >4500), Rope/Staircase `Descends => _elevationDelta < 0`, Shaft fall height. It does **not** affect rendering, pathing or vision. |
| `experienceMultiplier` | `ExperienceMultiplier` | double | 1.0 | yes | |
| `healthMultiplier` | `HealthMultiplier` | double | 1.0 | yes | |
| `level` | `Level` | double | 0 | yes | |
| `showTreasureInWater` | `ShowTreasureInWater` | bool | false | yes | |
| `bounds` | — | attrs `left top right bottom` | — | omitted if region has no tiles | **Write-only.** Computed from the minimal tile bounds (`GetMinimalBounds`, line 253-287). `right = left + width` and `bottom = top + height`, i.e. **exclusive** (one past the last tile). The constructor never reads it (line 95-112). Safe to omit. |
| `tile` | — | | | | one per non-null tile, iterated **y outer, x inner** over the bounds rectangle (line 167-180); attributes `x`, `y` are appended *after* the component children are built, but XElement attribute order is x then y. |

Region read: `_id = (int)element.Element("id")`, `_name = (string)element.Element("name")`, `_elevation = (int)element.Element("height")` — `id`, `name` and **`height` are required** (an InvalidCast/NullReference will throw if `height` is absent). The others use defaulting helpers from `Extensions/System.Xml.Linq/XElement.cs` (`Element(name, double default)`, `Element(name, bool default)`).

Region properties not serialized: none besides the above. Regions are stored as 100×100 chunks keyed by floor-divided coordinates, so **negative coordinates are valid** (`FloorDivide`, line 209-217). The sample has a hidden teleporter targeting `destinationY = -4`.

### 1.3 `<tile>` — `SegmentTile.GetSerializingElement` (`SegmentTile.cs:76-84`)

```xml
<tile x="12" y="5">
  <component type="FloorComponent"><ground>265</ground></component>
  <component type="WallComponent"><wall>31</wall><destroyed>0</destroyed><ruins>0</ruins></component>
  <component name="My Named Component" />     <!-- reference to Components.xml entry -->
  <template name="Pillar Room Corner" />      <!-- reference to Templates.xml entry -->
  <brush name="Forest Floor" />               <!-- reference to Brushes.xml entry -->
</tile>
```

- `x`, `y` integer attributes (read with `(int)element.Attribute("x")`).
- Children: one element per provider, **in list order**, each from `provider.GetReferencingElement()`:
  - `TerrainComponent` → full `<component type="…">…</component>` (`GetReferencingElement() => GetSerializingElement()`, `TerrainComponent.cs:117`).
  - `SegmentComponent` → `<component name="…"/>` (`SegmentComponent.cs:197-200`).
  - `SegmentTemplate` → `<template name="…"/>` (`SegmentTemplate.cs`).
  - `SegmentBrush` → `<brush name="…"/>` (`SegmentBrush.cs`).
- **Provider order = draw order input** (see §3). The DrawTool appends new components at the end; there is also UI to move a provider up/down.
- An empty `<tile>` (no children) is legal and is still a "tile" (it exists; region bounds include it). Tiles absent from the file are `null` and render nothing (black).

Tile read (`SegmentTile.cs:45-65`): every child element goes through `ComponentPalette.TryGetComponent(element)` (`Editor/ComponentPalette.cs:454-499`):

1. If the element has a `name` attribute and a palette entry with that name exists (case-insensitive; first match in category order across STATIC, EDITOR, SEGMENT→Components/Brushes/Templates), that palette object is used **regardless of element name** (`<component name=…>`, `<template name=…>`, `<brush name=…>` all resolve the same way). Note a `name` attribute on a full inline `<component type=…>` would also trigger this lookup, so **do not put a `name` attribute on inline components** unless you intend a palette reference.
2. Otherwise, only if the local name is exactly `component`: type is `Kesmai.WorldForge.Models.{type}` resolved with `Type.GetType` (so `type` is **case-sensitive** and must be the exact C# class name); if the `type` attribute is missing the type defaults to `StaticComponent`. The type's `(XElement)` constructor is invoked. Unknown type or failed ctor → element silently dropped (`TryGetComponent` returns false and the tile skips it).

### 1.4 `Locations.xml` — `SegmentLocation.cs`

```xml
<locations>
  <location name="Entrance" x="11" y="11" region="3" />
  <location name="Resurrect" x="8" y="15" region="1" />
  <location name="Facet" x="0" y="0" region="0" />
  <location name="Thief" x="0" y="0" region="0" />
</locations>
```

All four attributes required (`name` string, `x y region` int). The four names `Entrance`, `Resurrect`, `Facet`, `Thief` are **reserved** and auto-created in every new segment (`Segment.cs:30-33`); the locations collection prevents removing them.

### 1.5 `Subregions.xml` — `SegmentSubregion.cs`

```xml
<subregions>
  <subregion name="Town Square" type="Town" region="0">
    <rectangles>
      <rectangle left="10" top="10" right="20" bottom="20" />
    </rectangles>
  </subregion>
</subregions>
```

- `type` is the enum name `None | Town | Lair` (parsed case-insensitively; written as `ToString()`). Default `None`.
- `<rectangles>` is always written (possibly empty). Rectangle attrs are `SegmentBounds` Left/Top/Right/Bottom, **inclusive** (`SegmentBounds.Width = right-left+1`).
- Editor colors: None gray, Town green, Lair orange (overlay only).

### 1.6 `Entities.xml` — `SegmentEntity.cs`

```xml
<entities>
  <entity name="goblin">
    <script name="OnSpawn" enabled="true"><![CDATA[	return new Goblin();]]></script>
    <script name="OnDeath" enabled="false"><![CDATA[…]]></script>
    <script name="OnIncomingPlayer" enabled="true"><![CDATA[…]]></script>
    <notes>free text</notes>        <!-- omitted when empty -->
    <group>animals\mammals</group>  <!-- omitted when empty; backslash-separated tree path -->
  </entity>
</entities>
```

Scripts (`Editor/Scripting/Script.cs`): `<script name="…" enabled="true|false">` with the body as CDATA (`(string)element` on read, so any text works). Scripts with whitespace-only bodies are **not written**. Known script names per object come from `[Script(...)]` attributes: entity `OnSpawn` (`CreatureEntity OnSpawn()`, default body `return new MobileEntity();`), `OnDeath` (`void OnDeath(MobileEntity source, MobileEntity killer)`), `OnIncomingPlayer` (`void OnIncomingPlayer(MobileEntity source, PlayerEntity player)`). Unknown script names in the file are loaded but then dropped from the collection (only attribute-declared names survive `ValidateScripts`).

### 1.7 `Spawns.xml` — `SegmentSpawner.cs`, `Collections/SegmentSpawns.cs`

```xml
<spawns>
  <spawn type="LocationSegmentSpawner" name="EntranceSpawn" enabled="true">
    <minimumDelay>900</minimumDelay>     <!-- seconds, always written -->
    <maximumDelay>900</maximumDelay>     <!-- seconds, always written -->
    <maximum>1</maximum>                 <!-- omitted when <= 0 -->
    <script name="OnBeforeSpawn" enabled="false"><![CDATA[…]]></script>
    <script name="OnAfterSpawn" enabled="false"><![CDATA[…]]></script>
    <entry entity="goblin" size="1" minimum="1" maximum="1" />
    <location x="11" y="11" region="3" />
  </spawn>
  <spawn type="RegionSegmentSpawner" name="Forest" enabled="true">
    <minimumDelay>300</minimumDelay>
    <maximumDelay>600</maximumDelay>
    <maximum>10</maximum>
    <entry entity="wolf" size="2" minimum="1" maximum="3" />
    <bounds region="0">
      <inclusion left="0" top="0" right="50" bottom="50" />
      <exclusion left="10" top="10" right="12" bottom="12" />
    </bounds>
  </spawn>
</spawns>
```

- `type` written as the C# class name. On load (`SegmentSpawns.cs:70-71`) accepted aliases: `LocationSegmentSpawner` or legacy `LocationSpawner`; `RegionSegmentSpawner` or legacy `RegionSpawner`.
- `enabled` defaults to true if unparsable. Delays are integer seconds; non-integer → 0.
- `<entry entity="…" size="…" minimum="…" maximum="…"/>`: `entity` must name an existing `<entity>` (load throws otherwise, `SegmentSpawns.cs:96`); `size` is required.
- Location spawner: `<location x y region/>`. Region spawner: `<bounds region="…">` with zero or more `<inclusion>`/`<exclusion>` rectangles (inclusive coords; only rectangles with non-zero width and height are written).
- Scripts: `OnBeforeSpawn(Spawner spawner)`, `OnAfterSpawn(Spawner spawner, MobileEntity spawn)`.
- All location spawners are written first, then all region spawners.

### 1.8 `Treasures.xml` — `SegmentTreasure.cs`, `Collections/SegmentTreasures.cs`

```xml
<treasures>
  <treasure name="Goblin Loot">
    <notes>…</notes>                                   <!-- omitted when empty -->
    <entry weight="3">
      <notes>…</notes>
      <script name="OnCreate" enabled="true"><![CDATA[	return new Gold(50);]]></script>
    </entry>
    <entry weight="1" />
  </treasure>
  <treasure name="Dragon Hoard" hoard="true">
    <entry weight="1">…</entry>
    <script name="GetChance" enabled="true"><![CDATA[	return 100;]]></script>
  </treasure>
</treasures>
```

- `hoard="true"` attribute marks a `SegmentHoard` (adds `GetChance(Facet facet, int regionIndex)` script, written after entries). Attribute is added only for hoards.
- `entry weight` is required int; chance = weight / total weight (computed, not stored).
- Entry script: `OnCreate(MobileEntity from, Container container)` returning `ItemEntity`.

### 1.9 `Components.xml` (segment-local palette) — `Collections/SegmentComponents.cs`, `SegmentComponent.cs`

```xml
<components>
  <component type="WallComponent" name="Forge Wall (H)" category="Walls:Forge">
    <wall>1234</wall><destroyed>40</destroyed><ruins>45</ruins>
    <indestructible>true</indestructible>
    <color r="200" g="180" b="160" a="255" />
  </component>
</components>
```

A `SegmentComponent` is a named wrapper around one inline `TerrainComponent` definition. On save (`SegmentComponent.GetSerializingElement`, line 183-195) the stored element is cloned and its `name` attribute replaced with the current name. Optional `category="A:B:C"` attribute places it in a palette subtree (colon-separated, `ComponentPalette.cs:357-385`). Tiles reference it as `<component name="Forge Wall (H)"/>`; changing the definition changes every tile using it. The `type` attribute is required (XmlException otherwise).

The same element schema is used by the global palette `Content/WorldForge/Components.xml` (`<data>` root, `category` attribute **required** there, `ComponentPalette.Load`). That file ships 1137 named components in categories: Floors, Water, Structural, Customizable, Ruins, Doors, Stairs, Teleport, Ropes, Vegetation, Obstructions, Counters and Altars, Decorations, lighting and shade, Misc., Grove, Wall Doodads (H), Traps. Those names are also resolvable from tiles (`<component name="Town (H)"/>`), but the palette is fetched from the `Kesmai.Server.Reference` NuGet package at runtime, so a generator should prefer inline components.

### 1.10 `Templates.xml` — `SegmentTemplate.cs`

```xml
<templates>
  <template name="Pillar">
    <component type="FloorComponent"><ground>5</ground></component>
    <component type="ObstructionComponent"><obstruction>88</obstruction></component>
    <component name="Shared Rubble" />
  </template>
</templates>
```

A template is a **named stack of providers for a single tile** (not a multi-tile stamp). Children use the same referencing rules as `<tile>` children. See §4.

### 1.11 `Brushes.xml` — `SegmentBrush.cs`, `SegmentBrushEntry.cs`

```xml
<brushes>
  <brush name="Forest Floor">
    <entry weight="5"><component type="FloorComponent"><ground>13</ground></component></entry>
    <entry weight="1"><component type="FloorComponent"><ground>14</ground></component></entry>
    <entry weight="1"><template name="Mossy Rock" /></entry>
  </brush>
</brushes>
```

Each `<entry weight="n">` wraps exactly one provider element (first child used; `weight` defaults to 1). See §4.

### 1.12 Child order summary (region file)

`id, name, height, [experienceMultiplier], [healthMultiplier], [level], [showTreasureInWater], [bounds], tile*`. Inside `<component>`: `type` attribute, then base-class children `[color]`, `[comment]`, then the subclass children in the order listed in §2.

---

## 2. Component catalogue

Base behaviour (`Editor/MVP/Models/World/Components/TerrainComponent.cs`):

- `type` attribute = `GetType().Name` (`GetTypeAlias`, line 122). Namespace is fixed to `Kesmai.WorldForge.Models`.
- **Color**: `<color r="R" g="G" b="B" a="A"/>` with integer 0–255 channels; written **only when `Color != Color.White`** (255,255,255,255); default White on read when absent. Read requires all four attributes (`(int)colorElement.Attribute("a")` throws if missing). Color is passed to `SpriteBatch.Draw` as the tint (component-wise multiply with texture RGBA, premultiplied). Black (0,0,0) makes a sprite invisible. The sample .mapproj uses no colors at all.
- **Comment**: `<comment>text</comment>`, written when non-whitespace. Editor-only; shows a comment icon on the tile.
- `name` attribute on a component is palette metadata and is not serialized by `TerrainComponent` itself.
- Numeric children are written as plain integers; booleans as `true`/`false` (XElement bool formatting, lowercase).

Below, "ID" means a terrain id looked up in `TerrainManager` (§3.3). "Req" = constructor throws if missing. All classes live under `Editor/MVP/Models/World/Components/`.

### 2.1 `StaticComponent` (`StaticComponent.cs`)

| child | C# | type | default | omitted? | meaning |
|---|---|---|---|---|---|
| `static` | `Static` | int | Req | no | terrain id drawn. Pure decoration; server `Static` has no pathing/vision interface (walkable, see-through). |

Subclasses with identical XML: **`TrashComponent`** (Structural/TrashComponent.cs; server: trash can), **`LockersComponent`** (Environmental; default static id 119; server: locker interaction), **`Web`** (Magical/Web.cs; adds `<allowDispel>true</allowDispel>` omitted when false; default static id 131 in the editor constructor but `static` is still required from XML).

### 2.2 `FloorComponent` (Structural/FloorComponent.cs)

| child | C# | type | default | omitted? | meaning |
|---|---|---|---|---|---|
| `ground` | `Ground` | int | Req | no | terrain id |
| `movementCost` | `MovementCost` | int | 1 | when == 1 | server `Floor.GetMovementCost` returns it: cost to walk **off** this tile |

Subclasses:

- **`IceComponent`**: same XML as Floor (ctor forces movementCost 1 when created from code). Server `Ice`: passable; players slip (`Interrupted`) if `Random(1,20) > Willpower`.
- **`WaterComponent`**: adds `depth` (int, default 3, omitted when == 3). Editor ctor clamps movementCost to `min(depth,3)`. Server `Water`: `HandleMovementPath` → `Allowed` for flying creatures / WaterWalking status, else `Interrupted`; cost = `min(depth, movementCost)` (1 with water walking). Palette's "Water" entry is `ground 22, depth 3, movementCost 3`.
- **`PoisonedWaterComponent`**: Water + `potency` (int, default 3, omitted when == 3).

The DrawTool treats `FloorComponent, WaterComponent, IceComponent, SkyComponent` as mutually exclusive "floor types": placing one removes any existing one on the tile (`Editor/Tools/DrawTool.cs:41-46, 96-104`). For any other type it removes existing components whose type `IsAssignableFrom` the new type (so placing a `WallComponent` replaces an existing wall).

### 2.3 `WallComponent` (Structural/WallComponent.cs)

| child | C# | type | default | omitted? | meaning |
|---|---|---|---|---|---|
| `wall` | `Wall` | int | Req | no | terrain id of intact wall |
| `destroyed` | `Destroyed` | int | Req | no | terrain id shown when destroyed (0 allowed; sample uses 0) |
| `ruins` | `Ruins` | int | Req | no | terrain id of rubble drawn under the destroyed sprite (0 = none) |
| `indestructible` | `IsIndestructible` | bool | false | when false | cannot be broken |

Render: intact → `wall`; with the editor's "Break Walls" visibility toggle and not indestructible → `ruins` (if ≠0) then `destroyed`. Server `Wall`: `BlocksVision = !IsDestroyed`; `AllowMovementPath = _isDestroyed`; moving into an intact wall → `PathingResult.Daze`; spells pass only if destroyed or `CreatePortalSpell`. The HammerTool toggles `indestructible`.

Wall sprites are drawn at order 4 (vertical) / 5 (horizontal) and sit on the tile's north/west edge visually (sprite is 100×100 drawn at tile origin minus 45px, §3.1) — a wall occupies a whole tile cell in the grid; "H"/"V" palette variants are the two edge orientations.

### 2.4 `DoorComponent` (Structural/DoorComponent.cs)

| child | C# | type | default | omitted? | meaning |
|---|---|---|---|---|---|
| `openId` | `OpenId` | int | Req | no | terrain id when open |
| `closedId` | `ClosedId` | int | Req | no | terrain id when closed |
| `secretId` | `SecretId` | int | Req | no | terrain id shown while secret (looks like wall) |
| `destroyedId` | `DestroyedId` | int | Req | no | terrain id when destroyed |
| `isSecret` | `IsSecret` | bool | false | when false | |
| `isOpen` | `IsOpen` | bool | false | when false | |
| `isDestroyed` | `IsDestroyed` | bool | false | **bug: written only when `isOpen` is true** (line `if (_isOpen) element.Add("isDestroyed", _isDestroyed)`) — a closed destroyed door loses the flag on save | |
| `indestructible` | `IsIndestructible` | bool | false | when false | |

Child write order: openId, closedId, secretId, destroyedId, [isSecret], [isOpen], [isDestroyed], [indestructible]. Render: `isOpen` (or "Open Doors" toggle) → openId else closedId; secret + "Hide Secret Doors" toggle → secretId; destroyed (or "Break Walls" and not indestructible) → destroyedId. Server `Door`: `IsOpen => _isOpen || IsDestroyed`; `BlocksVision = !IsOpen`; `AllowMovementPath = IsOpen || !IsSecret`; path into a closed door → `Interrupted` (secret → `Daze`); cost 3 closed / 1 open; interaction opens/closes.

### 2.5 `ObstructionComponent` (Structural/ObstructionComponent.cs)

| child | C# | type | default | omitted? |
|---|---|---|---|---|
| `obstruction` | `Obstruction` | int | Req | no |
| `blockVision` | `BlockVision` | bool | false | when false |

Server: `PathingPriority = 1` (evaluated before walls/doors/water which are 0); movement **`Rejected`** (hard block, no daze); spells pass. Used for pillars, stalagmites, reefs, trees-as-blockers.

### 2.6 `RuinsComponent` (Structural/RuinsComponent.cs)

`ruins` (int, Req). Server: passable, movement `Interrupted`, cost 3. Standalone rubble.

### 2.7 `CounterComponent` (Structural/CounterComponent.cs)

| child | C# | type | default | omitted? |
|---|---|---|---|---|
| `counter` | `Counter` | int | Req | no |
| `direction` | `AccessDirection` | int (Direction index) | null | when null |

Direction index is the numpad layout `1 NW, 2 N, 3 NE, 4 W, 5 None, 6 E, 7 SW, 8 S, 9 SE` (`Shared/Direction.cs`); UI restricts counters to cardinal `2,4,6,8`. Editor draws counter **red** when no direction set. Server: impassable (`Daze`), spells blocked; the direction is the side players interact from.

### 2.8 `AltarComponent` (Structural/AltarComponent.cs)

`altar` (int, Req). Server: impassable (`Daze`).

### 2.9 Teleporters (Teleporters/)

Base **`TeleportComponent`** (abstract): `destinationX`, `destinationY`, `destinationRegion` (ints, each **omitted when 0**, default 0). Write order: dX, dY, dRegion, then subclass. Editor draws the sprite **red** if the destination region/tile does not exist in the segment (`IsValid`). The sample has 483 SkyComponents with dest 0 omitted.

| type | extra children (order) | default / omit | notes |
|---|---|---|---|
| `PassiveTeleporterComponent` | `teleporterId` int Req | always written | teleports on step-on |
| `SkyComponent` : Passive | none | | server: fall to destination; elevation delta = drop distance; flyers exempt |
| `ActiveTeleporter` (abstract) | `teleporterId` int Req | always | requires interaction (climb/stairs) |
| `StaircaseComponent` : Active | none (palette files carry a `<descends>` child that the **editor ignores** and does not write; server reads it) | | server `Descends = elevationDelta<0 || _descends` |
| `RopeComponent` : Active | `isSecret` bool (omit false), `slipChance` int (omit ≤0) | | secret ropes are not drawn in the editor |
| `ShaftComponent` : Active | `slipChance` int (omit ≤0) | | |
| `EgressComponent` (: TerrainComponent, not Teleport) | `egress` int Req, `destinationSegment` int (omit 0) | | cross-segment exit; drawn red when destinationSegment ≤ 0 |
| `HiddenTeleporterComponent` : Teleport | `lightphases`, `moonphases`, `professions`, `alignments` (always written), `message` int (omit ≤0), `level` int (omit ≤0), `allowNPC` bool (omit false) | | no terrain id; editor draws built-in `WorldForge/Terrain/Teleporter` sprite at order 9 tinted cyan (0,255,255,150). `Color` is hidden in the UI. |
| `ItemTeleporter` : Hidden | `type` string (omit empty), `fail` enum name (omit when `Allowed`; read default `Interrupted`) | | teleports items of a type |
| `SpeechTeleporter` : Hidden | `teleporterId` int (always; read default 0), `phrase` string (omit empty) | | if teleporterId>0 draws that terrain, else green teleporter marker |

Selector lists (Hidden): each of the four is written as `<x select="all"/>` when the full set is selected, `<x select="none"/>` when empty, otherwise the element text is a comma-joined list. On read a missing element means **all**; `select="all"` means all; any other `select` value yields an **empty** list; a text value is split on `,` and matched exactly (`First(...)` throws on an unknown name). Valid names:
- lightphases: `dawn, sunrise, daytime, sundown, midnight, nighttime` (`Shared/Lightphase.cs`)
- moonphases: `new, waxing crescent, first half, waxing gibbous, full, waning gibbous, last half, waning crescent`
- professions: `Fighter, Martial Artist, Thaumaturge, Thief, Wizard, Knight`
- alignments: `Lawful, Neutral, Chaotic, Evil` (uses `Description`)

`PathingResult` enum (`Shared/PathingResult.cs`): `Allowed=0, Rejected, Interrupted, Daze`.

### 2.10 Traps (Functional/)

All derive from abstract **`TrapComponent`**: `cooldown` int (omit ≤0), `trapCreatures` bool **default true** (written only when false), `trapPlayer` bool (omit false), `interruptMovement` bool (omit false). No terrain id; editor draws the cyan teleporter marker at order 9.

- `DamageTrap`: `damage` int (omit ≤0).
- `ActionTrap`: `action` string (omit empty) — C# snippet/handler name.
- `SpellTrap` (abstract): `skill` int (omit ≤0). Concrete types: `WhirlwindTrap` (+`direction` int index, omit null), `PoisonCloudTrap` (+`direction`), `BonfireTrap`, `FirestormTrap`, `ConcussionTrap`, `LightningBoltTrap`, `BlindTrap`, `FearTrap`, `StunTrap`.
- `ItemActionComponent` (not a trap): `tag`, `itemAdded`, `itemRemoved` strings (omit empty), `ignoreTeleports` bool (omit false). Drawn with a pale-cyan marker.

### 2.11 Magical (Magical/)

| type | children | render |
|---|---|---|
| `Darkness` | `allowDispel` bool (omit false) | hard-coded terrain **7** |
| `Fire` | `damage` int default 3 (omitted when ≤0 **or == 3**), `allowDispel` | hard-coded terrain **135** |
| `Whirlwind` | `damage` int (omit ≤0), `allowDispel` | hard-coded terrain **132** |
| `Web` | `static` (inherited, Req), `allowDispel` | its `static` id |

### 2.12 `TreeComponent` (Environmental/TreeComponent.cs)

| child | C# | type | default | omitted? |
|---|---|---|---|---|
| `tree` | `Tree` | int | Req | no |
| `canGrow` | `CanGrow` | bool | **Req** (`(bool)element.Element("canGrow")` throws if absent) | **never omitted** |
| `decayed` | `IsDecayed` | bool | false | when false |

Render: the tree id is looked up in a hard-coded alive/dead stage table (line 38-90); `decayed` draws the paired dead id (e.g. 98/99/100 → 101/102/103; 201/200/199 → same deads; 370→372; 403→402; 893-896→897; 1373-1377→1378; most others → 103). Unknown ids draw `101` when decayed. Trees are decoration only in the editor; the server `Tree` grows through stages when `canGrow`.

### 2.13 Types that exist in Components.xml but whose palette fields the editor drops

`StaircaseComponent` palette entries contain `<descends>`; the editor does not read or write it, so round-tripping a palette door through the editor loses it (the server reads it directly from the XML it is given, so a generator **may** include `<descends>true</descends>` and the editor will simply pass it through only if the tile references the palette entry by name; an inline component will lose it on next save).

---

## 3. Rendering

### 3.1 Grid, tile size, coordinates

- **Flat square grid, not isometric.** Each tile is `UnitSize = 55` px at zoom 1 (`ApplicationPresenter.cs:38`); `TileSize = floor(55 * zoom)` (`WorldGraphicsScreen.cs:119`).
- **x increases right, y increases down.** Screen position of tile `(x,y)` is `((x - view.Left) * TileSize, (y - view.Top) * TileSize)` (`GetRenderRectangle`, line 200-206). The camera stores the top-left tile.
- Every sprite of a tile is drawn with its top-left at **`tileOrigin - (45, 45) * zoom`** plus the sprite's own `<offset>` (`OnRenderTile` line 357-363, `OnRenderTerrain` line 400-413). Sprites in `Terrain-External.xml` are 100×100 source rects, so a 100-px sprite covers the 55-px cell plus a 45-px apron up and to the left, i.e. the sprite's bottom-right 55×55 is the cell. This is how walls "stand up" above the floor and overlap the tile to the north/west. Scale factor passed to `SpriteBatch.Draw` is `zoom / sprite.Resolution` (`resolution="2"` sprites are 200×200 sources drawn at half size).
- `BrushGraphicsScreen` and `TemplateGraphicsScreen` use the same constants (55 cell, −45 apron, 100 draw; template preview uses a 160-px box).
- Tiles are iterated x-outer, y-inner over the view (line 292-307); overlap between neighbouring tiles is therefore resolved by **iteration order, not by order value** — a tile at larger x is painted after its west neighbour, and within a column larger y after smaller y. Per-tile layer order (§3.2) only orders sprites of the same tile.
- Tint: `render.Color` → `SpriteBatch.Draw(..., color, ...)`. `SamplerState.PointClamp` (no filtering). Background is black. Missing tiles draw nothing.
- The editor renders to an offscreen target capped at 4096×16384 and only redraws on invalidation.

### 3.2 Per-tile draw order

`SegmentTile.UpdateTerrain` (`SegmentTile.cs:179-213`):

1. Walk `Providers` in list order; for each provider expand `GetComponents()` (a template yields its providers; a brush yields itself; a segment component yields its inner terrain component).
2. For each component passing the active filter, call `GetRenders()` → zero or more `ComponentRender(Terrain, Color)`.
3. Flatten every `TerrainLayer` of every terrain into `TerrainRender(layer, color)`.
4. **Stable insertion sort by `layer.Order` ascending** (equal orders keep provider order).

So the final draw order on a tile is `sprite order` attribute first, provider list order second. Order values used by the shipped art (comment block in `Terrain-External.xml` and actual data): `0` floors/water; `1` open doors (H), decorations, trees, tall grass; `2` open doors (V); `3` rubble, ruins, bridges, magic effects; `4` walls V, counters, obstructions, corner posts; `5` walls H; `6` closed doors V; `7` closed doors H. Editor-only markers (traps, hidden teleporters) use `9`.

Practical consequence: **placing a floor after a wall in the XML is fine** — the sort puts order-0 floors under order-4/5 walls regardless. Provider order only matters among same-order sprites (e.g. two statics).

### 3.3 Terrain id → sprites (`Editor/Terrain.cs`, `Editor/TerrainManager.cs`, `Game/GameSprite.cs`)

`TerrainManager` is a `Dictionary<int, Terrain>` built from `Data\Terrain.xml` (inside the `Data.bin` archive — the base Kesmai art, ids roughly 1–621, not in the repo) then `Data\Terrain-External.xml` (repo `Content/Data/`, ids 622–1599, 882 entries), with an optional override file at `{CustomArtPath}\Data\Terrain-External.xml`. Later definitions with the same id replace earlier ones.

```xml
<terrain id="624" action="0" cost="6">
  <sprite order="1" underpile="true" resolution="2">
    <texture>Tenser\Terrain\Trees</texture>   <!-- content path, or loose .png under CustomArtPath -->
    <source>(0,0,100,100)</source>            <!-- x,y,w,h in the sheet -->
    <offset>(0,-40)</offset>                  <!-- optional draw offset in px -->
    <frames step="150" keys="0-19"><frame>(0,0,100,100)</frame>…</frames>  <!-- animation; editor uses first frame only -->
  </sprite>
  <average>(52,105,23,255)</average>          <!-- avg color for 1px/tile heatmaps; editor ignores -->
</terrain>
```

- `Terrain` reads `id`, optional `lom`, optional comma list `tif` (legacy cross-reference ids; `FromLom`/`FromTIF` helpers), and each `<sprite>`'s `order` and `underpile`.
- `GameSprite.Initialize` reads `texture`, `source` (Vector4 "(x,y,z,w)"), optional `offset`, optional `resolution` attribute (default 1), optional `frames` (first frame rect is cut as a static texture). `Core.CustomArtPath` (`.storage\CustomArt.cfg` first line) lets loose `{texture}.png` files win over archived content.
- `action` (0=none, 1 climb down, 2 climb up, 3 close, 4 open, 5 up, 6 down, 13 search, 31 open locker, 33 look, 37 portal) and `cost` (115 terrains carry it; "a map tile selects the highest cost from all of its terrain") are **client/server** attributes; the editor ignores both.
- All 882 external terrains have exactly one `<sprite>`. 104 are `underpile="true"`; 101 are `resolution="2"`; 70 have offsets (common: `(0,9)`, `(2,1)`, `(-10,-10)`, `(0,-40)`, `(-40,0)`).

**Underpile**: `TerrainLayer.Underpile => _underpile || Order <= 3` (`Terrain.cs:73-80`) — anything at order ≤3 is implicitly under the treasure pile; the attribute can only force it for order >3. The **editor never reads `Underpile` when drawing** (grep confirms the only uses are the parser and the property). It is a client hint for drawing the item/treasure pile sprite between layers.

### 3.4 Visibility toggles and filters (editor only)

`RegionVisibility` (`Editor/RegionVisibility.cs`): `BreakWalls`, `OpenDoors`, `HideSecretDoors` change which id walls/doors render; `ShowTeleporters`, `ShowSpawns`, `ShowComments` add overlays (half-black veil, orange local / green cross-region teleporter boxes, cyan location-spawn boxes, magenta region-spawn boxes, red exclusions). `RegionFilters` offers selectors that hide other component types and recolor: Floor filter paints floors red when the tile has an indestructible wall; Static filter paints statics red when there is no floor/wall/obstruction/counter/altar under them ("walkable without floors"); Wall filter: indestructible+floor yellow, indestructible without floor red, destructible without floor green. These are useful validation rules for a generator (§6).

---

## 4. Templates and brushes

Both are `IComponentProvider`s that can sit in a tile's provider list by name, alongside inline components.

### 4.1 `SegmentTemplate` (`SegmentTemplate.cs`)

- Named, ordered list of providers (`Providers`), each of which may itself be an inline component, a named segment component, a brush, or another template (nesting capped at 8 levels in filters/comment lookups).
- `GetComponents()` yields its providers; `GetRenders()` concatenates their renders. A tile holding `<template name="X"/>` renders exactly as if X's children were inlined at that position.
- Editing a template changes every tile referencing it. `RegionGraphicsScreen.OnConvertTemplate` (line 459-520) turns a tile into a new template and replaces every tile in the segment with identical provider content by the reference — this is the intended "repeated tile" compression.
- A template is **one tile**, never a multi-tile stamp. Multi-tile prefabs are only possible via the clipboard (which serializes `<tile>` elements per cell, `ClipboardManager.cs:50-80`).

### 4.2 `SegmentBrush` (`SegmentBrush.cs`, `SegmentBrushEntry.cs`)

- Named list of `(weight, provider)` entries; `Chance = weight / TotalWeight`.
- **Deterministic weighted pick per coordinate**: `GetRenders(mx, my)` seeds `new Random(HashCode.Combine(mx, my, totalWeight, entries.Count, Name))` and rolls `Next(totalWeight)` against cumulative weights (line 139-160). Entries with null component or weight ≤0 are excluded. Note `HashCode.Combine` of a string is **randomized per process in .NET**, so the pattern changes between editor runs.
- `GetRenders()` (no coords) just renders the **first** entry.
- A brush placed on a tile stays a `<brush name=…/>` reference; it is never baked into concrete components by the editor. The region screen calls parameterless `GetRenders()` through `SegmentTile.GetRenderableTerrain`, so on the map a brush tile shows its first entry; only the brush preview window (`BrushGraphicsScreen`) shows the per-coordinate variation. There is no "bake" tool.

For procedural placement an external generator should therefore do its own weighted selection and emit concrete inline components (or named segment components), and reserve `<brush>` references for things meant to stay editable.

---

## 5. GenerateRegionWindow

`UI/Windows/GenerateRegionWindow.xaml(.cs)` is effectively a stub. It has one live tab, "MapGEN", visible only in debug builds (`Visibility="{x:Static worldForge:Core.DebugOnly}"`), whose Browse/Import handlers are wrapped in `#if (CanImport)` referencing a `MapGENImporter` class that **does not exist anywhere in the repo**; the symbol is never defined, so the handlers compile to nothing. An "Image" tab and a "Generator" tab exist only inside an XML comment. `ApplicationPresenter.GenerateRegions()` just shows the dialog. **There is no procedural generation in WorldForge.** `CreateRegion` makes an empty region with the next free ID.

---

## 6. Passability and collision semantics

The editor itself has no pathing logic; `PathingResult` in the editor is only used as the `fail` value of `ItemTeleporter`. The semantics come from the server classes (`Source/Kesmai.Server/Game/World/Maps/Components/`), summarised here because they define what a generated map *means*:

| Component | `PathingPriority` | `AllowMovementPath` | `HandleMovementPath` result | Movement cost (leaving) | Vision |
|---|---|---|---|---|---|
| Floor | — | (no IHandlePathing) | — | `movementCost` | — |
| Water | 0 | true | `Allowed` if flying / water-walking, else `Interrupted` | `min(depth, movementCost)`; 1 with water walking | — |
| Ice | 0 | true | `Allowed`, players `Interrupted` on failed Willpower roll | inherited | — |
| Ruins | 0 | true | `Interrupted` | 3 | — |
| Wall | 0 | destroyed only | `Daze` unless destroyed | — | blocks unless destroyed |
| Door | 0 | open, or not secret | closed: `Interrupted` (secret: `Daze`) | 3 closed / 1 open | blocks unless open |
| Obstruction | **1** | false | `Rejected` | — | blocks only if `blockVision` |
| Counter | 0 | false | `Daze` | — | — |
| Altar | 0 | false | `Daze` | — | — |
| Static / Tree / Trash / Lockers | — | — | — | — | — (walkable, transparent) |
| Teleporters | 0 | varies | — | 1 | — |

`PathingResult` meanings: `Allowed` move succeeds; `Rejected` move refused silently; `Interrupted` move refused / path stops with a message; `Daze` move refused and the entity is dazed (walked into a wall). Higher `PathingPriority` is consulted first, so an obstruction on a wall tile yields `Rejected` rather than `Daze`.

Rules a generator should respect (also what the editor's filters flag):
- Every walkable tile needs a floor-type component (`FloorComponent`/`WaterComponent`/`IceComponent`/`SkyComponent`); statics without one are flagged red.
- A wall tile normally has **no floor** (the Wall filter paints floored destructible walls as the default color and non-floored indestructible walls red — i.e. the editor expects indestructible walls to also carry a floor so the tile is valid once broken… read `WallSelector.TransformRender`: indestructible+floor = yellow, indestructible without floor = red, destructible without floor = green). Interpretation from the comment in `Wall.HandleMovementPath`: "if destroyed, there should exist a ground component to provide a pathing result and cost", so **destructible walls should have a floor under them**; indestructible walls need none.
- Only one floor-type per tile; only one wall per tile (DrawTool enforces on placement, not on load).
- Teleporter destinations must point at an existing tile in an existing region (drawn red otherwise).
- The sample uses `movementCost` 3 for water (1121 of 7128 floors carry an explicit cost).

---

## 7. Version string and migration

- Written: `version="{Core.Version}"` on `<segment>`, where `Core.Version = Assembly.GetExecutingAssembly().GetName().Version` (`Core.xaml.cs:94`), currently `0.117.0.0` (AssemblyVersion `0.117.0`). The sample `.mapproj` is `0.102.2.0`.
- Read: every `Load(XElement, Version)` receives `Core.Version`; the file's version is parsed in `ConvertSegment` (`Version.Parse`) and then unused. **No version-dependent branching exists.**
- Migration logic that does exist, all in `ConvertSegment` (§0.2): split `.mapproj` into files; 3-block → CDATA scripts; spawner `type` aliases `LocationSpawner`/`RegionSpawner` accepted on load.

---

## 8. Minimal valid region file (directory project)

`Regions/7.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<region>
  <id>7</id>
  <name>Temple Forge</name>
  <height>0</height>
  <tile x="0" y="0">
    <component type="WallComponent">
      <wall>27</wall>
      <destroyed>40</destroyed>
      <ruins>45</ruins>
      <indestructible>true</indestructible>
    </component>
  </tile>
  <tile x="1" y="0">
    <component type="FloorComponent">
      <ground>1</ground>
    </component>
    <component type="DoorComponent">
      <openId>77</openId>
      <closedId>65</closedId>
      <secretId>28</secretId>
      <destroyedId>83</destroyedId>
    </component>
  </tile>
  <tile x="1" y="1">
    <component type="FloorComponent">
      <ground>265</ground>
      <movementCost>2</movementCost>
    </component>
    <component type="StaticComponent">
      <static>624</static>
      <color r="180" g="200" b="180" a="255" />
    </component>
  </tile>
</region>
```

Plus `Segment.xml`:

```xml
<segment name="Eldrathor" version="0.117.0.0" />
```

and at least empty `<locations/>` (with the four reserved locations), `<subregions/>`, `<entities/>`, `<spawns/>`, `<treasures/>`, `<brushes/>`, `<components/>`, `<templates/>` files; the editor tolerates missing files (it only loads those that exist) but the server-side generator's csproj lists them as AdditionalFiles.

## 9. Rendering recipe for an external renderer (to match WorldForge at zoom 1)

```
for each tile (x,y) in the region, x ascending outer, y ascending inner:
    renders = []
    for provider in tile.children in order:
        for component in expand(provider):            # template → children, brush → first entry, named → definition
            for (terrainId, tint) in component.renders():   # per §2 (wall→wall id, floor→ground, door→closedId …)
                terrain = terrains[terrainId]
                for sprite in terrain.sprites:
                    renders.append((sprite.order, idx, sprite, tint))
    stable-sort renders by order
    for (_, _, sprite, tint) in renders:
        px = x*55 - 45 + sprite.offset.x
        py = y*55 - 45 + sprite.offset.y
        draw sprite.firstFrame scaled by 1/sprite.resolution at (px,py), multiplied by tint (default white)
```

Tint default (255,255,255,255); `Color` serialized as `<color r g b a/>` only when not white. Editor-only components (traps, hidden teleporters, item actions) draw a cyan/green marker from `WorldForge/Terrain/Teleporter` at order 9 and should be skipped by a game-faithful renderer.
