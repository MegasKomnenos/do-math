# -*- coding: utf-8 -*-
# 장부 7절 표와 부록 C 「기록의 글자와 이 글의 글자」 표를 행 단위로 견준다(부록 C는 R10의 몫 — 갈림만 모은다).
# 첫 칸은 역따옴표·공백을 걷어 맞추고, 둘째 칸은 기록 식별자의 집합으로, 셋째 칸은 $…$ 토큰의 열로 견준다.
# 넷째 칸은 옮길 때 꼬리표를 떼는 규칙이 있으므로 「(확인)」·날짜 꼬리표를 걷은 뒤 토큰만 견준다.
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
import importlib.util
spec = importlib.util.spec_from_file_location('t12','scripts/수학검사2/검토전체25_R13e_표12.py')
t12 = importlib.util.module_from_spec(spec); spec.loader.exec_module(t12)
A = io.open('장v2/부록C.md',encoding='utf-8').read().split('\n')
rowsC=[]
for i in range(277, 478):
    s=A[i-1]
    if s.startswith('|') and not s.startswith('|---'):
        rowsC.append((i,t12.split_row(s)))
rows7=t12.table(1243,1441)
def key(c0):
    k=c0.replace('`','')
    k=re.sub(r'\s+','',k)
    return k
def recs(x): return re.findall(r'\[(r[0-9a-f]{7})\]', x)
def toks(x): return [re.sub(r'\s+','',t) for t in re.findall(r'\$([^$]+)\$', x)]
print('7절 행 %d, 부록 C 행 %d'%(len(rows7),len(rowsC)))
mapC={}
for i,c in rowsC: mapC.setdefault(key(c[0]),[]).append((i,c))
used=set()
for ln,c in rows7:
    k=key(c[0])
    cand=mapC.get(k)
    if not cand:
        # 첫 칸의 토큰 집합으로 느슨히
        tk=set(toks(c[0])); best=None
        for i,cc in rowsC:
            if set(toks(cc[0]))==tk and recs(cc[1])==recs(c[1]): best=(i,cc); break
        if best: cand=[best]
    if not cand:
        print('7절 %d행: 부록 C에 같은 첫 칸의 행이 없음 — %s | %s'%(ln,c[0][:90],c[1][:60])); continue
    # 같은 첫 칸이 여럿이면 기록이 같은 것을 고른다
    pick=None
    for i,cc in cand:
        if recs(cc[1])==recs(c[1]): pick=(i,cc); break
    if not pick: pick=cand[0]
    i,cc=pick; used.add(i)
    d=[]
    if recs(cc[1])!=recs(c[1]): d.append('기록: 7절 %s / 부록 C %s'%(recs(c[1]),recs(cc[1])))
    if key(cc[0])!=k: d.append('첫 칸: 7절 「%s」 / 부록 C 「%s」'%(c[0][:120],cc[0][:120]))
    if toks(cc[2])!=toks(c[2]):
        a,b=toks(c[2]),toks(cc[2])
        d.append('셋째 칸 토큰: 7절에만 %s / 부록 C에만 %s'%([x for x in a if x not in b][:6],[x for x in b if x not in a][:6]))
    if toks(cc[3])!=toks(c[3]):
        a,b=toks(c[3]),toks(cc[3])
        d.append('넷째 칸 토큰: 7절에만 %s / 부록 C에만 %s'%([x for x in a if x not in b][:6],[x for x in b if x not in a][:6]))
    if d: print('7절 %d행 ↔ 부록 C %d행: %s'%(ln,i,' ‖ '.join(d)))
for i,c in rowsC:
    if i not in used: print('부록 C %d행: 7절에 짝이 없음 — %s | %s'%(i,c[0][:90],c[1][:60]))
