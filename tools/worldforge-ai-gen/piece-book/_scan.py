import json, sys, xml.etree.ElementTree as ET, collections
SCR='/tmp/claude-0/-home-claude/eefa0aad-b4bd-534f-9fe5-a075e74d566e/scratchpad'
FILES={'Blackburrow':'/home/claude/corpus/cleaned_Blackburrow.mapproj','Leng':'/home/claude/corpus/cleaned_Leng.mapproj',
 'Axe Glacier':'/home/claude/corpus/cleaned_axe_glacier.mapproj','Oakvael':'/home/claude/corpus/cleaned_oakvael.mapproj',
 'Underkingdom':'/home/claude/corpus/cleaned_underkingdom.mapproj','Praetoseba':'/home/claude/jkachhad/stormhalter/Segments/Praetoseba.mapproj'}
DECO={'StaticComponent':'static','LockersComponent':'static','TrashComponent':'static','TreeComponent':'tree',
 'ObstructionComponent':'obstruction','AltarComponent':'altar','CounterComponent':'counter','DoorComponent':'closedId'}
FLOORT={'FloorComponent':'ground','WaterComponent':'ground','IceComponent':'ground','PoisonedWaterComponent':'ground'}
book=json.load(open('/home/claude/out/2026-10-29 piece-book-draft.json'))
byid=collections.defaultdict(list)
for e in book: byid[e['id']].append(e)
floor_only=set(i for i,es in byid.items() if all(e['category']=='Floors' or e['type'] in FLOORT for e in es))
def name(i,typ=None):
    es=byid.get(i,[])
    if not es: return f'id{i}'
    for e in es:
        if e['type']==typ: return e['name']
    return es[0]['name']
out=[]
for seg,path in FILES.items():
    root=ET.parse(path).getroot()
    for r in root.iter('region'):
        rid=int(r.findtext('id')); rname=r.findtext('name') or ''
        tiles=r.findall('tile')
        if not tiles: continue
        floors={}; walls={}; decos=collections.defaultdict(list)
        for t in tiles:
            x,y=int(t.get('x')),int(t.get('y'))
            for c in t.findall('component'):
                typ=c.get('type')
                if typ in FLOORT:
                    v=c.findtext(FLOORT[typ]); 
                    if v: floors[(x,y)]=int(v)
                elif typ=='WallComponent':
                    v=c.findtext('wall'); 
                    if v: walls[(x,y)]=int(v)
                elif typ in DECO:
                    v=c.findtext(DECO[typ])
                    if v is None: continue
                    i=int(v)
                    if typ=='StaticComponent' and i in floor_only: continue
                    decos[(x,y)].append((typ,i))
        xs=[int(t.get('x')) for t in tiles]; ys=[int(t.get('y')) for t in tiles]
        minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
        wins=[]
        for wy in range(miny,max(miny,maxy-19)+1,10):
            for wx in range(minx,max(minx,maxx-19)+1,10):
                ids=collections.Counter(); n=0; fl=collections.Counter(); wl=collections.Counter(); tcount=0
                for (x,y),lst in decos.items():
                    if wx<=x<wx+20 and wy<=y<wy+20:
                        for typ,i in lst: ids[(typ,i)]+=1; n+=1
                if n<8 or len(ids)<4: continue
                for (x,y),i in floors.items():
                    if wx<=x<wx+20 and wy<=y<wy+20: fl[i]+=1
                for (x,y),i in walls.items():
                    if wx<=x<wx+20 and wy<=y<wy+20: wl[i]+=1
                wins.append(dict(seg=seg,region=rid,rname=rname,x0=wx,y0=wy,x1=min(wx+19,maxx),y1=min(wy+19,maxy),
                    n=n,distinct=len(ids),types=sorted(set(t for t,_ in ids)),
                    floors=[(i,name(i,'FloorComponent'),c) for i,c in fl.most_common(4)],
                    walls=[(i,name(i,'WallComponent'),c) for i,c in wl.most_common(4)],
                    ids=[(t,i,name(i,t),c) for (t,i),c in ids.most_common(40)],
                    bbox=[minx,miny,maxx,maxy]))
        out.extend(wins)
        print(seg,rid,repr(rname),'tiles',len(tiles),'decotiles',len(decos),'wins',len(wins),file=sys.stderr)
json.dump(out,open(SCR+'/windows.json','w'))
print(len(out))
