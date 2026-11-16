# T14: 의존지도 2.1 주장(라벨 379개·비순환·강결합 16개)과 1절 부록 D·문헌 열의 11장 표 대조
import re, os, sys
sys.setrecursionlimit(10000)
root=r"C:\math\임시\주차함수_증명"
rows=[]
for l in open(os.path.join(root,"의존지도_v2.md"),encoding='utf-8'):
    if l.startswith('## 2') or l.startswith('### 1.1'): break
    if l.startswith('| `{{'):
        rows.append(l)
labels=[]; headg={}; fullg={}; dcol={}; litcol={}
for l in rows:
    cells=[x.strip() for x in re.split(r'\s\|\s', l.strip()[1:-1].strip())]
    lab=cells[0].strip('`'); labels.append(lab)
    inp=cells[5]
    hp=inp.split('본문 인용:')[0]; bp=inp.split('본문 인용:')[1] if '본문 인용:' in inp else ''
    headg[lab]=set(re.findall(r'\{\{\d+:[^}]+\}\}',hp))-{lab}
    fullg[lab]=set(re.findall(r'\{\{\d+:[^}]+\}\}',inp))-{lab}
    # 부록 D 열: 행 전체에서 D 라벨 (지위·비고에는 D 라벨이 없다고 가정)
    dcol[lab]=set(re.findall(r'\{\{D:[^}]+\}\}',cells[8])) if len(cells)>8 else set(re.findall(r'\{\{D:[^}]+\}\}',l))
    litcol[lab]=cells[7] if len(cells)>7 else ''
S=set(labels)
cited=set().union(*fullg.values())
print("라벨 수",len(labels),"인용 라벨(중복 제외)",len(cited),"정의 안 된 인용",sorted(cited-S))
# acyclic on head graph
def has_cycle(g):
    color={}
    def dfs(u):
        color[u]=1
        for v in g.get(u,()):
            if v not in g: continue
            if color.get(v)==1: return True
            if color.get(v) is None and dfs(v): return True
        color[u]=2; return False
    return any(color.get(u) is None and dfs(u) for u in g)
print("머리 선언 그래프 순환:",has_cycle(headg))
# SCC on full graph (Tarjan)
idx={}; low={}; st=[]; on=set(); comps=[]; c=[0]
def sc(v):
    idx[v]=low[v]=c[0]; c[0]+=1; st.append(v); on.add(v)
    for w in fullg.get(v,()):
        if w not in fullg: continue
        if w not in idx: sc(w); low[v]=min(low[v],low[w])
        elif w in on: low[v]=min(low[v],idx[w])
    if low[v]==idx[v]:
        comp=[]
        while True:
            w=st.pop(); on.discard(w); comp.append(w)
            if w==v: break
        if len(comp)>1: comps.append(sorted(comp))
for v in fullg:
    if v not in idx: sc(v)
print("강결합 성분(크기>=2):",len(comps))
for comp in sorted(comps,key=len): print(len(comp),comp[:6],'...' if len(comp)>6 else '')
# 11.2 부록 D 열
t11=open(os.path.join(root,"장v2","장11.md"),encoding='utf-8').read().split('\n')
exp={}
in4=False; lit={}
for l in t11:
    if l.startswith('| 부록 D.{{D:'):
        c=[x.strip() for x in l.strip().strip('|').split('|')]
        d=re.search(r'\{\{D:[^}]+\}\}',c[0]).group(0)
        for lab in re.findall(r'\{\{\d+:[^}]+\}\}',c[1]): exp.setdefault(lab,set()).add(d)
    if l.startswith('### 11.4'): in4=True
    if in4 and l.startswith('|') and '{{' in l:
        for lab in re.findall(r'\{\{\d+:[^}]+\}\}',l): lit.setdefault(lab,0); lit[lab]+=1
print("== 11.2 부록 D 열")
for lab,ds in exp.items():
    if lab not in dcol: print("지도에 없음",lab); continue
    if dcol[lab]!=ds: print(f"{lab}: 11.2={sorted(ds)} 지도={sorted(dcol[lab])}")
for lab,ds in dcol.items():
    if ds and lab not in exp: print(f"{lab}: 지도 {sorted(ds)} 11.2 표에 없음")
print("== 11.4 문헌 열")
for lab in lit:
    if lab in litcol and litcol[lab] in ('—',''): print(f"{lab}: 11.4에 쓰인 자리로 있으나 지도 문헌 열 비어 있음")
for lab,v in litcol.items():
    if v not in ('—','') and lab not in lit: print(f"{lab}: 지도 문헌 열 있으나 11.4에 자리 없음: {v[:60]}")
