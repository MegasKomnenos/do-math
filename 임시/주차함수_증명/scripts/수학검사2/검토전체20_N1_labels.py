import re,glob,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
src=open(sys.argv[1],encoding='utf-8').read()
labels=sorted(set(re.findall(r'\{\{(\w+):([^}]+)\}\}',src)))
files=glob.glob('장v2/*.md')
heads={}
for f in files:
    for i,l in enumerate(open(f,encoding='utf-8'),1):
        m=re.match(r'\*\*(정리|명제|보조정리|따름정리|정의|가설|관찰|문제)\s+\{\{(\w+):([^}]+)\}\}',l)
        if m: heads[(m.group(2),m.group(3))]=(f,i,l.strip()[:400])
for ch,lab in labels:
    h=heads.get((ch,lab))
    print(f'== {{{{{ch}:{lab}}}}}')
    print('   ',h if h else 'NOT FOUND')
