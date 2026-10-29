import json,collections,re
SCR='/tmp/claude-0/-home-claude/eefa0aad-b4bd-534f-9fe5-a075e74d566e/scratchpad'
def classify(w):
    f=' '.join(n.lower() for i,n,c in w['floors'][:2]); wl=' '.join(n.lower() for i,n,c in w['walls'][:2])
    f1=w['floors'][0][1].lower() if w['floors'] else ''; w1=w['walls'][0][1].lower() if w['walls'] else ''
    wallc=sum(c for i,n,c in w['walls']); floorc=sum(c for i,n,c in w['floors'])
    ids=' '.join((n or '').lower() for t,i,n,c in w['ids'])
    types=set(w['types'])
    if 'egypt' in wl or 'egypt' in f: return 'Egyptian'
    if 'temple' in wl or ('AltarComponent' in types and ('marble' in f or 'temple' in f)): return 'temple'
    if 'undead' in wl or 'skull' in f1 or 'mausoleum' in w['rname'].lower() or 'crypt' in w['rname'].lower() or 'undead' in w['rname'].lower(): return 'crypt/undead'
    if 'palace' in wl or 'mythril' in wl or 'blue marble' in wl: return 'castle/palace'
    if 'pagoda' in wl or 'shoji' in wl: return 'pagoda/town'
    if 'mine' in wl: return 'mines'
    if 'town' in wl or ('hardwood' in f or 'wood (' in f) and wallc>20: return 'town'
    if 'dungeon' in wl: return 'dungeon'
    if 'sandstone' in wl or 'sandstone' in f1: return 'sandstone'
    if 'lava' in f or 'ash' in f1 or 'burnt' in f1: return 'lava/ash'
    if 'swamp' in wl or 'swamp' in f or 'tidal' in f1 or 'reeds' in f1: return 'swamp'
    if 'snow' in f1 or 'ice' in f1: return 'snow/ice'
    if 'water' in f1 or 'waves' in f or 'shoreline' in f or ('water' in f and 'sand' in f): return 'water/coast'
    if 'cave' in wl or 'cave' in f1 or 'stalagmite' in wl or 'solid rock' in wl or 'bedrock' in f1 or 'granite' in wl: return 'cave'
    if 'jungle' in f or 'bamboo' in f1: return 'jungle'
    if 'forest' in f1 or 'grass' in f1 or 'thicket' in wl or 'alfalfa' in f1 or 'TreeComponent' in types: return 'forest/grass'
    if 'cobble' in f1 or 'road' in f1 or 'flagstone' in f1 or 'gravel' in f1 or 'path' in f1: return 'town street'
    if 'dirt' in wl or 'logs' in wl: return 'dungeon/earth'
    return 'other'
if __name__=='__main__':
    W=json.load(open(SCR+'/windows.json'))
    for w in W: w['cls']=classify(w)
    json.dump(W,open(SCR+'/windows_c.json','w'))
    print(collections.Counter(w['cls'] for w in W))
    print(collections.Counter((w['seg'],w['cls']) for w in W))
