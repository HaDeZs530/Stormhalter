import json, base64, glob, sys
pieces=json.load(open('pieces.json'))
drafts={}
for f in sorted(glob.glob('drafts/sheet_*.json')):
    try:
        for d in json.load(open(f)): drafts[d['n']]=d
    except Exception as e: print('bad',f,e)
for p in pieces:
    d=drafts.get(p['n'],{})
    for k in ('look','kind','mood','size','placement','pairs_with','notes'): p[k]=d.get(k,'' if k not in('mood','pairs_with') else [])
print(len(drafts),'drafted of',len(pieces))
atlas='data:image/webp;base64,'+base64.b64encode(open('/home/claude/viewer/atlas.webp','rb').read()).decode()
idx=json.load(open('/home/claude/viewer/atlas-index.json')); idx.pop('names',None)
html=open('template.html').read().replace('__DATA__',json.dumps(pieces,separators=(',',':')).replace('</script>','<\\/script>')).replace('__ATLAS__',atlas).replace('__INDEX__',json.dumps(idx,separators=(',',':')))
out=sys.argv[1]; open(out,'w').write(html); print(out,len(html)//1024,'KB')
