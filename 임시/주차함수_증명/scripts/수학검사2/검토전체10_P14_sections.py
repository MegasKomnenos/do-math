# 각 진술 머리가 놓인 절을 구해 장부 4절 「둘째 판 절」·1.2 「정의 절」과 대조
import re,glob,os,io
base=r"C:\math\임시\주차함수_증명"
headsec={}
for f in sorted(glob.glob(os.path.join(base,"장v2","장*.md"))):
    cur=None
    for line in io.open(f,encoding='utf-8'):
        m=re.match(r'^#{2,4} (\d+(?:\.\d+)*)',line)
        if m: cur=m.group(1); continue
        m=re.match(r'^\*\*(정리|보조정리|명제|정의|따름정리) \{\{([^}]+)\}\}',line)
        if m: headsec.setdefault(m.group(2),[]).append(cur)
jb=io.open(os.path.join(base,"장부_v2.md"),encoding='utf-8').read().split('\n')
for i in range(743,1191):
    l=jb[i]
    cells=[c.strip() for c in l.strip().strip('|').split('|')]
    if len(cells)<6: continue
    m=re.search(r'\{\{([^}]+)\}\}',cells[5])
    if not m: continue
    lab=m.group(1); sec=cells[4]
    secs=headsec.get(lab,[])
    # compare at 2-level
    ok=any(s and (s==sec or s.startswith(sec+'.')) for s in secs)
    if not ok: print("4절 절 불일치",i+1,lab,"4절:",sec,"장:",secs)
