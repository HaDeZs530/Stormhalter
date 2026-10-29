# Piece Book — second-opinion pass

You are describing game sprites for a map-building tool for Stormhalter (a Legends of Kesmai
revival, a fantasy world). Each contact sheet image has 48 cards (8 across, 6 down). Each card
shows the sprite on a grey box, then "#n id N", the palette name, and "Type · Category". Tall
pieces lean up and to the left; that is how this art works, not an error.

For EVERY card on the sheet I give you, return one JSON object, in card order, as a JSON list:

{
 "n": 480,
 "id": 1264,
 "look": "one sentence, under 25 words: shape, colour, material, orientation",
 "kind": "what the thing is, 2-6 words",
 "setting": ["1-2 from: temple, crypt, dungeon, cave, mine, castle, palace, town, village, tavern, home, camp, forest, swamp, jungle, desert, coast, snow, lava, sewer, garden, farm, wizard, ship, ruins"],
 "tone": ["1-2 from: blessed, cursed, undead, corrupted, grand, overgrown, hot, cold, wet, bright, dark"],
 "size": "tile | small | medium | large | tall",
 "placement": "one of: floor-fill | wall-H | wall-V | wall-corner | wall-mass | door-H | door-V | against-wall | corner | free-standing | scatter | cluster | path | edge | overlay | stairs | portal | trap | unknown",
 "scene_use": "one sentence on where a level designer would use it and what feeling it adds",
 "notes": "name disagrees with picture, looks identical to another card, unreadable, etc."
}

Rules: describe only what is visible; trust the picture over the palette name and say so in
notes when they disagree. A wall marked (H) runs left-right, (V) runs up-down, (C) is a corner
post. If a card is blank, say so and set kind to "unknown". Use only tags from the lists; leave
a list empty rather than inventing a tag. Output only the JSON list, nothing else.

Save each answer as sheet_NN.chatgpt.json (NN = the sheet number in the image filename) and drop
the files in Dropbox\WorldForge AI Gen\in\.
