# WorldForge AI Gen — tools

Scripts for generating and previewing Stormhalter regions outside WorldForge.
Design and findings: `docs/worldforge-ai-gen/`. Legend and terrain index: `data/worldforge-ai-gen/`.

- `xnb2png.py <xnb-root> <out-dir>` — decode MonoGame XNB textures (LZ4, RGBA8) from the client's
  unzipped `Kesmai.bin` / `Stormhalter.bin` into PNGs, keeping relative paths. Needs `lz4`, `pillow`.
- `wf_render.py <segment.mapproj|region.xml> <regionId> <out.png>` — render a region the way the editor
  does (55 px grid, sprites at cell −45, scaled 1/resolution, tinted, stable-sorted by sprite order,
  tiles drawn x-outer/y-inner). Edit `ART` and `TERR` at the top to point at your decoded art and the
  two Terrain.xml files.

The decoded art and the dev map corpus are not in git; they live in
`OneDrive\Stormhalter Worlds\WorldForge AI Gen\`.

## Forge Viewer (HTML)
- `build_atlas.py` — pack every terrain sprite layer into `atlas.webp` + `atlas-index.json` (needs the decoded art and `data/worldforge-ai-gen/terrain-index-merged.json`).
- `build.py <out.html>` — assemble `viewer-template.html` + atlas + a sample region into one self-contained page.
  Open it in any browser and drop a `Regions\N.xml` or `.mapproj` on it. Grid lines every 10 tiles, hover inspector with palette names, layer toggles, Structure overlay (red = blocking, amber = door, green = floor), Break-walls view.
