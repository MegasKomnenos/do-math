# O9: every {{N:label}} cited in 장9 must have a head in chapter N files (or D:label in 부록D files).
import re,glob,io
src=io.open('장v2/장9.md',encoding='utf-8').read()
cited=set(re.findall(r'\{\{(\d+|D):([^}]+)\}\}',src))
files={}
for f in glob.glob('장v2/*.md'):
    files[f]=io.open(f,encoding='utf-8').read()
heads=set()
for f,t in files.items():
    for m in re.finditer(r'^(\*\*|###? )[^\n]*?\{\{(\d+|D):([^}]+)\}\}',t,flags=re.M):
        heads.add((m.group(2),m.group(3)))
missing=[c for c in sorted(cited) if c not in heads]
print("cited:",len(cited)," missing heads:",missing)
# labels defined in 장9 but never cited elsewhere
own=[h for h in heads if h[0]=='9']
other=''.join(t for f,t in files.items() if not f.endswith('장9.md'))
print("9-labels not cited outside ch9:",[h[1] for h in sorted(own) if '{{9:'+h[1]+'}}' not in other])
