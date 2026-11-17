# -*- coding: utf-8 -*-
# 의존지도 1절 표를 장 파일 머리·본문 인용·10.2/10.3 표와 맞댄다. 1.1의 수와 2.1의 수(263·272·13)를 다시 센다.
import re, json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체23_R13_lib import *
L = open(os.path.join(base,"의존지도_v2.md"),encoding="utf-8").read().split("\n")
s1 = next(i for i,l in enumerate(L) if l.startswith("## 1. "))
s11 = next(i for i,l in enumerate(L) if l.startswith("### 1.1 "))
s2 = next(i for i,l in enumerate(L) if l.startswith("## 2. "))
rows=[]
for i in range(s1,s11):
    l=L[i]
    if l.startswith("| `{{"):
        c=[x.strip() for x in l.strip()[1:-1].split(" | ")]
        rows.append((i+1,c))
print("1절 행",len(rows), "칸수", collections.Counter(len(c) for _,c in rows))
LAB=re.compile(r"\{\{(\d+:[A-Za-z0-9\-]+)\}\}")
order=[c[0].strip("`")[2:-2] for _,c in rows]
print("순서 같음", order==[h["label"][2:-2] for h in heads])
edges_head={}; edges_all={}
for ln,c in rows:
    lab=c[0].strip("`")[2:-2]
    h=hd.get(lab)
    if not h: print("머리 없음",ln,lab); continue
    if c[1]!=h["sec3"]: print("절 다름",ln,lab,c[1],h["sec3"])
    # 요지=머리 이름
    # 지위
    st=h["status"]
    head_line=lines(h["file"])[h["line"]-1]
    if h["kind"]=="정의":
        exp_status="정의"
    else:
        exp_status=st.split(";")[0].strip() if st else None
    if c[4]!=exp_status:
        print("지위 다름",ln,lab,"\n   표:",c[4][:200],"\n   머리:",(exp_status or "")[:200])
    # 머리 줄 인용 라벨
    m=re.match(r"^\*\*.*?\]\.\*\*",head_line)
    headpart = m.group(0) if m else head_line.split(".**")[0]
    hl=[x for x in LAB.findall(headpart) if x!=lab]
    cell=c[5]
    parts=cell.split("본문 인용:")
    tl_head=LAB.findall(parts[0]); tl_body=LAB.findall(parts[1]) if len(parts)>1 else []
    if set(hl)!=set(tl_head):
        print("머리 인용 다름",ln,lab,"표에만:",sorted(set(tl_head)-set(hl)),"머리에만:",sorted(set(hl)-set(tl_head)))
    # 본문 인용: 머리 다음부터 다음 머리 전까지
    stt,full=block(lab)
    body=full[len(head_line):] if full.startswith(head_line) else full
    bl=set(x for x in LAB.findall(head_line[len(headpart):]+body) if x!=lab)-set(hl)
    edges_head[lab]=set(hl); edges_all[lab]=set(tl_head)|set(tl_body)
    diff_a=set(tl_body)-bl; diff_b=bl-set(tl_body)
    if diff_a or diff_b:
        print("본문 인용 다름(뒤로 미룬 증명일 수 있음)",ln,lab,"표에만:",sorted(diff_a),"글에만:",sorted(diff_b))
    # 기록
    rec=re.findall(r"r[0-9a-f]{7}",st.split(";",1)[1]) if st and ";" in st else (re.findall(r"r[0-9a-f]{7}",st) if st else [])
    trec=re.findall(r"r[0-9a-f]{7}",c[6])
    if set(rec)!=set(trec): print("기록 다름",ln,lab,"표:",c[6][:120],"| 머리:",rec)
# 2.1의 수
allin=set()
for lab in edges_all: allin|=edges_all[lab]
print("입력 라벨 수(중복 제외)",len(allin),"그 중 머리 없는 것",[x for x in allin if x not in hd])
# 순환(머리 의존)
def scc(g):
    idx={};low={};st=[];on=set();res=[];c=[0]
    sys.setrecursionlimit(10000)
    def visit(v):
        idx[v]=low[v]=c[0];c[0]+=1;st.append(v);on.add(v)
        for w in g.get(v,()):
            if w not in idx:
                visit(w);low[v]=min(low[v],low[w])
            elif w in on: low[v]=min(low[v],idx[w])
        if low[v]==idx[v]:
            comp=[]
            while True:
                w=st.pop();on.discard(w);comp.append(w)
                if w==v:break
            res.append(comp)
    for v in g:
        if v not in idx: visit(v)
    return res
c1=[c for c in scc(edges_head) if len(c)>1]
c2=[c for c in scc(edges_all) if len(c)>1]
print("머리 의존 그래프 강결합(>1):",len(c1),[len(c) for c in c1],"자기 고리:",[v for v in edges_head if v in edges_head[v]])
print("본문 포함 그래프 강결합(>1):",len(c2),sorted(len(c) for c in c2))
# 1.1
dead=[l for l in L[s11:s2] if l.startswith("| `(") or l.startswith("| (라벨 없음)")]
print("1.1 행 수",len(dead), "라벨 있는 것", sum(1 for l in dead if l.startswith("| `(")))
json.dump({"dead11":[l.split(" | ")[0].strip("| `") for l in dead]},open(os.path.join(base,"scripts","수학검사2","검토전체23_R13_dead11.json"),"w",encoding="utf-8"),ensure_ascii=False)
