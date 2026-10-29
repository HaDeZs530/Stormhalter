#!/usr/bin/env bash
# Rebuild the WorldForge AI Gen working tree in a fresh cloud session.
# The tools expect these paths (they were built in /home/claude):
#   /home/claude/tools/wf_render.py                      renderer
#   /home/claude/art/<texture>.png                       sprite sheets   (from Dropbox reference/art.zip)
#   /home/claude/client-bins/Data/Data/Terrain.xml       client terrain  (from Dropbox reference/data/Terrain.xml)
#   /home/claude/client-bins/Data/Data/Terrain-External.xml   (from this repo)
#   /home/claude/out/2026-10-29 piece-book-draft.json    piece book      (from Dropbox piece-book/)
#   /home/claude/lok-studio                              wall engine     (github HaDeZs530/LOK-Studio)
#   /home/claude/jkachhad/stormhalter/Segments/Praetoseba.mapproj   (this repo, Segments/)
#   /home/claude/pilot/*.py                              plan runner, design builder
# Usage: bash setup.sh <dir with art.zip, Terrain.xml, piece-book-draft.json staged from Dropbox>
set -e
STAGE="${1:?give the folder holding art.zip, Terrain.xml and the piece-book json}"
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
H=/home/claude
mkdir -p $H/tools $H/client-bins/Data/Data $H/out $H/pilot $H/jkachhad
cp "$REPO/tools/worldforge-ai-gen/wf_render.py" $H/tools/
cp "$REPO/tools/worldforge-ai-gen/pilot/"*.py $H/pilot/
[ -d $H/art ] || (cd $H && unzip -q "$STAGE/art.zip")
cp "$STAGE/Terrain.xml" $H/client-bins/Data/Data/Terrain.xml
find "$REPO" -name 'Terrain-External.xml' -path '*Data*' | head -1 | xargs -I{} cp {} $H/client-bins/Data/Data/Terrain-External.xml
cp "$STAGE/"*piece-book-draft.json "$H/out/2026-10-29 piece-book-draft.json"
[ -e $H/jkachhad/stormhalter ] || ln -s "$REPO" $H/jkachhad/stormhalter
[ -d $H/lok-studio ] || git clone -q https://github.com/HaDeZs530/LOK-Studio $H/lok-studio
pip install --break-system-packages -q pillow >/dev/null 2>&1 || true
python3 -I $H/pilot/design_build.py "$REPO/tools/worldforge-ai-gen/pilot/examples/testD/design.json" /tmp/wfai-selftest | head -1
echo "setup done; self-test above should say: pass"
