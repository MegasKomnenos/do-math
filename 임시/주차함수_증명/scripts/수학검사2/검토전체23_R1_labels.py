import re,glob,io,sys
sys.stdout.reconfigure(encoding='utf-8')
files=sorted(glob.glob('장v2/*.md'))
defs={}
for f in files:
    for i,line in enumerate(io.open(f,encoding='utf-8'),1):
        m=re.match(r'\*\*(정리|명제|보조정리|따름정리|정의|문제|가설|관찰|주의)\s*\{\{([^}]+)\}\}',line)
        if m:
            defs.setdefault(m.group(2),[]).append((f,i,m.group(1)))
        for m in re.finditer(r'^#+\s*D\.\{\{([^}]+)\}\}',line):
            defs.setdefault(m.group(1),[]).append((f,i,'D'))
used={}
for f in ['장v2/장1.md','장v2/장2.md']:
    for i,line in enumerate(io.open(f,encoding='utf-8'),1):
        for m in re.finditer(r'(정리|명제|보조정리|따름정리|정의|D\.)?\s*\{\{([^}]+)\}\}',line):
            used.setdefault(m.group(2),[]).append((f,i,m.group(1)))
for lab,us in sorted(used.items()):
    d=defs.get(lab)
    if not d:
        print('NODEF',lab,us[:3])
    else:
        kinds={k for (_,_,k) in d}
        for (f,i,k) in us:
            if k and k!='D.' and k not in kinds:
                print('KINDMISMATCH',lab,f,i,k,'def:',d)
print(len(used),'labels used')
