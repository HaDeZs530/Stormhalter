# DECOR_LEGEND — the component dictionary for map decoration

**Generated 2026-08-12 · Cowork (decoration setup) · at HANDOFF #019.**
Built from `Stormhalter Maps\reference\Components.xml` (the names WorldForge itself shows in the
palette), `Terrain-External.xml`, and a read-only census of the real region files in
`HaDeZs Test\Regions\` (0, 1, 2, 3, 5, 7 — no original was touched).

**Confidence marks:**
- **certain** — the name is WorldForge's own palette label, so identity isn't in question.
  Everything in the dictionary below is certain unless marked otherwise.
- **inferred** — a usage characterization read from how the decorated maps actually use the ID.
  Marked ⟨inferred⟩ where it appears.
- **UNKNOWN** — needs Tony's eyes. All of these are batched in one list below; nothing was
  guessed silently.

**How to read the usage column:** `L1:1441@0.97` means 1,441 placements in the L1 region,
and 97% of them touch another tile carrying the same ID. High adjacency = massed fill;
near zero = scattered singles. Blank = not yet used in any of Tony's regions (most of the
catalog — that's normal, it's a big palette).

Structural vocabulary (walls, doors, stairs, ropes, teleports, traps) is deliberately not
here — that's the `eldrathor-maps` skill and `Components.xml` itself. This file is the
decoration palette.

---

## The recipes — how the finished areas are actually decorated (observed fact)

**Base coats.** Every area is a two-or-three floor mix, not a single fill:
L1 harbor: Short Grass 13 (3,271) + Light 1 (2,431) with Water 22 + Shoreline (Shallow) 601
for the coast, Beaten Path 16 as trails, Worn Cobblestone 184 in town. L2 ruins: Light 1 +
Short Grass 13 south, Dirt 12 + Cobblestone [Fireal] 607 in the ruin, Sand [Zrikz] 603 at the
waterline. Spire floors: Light 1 + Short Grass 13 islands over SkyComponent void, Worn
Cobblestone 184 paths, Rope Bridge (H) 239 spans. Temple Forge: Worn Marble 176 + Gray Tile
178 + Dirt 12.

**The forest recipe (L1/L2)** ⟨inferred from the census⟩:
- **Large Tree 98** is the canopy mass — 1,441 in L1 at 0.97 adjacency, sitting on Short Grass.
- **Heavy Oak 266** (Obstruction) is the impassable core — 876 at 0.98 adjacency, mostly on
  Light 1. The forest reads: grass → tree carpet → oak wall where players shouldn't go.
- **Accents scatter, never mass:** Cherry Tree (Blossoms) 906 (77 @ 0.1), Wierd Tree 370
  (35 @ 0.06), **Burnt Wierd Tree 372 (59 @ 0.0)** — and 372 is doing corruption-accent work
  in the harbor forest already. Swamp Cypress 1112 and flowers (206/207) same pattern.

**The water edge recipe** ⟨inferred⟩: Shoreline (Shallow) 601 ribbon → Reef 19 / Reef [Zrikz]
605 massed at 1.0 adjacency as the swim-stopper → cattail cluster 1106, lilly pads 1100/1105,
swamp assorted 1101 scattered on the shoreline tiles. Reefs are the water's Heavy Oak.

**The Spire recipe** ⟨inferred⟩: Jungle Foliage 94/95 as the greenery workhorses (700+ each,
~0.85 adjacency — small massed patches), Medium/Small Tree 99/100 and Pines 200/201 in
clumps on Short Grass, Mossy Pillar 1001 as scattered singles, ruins pieces sparse.

**Interiors (L2 guildhall etc.):** singles with intent — bookshelves 243/244/764/765, chairs
1198–1200, red rug 741 (massed 6 @ 1.0 as one rug), Red Carpet 317, braziers 1037/1031/1032,
Wood (H) counters 86, Granite Altar (2) 163, Oak Throne 251, Vases 656/657, crates 880/881/886/889/890/891.

**What the decorated maps do NOT do:** no `<color>` tints anywhere (corruption is told with
sprite choice and floor choice, not tinting — so far), and no decoration ever replaces the
floor under it.

---

## Resolved 2026-08-12 — the contact-sheet pass

The unknowns went through a five-region test-map pass (segment `Claude Worldforge Testing`,
coordinate key in `CLAUDE_TEST_KEY.md` there). Tony screenshotted, Claude matched every tile
against the key. Results, now **certain**:

1. **Jungle Foliage 92/93/94/95** — same foliage art at four different tile positions/densities.
   Position variants for massing; mix them for full coverage (that's how the Spire uses 94/95).
2. **(Lava) floor 10** — damaging to players who walk it, but decorative by intent (Tony).
   Bright orange. Palettes may use it, consciously.
3. **(PH) floor 11 renders as a RED, molten-looking floor — it is NOT wood.** Tony's wood
   sketch-floor is **Wood (H) 14 / Wood (V) 15** (confirmed by screenshot). Floor 12 is Dirt,
   as the 446 rule always said. **(PH) 406** is an orange-tan mottled floor (fallen-leaves look).
4. **Grove statics 226/227** — 226 a low green shrub/bush cluster, 227 a taller thin
   sapling-like plant. No official name; Tony didn't know them by number either.
5. **Same-label pairs are mostly fill-vs-edge coverage shapes, not duplicates:** Tall Grass
   105 = full cube / 107 = corner slope; Tall Reeds 106/108 and Tall Bamboo 109/110 same
   pattern. Sand [Zrikz] 602 renders dark green (⟨inferred⟩ possibly seagrass-like shallow),
   603 is the true pale sand. Sandstone Cobblestones 277 (olive knobbly) and 393 (orange
   basket-weave) are completely different art. Pagoda Framed Ruins 476/477 are plain brown,
   484/485 white-framed. **Heavy Snow 121 is engine-animated snow — invisible in WorldForge,
   real in game (like the portal block). Don't "fix" it.** 122 is the static white patch.
6. Tilt-filler: per Tony, stacked tiles simply render what's beneath; his files contain no
   blank-blocker walls. Working reading: **every wall hex carries a real wall sprite.**

---

## Visual notes from the contact-sheet pass (2026-08-12, certain)

- **Lighting is a two-mode system:** standard torches/braziers/candelabras include a built-in
  darkness "shade" (light + surrounding gloom in one sprite); the `without shade` line
  (1025–1037) is bare flame for lit rooms. Green fire and blue fire variants exist in both.
- **Counters (Wood/Slate/Gilded/Table) all render as near-identical bright red blocks** —
  classic Kesmai counter red. Pick by name, expect red. Stone/Alchemy tables differ more.
- **Every wall material has a matching H/V/C ruins family** (town, temple, dungeon, sandstone,
  dirt, dirty marble, dragon + dragon blue, high mountain, shoji, pagoda, blue marble,
  Egyptian) plus rubble piles (sandstone/blue marble/Egyptian/pagoda/thicket/ice/lava). Ruined
  versions of whatever stands = the backbone of ruin decoration.
- **Stair dressing kit:** Up/Down × N/S/E/W in rug, snow/ice, bloodied, mossy, grassy, floral
  (817–930). Stairs can belong to their environment.
- **Grave (1) 216 is a fresh brown mound; Grave (2) 217 a mossy old one** — age in two sprites.
  Full cemetery line: headstones + sarcophagi (sleeping-woman/blank/rejuvinated, V+H) 1248–1257.
- **The dungeon-dreary statuary comes in three coordinated color families** — purple/blue/green
  kings, dragons, columns (region 2) and cultist/maiden statues (region 4). Room theming by
  accent color with shared geometry.
- **Tent kit 726–757:** back-boards, ropes, flaps, shade-screens + rugs — modular tents
  (the natural Spire Watch camp vocabulary).
- **Corruption kit already in the palette, before any tinting:** burnt wheat/corn/grapevines,
  Burnt Tree L/M/S, Burnt Wierd Tree (blue-purple cast, as is the live Wierd Tree), Burnt
  Fruit Tree, Dead Shrubs, Dead Tree 1005 (thin red coral-like branches — confirmed), dead
  Swamp Cypress, plus Congealed Lava 137 as an accent distinct from damaging floor 10.
- **Reef 19/605 render as self-contained water tiles with rocks** — they bring their own look.
- **Heavy Oak 266 is a solid leaf-block** — why massing it works as the forest core.
- **Fog 193 is a large soft white cloud** — a mood overlay, not an object.
- **Magic circles 1188–1190** — full-tile ornate glyphs (gold pentagram, blue star, blue triangle).
- Small accents (vases 649–657, wizard emblems, daggers/maces, swamp flowers, mushroom
  clusters) read at a few pixels; they're meant to be **layered** — 2–3 statics stacked on one
  tile is normal practice (Tony).
- **Some catalog sprites are "useless" in Tony's view** — invisible, unappealing, or one-off
  legacy art. He uses a small handful. A Tony-taste dimension will accumulate on this file as
  palettes get judged. Some tiles carry special effects (lighting, movement) beyond their
  sprite — noted per-ID as discovered.

- **Floors/water pass (region 6):** jungle floor trio (Jungle / Moss / Foliage) is a density
  ramp; swamp floor trio (cave/mossy/rock); coastline kit = Water + Shoreline (solid blue) +
  directional Waves 622/623/1018/1019 (white breakers); Reef 605 also exists as a floor.
  [Fireal] customs are a distinct visual language (Labyrinth, Ornate, Egypt pair, Glass Lava);
  nidavellir dark/light and the icy rock/snow/glacier line cover cold zones; two skull-floor
  art styles. Names can mislead: Tile = magenta checkerboard, Fine Marble = yellow lattice —
  choose floors from these notes, not the label.
- **Wall doodads (region 7):** modular banner system (pole + trims + low/high contrast +
  Yasnaki / Mu / Kesmai-dragon symbols), shield ornament kit, dragon head mounts, arch toppers
  (dragon/bull/lion), stained glass (dragon/priest/court), murals, vampire portraits, and bat
  ornaments + wall carvings in the same purple/blue/green families as the statuary.
- **Walls (region 8):** every family verified in H/V(/C) — town, temple, dirty marble, heavy
  logs, dragon, cave, dungeon, granite, Egyptian carved set, shimmer, ice glass, ice labyrinth,
  lava tube, log fortification, swamp (plain/vine/pillars), sewer gratings, fireplaces,
  purple dungeon-dreary panels, red brick, nidavellir starry-dark.

**⚠ Format fact (verified the hard way, 2026-08-12): a `WallComponent` written without
`destroyed` and `ruins` children CRASHES WorldForge on load.** Always emit the full child set
from `Components.xml`. Also: `PoisonedWaterComponent` exists as its own type (ground 180).

**Coverage: as of 2026-08-12 the ENTIRE decoration-relevant catalog has been verified visually**
via the contact-sheet segment (`Claude Worldforge Testing`, regions 1–8, keys in
`CLAUDE_TEST_KEY.md` there). Not yet sheeted: doors, stairs, ropes, teleports, traps, sky, and
the 29 tintable "Customizable" entries (color-value format unknown — learn it from a real
tinted tile, don't guess).

---

## THE CORRUPTION PALETTE — Tony's reference strip (certain, logged 2026-08-13)

**Tony built a physical swatch strip into Harbor Town at (-152,-55) → (-148,-45).** Three columns,
one per floor tint, with the corruption objects laid over each so the pairings can be seen in the
editor. **This is the reference — read it out of the map rather than guessing tints.**

### The floors — three tones, and only three

| | Colour | Ground |
|---|---|---|
| Column x=-152 | `rgba(0, 191, 255, 255)` | 1 (Light) |
| Column x=-150 | `rgba(0, 160, 255, 255)` | 1 (Light) |
| Column x=-148 | `rgba(0, 112, 255, 255)` | 1 (Light) |

**Scattered, not banded** — the three tones mottle across the corrupted ground. Any other green
value on a tinted Light floor in this pattern is an error — **except 212, which is Tony's
work-marker (see the rule above).**

### The mottle recipe — measured from Harbor Town, applied to Town Ruins 2026-08-13

| Tone | Share | Isolated (no same-tone neighbour) | With 2+ same neighbours |
|---|---|---|---|
| `0,191,255` light | ~37% | 4–6% | ~75–82% |
| `0,160,255` mid | ~47% | 3% | ~87% |
| `0,112,255` dark | ~16% | **33–42%** | **16–21%** |

**The dark tone is deliberately lonely** — that's the "don't clump the darks" rule in numbers.
Generate by weighted random, then repair: any 112 with more than 2 same-tone neighbours flips to
160 or 212… (i.e. to mid or light), and the dark count is topped back up on isolated tiles only.
**Region 1 result: 191 × 863 (36%) · 160 × 1,136 (48%) · 112 × 382 (16%), darks 33% isolated,
16% with 2+.** Matches Harbor Town within a couple of points.

**⚠ Find the outliers before you generate, and ASK — don't decide for him.** Region 1's pass held
back 11 tiles for review: Tony's **L2 reference swatch strip** at x=-108/-106, y=-90..-76 (a light
column beside a 160 column, spaced two apart, Heavy Oak over one, a 112 sample) and **four brazier
tiles** inside a building at (-24,-160), (-24,-159), (-22,-160), (-22,-159). **He ruled both to
191**, same as the ground. So the outcome was "everything is 191" — but the value was in *asking*
rather than silently mottling a reference strip into noise. **Run a connected-components check
before every pass and inspect anything small or regularly spaced.**

**Region 1 final: 191 × 863 · 160 × 1,136 · 112 × 382**, plus the one marker swatch below.

### 📋 THE TEMPLATE STRIP — the canonical layout, both regions identical

**Rebuilt 2026-08-13 so region 0 and region 1 match exactly.** Columns spaced two apart (walls and
tall sprites lean up-left), rows spaced two apart, running **south**.

| Row | What | Region 0 (harbor) | Region 1 (town ruins) |
|---|---|---|---|
| 1 | **Heavy Oak 266** | y = -55 | y = -86 |
| 2 | **forest large 98** | -53 | -84 |
| 3 | **forest small 99** | -51 | -82 |
| 4 | **light tree 906** | -49 | -80 |
| 5 | **bare** — the plain tone | -47 | -78 |
| 6 | **stalagmite, wall 371** | -45 | -76 |
| 7 | **swamp leafy 370** | -43 | -74 |
| 8 | **swamp bare 372** | -41 | -72 |

Tone columns: **x = -152 / -150 / -148** (harbor) and **-108 / -106 / -104** (town ruins), carrying
`0,191,255` · `0,160,255` · `0,112,255`. **The 212 work-marker sits one column further out** —
(-146,-55) and (-102,-86) — so a selection across all four columns copies tones, objects and marker
as one block.

**Stalagmite — `WallComponent` wall 371, destroyed 641, ruins 170, indestructible true.** Catalog
name "Stalagmite". Cave decoration, and **the first tint in the palette whose red channel isn't
zero: `rgba(255,190,255,255)`** — confirmed by Tony 2026-08-13. Note the difference from the ground
tones, which are all `r=0`; **don't assume r=0 for an object tint.** The one pre-existing stalagmite at
(-141,-44) in region 0 was untinted and **Tony ruled it should match — it now carries the same
tint.** Every stalagmite in the zone is `255,190,255`.

> ### 🔴 EXCLUDE THE TEMPLATE STRIPS FROM EVERY PASS
>
> The 2026-08-13 tree pass planted four trees onto region 1's strip because the exclusion list
> was rebuilt for that pass and the strip wasn't in it. **The mottle pass had excluded it; the tree
> pass forgot.** They were removed when the template was rebuilt.
>
> **Every decoration pass must exclude the template rows before it generates** — they are
> reference, not ground. Build the exclusion set once and reuse it.

### The old copy-paste note

**Region 1, x = -108 / -106 / -104 / -102, rows y = -86, -84, -82, -80, -78, -76** (columns spaced
two apart, since walls and tall sprites lean up-left).

| Column | Tint | Role |
|---|---|---|
| x = -108 | `0,191,255` | light corruption tone |
| x = -106 | `0,160,255` | mid tone |
| x = -104 | `0,112,255` | dark tone |
| **x = -102** | **`0,212,255`** | **the WORK MARKER** — added 2026-08-13 at (-102,-86) so the
  whole template, tones plus marker, copies as one block |

Row y = -86 also carries Heavy Oak 266 over each of the three tones, so the object-over-ground
pairing is visible in the same strip. **Region 0 has the same strip at (-152,-55) → (-148,-45).**

**Workflow it supports:** paste the strip anywhere, paint an area with the 212 marker, and a
decoration session takes those tiles as its input set and mottles them 191/160/112.

> ### 🔴 CORRUPTION REPLACES THE FLOOR. IT DOES NOT TINT IT. — Tony, 2026-08-13
>
> **A corrupted tile is `ground 1` (Light) carrying one of the three tones.** Whatever the tile was
> before — Short Grass 13, anything else eligible — **the ground value is CHANGED to 1** and the
> tint goes on. Tony's words: *"it should be a copy paste of the whole tile, not a recolor."*
>
> **Tinting a grass tile just gives you dark grass.** That's the failure — it looks muddy and wrong
> beside proper corruption, and it's exactly what happened on Serpent's Spire before this was
> caught.
>
> **Why it hid for so long:** every corrupted tile in Harbor Town and Town Ruins was *already*
> ground 1, so a tint-only pass produced the right result by luck. **The Spire is the first map
> where corruption crosses onto grass.** Any future zone with mixed eligible ground will hit this.
>
> So a corruption pass does two things per tile, not one: **set `<ground>` to 1** and **insert the
> `<color>`**.
>
> ### ⚠ CORRUPTED GROUND LOSES ITS LIVING UNDERGROWTH
>
> **Jungle Foliage 94 and 95 come OFF a tile when it corrupts** — ruled for SS1, 2026-08-13
> (175 tiles cleaned there). Everything else on the tile stays; it's those two specifically.
> Foliage outside the corruption is untouched. **SS2 was deliberately left as-is**, so this is
> SS1's rule until Tony extends it — ask before applying it to a new map.

> ### ⚠ TONY NAMES THE REPLACEABLE FLOORS. NEVER INFER THEM.
>
> **Which floor types a pass is allowed to replace is Tony's input, given per pass** — because some
> floors are ones he wants kept exactly as they are. His words, 2026-08-13: *"if an area is
> affected, I will give you the 'replace' floor tiles so we don't change a floor I want to keep,
> and replace them with the floor tile 1 with the color change."*
>
> For Serpent's Spire 1 and 2 he named **ground 1 and ground 13**; everything else stayed untouched.
> **Don't widen that list by reasoning about what looks corruptible.** If he hasn't named the
> floors for an area, ask — it's one question and it protects the floors he's chosen deliberately.

> ### 🔴 GREEN 212 IS A WORK MARKER, NOT A TONE — Tony's rule, 2026-08-13
>
> **`rgba(0,212,255,255)` means "this area needs work."** Tony paints ground 212 to flag a region
> for a decoration pass. **It is never a finished colour.**
>
> **THE CORRUPTION MOTTLE IS ALWAYS 191 · 160 · 112.** Every level, no exceptions. If you find 212
> on a floor, it is either an area waiting for a pass or a leftover — **it is not the look.**
>
> Practical consequence: **a mottle pass takes the 212 tiles as its input set** and writes
> 191/160/112 over them. When the pass is done, no 212 should remain in the worked area. Tiles
> Tony wants held back (reference strips, architecture) are the exception and get named explicitly.

> ### ⚠ 191 IS THE TONE, NOT 212 — read this before "fixing" anything
>
> This went both ways on 2026-08-13 and the second call is the live one. **Tony's first read was
> that 212 was correct and 191 was build drift**, so 680 tiles were converted 191→212. Seeing it in
> the editor he reversed it — *"it looks too off now. I know why it was left at 191"* — and the
> whole region went to **191**, including the reference strip, which had been the last 212 holdout.
>
> **Region 0 is now uniform: 191 · 160 · 112, 790 / 983 / 334 tiles.** Two strays were folded in on
> the way: (-104,-54) 143→160 and (-110,-49) 179→191.
>
> **Do not re-propose 212 for Harbor Town.** If a future file or note says 212 is the corruption
> tone there, it predates this and is stale. ⚠ **Town Ruins (region 1) is a separate question** —
> it carries **2,367 floor tiles at 212** and nobody has looked at whether it should follow. Ask
> Tony; don't convert it on the strength of this.

### What sits on them, as built in the strip

| Row | Component | Tint at x=-152 (191) | at x=-150 (160) | at x=-148 (112) |
|---|---|---|---|---|
| y=-55 | Obstruction **266** Heavy Oak | `175,131,255` | `175,131,255` | `174,130,255` |
| y=-53 | Tree **98** Large Tree | `0,154,255` | `0,151,255` | `0,153,255` |
| y=-51 | Tree **99** Medium Tree | `0,154,255` | `0,153,255` | `0,153,255` |
| y=-49 | Tree **906** Cherry (Blossoms) | `0,134,214` | `0,133,215` | `0,134,217` |
| y=-47, -45 | bare floor | — | — | — |

Visually: Heavy Oak reads as the **dark grey-violet canopy mass**, Large/Medium Tree as **green
crowns**, and the tinted Cherry as the **pale blue blossom tree** — the three-object vocabulary of
the corrupted forest, over the three-tone floor.

### ⚠ The object tints vary slightly and it is NOT a system

The strip itself carries the variance: Heavy Oak is `175,131` twice and `174,130` once; Large Tree
is 154 / 151 / 153 across three columns; the Cherry is 134,214 / 133,215 / 134,217. **The variation
does not track the floor tint** — Tree 98 and Tree 99 disagree in the same column. Across the whole
region the same spread appears (Heavy Oak 541× at `175,131` and 54× at `174,130`; Tree 98 63/34/18
across greens 151/153/154; Tree 906 four values).

**Reading: the object tints are hand-picked per placement with a few values of slop, and the floors
are the part that's exact.** So don't "normalize" object tints as though they were drift — and when
a palette places these objects, **the dominant values are the safe default**: Heavy Oak
`175,131,255`, Large Tree `0,151,255`, Cherry `0,134,217`. (Whether Tony wants them collapsed to one
value each is **his call and unasked** — flagged, not fixed.)

### The tint format — answers T38

```xml
<component type="FloorComponent">
  <color r="0" g="212" b="255" a="255" />
  <ground>1</ground>
