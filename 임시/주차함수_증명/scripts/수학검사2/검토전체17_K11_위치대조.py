import re,glob,io
root=r'C:\math\임시\주차함수_증명'
out=io.open(root+r'\scripts\수학검사2\_K11_위치대조_out.txt','w',encoding='utf-8')
# chapter files: map label -> (file, line, section, head text)
chap={}
for f in glob.glob(root+r'\장v2\장*.md'):
    name=f.replace(chr(92),'/').split('/')[-1]
    sec=''
    for i,l in enumerate(io.open(f,encoding='utf-8'),1):
        m=re.match(r'### (\d+\.\d+)',l)
        if m: sec=m.group(1)
        for m in re.finditer(r'\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+:[^}]+)\}\}(.*?)\*\*',l):
            lab=m.group(2)
            if lab not in chap: chap[lab]=(name,i,sec,m.group(1),m.group(3)[:400])
# D entries
entries={}
for f in sorted(glob.glob(root+r'\장v2\부록D_장*.md')):
    txt=io.open(f,encoding='utf-8').read()
    for p in re.split(r'\n(?=### D\.\{\{D:)',txt):
        m=re.match(r'### D\.\{\{D:([^}]+)\}\}(.*)',p)
        if not m: continue
        d={'head':m.group(2).strip()}
        mm=re.search(r'\*\*산술 등급\.\*\*\s*(.*)',p); d['grade']=mm.group(1).strip() if mm else ''
        entries[m.group(1)]=d
t=io.open(root+r'\장v2\장11.md',encoding='utf-8').read().split('\n')
for i,l in enumerate(t,1):
    if not l.startswith('| 부록 D.{{D:'): continue
    c=[x.strip() for x in l.strip().strip('|').split(' | ')]
    lab=re.match(r'부록 D\.\{\{D:([^}]+)\}\}',c[0]).group(1)
    e=entries[lab]
    hp=re.search(r'\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$',e['head'])
    hstmt=hp.group(1) if hp else '??'
    out.write('\n=== %d %s\n TBL: %s\n D  : %s  %s\n grade TBL=%s | D=%s\n loc TBL=%s\n'%(i,lab,c[1],hstmt,'OK' if hstmt==c[1] else '**DIFF**',c[2],e['grade'][:160],c[3]))
    for s in re.findall(r'\{\{(\d+:[^}]+)\}\}',c[1]):
        info=chap.get(s)
        if info: out.write('   %s -> %s L%d sec %s %s %s\n'%(s,info[0],info[1],info[2],info[3],info[4][:300]))
        else: out.write('   %s -> NOT FOUND\n'%s)
out.close()
