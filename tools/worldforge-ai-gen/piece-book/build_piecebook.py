import json, base64, glob, sys
# the merged piece data (drafts + Tony's legend/corrections) is the single source
pieces=json.load(open(sys.argv[2] if len(sys.argv)>2 else '/home/claude/out/2026-10-29 piece-book-draft.json'))
print(len(pieces),'pieces')
atlas='data:image/webp;base64,'+base64.b64encode(open('/home/claude/viewer/atlas.webp','rb').read()).decode()
idx=json.load(open('/home/claude/viewer/atlas-index.json')); idx.pop('names',None)
html=open('template.html').read().replace('__DATA__',json.dumps(pieces,separators=(',',':')).replace('</script>','<\\/script>')).replace('__ATLAS__',atlas).replace('__INDEX__',json.dumps(idx,separators=(',',':')))
out=sys.argv[1]; open(out,'w').write(html); print(out,len(html)//1024,'KB')
