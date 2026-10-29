import json,collections,os,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
SCR='/tmp/claude-0/-home-claude/eefa0aad-b4bd-534f-9fe5-a075e74d566e/scratchpad'
OUT='/home/claude/scenes'
FILES={'Blackburrow':'/home/claude/corpus/cleaned_Blackburrow.mapproj','Leng':'/home/claude/corpus/cleaned_Leng.mapproj',
 'Axe Glacier':'/home/claude/corpus/cleaned_axe_glacier.mapproj','Oakvael':'/home/claude/corpus/cleaned_oakvael.mapproj',
 'Underkingdom':'/home/claude/corpus/cleaned_underkingdom.mapproj','Praetoseba':'/home/claude/jkachhad/stormhalter/Segments/Praetoseba.mapproj'}
DECO={'StaticComponent':'static','LockersComponent':'static','TrashComponent':'static','TreeComponent':'tree',
 'ObstructionComponent':'obstruction','AltarComponent':'altar','CounterComponent':'counter','DoorComponent':'closedId'}
FLOORT={'FloorComponent':'ground','WaterComponent':'ground','IceComponent':'ground','PoisonedWaterComponent':'ground'}
U=55; MARGIN=2; CAP=30
book=json.load(open('/home/claude/out/2026-10-29 piece-book-draft.json'))
byid=collections.defaultdict(list)
for e in book: byid[e['id']].append(e)
floor_only=set(i for i,es in byid.items() if all(e['category']=='Floors' or e['type'] in FLOORT for e in es))
def entry(i,typ):
    es=byid.get(i,[])
    for e in es:
        if e['type']==typ: return e
    for e in es:
        if e['type']!='(no palette entry)': return e
    return es[0] if es else None
def name(i,typ):
    e=entry(i,typ); return ((e.get('name') or e.get('kind')) if e else None) or f'id{i}'
F_BIG=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22)
F_PIN=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',15)
chosen=json.load(open(SCR+'/chosen.json'))
regions={}
for w in chosen:
    k=(w['seg'],w['region'])
    if k in regions: continue
    root=ET.parse(FILES[w['seg']]).getroot()
    r=[r for r in root.iter('region') if int(r.findtext('id'))==w['region']][0]
    tiles=r.findall('tile'); floors={}; walls={}; decos=collections.defaultdict(list)
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
    regions[k]=dict(minx=min(xs),miny=min(ys),floors=floors,walls=walls,decos=decos,
        img=Image.open(f"{SCR}/renders/{w['seg'].replace(' ','_')}_{w['region']}.png").convert('RGBA'))
