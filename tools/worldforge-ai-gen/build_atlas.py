"""Build the sprite atlas + index for the WorldForge viewer page."""
import json, math, sys
from PIL import Image
ART='/home/claude/art'
idx=json.load(open('/home/claude/terrain-index-merged.json'))
legend=json.load(open('/home/claude/out/components-legend.json'))
layers=[]  # (tid, sprite)
for tid,e in idx.items():
    for s in e['sprites']: layers.append((int(tid),s))
cols=math.ceil(math.sqrt(len(layers))); cell=100
atlas=Image.new('RGBA',(cols*cell, math.ceil(len(layers)/cols)*cell),(0,0,0,0))
sheets={}; out={}
for i,(tid,s) in enumerate(layers):
    sh=sheets.get(s['texture'])
    if sh is None: sh=sheets[s['texture']]=Image.open(f"{ART}/{s['texture']}.png").convert('RGBA')
    x,y,w,h=s['source']; im=sh.crop((x,y,x+w,y+h))
    r=s['resolution']
    if r!=1: im=im.resize((w//r,h//r),Image.NEAREST)
    # client treats pure magenta as transparent for built art
    px=im.load()
    for yy in range(im.height):
        for xx in range(im.width):
            p=px[xx,yy]
            if p[0]==255 and p[1]==0 and p[2]==255: px[xx,yy]=(0,0,0,0)
    ax,ay=(i%cols)*cell,(i//cols)*cell
    atlas.paste(im,(ax,ay))
    out.setdefault(tid,[]).append({'ax':ax,'ay':ay,'w':im.width,'h':im.height,'o':s['order'],'off':s.get('offset',[0,0])})
atlas.save('atlas.webp',lossless=True,quality=100)
atlas.save('atlas.png',optimize=True)
# names: id -> palette name (first seen), keyed by the prop that references it
names={}
for e in legend:
    for k,v in e['props'].items():
        try: v=int(v)
        except: continue
        if v and k in('ground','wall','static','tree','obstruction','closedId','counter','altar','staircase','ruins','egress','shaft','rope','sky','teleporterId') and v not in names:
            names[v]=e['name']
json.dump({'cell':cell,'cols':cols,'sprites':out,'names':names},open('atlas-index.json','w'),separators=(',',':'))
import os; print(len(layers),'layers',atlas.size, 'webp',os.path.getsize('atlas.webp')//1024,'KB png',os.path.getsize('atlas.png')//1024,'KB', 'index',os.path.getsize('atlas-index.json')//1024,'KB')
