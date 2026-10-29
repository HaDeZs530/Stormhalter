# How we work — WorldForge AI Gen (2026-10-29)

Three of us: Tony decides, ChatGPT designs and reviews, Claude builds and checks. Everything moves through
numbered pass folders in Dropbox, and every handoff ends with a written summary so all three of us can see
what happened and adjust.

## Why we work this way
Goal: ChatGPT designs real game areas (streets, buildings, interiors, vegetation, decoration) from Tony's
concept, dimensions, setting/tone and gameplay needs; Claude turns the design into exact WorldForge regions
and proves them with renders and checks; Tony fine-tunes in WorldForge. The three product goals: (1) generate
fully decorated sections up to ~50x50 tiles from a brief; (2) decorate existing areas by theme without
breaking walls; (3) check-and-fix passes for hand-made maps. The piece book is the shared model of every
piece (what it is, how it is placed, what feeling it adds); everything either AI decides about a piece
traces back to it.

Why passes: a numbered folder per pass means nothing is overwritten, before/after is always two folders, and
Tony never has to read file names. Why pins and coordinates: vision is good at composition ("the altar sits
on the axis, the route is clear") and bad at identifying small sprites, so pieces are always named by id and
located by tile, and the picture is for judging the whole. Why the validator is unforgiving: WorldForge
crashes or misdraws on bad XML (a wall without destroyed/ruins ids, unknown ids, illegal combinations), so
mechanical failures are facts, not opinions. Why the summary: three parties, two of whom never talk directly,
need one written record of what happened and what is owed.

## Pushback and changing the rules (both AIs, both directions)
- Before doing a pass: if the prompt conflicts with the goal, the rules or the piece book, write
  `PUSHBACK:` with the reason and the alternative, stop, and wait for Tony. Do not silently do a different
  thing, and do not do the conflicting thing.
- After a pass: if you want the other AI to work differently (file format, what the diag image shows, how
  plans are structured, anything), write `CHANGE HOW WE WORK:` in the summary with the concrete change and
  why. Tony approves or rejects. On approval Claude updates `_HOW WE WORK.md`, the ChatGPT instructions and
  the Claude skill together, so the three copies never drift.

## Roles
- Tony: picks what gets built, scores renders, imports into WorldForge, carries messages between the two AIs.
- ChatGPT: reads `to-GPT\`, writes `from-GPT\`. Designs rooms, reviews pieces and scenes, proposes revisions.
- Claude: reads `from-GPT\`, writes `to-GPT\`. Builds region XML, renders, validates, exports, keeps INDEX.md.

## Folder
```
WorldForge AI Gen\
  INDEX.md                 the only file Tony needs to read: every pass, its status, open tasks per person
  _HOW WE WORK.md          this file
  reference\               art, corpus, data, docs, tool, renders, forge-viewer. Never written during a pass.
  piece-book\              the Piece Book, draft JSON, DECOR_LEGEND.md, stats. The living result of all passes.
  passes\
    pass-NN YYYY-MM-DD name\
      _PASS.md             purpose, status, the prompt with the save path filled in, and the running log
      to-GPT\              what ChatGPT reads (Claude writes here)
      from-GPT\            what ChatGPT produces (ChatGPT writes here)
```
A pass folder is never reused. A redo or the next round is a new number. Nothing is moved or renamed
without saying first exactly where it goes.

## A pass, start to finish
1. Claude opens pass-NN: writes `to-GPT\`, `_PASS.md` (purpose, prompt, save path), updates `INDEX.md`,
   and tells Tony "pass NN is ready" with a copy/paste box of the prompt.
2. Tony pastes the prompt into ChatGPT.
3. ChatGPT opens every PNG with vision (never through code), does the work, saves its files in `from-GPT\`
   with the names the prompt gives, and ALWAYS also saves `from-GPT\_SUMMARY.md` (format below).
   Its chat reply is the same summary, so Tony can paste it to Claude.
4. Tony tells Claude "pass NN is in" (pasting ChatGPT's summary is enough).
5. Claude reads `from-GPT\`, does the work, writes its own summary into `_PASS.md`, marks the pass in
   `INDEX.md`, and opens the next pass. Claude's reply to Tony is also a summary in the same format.

## The summary (every handoff, both AIs, same shape)
```
PASS NN — <name> — <who> — <date>
DID:        what was produced, file names
COULD NOT:  what was skipped or failed, and why
FOUND:      anything learned that changes the book, the rules, or the plan
TASKS:
  Tony:     ...
  Claude:   ...
  ChatGPT:  ...
PUSHBACK:            (only before a pass, when the prompt conflicts with goal/rules; then stop)
CHANGE HOW WE WORK:  (optional: a concrete change you want from the other side, and why)
```
Tasks named here are the task list. Claude copies open tasks into `INDEX.md`; nobody keeps a separate list.

## What ChatGPT may write into a plan
- piece ids only from that pass's `pieces.json`, always with the component type
- tile x,y read from the diag image; the tile is the anchor; no pixel offsets, rotation, scaling, z-order
- no tint, no new floors, no wall or door changes unless the pass says so
- protected walls and doors are never removed or altered; wall-mounted pieces may go on wall tiles when the
  piece's placement class allows it
- stable ids on every placement (p01, p02 ...) and on every group, so revisions can say "move p07"
- a revision is a patch against the previous plan, never a rewrite

## What Claude guarantees
- every render is made from the region XML in the same folder; WorldForge imports that XML unchanged
- every pass ships `clean.png` (no labels) and `diag.png` (grid, coordinates, pins, routes, flags) at native
  resolution, plus `validation.json`; crops at 2x on request
- validation failures are fixed by changing the plan, never by overriding the check
- Tony's hand-placed components survive every pass
- every file Claude produces carries its creation date

## Tony's rules for Claude
- plain language; a visual for anything subtle; no code in explanations
- after any tool change, a TLDR of how to test it
- discuss before building anything structural (folders, skills, workflows)
- never touch or view the HaDeZs Test* folders
- never make Tony sift through hundreds of file names: INDEX.md is the view
