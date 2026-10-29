"""Assemble forge-viewer.html: template + atlas data URI + index + sample region."""
import base64, json, sys
tpl=open('viewer-template.html').read()
atlas='data:image/webp;base64,'+base64.b64encode(open('atlas.webp','rb').read()).decode()
idx=open('atlas-index.json').read()
sample=open('sample-region.xml').read().replace('</script>','<\\/script>')
out=tpl.replace('__ATLAS__',atlas).replace('__INDEX__',idx).replace('__SAMPLE__',sample)
open(sys.argv[1] if len(sys.argv)>1 else 'forge-viewer.html','w').write(out)
print(len(out)//1024,'KB')