index=[]
for n,w in enumerate(chosen,1):
    R=regions[(w['seg'],w['region'])]; x0,y0,x1,y1=w['x0'],w['y0'],w['x1'],w['y1']
    # decorations in window
    items=[]
    for (x,y),lst in R['decos'].items():
        if x0<=x<=x1 and y0<=y<=y1:
            for typ,i in lst: items.append((x,y,typ,i))
    # cap: one per distinct (typ,id) first, then round-robin
    groups=collections.defaultdict(list)
    for it in sorted(items,key=lambda z:(z[1],z[0])): groups[(it[2],it[3])].append(it)
    sel=[]; 
    if len(items)<=CAP: sel=items
    else:
        qs={k:list(v) for k,v in groups.items()}
        order=sorted(qs,key=lambda k:len(groups[k]))  # rare ids first
        for percap in (1,3,5,10**6):
            while len(sel)<CAP and any(len(qs[k])>0 and (len(groups[k])-len(qs[k]))<percap for k in qs):
                for k in order:
                    if qs[k] and (len(groups[k])-len(qs[k]))<percap and len(sel)<CAP: sel.append(qs[k].pop(0))
    sel.sort(key=lambda z:(z[1],z[0],z[2],z[3]))
    # crop
    cx0=(x0-MARGIN-R['minx']+1)*U; cy0=(y0-MARGIN-R['miny']+1)*U; cx1=(x1+MARGIN-R['minx']+2)*U; cy1=(y1+MARGIN-R['miny']+2)*U
    im=R['img']; cx0c,cy0c,cx1c,cy1c=max(0,cx0),max(0,cy0),min(im.width,cx1),min(im.height,cy1)
    crop=im.crop((cx0c,cy0c,cx1c,cy1c))
    ox,oy=cx0c-cx0,cy0c-cy0  # offset if clipped
    HB=44
    page=Image.new('RGBA',(crop.width,crop.height+HB),(0,0,0,255)); page.paste(crop,(0,HB))
    d=ImageDraw.Draw(page,'RGBA')
    # grid
    for gx in range(0,crop.width+1,U): d.line([(gx,HB),(gx,HB+crop.height)],fill=(255,255,255,40),width=1)
    for gy in range(0,crop.height+1,U): d.line([(0,HB+gy),(crop.width,HB+gy)],fill=(255,255,255,40),width=1)
    # window outline
    wx=(x0-MARGIN-R['minx']+1)*U-cx0c+MARGIN*U; wy=(y0-MARGIN-R['miny']+1)*U-cy0c+MARGIN*U
    d.rectangle([wx,HB+wy,wx+(x1-x0+1)*U,HB+wy+(y1-y0+1)*U],outline=(255,255,0,150),width=2)
    # pins
    pins=[]; stack=collections.Counter()
    for k,(x,y,typ,i) in enumerate(sel,1):
        px=(x-R['minx']+1)*U-cx0c; py=(y-R['miny']+1)*U-cy0c+HB
        s=stack[(x,y)]; stack[(x,y)]+=1
        cxp=px+U//2+(s%2)*16-8*(s>0); cyp=py+U//2+(s//2)*16-(s>0)*8
        if s==1: cxp,cyp=px+U//2+14,py+U//2+14
        if s==2: cxp,cyp=px+U//2-14,py+U//2+14
        if s>=3: cxp,cyp=px+U//2+14*((s+1)%3-1),py+U//2-14
        r=13
        d.ellipse([cxp-r-2,cyp-r-2,cxp+r+2,cyp+r+2],fill=(0,0,0,255))
        d.ellipse([cxp-r,cyp-r,cxp+r,cyp+r],fill=(255,230,0,255))
        d.text((cxp,cyp),str(k),fill=(0,0,0,255),font=F_PIN,anchor='mm')
        e=entry(i,typ) or {}
        pins.append({'pin':k,'x':x,'y':y,'id':i,'type':typ,'name':name(i,typ),
            'book':{kk:e.get(kk) for kk in ['look','kind','placement','setting','tone']} if e else {}})
    # header
    d.rectangle([0,0,page.width,HB],fill=(255,220,0,255))
    hdr=f"SCENE {n:02d} — {w['seg']} region {w['region']} '{w['rname']}' tiles {x0}..{x1}, {y0}..{y1} — {w['cls']}"
    fnt=F_BIG
    while d.textlength(hdr,font=fnt)>page.width-16 and fnt.size>11: fnt=ImageFont.truetype(fnt.path,fnt.size-1)
    d.text((8,HB//2),hdr,fill=(0,0,0,255),font=fnt,anchor='lm')
    page.convert('RGB').save(f"{OUT}/scene_{n:02d}.png")
    fl=collections.Counter(v for (x,y),v in R['floors'].items() if x0<=x<=x1 and y0<=y<=y1)
    wl=collections.Counter(v for (x,y),v in R['walls'].items() if x0<=x<=x1 and y0<=y<=y1)
    key={'scene':n,'segment':w['seg'],'region':w['region'],'name':w['rname'],'window':[x0,y0,x1,y1],'class':w['cls'],
        'floors':[{'id':i,'name':name(i,'FloorComponent'),'count':c} for i,c in fl.most_common()],
        'walls':[{'id':i,'name':name(i,'WallComponent'),'count':c} for i,c in wl.most_common()],
        'decorations_in_window':len(items),'pins':pins}
    json.dump(key,open(f"{OUT}/scene_{n:02d}.key.json",'w'),indent=1)
    index.append((n,w['seg'],w['region'],w['rname'],w['cls'],len(pins),len(items),w['why'],page.size))
    print(n,w['seg'],w['region'],w['cls'],'pins',len(pins),'of',len(items),page.size)
with open(f"{OUT}/INDEX.md",'w') as f:
    f.write("# Scene kit index — 2026-10-29\n\nRendered 20x20-tile windows (plus 2-tile margin) from the developers' own Stormhalter regions. Pins mark decorated tiles; each scene has a matching `scene_NN.key.json`.\n\n")
    f.write("| Scene | Segment | Region | Class | Pins (of decos in window) | Why chosen |\n|---|---|---|---|---|---|\n")
    for n,seg,rid,rn,cls,np_,ni,why,sz in index:
        f.write(f"| {n:02d} | {seg} | {rid} '{rn}' | {cls} | {np_} ({ni}) | {why} |\n")
