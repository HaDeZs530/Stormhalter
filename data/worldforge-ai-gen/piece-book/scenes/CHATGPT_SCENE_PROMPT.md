# Scene pass — how decorations are used in real built worlds

You are reading rendered scenes from the game developers' own Stormhalter maps (Legends of Kesmai revival; isometric-looking 2D tiles, 55 px per tile, tall pieces lean up and to the left). Each image has a yellow "SCENE NN" band at the top and numbered pins on the decorated tiles. The key file for the scene lists every pin: its tile coordinates, id, palette name, and what our piece book currently says about that piece.

For each scene return ONE JSON object:

{
 "scene": NN,
 "purpose": "what this room or area is and what tells you so (one or two sentences)",
 "setting": ["1-2 from: temple, crypt, dungeon, cave, mine, castle, palace, town, village, tavern, home, camp, forest, swamp, jungle, desert, coast, snow, lava, sewer, garden, farm, wizard, ship, ruins"],
 "tone": ["1-2 from: blessed, cursed, undead, corrupted, grand, overgrown, hot, cold, wet, bright, dark"],
 "composition": "how the space is organised: focal point, paths, where the eye goes, what is kept clear",
 "pins": [
  {"pin": 1, "id": 163,
   "role": "what this piece does in this scene (a few words)",
   "rule": "the placement rule you would write from this evidence, in terms of walls, doors, corners, other pieces and spacing — e.g. 'against the north wall, centred on the room', 'flanks a doorway in a pair', 'rows two tiles apart facing the altar', 'scattered singles in dark corners, never on paths'",
   "correct": {"placement": "only if the piece book's placement is wrong here, one of: floor-fill | wall-H | wall-V | wall-corner | wall-mass | door-H | door-V | against-wall | corner | free-standing | scatter | cluster | path | edge | overlay | stairs | portal | trap", "setting": [], "tone": [], "look": "only if the picture contradicts the piece book's look"}
  }
 ],
 "patterns": ["2-5 reusable patterns you see in this scene that a generator could copy, each one sentence"]
}

Rules: describe what is visible; use only tags from the lists; leave "correct" empty ({}) when the piece book is right; do not invent lore. Output only the JSON, starting with the line SCENE NN. I will save the file myself as scene_NN.chatgpt.json.
