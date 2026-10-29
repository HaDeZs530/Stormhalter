"""Prototype: render a WorldForge region exactly as the editor does.
55px grid; each sprite drawn at (cell-45, cell-45) + offset, scaled 1/resolution,
tinted by component color, layers stable-sorted by sprite order."""
import sys, xml.etree.ElementTree as ET
from PIL import Image

ART='/home/claude/art'   # decoded sprite root (WorldForge AI Gen\art)
TERR=['/home/claude/client-bins/Data/Data/Terrain.xml','/home/claude/client-bins/Data/Data/Terrain-External.xml']
UNIT=55

def vec(s): return [int(float(v)) for v in s.strip('()').split(',')]

class Sprites:
    def __init__(s):
        s.terrain={}; s.cache={}
        for f in TERR:
            for t in ET.parse(f).getroot().iter('terrain'):
                layers=[]
                for sp in t.iter('sprite'):
                    layers.append(dict(tex=sp.findtext('texture').replace('\\','/'),
                        src=vec(sp.findtext('source')), res=int(sp.get('resolution',1)),
                        order=int(sp.get('order',0)),
                        off=vec(sp.findtext('offset')) if sp.find('offset') is not None else [0,0]))
                s.terrain[int(t.get('id'))]=layers   # external overrides core
    def img(s,L):
        k=(L['tex'],tuple(L['src']),L['res'])
        if k not in s.cache:
            sheet=Image.open(f"{ART}/{L['tex']}.png").convert('RGBA')
            x,y,w,h=L['src']; im=sheet.crop((x,y,x+w,y+h))
            if L['res']!=1: im=im.resize((w//L['res'],h//L['res']),Image.NEAREST)
            s.cache[k]=im
        return s.cache[k]

def tint(im,c):
    if c==(255,255,255,255): return im
    r,g,b,a=im.split()
    r=r.point(lambda v:v*c[0]//255); g=g.point(lambda v:v*c[1]//255); b=b.point(lambda v:v*c[2]//255); a=a.point(lambda v:v*c[3]//255)
    return Image.merge('RGBA',(r,g,b,a))

# which child element of each component carries the terrain id(s) to draw
ID_FIELDS={'FloorComponent':['ground'],'WallComponent':['wall'],'StaticComponent':['static'],'TreeComponent':['tree'],
 'WaterComponent':['ground'],'RuinsComponent':['ruins'],'ObstructionComponent':['obstruction'],'LockersComponent':['static'],
 'TrashComponent':['static'],'AltarComponent':['altar'],'CounterComponent':['counter'],'IceComponent':['ground'],
 'PoisonedWaterComponent':['ground'],'DoorComponent':['closedId'],'StaircaseComponent':['staircase'],'ShaftComponent':['shaft'],
 'RopeComponent':['rope'],'SkyComponent':['sky'],'EgressComponent':['egress'],'TeleportComponent':['teleporter'],
 'DarknessComponent':['darkness'],'FireComponent':['fire'],'WebComponent':['web'],'WhirlwindComponent':['whirlwind']}

def render_region(region, sprites, pad=1):
    tiles=region.findall('tile')
    xs=[int(t.get('x')) for t in tiles]; ys=[int(t.get('y')) for t in tiles]
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
    W=(x1-x0+1+2*pad)*UNIT; H=(y1-y0+1+2*pad)*UNIT
    canvas=Image.new('RGBA',(W,H),(0,0,0,255))
    unknown=set()
    tiles=sorted(tiles,key=lambda t:(int(t.get("x")),int(t.get("y"))))  # editor draws x outer, y inner
    for t in tiles:
        cx=(int(t.get('x'))-x0+pad)*UNIT; cy=(int(t.get('y'))-y0+pad)*UNIT
        layers=[]
        for c in t.findall('component'):
            typ=c.get('type'); col=c.find('color')
            color=(int(col.get('r')),int(col.get('g')),int(col.get('b')),int(col.get('a'))) if col is not None else (255,255,255,255)
            if typ=='DoorComponent' and c.findtext('isOpen')=='true': fields=['openId']
            else: fields=ID_FIELDS.get(typ)
            if not fields: unknown.add(typ); continue
            for fld in fields:
                v=c.findtext(fld)
                if v is None: continue
                for L in sprites.terrain.get(int(v),[]): layers.append((L['order'],L,color))
        layers.sort(key=lambda z:z[0])  # stable
        for _,L,color in layers:
            im=tint(sprites.img(L),color)
            canvas.alpha_composite(im,(cx-45+L['off'][0],cy-45+L['off'][1]))
    return canvas,unknown

if __name__=='__main__':
    proj,rid,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
    root=ET.parse(proj).getroot()
    region=[r for r in root.iter('region') if int(r.findtext('id'))==rid][0]
    img,unk=render_region(region,Sprites())
    img.save(out); print(out,img.size,'unknown types:',unk)
