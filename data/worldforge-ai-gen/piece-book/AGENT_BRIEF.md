# Piece book drafting brief

You are writing first-draft descriptions of game sprites for a map-building tool for the Stormhalter server (a Legends of Kesmai revival; isometric-looking 2D tiles, 100x100 px sprites drawn on a 55 px grid, so tall pieces lean up and to the left). The map builder (Tony) will correct every description; your job is to describe what you SEE accurately so his corrections are small.

Input: contact sheets at /home/claude/piecebook/sheets/sheet_NN.png (8 x 6 cards, each card: the sprite on a grey box, then "#n id N", the palette name, and "Type · Category"). The piece list with ids/names/types/props is /home/claude/piecebook/pieces.json (field "n" is the card number). Read each sheet image with the Read tool, then write one JSON object per card.

Output: /home/claude/piecebook/drafts/sheet_NN.json — a JSON list, one object per card on that sheet, in card order:

{
 "n": 480,
 "id": 1264,
 "look": "one sentence on what the sprite looks like: shape, colour, material, orientation (lean, which edge it sits on)",
 "kind": "what the thing is, 2-6 words (e.g. 'broken wall segment, horizontal run', 'floor tile', 'stone altar', 'hanging lantern')",
 "mood": ["2-4 tags from: sacred, ruined, cosy, cold, hot, wet, dark, bright, wild, tended, royal, poor, military, arcane, dead, festive, industrial, natural, urban, cave, desert, snow, swamp, jungle, sea"],
 "size": "tile | small | medium | large | tall",
 "placement": "one of: floor-fill | wall-H | wall-V | wall-corner | wall-mass | door-H | door-V | against-wall | corner | free-standing | scatter | cluster | path | edge | overlay | stairs | portal | trap | unknown",
 "pairs_with": ["optional: names or ids of pieces this belongs with, e.g. the matching (V) piece, the ruin of this wall"],
 "notes": "anything useful: looks identical to id X, is a colour variant, is a 2-tile piece, has a frame animation, is a placeholder, is unreadable at this size"
}

Rules:
- Describe only what is visible; if a card is blank or a tiny mark, say so in "look" and set kind to "unknown".
- Names in the palette can lie (e.g. 'Tile' is a magenta checkerboard, '(PH)' is a red placeholder). Trust the picture over the name; mention the disagreement in notes.
- Wall pieces: say which way they run. In this art an (H) piece is a wall that runs left-right (it draws along the south edge of its tile), a (V) piece runs up-down (east edge), a (C) is the corner post. Ruins are broken versions of walls, same orientation rule.
- Floors: say the pattern and colour; note if it tiles seamlessly or has a visible border.
- Doors: state (H)/(V), material, whether it looks open, closed, secret (looks like wall), destroyed.
- Decorations: say whether it would read as something that sits against a wall (shelves, banners, wall doodads), in a corner, free in the room, or scattered outdoors.
- Keep "look" under 25 words. No speculation about lore.
- Do not modify pieces.json or the sheet images. Write only your draft files.