</component>
```

> ### ⚠ DON'T ASSUME `r=0`. GROUND TONES AND OBJECT TINTS ARE DIFFERENT FAMILIES.
>
> **Every floor tint in this zone is `r=0`** — the corruption tones `0,191,255` · `0,160,255` ·
> `0,112,255`, the harbor water, all of it. It is very easy to read that as "the convention" and
> carry it onto an object.
>
> **It is not the convention.** The stalagmite is `rgba(255,190,255,255)` — **red at full.** Heavy
> Oak is `175,131,255`. The Swamp Cypress is `0,168,255`. Object tints go wherever the object needs
> to go.
>
> **Read the tint off the object, or ask. Never derive it from the floor palette.** This was got
> wrong on 2026-08-13 — a stalagmite was filed as `0,190,255` because every neighbouring value
> started with a zero.

`<color>` is an **empty element with r/g/b/a attributes, written FIRST in the component** — before
`ground`/`tree`/`obstruction`. Verified across thousands of live tiles in region 0. Alpha is
normally 255; one tile in the map uses 136, so partial alpha does load. **The "Customizable"
components were never blocked by anything but not knowing this.**

---

## THE TREE VOCABULARY — Tony's names, and the corruption planting recipe

**Use these names when talking to Tony.** They're his, set 2026-08-13.

| His name | IDs | Component | Tint on corrupted ground |
|---|---|---|---|
| **Forest trees** | **98** (large) · **99** (small) | `TreeComponent`, `canGrow` true | 98 → `0,151,255` · 99 → `0,153,255` |
| **Light trees** — the highlight accent | **906** (Cherry, blossoms) | `TreeComponent`, `canGrow` **false** | `0,134,217` |
| **Swamp trees** — highlight, used in quantity | **370** (leafy) · **372** (bare) | 370 `TreeComponent` · **372 is a `StaticComponent`** | **none — left untinted**, they're already blue-purple |

Both reference strips carry them: harbor **(-152,-53)** large · **(-152,-51)** small · **(-152,-49)**
light, and the swamp pair alone at **(-148,-61)** bare and **(-148,-59)** leafy.

### The planting recipe — L2 Town Ruins, applied 2026-08-13

**Coverage is set per zone, by Tony:**

| Zone | Coverage | Character |
|---|---|---|
| **Town** (outside the caves) | **60%** | forest-led — large clumps, small trees feathering the edges |
| **Cave system** | **30%** | swamp-led and airier — more open space |

**Mix as built** — town: 98 50% · 99 24% · 906 12% · swamp 14%. Cave: swamp **61%** · 98 16% ·
906 16% · 99 8%.

**The structural rules, and they matter more than the percentages:**

- **Large trees grow in clumps** (99% of them touch another large tree; harbor town runs 67%).
- **Small trees ring the clumps** — placed on the outskirts of a 98 mass, never as their own field.
- **Light trees scatter** and avoid touching each other.
- **Swamp trees scatter as singles**, at most one same-type neighbour.
- **Seed a third of the clumps beside trees already standing on the grass** so the corrupted mass
  flows into the healthy forest instead of stopping at a line.
- **Spread the remaining seeds with a minimum spacing** (5 tiles town, 6 cave) — otherwise every
  clump anchors to the existing forest and one half of the map ends up bare. That happened on the
  first attempt and had to be regenerated. Per-block coverage should land around the target with
  real variation (town came out 12–100% around a 61% median), not uniform.

**Exclusions — ask, don't infer.** The **temple interior (-94,-150) → (-77,-134)** gets no trees;
Tony gave that rect. Building interiors are the same rule, but **only 31 tinted tiles in region 1
are actually sealed by walls** — the structures are open-walled ruins, so enclosure detection can't
find them. **Get the rect from Tony rather than guessing.**

**Result:** 1,012 trees — 98 +395, 99 +190, 906 +133, 370 +158, 372 +136. Census delta showed those
five components and nothing else; every floor tint identical before and after.

---

## Dictionary

### Floors  (103 entries)

| ID | Type | Name | Observed usage | Notes |
|---|---|---|---|---|
| 1 | Floor | Light | L1:2431@0.99 · L2:2440@0.99 · L3:1837@1.0 · L4:689@1.0 · L5:269@0.99 · L6:138@0.99 |  |
| 2 | Floor | Tile | L1:214@0.02 · L2:96@0.03 · L3:206@0.0 · L4:1@0.0 · L6:189@0.03 |  |
| 3 | Floor | Hardwood (H) | L1:169@1.0 · L2:96@1.0 · L3:15@1.0 |  |
| 4 | Floor | Hardwood (V) | L1:136@1.0 · L2:29@1.0 · L3:52@1.0 |  |
| 5 | Floor | Temple | L4:1@0.0 |  |
| 6 | Floor | Burnt Stone | L3:2@0.0 · L4:1@0.0 · L6:13@1.0 |  |
| 10 | Floor | (Lava) | L6:116@0.94 |  |
| 11 | Floor | (PH) |  |  |
| 12 | Floor | Dirt | L1:7@1.0 · L2:634@1.0 · L3:650@1.0 · L4:507@0.99 · L5:164@1.0 · L6:846@1.0 |  |
| 13 | Floor | Short Grass | L1:3271@1.0 · L2:919@1.0 · L3:400@1.0 · L4:779@1.0 · L5:136@1.0 |  |
| 14 | Floor | Wood (H) | L1:57@0.98 · L2:94@0.98 · L3:62@1.0 |  |
| 15 | Floor | Wood (V) |  |  |
| 16 | Floor | Beaten Path | L1:122@0.93 |  |
| 17 | Ice | Snow |  |  |
| 18 | Floor | Sand |  | cost 2 |
| 20 | Ice | Ice |  |  |
| 21 | Floor | Bog |  |  |
| 23 | Floor | Forest |  |  |
| 24 | Floor | Honeycomb Flagstone |  |  |
| 89 | Floor | Jungle |  |  |
| 90 | Floor | Jungle (Moss) |  |  |
| 91 | Floor | Jungle (Foliage) |  |  |
| 115 | Floor | Bridge (H) | L1:5@0.6 · L2:7@1.0 |  |
| 116 | Floor | Bridge (V) | L1:4@0.5 |  |
| 175 | Floor | Giant Logs |  |  |
| 176 | Floor | Worn Marble | L1:30@1.0 · L3:4@0.0 · L4:11@0.64 · L5:467@1.0 · L6:1974@1.0 |  |
| 178 | Floor | Gray Tile | L1:72@1.0 · L5:1@0.0 · L6:697@0.98 |  |
| 179 | Floor | Dusty Cave | L2:7@0.29 |  |
| 182 | Floor | Slate Flagstone |  |  |
| 183 | Floor | Mossy Granite |  |  |
| 184 | Floor | Worn Cobblestone | L1:276@0.97 · L2:224@0.96 · L3:252@0.98 · L4:239@1.0 |  |
| 185 | Floor | Tidal Mud |  |  |
| 186 | Floor | Fine Marble |  |  |
| 196 | Floor | Oriental Rug |  |  |
| 239 | Floor | Rope Bridge (H) | L3:49@1.0 · L4:35@1.0 |  |
| 252 | Floor | Stone Bridge (H) |  |  |
| 264 | Floor | Gravel Road |  |  |
| 265 | Floor | Sandstone Slabs |  |  |
| 277 | Floor | Sandstone Cobblestones |  |  |
| 289 | Floor | Green Alfalfa |  |  |
| 301 | Floor | Rosey Viens Granite |  |  |
| 325 | Floor | Yellow Brick Road |  |  |
| 341 | Floor | Jade Bricks |  |  |
| 369 | Floor | Mossy Cave Floor |  |  |
| 375 | Floor | Torn Cobblestones | L4:6@0.83 |  |
| 387 | Floor | Skulls |  |  |
| 388 | Floor | Blue Marble |  |  |
| 393 | Floor | Sandstone Cobblestones |  |  |
| 406 | Floor | (PH) |  |  |
| 419 | Floor | Ash |  |  |
| 445 | Floor | Blue Brick Road |  |  |
| 492 | Floor | Dark Wood |  |  |
| 493 | Floor | Bamboo |  |  |
| 602 | Floor | Sand [Zrikz] |  | cost 2 |
| 603 | Floor | Sand [Zrikz] | L2:77@1.0 | cost 2 |
| 604 | Floor | Sandflats [Zrikz] |  | cost 2 |
| 605 | Floor | Reef [Zrikz] |  | cost 2 |
| 606 | Floor | Aqua [Fireal] |  |  |
| 607 | Floor | Cobblestone [Fireal] | L1:10@0.9 · L2:152@1.0 · L5:6@0.0 · L6:14@1.0 |  |
| 608 | Floor | Cut Wood [Fireal] | L3:4@1.0 · L4:9@0.78 · L5:16@1.0 |  |
| 609 | Floor | Druid Cove [Fireal] |  |  |
| 610 | Floor | Egypt (1) [Fireal] |  |  |
| 611 | Floor | Egypt (2) [Fireal] |  |  |
| 612 | Floor | Fantasy Flower [Fireal] |  |  |
| 613 | Floor | Glass Lava [Fireal] |  |  |
| 614 | Floor | Grass [Fireal] |  |  |
| 615 | Floor | Ice [Fireal] |  |  |
| 616 | Floor | Labyrinth [Fireal] |  |  |
| 617 | Floor | Ornate [Fireal] |  |  |
| 618 | Floor | Paving Slabs [Fireal] |  |  |
| 619 | Floor | Skulls [Fireal] |  |  |
| 620 | Floor | Cobble Puzzle [Fireal] | L2:17@0.35 |  |
| 621 | Floor | Cobbles [Fireal] |  |  |
| 628 | Floor | Sewer Drain [Tenser] |  |  |
| 629 | Floor | Sewer Floor [Tenser] |  |  |
| 671 | Floor | light stone floor |  |  |
| 680 | Floor | rock floor |  |  |
| 689 | Floor | cave floor |  |  |
| 700 | Floor | dark wood floor |  |  |
| 945 | Floor | light wood floor |  |  |
| 992 | Ice | Ice Labyrinth Floor |  |  |
| 1003 | Floor | Bedrock [Lux] | L3:1@0.0 · L4:1@0.0 |  |
| 1004 | Floor | Roots [Lux] |  |  |
| 1009 | Floor | Lava Tube Floor |  |  |
| 1027 | Floor | Flat Stone Bridge (H) | L3:1@0.0 |  |
| 1028 | Floor | Flat Stone Bridge (V) | L3:13@1.0 · L4:8@1.0 |  |
| 1091 | Floor | Swamp cave floor |  |  |
| 1098 | Floor | Swamp mossy floor |  |  |
| 1099 | Floor | Swamp rock floor |  |  |
| 1214 | Floor | mine floor |  |  |
| 1226 | Floor | new dungeon floor |  |  |
| 1237 | Floor | rustic wood floor |  |  |
| 1259 | Floor | purple floor texture |  |  |
| 1283 | Floor | desat-blue floor texture |  |  |
| 1307 | Floor | dbl desat-green floor texture |  |  |
| 1341 | Floor | red brick floor |  |  |
| 1349 | Ice | Icy cave Floor |  |  |
| 1357 | Ice | glacier Floor |  |  |
| 1365 | Floor | nidavellir dark floor |  |  |
| 1372 | Floor | nidavellir light floor |  |  |
| 1409 | Floor | icy rock floor |  |  |
| 1410 | Floor | icy snow floor |  |  |
| 1411 | Floor | snow floor |  |  |

### Water  (12 entries)

| ID | Type | Name | Observed usage | Notes |
|---|---|---|---|---|
| 22 | Water | Water | L1:2112@1.0 · L2:984@1.0 · L6:28@1.0 | cost 3, depth 3 |
| 177 | Water | Fresh Water | L6:69@0.99 | cost 3, depth 3 |
| 180 | PoisonedWater | Poisoned Water |  | cost 3 |
| 180 | Water | Dark and Cloudy Water |  | cost 3, depth 3 |
| 374 | Water | Dark Red Liquid |  | cost 3, depth 3 |
| 601 | Water | Shoreline (Shallow) [Zrikz] | L1:367@1.0 · L2:237@1.0 | cost 3, depth 3 |
| 601 | Water | Shoreline [Zrikz] | L1:367@1.0 · L2:237@1.0 | cost 3, depth 3 |
| 602 | Water | Sewer [Zrikz] |  | cost 3, depth 3 |
| 622 | Water | Waves (H) [Tenser] |  | cost 3, depth 3 |
| 623 | Water | Waves (V) [Tenser] |  | cost 3, depth 3 |
| 1018 | Water | Waves (E) [Tenser] |  | cost 3, depth 3 |
| 1019 | Water | Waves (S) [Tenser] |  | cost 3, depth 3 |

### Vegetation  (80 entries)

| ID | Type | Name | Observed usage | Notes |
|---|---|---|---|---|
| 92 | Static | Jungle Foliage | L3:1@0.0 · L5:10@0.4 |  |
| 93 | Static | Jungle Foliage | L3:11@0.0 · L4:8@0.0 · L5:3@0.67 |  |
| 94 | Static | Jungle Foliage | L2:51@0.73 · L3:408@0.84 · L4:356@0.88 · L5:61@0.56 |  |
| 95 | Static | Jungle Foliage | L3:315@0.79 · L4:262@0.89 · L5:39@0.46 |  |
| 98 | Tree | Large Tree | L1:1441@0.97 · L2:306@0.98 · L3:3@0.0 |  |
| 99 | Tree | Medium Tree | L1:6@0.33 · L3:22@0.55 · L4:169@0.65 · L5:27@0.81 |  |
| 100 | Tree | Small Tree | L3:17@0.53 · L4:55@0.24 · L5:14@0.57 |  |
| 101 | Static | Burnt Tree (L) |  |  |
| 102 | Static | Burnt Tree (M) |  |  |
| 103 | Static | Burnt Tree (S) |  |  |
| 105 | Static | Tall Grass |  |  |
| 106 | Static | Tall Reeds |  |  |
| 107 | Static | Tall Grass |  |  |
| 108 | Static | Tall Reeds |  |  |
| 109 | Static | Tall Bamboo |  |  |
| 110 | Static | Tall Bamboo |  |  |
| 121 | Static | Heavy Snow |  |  |
| 122 | Static | Heavy Snow |  |  |
| 199 | Tree | Large Pine Tree |  |  |
| 200 | Tree | Medium Pine Tree | L3:55@0.65 · L4:45@0.11 · L5:7@0.0 |  |
| 201 | Tree | Small Pine Tree | L3:52@0.71 |  |
| 202 | Tree | Large Pine Tree (Snow) |  |  |
| 203 | Tree | Medium Pine Tree (Snow) |  |  |
| 204 | Tree | Small Pine Tree (Snow) |  |  |
| 205 | Static | Creosote Bush |  |  |
| 206 | Static | Red Flowers | L1:11@0.18 |  |
| 207 | Static | Yellow Flowers | L1:11@0.18 |  |
| 208 | Static | Large Oak Trunk |  |  |
| 247 | Tree | Small Jungle Tree | L1:1@0.0 · L2:1@0.0 |  |
| 326 | Static | Fig Tree |  |  |
| 370 | Tree | Wierd Tree | L1:35@0.06 · L2:1@0.0 |  |
| 372 | Static | Burnt Wierd Tree | L1:59@0.0 · L2:1@0.0 |  |
| 403 | Tree | Bamboo |  |  |
| 624 | Tree | Palm Tree [Tenser] |  |  |
| 625 | Tree | Large Palm Tree (1) [Tenser] |  |  |
| 626 | Tree | Large Palm Tree (2) [Tenser] |  |  |
| 627 | Tree | Banana Tree [Tenser] |  |  |
| 873 | Static | Corn |  |  |
| 874 | Static | Burnt Corn |  |  |
| 875 | Static | Wheat |  |  |
| 876 | Static | Burnt Wheat |  |  |
| 877 | Static | Grapevines |  |  |
| 878 | Static | Burnt Grapevines |  |  |
| 893 | Tree | Pear Tree |  |  |
| 894 | Tree | Peach Tree |  |  |
| 895 | Tree | Apple Tree |  |  |
| 896 | Tree | Orange Tree |  |  |
| 897 | Static | Burnt Fruit Tree |  |  |
| 898 | Tree | Autumn Brown Tree |  |  |
| 899 | Tree | Autumn Orange Tree |  |  |
| 900 | Tree | Autumn Dark Red Tree |  |  |
| 901 | Tree | Autumn Light Red Tree |  |  |
| 902 | Tree | Autumn Yellow Tree |  |  |
| 903 | Tree | Dormant Deciduous Tree |  |  |
| 904 | Tree | Frozen Deciduous Tree |  |  |
| 905 | Tree | Cherry Tree |  |  |
| 906 | Tree | Cherry Tree (Blossoms) | L1:77@0.1 |  |
| 1002 | Static | Dead Shrubs |  |  |
| 1005 | Static | Dead Tree |  |  |
| 1100 | Static | lilly pads | L1:17@0.24 |  |
| 1101 | Static | swamp assorted | L1:5@0.0 |  |
| 1102 | Static | reeds and cattails |  |  |
| 1103 | Static | swamp flower purple |  |  |
| 1104 | Static | swamp flower white |  |  |
| 1105 | Static | lilly pad cluster | L1:23@0.09 |  |
| 1106 | Static | cattail cluster | L1:25@0.52 |  |
| 1107 | Static | tall reeds |  |  |
| 1112 | Static | Swamp Cypress | L1:17@0.12 |  |
| 1113 | Static | Swamp Cypress dead |  |  |
| 1233 | Static | short hedge V |  |  |
| 1234 | Static | short hedge H |  |  |
| 1243 | Static | round topiari |  |  |
| 1245 | Static | fir topiari |  |  |
| 1373 | Static | med blooming mushroom |  |  |
| 1374 | Static | large and med mushroom |  |  |
| 1375 | Static | 2 med mushrooms |  |  |
| 1376 | Static | large mushroom |  |  |
| 1377 | Static | med mushroom |  |  |
| 1378 | Static | small mushroom cluster (right) |  |  |
| 1379 | Static | small mushroom cluster (left) |  |  |

### Grove  (7 entries)

| ID | Type | Name | Observed usage | Notes |
|---|---|---|---|---|
| 23 | Floor | ⟨UNNAMED — see unknowns #4⟩ |  |  |
| 157 | Wall | ⟨UNNAMED — see unknowns #4⟩ |  | destroyed→160, ruins→170 |
| 158 | Wall | ⟨UNNAMED — see unknowns #4⟩ |  | destroyed→161, ruins→170 |
| 226 | Static | ⟨UNNAMED — see unknowns #4⟩ |  |  |
| 227 | Static | ⟨UNNAMED — see unknowns #4⟩ |  |  |

### Obstructions  (31 entries)

| ID | Type | Name | Observed usage | Notes |
|---|---|---|---|---|
| 19 | Obstruction | Reef | L1:33@1.0 · L2:225@1.0 |  |
| 164 | Obstruction | Massive Anvil |  |  |
| 165 | Obstruction | Iron Porticullus (H) |  |  |
| 166 | Obstruction | Iron Porticullus (V) |  |  |
| 168 | Obstruction | Dirty Marble Pillar | L2:4@0.0 |  |
| 266 | Obstruction | Heavy Oak | L1:876@0.98 · L2:3@0.0 |  |
| 313 | Obstruction | Sandstone Pillar |  |  |
| 449 | Obstruction | Jail (H) |  |  |
| 450 | Obstruction | Jail (V) |  |  |
| 605 | Obstruction | Reef [Zrikz] | L1:30@1.0 · L2:35@1.0 |  |
| 857 | Obstruction | Large dragonscale pillar |  |  |
| 866 | Obstruction | small dragonscale pillar |  |  |
| 879 | Obstruction | Crate (L) |  |  |
| 882 | Obstruction | Crate of Grains |  |  |
| 883 | Obstruction | Mace Display Crate | L4:1@0.0 |  |
| 884 | Obstruction | Greataxe Display Crate |  |  |
| 885 | Obstruction | Sword Display Crate |  |  |
| 887 | Obstruction | Cart (V) |  |  |
| 892 | Obstruction | Cart (H) |  |  |
| 954 | Obstruction | Big City cemetary fence post |  |  |
| 955 | Obstruction | Big City gargoyle Gate post |  |  |
| 1246 | Obstruction | Big City knight memorial |  |  |
| 1271 | Obstruction | dungeon dreary purple column |  |  |
| 1280 | Obstruction | dungeon dreary plain king statue |  |  |
| 1281 | Obstruction | dungeon dreary plain dragon statue |  |  |
| 1295 | Obstruction | dungeon dreary blue column |  |  |
| 1304 | Obstruction | dungeon dreary blue king statue |  |  |
| 1305 | Obstruction | dungeon dreary blue dragon statue |  |  |
| 1319 | Obstruction | dungeon dreary green column |  |  |
| 1328 | Obstruction | dungeon dreary green king statue |  |  |
| 1329 | Obstruction | dungeon dreary green dragon statue |  |  |

### Ruins  (158 entries)

| ID | Type | Name | Observed usage | Notes |
|---|---|---|---|---|
| 38 | Ruins | Dungeon Wall Ruins (H) |  |  |
| 39 | Ruins | Dungeon Wall Ruins (V) |  |  |
| 40 | Ruins | Town Wall Ruins (H) | L2:7@0.29 |  |
| 41 | Ruins | Town Wall Ruins (V) | L2:10@0.6 |  |
| 42 | Ruins | Temple Wall Ruins (H) | L2:5@0.4 |  |
| 43 | Ruins | Temple Wall Ruins (V) | L2:6@0.0 |  |
| 44 | Ruins | Dungeon | L3:6@1.0 |  |
| 45 | Ruins | Town | L2:14@0.0 · L4:7@0.71 |  |
| 46 | Ruins | Temple | L2:12@0.17 · L5:5@0.4 · L6:34@0.71 |  |
| 141 | Ruins | Dirty Marble Ruins (H) | L6:2@1.0 |  |
| 142 | Ruins | Dirty Marble Ruins (V) |  |  |
| 144 | Ruins | Temple Wall Ruins (C) |  |  |
| 144 | Ruins | Dirty Marble Ruins (C) |  |  |
| 147 | Ruins | Heavy Log Ruins (H) |  |  |
| 148 | Ruins | Heavy Log Ruins (V) |  |  |
| 150 | Ruins | Heavy Log Ruins (C) |  |  |
| 153 | Ruins | Dragon Ruins (H) |  |  |
| 154 | Ruins | Dragon Ruins (V) |  |  |
| 156 | Ruins | Dragon Ruins (C) |  |  |
| 170 | Ruins | Cave | L2:3@0.0 |  |
| 226 | Ruins | Thicket Ruins (H) |  |  |
| 227 | Ruins | Thicket Ruins (V) |  |  |
| 228 | Ruins | Thicket Ruins (C) |  |  |
| 260 | Ruins | Egyptian Ruins (H) |  |  |
| 261 | Ruins | Egyptian Ruins (V) |  |  |
| 263 | Ruins | Egyptian Ruins (C) |  |  |
| 338 | Ruins | Sandstone Wall Ruins (H) |  |  |
| 339 | Ruins | Sandstone Wall Ruins (V) |  |  |
| 342 | Ruins | Dirt Wall Ruins (H) |  |  |
| 343 | Ruins | Dirt Wall Ruins (V) |  |  |
| 356 | Ruins | Dirt Wall Ruins (C) |  |  |
| 360 | Ruins | Sandstone Wall Ruins (C) |  |  |
| 364 | Ruins | Red Shoji Ruins (H) |  |  |
| 365 | Ruins | Red Shoji Ruins (V) |  |  |
| 367 | Ruins | Red Shoji Ruins (C) |  |  |
| 380 | Ruins | Red Shoji |  |  |
| 396 | Ruins | Blue Marble Ruins (H) |  |  |
| 397 | Ruins | Blue Marble Ruins (V) |  |  |
| 398 | Ruins | Mines |  |  |
| 410 | Ruins | Blue Marble Ruins (C) |  |  |
| 432 | Ruins | Dragon |  |  |
| 441 | Ruins | Dragon Ruins Blue (H) |  |  |
| 442 | Ruins | Dragon Ruins Blue (V) |  |  |
| 444 | Ruins | Dragon Ruins Blue (C) |  |  |
| 461 | Ruins | High Mountain Ruins (H) |  |  |
| 462 | Ruins | High Mountain Ruins (V) |  |  |
| 464 | Ruins | High Mountain Ruins (C) |  |  |
| 465 | Ruins | Highmountain |  |  |
| 472 | Ruins | Pagoda Shoji Ruins (H) |  |  |
| 473 | Ruins | Pagoda Shoji Ruins (V) |  |  |
| 476 | Ruins | Pagoda Framed Ruins (H) |  |  |
| 477 | Ruins | Pagoda Framed Ruins (V) |  |  |
| 481 | Ruins | Pagoda Shoji Ruins (C) |  |  |
| 481 | Ruins | Pagoda Framed Ruins (C) |  |  |
| 481 | Ruins | Pagoda Ruins (C) |  |  |
| 484 | Ruins | Pagoda Framed Ruins (H) |  |  |
| 485 | Ruins | Pagoda Framed Ruins (V) |  |  |
| 488 | Ruins | Pagoda Ruins (H) |  |  |
| 489 | Ruins | Pagoda Ruins (V) |  |  |
| 638 | Ruins | Sewer Wall Ruins (H) |  |  |
| 639 | Ruins | Sewer Wall Ruins (V) |  |  |
| 640 | Ruins | Broken Portal Pillar (Clean) | L5:6@0.0 · L6:5@0.4 |  |
| 641 | Ruins | Broken Stalagmite (Clean) |  |  |
| 642 | Ruins | Broken Portal Pillar | L2:3@0.0 · L5:2@0.0 · L6:3@0.0 |  |
| 643 | Ruins | Broken Stalagmite |  |  |
| 674 | Ruins | light stone rubble |  |  |
| 675 | Ruins | light stone wall ruin (V) |  |  |
| 676 | Ruins | light stone wall ruin (H) |  |  |
| 677 | Ruins | light stone column ruin |  |  |
| 683 | Ruins | rock rubble |  |  |
| 684 | Ruins | rock wall ruin (V) |  |  |
| 685 | Ruins | rock wall ruin (H) |  |  |
| 686 | Ruins | rock wall column ruin |  |  |
| 692 | Ruins | cave rubble |  |  |
| 693 | Ruins | cave wall ruin (V) |  |  |
| 694 | Ruins | cave wall ruin (H) |  |  |
| 695 | Ruins | cave wall column ruin |  |  |
| 703 | Ruins | Big City wood and stone rubble |  |  |
| 704 | Ruins | Big City wood and stone V |  |  |
| 705 | Ruins | Big City wood and stone H |  |  |
| 706 | Ruins | Big City wood and stone column ruin |  |  |
| 710 | Ruins | Panel Wall Ruins (H) |  |  |
| 712 | Ruins | Panel wall ruins (V) |  |  |
| 716 | Ruins | Lodge Wall Ruins (H) |  |  |
| 716 | Ruins | Lodge Wall Ruins (h) |  |  |
| 717 | Ruins | Heavy Logs Rubble | L2:15@0.13 |  |
| 718 | Ruins | Lodge wall ruins (V) |  |  |
| 718 | Ruins | Lodge Wall Ruins (v) |  |  |
| 783 | Ruins | Dungeon Wall Ruins (C) |  |  |
| 784 | Ruins | Town Wall Ruins (C) | L2:3@0.0 |  |
| 938 | Ruins | Big City stone wall ruin H |  |  |
| 947 | Ruins | Big City stone wall ruin V |  |  |
| 965 | Ruins | Big City wood sided wall ruin H |  |  |
| 994 | Ruins | Ice Labyrinth Wall ruins(H) |  |  |
| 995 | Ruins | Ice Wall Rubble |  |  |
| 996 | Ruins | Ice Labyrinth Wall ruins (V) |  |  |
| 998 | Ruins | Ice Labyrinth Corner pillar ruins |  |  |
| 1011 | Ruins | Lava Tube Wall ruins (H) |  |  |
| 1012 | Ruins | Lava Tube Rubble |  |  |
| 1013 | Ruins | Lava Tube Wall ruins (V) |  |  |
| 1015 | Ruins | Lava Tube Corner pillar ruins |  |  |
| 1020 | Ruins | Sandstone Rubble |  |  |
| 1021 | Ruins | Blue Marble Rubble |  |  |
| 1022 | Ruins | Egyptian Rubble |  |  |
| 1023 | Ruins | Pagoda Rubble |  |  |
| 1024 | Ruins | Thicket Rubbish | L4:3@0.0 |  |
| 1093 | Ruins | swamp cave wall ruin (h) |  |  |
| 1094 | Ruins | swamp cave rubble |  |  |
| 1095 | Ruins | swamp cave wall ruin (v) |  |  |
| 1097 | Ruins | swamp cave column ruin |  |  |
| 1161 | Ruins | palace right pillar ruins (h) |  |  |
| 1162 | Ruins | palace right pillar ruins (v) |  |  |
| 1163 | Ruins | palace left pillar ruins (h) |  |  |
| 1164 | Ruins | palace left pillar ruins (v) |  |  |
| 1165 | Ruins | palace wall ruins (v) |  |  |
| 1166 | Ruins | palace wall ruins (h) |  |  |
| 1167 | Ruins | art niche wall ruin (v) |  |  |
| 1168 | Ruins | art niche wall ruin (h) |  |  |
| 1169 | Ruins | palace column ruin |  |  |
| 1185 | Ruins | palace arch ruins (h) |  |  |
| 1186 | Ruins | palace arch ruins (v) |  |  |
| 1217 | Ruins | mine rubble |  |  |
| 1228 | Ruins | irr wall ruin (h) |  |  |
| 1229 | Ruins | irr wall rubble |  |  |
| 1230 | Ruins | irr wall ruin (v) |  |  |
| 1232 | Ruins | irr post ruin |  |  |
| 1236 | Ruins | Big City log wall ruin |  |  |
| 1238 | Ruins | Big City log column ruin |  |  |
| 1239 | Ruins | Big City wood sided wall rubble |  |  |
| 1262 | Ruins | dungeon dreary purple wall rubble |  |  |
| 1263 | Ruins | dungeon dreary purple wall ruin V |  |  |
| 1264 | Ruins | dungeon dreary purple wall ruin H |  |  |
| 1265 | Ruins | dungeon dreary purple column ruin |  |  |
| 1286 | Ruins | dungeon dreary desaturated blue rubble |  |  |
| 1287 | Ruins | dungeon dreary desaturated blue wall V |  |  |
| 1288 | Ruins | dungeon dreary desaturated blue wall H |  |  |
| 1289 | Ruins | dungeon dreary desaturated blue column |  |  |
| 1310 | Ruins | dungeon dreary 2x desaturated green rubble |  |  |
| 1311 | Ruins | dungeon dreary 2x desaturated green wall V |  |  |
| 1312 | Ruins | dungeon dreary 2x desaturated green wall H |  |  |
| 1313 | Ruins | dungeon dreary 2x desaturated green column |  |  |
| 1343 | Ruins | red brick post ruin |  |  |
| 1344 | Ruins | red brick rubble |  |  |
| 1345 | Ruins | red brick wall ruin (v) |  |  |
| 1346 | Ruins | red brick wall ruin (h) |  |  |
| 1352 | Ruins | icy cave rubble |  |  |
| 1353 | Ruins | icy cave wall ruin (v) |  |  |
| 1354 | Ruins | icy cave wall ruin (h) |  |  |
| 1355 | Ruins | icy cave post ruin |  |  |
| 1359 | Ruins | glacier wall ruin (h) |  |  |
| 1360 | Ruins | glacier rubble |  |  |
| 1361 | Ruins | glacier wall ruin (v) |  |  |
| 1363 | Ruins | glacier post ruin |  |  |
| 1368 | Ruins | nidavellir rubble |  |  |
| 1369 | Ruins | nidavellir wall ruin (v) |  |  |
| 1370 | Ruins | nidavellir wall ruin (h) |  |  |
| 1371 | Ruins | nidavellir post ruin |  |  |

### Decorations  (225 entries)

| ID | Type | Name | Observed usage | Notes |
|---|---|---|---|---|
| 114 | Static | Boxing Ring |  |  |
| 117 | Static | Mirror (H) |  |  |
| 118 | Static | Mirror (V) |  |  |
| 137 | Static | Congealed Lava |  |  |
| 167 | Static | Blood Stains |  |  |
| 171 | Static | Torn Tapestry (H) |  |  |
| 172 | Static | Torn Tapestry (V) |  |  |
| 173 | Static | Crushed Bones |  |  |
| 191 | Static | Waterfall (H) |  |  |
| 192 | Static | Waterfall (V) |  |  |
| 193 | Static | Fog |  |  |
| 194 | Static | Shimmering Wall (H) |  |  |
| 195 | Static | Shimmering Wall (V) |  |  |
| 197 | Static | Oriental Tapestry (H) |  |  |
| 198 | Static | Oriental Tapestry (V) |  |  |
| 209 | Static | Fountain Pool |  |  |
| 210 | Static | Fountain Center |  |  |
| 211 | Static | Sordid Remains (H) |  |  |
| 212 | Static | Sordid Remains (V) |  |  |
| 213 | Static | Gravestone (1) |  |  |
| 214 | Static | Gravestone (2) |  |  |
| 215 | Static | Gravestone (3) |  |  |
| 216 | Static | Grave (1) |  |  |
| 217 | Static | Grave (2) |  |  |
| 218 | Static | Open Stones |  |  |
| 219 | Static | Iron Throne |  |  |
| 220 | Static | Hanging Skeleton (H) |  |  |
| 221 | Static | Hanging Skeleton (V) |  |  |
| 222 | Static | Dragon Throne |  |  |
| 235 | Static | Barrel Water |  |  |
| 236 | Static | Blood over Altar |  |  |
| 242 | Static | Small Spring |  |  |
| 243 | Static | Bookshelf (H) | L2:1@0.0 |  |
| 244 | Static | Bookshelf (V) | L2:1@0.0 |  |
| 245 | Static | Wizard Emblems (H) | L2:1@0.0 |  |
| 246 | Static | Wizard Emblems (V) | L2:2@0.0 |  |
| 250 | Static | Tailor Scraps | L2:1@0.0 |  |
| 251 | Static | Oak Throne | L2:1@0.0 |  |
| 305 | Static | Mace (H) |  |  |
| 306 | Static | Mace (V) |  |  |
| 317 | Static | Red Carpet | L2:4@0.5 |  |
| 348 | Static | Price List (H) |  |  |
| 349 | Static | Treasure | L4:4@0.0 |  |
| 361 | Static | Price List (V) |  |  |
| 373 | Static | Campfire | L3:1@0.0 · L4:4@0.0 |  |
| 385 | Static | Dagger (H) |  |  |
| 386 | Static | Dagger (V) |  |  |
| 401 | Static | Wine Cask (V) | L4:1@0.0 |  |
| 411 | Static | Jail Cot (H) |  |  |
| 412 | Static | Jail Cot (V) |  |  |
| 422 | Static | Torii (H) |  |  |
| 423 | Static | Torii (V) |  |  |
| 424 | Static | Closed Sarcophagus (H) |  |  |
| 425 | Static | Closed Sarcophagus (V) |  |  |
| 437 | Static | Open Sarcophagus (H) |  |  |
| 438 | Static | Open Sarcophagus (V) |  |  |
| 439 | Static | Storage Shelf (H) | L2:2@0.0 |  |
| 440 | Static | Storage Shelf (V) | L2:3@1.0 |  |
| 478 | Static | Crane (H) |  |  |
| 479 | Static | Crane (V) |  |  |
| 490 | Static | Fuji (H) |  |  |
| 491 | Static | Fuji (V) |  |  |
| 630 | Static | Sewer Wall (V) |  |  |
| 631 | Static | Sewer Wall (H) |  |  |
| 632 | Static | Sewer Wall Drain (1) |  |  |
| 633 | Static | Sewer Wall Drain (2) |  |  |
| 634 | Static | Sewer Wall Drain (3) |  |  |
| 635 | Static | Sewer Wall Drain (4) |  |  |
| 636 | Static | Sewer Wall Full (V) |  |  |
| 637 | Static | Sewer Wall Full (H) |  |  |
| 642 | Static | Collapsed Portal Pillar |  |  |
| 643 | Static | Shattered Stalagmite |  |  |
| 649 | Static | Vase (Base) |  |  |
| 650 | Static | Vase (Single Ring) |  |  |
| 651 | Static | Vase (Double Ring) |  |  |
| 652 | Static | Vase (Pattern 1) |  |  |
| 653 | Static | Vase (Pattern 2) |  |  |
| 654 | Static | Vase (Pattern 3) |  |  |
| 655 | Static | Vase (Shadow) |  |  |
| 656 | Static | Vase (Broken) | L2:2@0.0 |  |
| 657 | Static | Vases | L2:4@0.0 |  |
| 659 | Static | snowdrift edge (V) |  |  |
| 660 | Static | snowdrift edge (H) |  |  |
| 661 | Static | webbed soul (H) |  |  |
| 662 | Static | webbed soul (V) |  |  |
| 663 | Static | web(H) |  |  |
| 664 | Static | web(V) |  |  |
| 665 | Static | crushed skeleton | L4:2@0.0 |  |
| 668 | Static | skeleton 1 |  |  |
| 669 | Static | skeleton 2 |  |  |
| 678 | Static | skeleton 3 |  |  |
| 687 | Static | skeleton 4 |  |  |
| 696 | Static | armored skeleton |  |  |
| 726 | Static | Plaster-set Back-board (H) |  |  |
| 729 | Static | Plaster-set Back-board (V) |  |  |
| 738 | Static | inside-back rope (H) |  |  |
| 739 | Static | left-inside rope (V) |  |  |
| 740 | Static | right flap-1 (V) |  |  |
| 741 | Static | red rug | L2:6@1.0 |  |
| 742 | Static | gray rug |  |  |
| 743 | Static | front flap-2 (H) |  |  |
| 744 | Static | inside back rope accent (H) |  |  |
| 745 | Static | inside-left rope accent (V) |  |  |
| 746 | Static | right flap-2 (V) |  |  |
| 747 | Static | square fur rug |  |  |
| 748 | Static | bear rug (V) |  |  |
| 749 | Static | front flap-1 accent (H) |  |  |
| 750 | Static | inside-back shade-screen (H) |  |  |
| 751 | Static | inside left shade screen (V) |  |  |
| 752 | Static | right flap-1 accent (V) |  |  |
| 753 | Static | bear rug (H) |  |  |
| 754 | Static | front flap-2 accent (H) |  |  |
| 755 | Static | inside back stripe accent (H) |  |  |
| 756 | Static | inside left stripe accent (V) |  |  |
| 757 | Static | right flap-2 accent (V) |  |  |
| 762 | Static | snowdrift (H) |  |  |
| 763 | Static | snowdrift2 (V) |  |  |
| 764 | Static | librarybookshelf (H) | L2:2@0.0 |  |
| 765 | Static | librarybookshelf2 (V) | L2:1@0.0 |  |
| 817 | Static | Stair Rug Down South |  |  |
| 818 | Static | Stair Rug Down East |  |  |
| 819 | Static | Stair Rug Down West |  |  |
| 820 | Static | Stair Rug Down North |  |  |
| 821 | Static | Stair Rug Up North |  |  |
| 822 | Static | Stair Rug Up West |  |  |
| 823 | Static | Stair Rug Up East |  |  |
| 824 | Static | Stair Rug Up South |  |  |
| 841 | Static | Snow and Icey Stair Down South |  |  |
| 842 | Static | Snow and Icey Stair Down East |  |  |
| 843 | Static | Snow and Icey Stair Down West |  |  |
| 844 | Static | Snow and Icey Stair Down North |  |  |
| 845 | Static | Snow and Icey Stair Up North |  |  |
| 846 | Static | Snow and Icey Stair Up West |  |  |
| 847 | Static | Snow and Icey Stair Up East |  |  |
| 848 | Static | Snow and Icey Stair Up South |  |  |
| 849 | Static | Bloodied Stair Down South |  |  |
| 850 | Static | Bloodied Stair Down East |  |  |
| 851 | Static | Bloodied Stair Down West |  |  |
| 852 | Static | Bloodied Stair Down North |  |  |
| 853 | Static | Bloodied Stair Up North |  |  |
| 854 | Static | Bloodied Stair Up West |  |  |
| 855 | Static | Bloodied Stair Up East |  |  |
| 856 | Static | Bloodied Stair Up South |  |  |
| 879 | Static | Sealed Crate (L) |  |  |
| 880 | Static | Crated Fruits | L2:2@0.0 · L3:3@0.0 · L4:7@0.0 |  |
| 881 | Static | Crated Veggies and Grains | L2:2@0.0 · L3:4@0.0 · L4:1@0.0 |  |
| 886 | Static | Sealed Crate (S) | L2:1@0.0 · L4:1@0.0 |  |
| 888 | Static | Open Crate (L) |  |  |
| 889 | Static | Destroyed Crate (L) | L2:1@0.0 · L4:1@0.0 |  |
| 890 | Static | Open Crate (S) | L4:1@0.0 |  |
| 891 | Static | Destroyed Crate (S) | L3:2@0.0 · L4:4@0.0 |  |
| 907 | Static | Mossy Stairs Down South |  |  |
| 908 | Static | Mossy Stairs Down East |  |  |
| 909 | Static | Mossy Stairs Down West |  |  |
| 910 | Static | Mossy Stairs Down North |  |  |
| 911 | Static | Mossy Stairs Up North |  |  |
| 912 | Static | Mossy Stairs Up West |  |  |
| 913 | Static | Mossy Stairs Up East |  |  |
| 914 | Static | Mossy Stairs Up South |  |  |
| 915 | Static | Grassy Stairs Down South |  |  |
| 916 | Static | Grassy Stairs Down East |  |  |
| 917 | Static | Grassy Stairs Down West |  |  |
| 918 | Static | Grassy Stairs Down North |  |  |
| 919 | Static | Grassy Stairs Up North |  |  |
| 920 | Static | Grassy Stairs Up West |  |  |
| 921 | Static | Grassy Stairs Up East |  |  |
| 922 | Static | Grassy Stairs Up South |  |  |
| 923 | Static | Floral Stair Accent Down South |  |  |
| 924 | Static | Floral Stair Accent Down East |  |  |
| 925 | Static | Floral Stair Accent Down West |  |  |
| 926 | Static | Floral Stair Accent Down North |  |  |
| 927 | Static | Floral Stair Accent Up North |  |  |
| 928 | Static | Floral Stair Accent Up West |  |  |
| 929 | Static | Floral Stair Accent Up East |  |  |
| 930 | Static | Floral Stair Accent Up South |  |  |
| 1001 | Static | Mossy Pillar | L3:45@0.0 · L4:9@0.56 |  |
| 1006 | Static | Waterfall Animated (H) |  |  |
| 1007 | Static | Waterfall Animated (V) |  |  |
| 1109 | Static | swamp vines for tree column |  |  |
| 1110 | Static | swamp vines wrap for tree column |  |  |
| 1111 | Static | swamp vines floral for tree column |  |  |
| 1188 | Static | Magic circle 3 |  |  |
| 1189 | Static | Magic circle 2 |  |  |
| 1190 | Static | Magic circle 1 |  |  |
| 1191 | Static | lectern (h) |  |  |
| 1192 | Static | lectern (v) |  |  |
| 1193 | Static | desk (h) |  |  |
| 1194 | Static | desk (v) |  |  |
| 1195 | Static | single bed (v) |  |  |
| 1196 | Static | double bed (v) |  |  |
| 1197 | Static | rightfacing chair (h) |  |  |
| 1198 | Static | southfacing chair (v) | L2:2@0.0 |  |
| 1199 | Static | leftfacing chair (h) | L2:1@0.0 |  |
| 1200 | Static | northfacing chair (v) | L2:1@0.0 |  |
| 1201 | Static | wardrobe (v) |  |  |
| 1202 | Static | wardrobe (h) |  |  |
| 1203 | Static | nightstand (h) |  |  |
| 1204 | Static | nightstand (v) |  |  |
| 1205 | Static | single bed (h) |  |  |
| 1206 | Static | double bed (h) |  |  |
| 1207 | Static | bunk (v) |  |  |
| 1208 | Static | bunk (h) |  |  |
| 1209 | Static | big chest (h) |  |  |
| 1210 | Static | big chest (v) |  |  |
| 1211 | Static | nightstand (h) chamber pot,wash basin, candle |  |  |
| 1212 | Static | nightstand (v) candle |  |  |
| 1242 | Static | cauldron |  |  |
| 1244 | Static | headstone 1 |  |  |
| 1247 | Static | small headstone 1 |  |  |
| 1248 | Static | cross headstone 1 |  |  |
| 1249 | Static | sleeping woman sarcophagus V |  |  |
| 1250 | Static | blank sarcophagus V |  |  |
| 1251 | Static | rejuvinated sarcophagus V |  |  |
| 1252 | Static | headstone 1 V |  |  |
| 1253 | Static | small headstone 1 V |  |  |
| 1254 | Static | cross headstone 1 V |  |  |
| 1255 | Static | rejuvinated sarcophagus H |  |  |
| 1256 | Static | sleeping woman sarophagus H |  |  |
| 1257 | Static | blank sarcophagus H |  |  |
| 1274 | Static | purple cultist statue |  |  |
| 1275 | Static | purple maiden statue |  |  |
| 1298 | Static | blue cultist statue |  |  |
| 1299 | Static | blue maiden statue |  |  |
| 1322 | Static | green cultist statue |  |  |
| 1323 | Static | green maiden statue |  |  |

### lighting and shade  (25 entries)

| ID | Type | Name | Observed usage | Notes |
|---|---|---|---|---|
| 931 | Static | Torchlight (H) |  |  |
| 932 | Static | Torchlight (V) |  |  |
| 933 | Static | Wall Darkened (H) |  |  |
| 934 | Static | Wall Darkened (V) |  |  |
| 935 | Static | Floor Darkened |  |  |
| 975 | Static | Floor Brazier |  |  |
| 976 | Static | Wall Brazier (H) |  |  |
| 977 | Static | Wall Brazier (V) |  |  |
| 978 | Static | Wall Brazier Greenfire(H) |  |  |
| 979 | Static | Wall Brazier Greenfire(V) |  |  |
| 980 | Static | Wall Brazier Bluefire(H) |  |  |
| 981 | Static | Wall Brazier Bluefire(V) |  |  |
| 982 | Static | Candelabra |  |  |
| 1025 | Static | Candelabra without Shade |  |  |
| 1029 | Static | torches (H) no shade |  |  |
| 1030 | Static | torches (v) no shade |  |  |
| 1031 | Static | blue wall brazier without shade (H) | L2:4@0.0 · L5:2@0.0 |  |
| 1032 | Static | blue wall brazier without shade (V) | L2:1@0.0 |  |
| 1033 | Static | green wall brazier without shade (H) |  |  |
| 1034 | Static | green wall brazier without shade (V) |  |  |
| 1035 | Static | wall brazier without shade (H) |  |  |
| 1036 | Static | wall brazier without shade (V) |  |  |
| 1037 | Static | floor brazier without shade | L2:10@0.0 · L5:3@0.0 |  |
| 1038 | Static | Sidewall Darkened (V) |  |  |
| 1039 | Static | Sidewall Darkened (H) |  |  |

### Wall Doodads (H)  (53 entries)

| ID | Type | Name | Observed usage | Notes |
|---|---|---|---|---|
| 767 | Static | Shield Ornamental (for the shadow) (H) | L2:2@0.0 |  |
| 768 | Static | Crossed swords (H) | L2:1@0.0 |  |
| 769 | Static | Shiny Shield Ornamental (H) |  |  |
| 770 | Static | Shield Ornamental Trim 1 (H) |  |  |
| 771 | Static | Shield Ornamental Trim 2 (H) |  |  |
| 772 | Static | Shield Ornamental Matte Shield (H) |  |  |
| 773 | Static | Shield Ornamental Chevron (H) |  |  |
| 774 | Static | Shield Ornamental inverted Chevron (H) |  |  |
| 775 | Static | Banner Low Contrast (H) |  |  |
| 776 | Static | Banner trim 1 (H) |  |  |
| 777 | Static | Banner Yasnaki symbol (H) |  |  |
| 778 | Static | Banner High contrast (H) |  |  |
| 779 | Static | Banner Mu Symbol (H) |  |  |
| 780 | Static | Banner pole (H) |  |  |
| 781 | Static | Banner trim 2 (H) |  |  |
| 782 | Static | Banner Kesmai Dragon symbol (H) |  |  |
| 1136 | Static | dragon head mount (v) |  |  |
| 1137 | Static | dragon head mount (h) |  |  |
| 1138 | Static | vampire portrait (v) |  |  |
| 1139 | Static | vampire portrait (h) |  |  |
| 1141 | Static | dragon head arch topper (h) |  |  |
| 1142 | Static | dragon head arch topper (v) |  |  |
| 1143 | Static | bull head arch topper (h) |  |  |
| 1144 | Static | bull head arch topper (v) |  |  |
| 1159 | Static | lion head arch topper (v) |  |  |
| 1160 | Static | lion head arch topper (h) |  |  |
| 1171 | Static | stained glass - dragon (v) |  |  |
| 1172 | Static | stained glass - dragon (h) |  |  |
| 1173 | Static | red dragon banner (v) |  |  |
| 1174 | Static | red dragon banner (h) |  |  |
| 1175 | Static | dragon mural (v) |  |  |
| 1176 | Static | dragon mural (h) |  |  |
| 1177 | Static | stained glass - priest (v) |  |  |
| 1178 | Static | stained glass - priest (h) |  |  |
| 1179 | Static | stained glass - court (v) |  |  |
| 1180 | Static | stained glass - court (h) |  |  |
| 1181 | Static | purple Mu banner (v) |  |  |
| 1182 | Static | purple Mu banner (h) |  |  |
| 1183 | Static | green banner (v) |  |  |
| 1184 | Static | green banner (h) |  |  |
| 1187 | Static | black banner (h) |  |  |
| 1276 | Static | purple bat ornament (h) |  |  |
| 1277 | Static | purple bat ornament (v) |  |  |
| 1278 | Static | purple wall carving (h) |  |  |
| 1279 | Static | purple wall carving (v) |  |  |
| 1300 | Static | blue bat ornament (h) |  |  |
| 1301 | Static | blue bat ornament (v) |  |  |
| 1302 | Static | blue wall carving (h) |  |  |
| 1303 | Static | blue wall carving (v) |  |  |
| 1324 | Static | green bat ornament (h) |  |  |
| 1325 | Static | green bat ornament (v) |  |  |
| 1326 | Static | green wall carving (h) |  |  |
| 1327 | Static | green wall carving (v) |  |  |

### Counters and Altars  (24 entries)

| ID | Type | Name | Observed usage | Notes |
|---|---|---|---|---|
| 86 | Counter | Wood (H) |  |  |
| 87 | Counter | Wood (V) |  |  |
| 96 | Counter | Slate (H) |  |  |
| 97 | Counter | Slate (V) |  |  |
| 113 | Altar | Temple Altar |  |  |
| 138 | Altar | Granite Altar (1) |  |  |
| 163 | Altar | Granite Altar (2) |  |  |
| 169 | Altar | Skull Altar |  |  |
| 174 | Altar | Carved Wood Altar |  |  |
| 248 | Counter | Gilded (H) |  |  |
| 249 | Counter | Gilded (V) |  |  |
| 267 | Counter | Table (H) |  |  |
| 268 | Counter | Table (V) |  |  |
| 269 | Counter | Alchemy Table (H) |  |  |
| 270 | Counter | Alchemy Table (V) |  |  |
| 278 | Altar | Egyptian Altar (1) |  |  |
| 290 | Altar | Egyptian Altar (2) |  |  |
| 302 | Altar | Egyptian Altar (3) |  |  |
| 314 | Altar | Egyptian Altar (4) |  |  |
| 324 | Altar | Egyptian Altar (5) |  |  |
| 327 | Altar | Egyptian Altar (6) |  |  |
| 368 | Altar | Blue Marble (6) |  |  |
| 399 | Counter | Stone Table (H) |  |  |
| 400 | Counter | Stone Table (V) |  |  |

---

*Regenerable: the census scripts and intermediate data for this file were produced by the*
*decoration Cowork session of 2026-08-12; the source of truth is always `Components.xml` +*
*the region files themselves. If Tony's regions change, re-run the census — don't trust old*
*counts (same rule as the maps KB).*
