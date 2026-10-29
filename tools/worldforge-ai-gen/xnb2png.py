"""Convert MonoGame/XNA Texture2D .xnb files to PNG, keeping the relative path."""
import sys, os, struct, lz4.block
from PIL import Image

def read7(b,i):
    r=0;s=0
    while True:
        c=b[i];i+=1;r|=(c&0x7f)<<s
        if not c&0x80: return r,i
        s+=7
def readstr(b,i):
    n,i=read7(b,i);return b[i:i+n].decode('utf8'),i+n

def convert(src,dst):
    d=open(src,'rb').read()
    if d[:3]!=b'XNB': return 'not xnb'
    flags=d[5]
    if flags&0x80: return 'lzx-compressed (unsupported)'
    if flags&0x40:
        dsize=struct.unpack('<I',d[10:14])[0]
        raw=lz4.block.decompress(d[14:],uncompressed_size=dsize)
    else: raw=d[10:]
    i=0; n,i=read7(raw,i); readers=[]
    for _ in range(n):
        s,i=readstr(raw,i); i+=4; readers.append(s)
    _,i=read7(raw,i)   # shared resources
    tid,i=read7(raw,i)
    if 'Texture2DReader' not in readers[tid-1]: return 'not texture: '+readers[tid-1]
    fmt,w,h,mips=struct.unpack('<iiii',raw[i:i+16]); i+=16
    size=struct.unpack('<I',raw[i:i+4])[0]; i+=4
    px=raw[i:i+size]
    if fmt!=0: return f'surfaceformat {fmt} (unsupported)'
    img=Image.frombytes('RGBA',(w,h),px)
    os.makedirs(os.path.dirname(dst),exist_ok=True); img.save(dst)
    return f'{w}x{h}'

if __name__=='__main__':
    root,out=sys.argv[1],sys.argv[2]; ok=0; bad=[]
    for dp,_,fs in os.walk(root):
        for f in fs:
            if not f.lower().endswith('.xnb'): continue
            src=os.path.join(dp,f); rel=os.path.relpath(src,root)[:-4]+'.png'
            r=convert(src,os.path.join(out,rel))
            if 'x' in r and r[0].isdigit(): ok+=1
            else: bad.append((rel,r))
    print('converted',ok,'failed',len(bad))
    for b in bad[:30]: print(' ',b)
