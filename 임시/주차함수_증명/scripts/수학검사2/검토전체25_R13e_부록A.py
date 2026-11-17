# -*- coding: utf-8 -*-
# 부록 A의 「기록의 글자」 열을 장부 1.2의 같은 열과 행 단위로 견준다(부록 A는 R10의 몫 — 갈림만 모은다).
# 첫 칸을 공백 걷어 맞추고, 기록 식별자의 열과 $…$ 토큰의 열을 견준다.
import sys, io, re, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
spec = importlib.util.spec_from_file_location('t12','scripts/수학검사2/검토전체25_R13e_표12.py')
t12 = importlib.util.module_from_spec(spec); spec.loader.exec_module(t12)
A = io.open('장v2/부록A.md',encoding='utf-8').read().split('\n')
rowsA=[]
for i,s in enumerate(A,1):
    if s.startswith('|') and not s.startswith('|---') and not s.startswith('| 기호'):
        c=t12.split_row(s)
        if len(c)==4: rowsA.append((i,c))
def key(x): return re.sub(r'\s+','',x.replace('`',''))
def recs(x): return re.findall(r'\[(r[0-9a-f]{7})\]', x)
def toks(x): return [re.sub(r'\s+','',t) for t in re.findall(r'\$([^$]+)\$', x)]
mapA={key(c[0]):(i,c) for i,c in rowsA}
rows12=t12.table(49,288)
print('1.2 행 %d, 부록 A 4칸 행 %d'%(len(rows12),len(rowsA)))
used=set(); nd=0
for ln,c in rows12:
    k=key(c[0])
    if k not in mapA:
        print('1.2 %d행 %s: 부록 A에 같은 기호 칸 없음'%(ln,c[0])); continue
    i,cc=mapA[k]; used.add(i)
    d=[]
    if recs(cc[3])!=recs(c[6]): d.append('기록: 1.2 %s / 부록 A %s'%(recs(c[6]),recs(cc[3])))
    a,b=toks(c[6]),toks(cc[3])
    if a!=b: d.append('토큰: 1.2에만 %s / 부록 A에만 %s'%([x for x in a if x not in b][:5],[x for x in b if x not in a][:5]))
    # 정의 절
    if key(cc[2])!=key(c[3]): d.append('정의 절: 1.2 「%s」 / 부록 A 「%s」'%(c[3][:60],cc[2][:60]))
    if d: nd+=1; print('1.2 %d행 ↔ 부록 A %d행 %s: %s'%(ln,i,c[0][:40],' ‖ '.join(d)))
print('갈린 행', nd)
for i,c in rowsA:
    if i not in used and i>30: print('부록 A %d행: 1.2에 짝 없음 — %s'%(i,c[0][:80]))
