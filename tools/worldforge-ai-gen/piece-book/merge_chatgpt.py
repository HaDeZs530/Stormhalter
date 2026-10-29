import json,glob,sys
P=sys.argv[1] if len(sys.argv)>1 else '/home/claude/out/2026-10-29 piece-book-draft.json'
pieces=json.load(open(P)); byn={p['n']:p for p in pieces}; n=0; bad=[]
for f in sorted(glob.glob('/home/claude/piecebook/chatgpt/*.json')):
    for e in json.load(open(f)):
        p=byn.get(e.get('n'))
        if not p or p['id']!=e.get('id'): bad.append((f,e.get('n'),e.get('id'))); continue
        p['gpt']={k:e[k] for k in ('look','kind','setting','tone','size','placement','scene_use','notes') if k in e}
        if not p.get('scene_use') and e.get('scene_use'): p['scene_use']=e['scene_use']
        n+=1
json.dump(pieces,open(P,'w'),indent=0); print('merged',n,'chatgpt entries; mismatches:',bad[:5])
