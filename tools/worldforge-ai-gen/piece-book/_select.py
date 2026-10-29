import json,collections
SCR='/tmp/claude-0/-home-claude/eefa0aad-b4bd-534f-9fe5-a075e74d566e/scratchpad'
W=json.load(open(SCR+'/windows_c.json'))
def feats(w):
    names=' '.join((n or '').lower() for t,i,n,c in w['ids'])
    cnt=collections.Counter()
    for t,i,n,c in w['ids']: cnt[t]+=c
    return dict(altar=cnt['AltarComponent']>0, counter=cnt['CounterComponent']>0,
        bed=any(k in names for k in ['bed','shelf','shelves','bookcase','table','chair','barrel','keg','stool','bench','cask']),
        trees=cnt['TreeComponent'], obst=cnt['ObstructionComponent'], doors=cnt['DoorComponent'],
        wallc=sum(c for i,n,c in w['walls']), ntypes=len(w['types']))
for w in W:
    w['f']=feats(w); f=w['f']
    w['score']=w['distinct']*3+min(w['n'],30)+f['ntypes']*2
chosen=[]
def ok(w):
    for c in chosen:
        if c['seg']==w['seg'] and c['region']==w['region'] and max(abs(c['x0']-w['x0']),abs(c['y0']-w['y0']))<20: return False
    return True
def pick(label,pred,k,prefer=None):
    cands=[w for w in W if pred(w) and ok(w) and w not in chosen]
    cands.sort(key=lambda w:(-(prefer(w) if prefer else 0),-w['score']))
    got=0
    for w in cands:
        if got>=k: break
        if ok(w): w['why']=label; chosen.append(w); got+=1
    return got
f=lambda w:w['f']
FORCED=[('Praetoseba',1,10,0,'Egyptian temple interior with altars'),('Underkingdom',14,-1,0,'crypt: sarcophagi rows'),
 ('Leng',18,22,2,'dungeon: doors, skeletons, blood'),('Axe Glacier',6,20,10,'snow/ice forest'),('Underkingdom',8,-1,-3,'temple courtyard with altars'),('Blackburrow',1,-2,-35,'tavern/home: counters, bookshelves, lockers, braziers'),('Leng',1,10,12,'tavern/home: counters, throne, altar, doors')]
for seg,rid,x0,y0,why in FORCED:
    w=[w for w in W if w['seg']==seg and w['region']==rid and w['x0']==x0 and w['y0']==y0][0]; w['why']=why; chosen.append(w)
print('altar/counter interior',pick('interior with altar/counter',lambda w:(f(w)['altar'] or f(w)['counter']) and f(w)['wallc']>=40 and w['cls'] not in('town','pagoda/town'),3,
     prefer=lambda w:(f(w)['altar']+f(w)['counter'])*10 - (w['seg']=='Blackburrow' and w['region']==1)*5))
print('tavern/home',pick('tavern/home: counters, beds, shelves',lambda w:f(w)['counter'] and f(w)['bed'] and f(w)['doors']>=2,0,prefer=lambda w:-f(w)['trees']))
print('crypt',pick('crypt/undead',lambda w:w['cls']=='crypt/undead',2,prefer=lambda w:w['seg']!='Blackburrow'))
print('mines',pick('mines',lambda w:w['cls']=='mines',2))
print('town street',pick('town street/market',lambda w:w['cls'] in('town','pagoda/town','town street') and f(w)['doors']>=3,2,prefer=lambda w:w['cls']=='pagoda/town'))
print('forest',pick('forest edge: trees + obstructions',lambda w:w['cls'] in('forest/grass','jungle') and f(w)['trees']>=5 and f(w)['obst']>=3,3,prefer=lambda w:(w['seg']!='Blackburrow')*2+(w['seg']=='Oakvael' and w['region']==236)))
print('swamp',pick('swamp',lambda w:w['cls']=='swamp',2))
print('coast',pick('coast/water',lambda w:w['cls']=='water/coast',2,prefer=lambda w:w['seg']=='Oakvael'))
print('egypt',pick('Egyptian / Praetoseba',lambda w:w['cls']=='Egyptian',2,prefer=lambda w:w['seg']=='Praetoseba'))
print('castle',pick('castle/palace',lambda w:w['cls']=='castle/palace',1))
# fill: coverage of (seg,cls) pairs not yet chosen
have=set((w['seg'],w['cls']) for w in chosen)
rest=sorted([w for w in W if w not in chosen],key=lambda w:-w['score'])
for w in rest:
    if len(chosen)>=35: break
    if (w['seg'],w['cls']) in have or not ok(w): continue
    w['why']=f"coverage: {w['seg']} {w['cls']}"; chosen.append(w); have.add((w['seg'],w['cls']))
for w in rest:
    if len(chosen)>=35: break
    if w in chosen or not ok(w): continue
    w['why']=f"high variety ({w['distinct']} ids)"; chosen.append(w)
for i,w in enumerate(chosen,1):
    print(f"{i:2} {w['seg'][:7]:7} r{w['region']:<3} {w['rname'][:20]:20} ({w['x0']:4},{w['y0']:4}) n={w['n']:3} d={w['distinct']:2} {w['cls']:14} {w['why']}")
json.dump(chosen,open(SCR+'/chosen.json','w'))
print(collections.Counter(w['seg'] for w in chosen)); print(collections.Counter(w['cls'] for w in chosen))
