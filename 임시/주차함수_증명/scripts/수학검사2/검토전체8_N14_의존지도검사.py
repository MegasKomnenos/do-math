# -*- coding: utf-8 -*-
"""의존지도 1절의 열(절·요지·지위·입력 라벨·기록 식별자)을 장 파일 현행에서 다시 만들어 견준다."""
import re, sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:\math\임시\주차함수_증명"
order = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
CH_RE = re.compile(r"^## (\d+)\.")
SEC_RE = re.compile(r"^#{3,4} (\d+\.\d+(?:\.\d+)?)")
LAB = re.compile(r"\{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}")
RID = re.compile(r"\br[0-9a-f]{7}\b")
cur = {}; orderkeys=[]
chapter=None; sec=None; curkey=None
for name in order:
    for line in open(os.path.join(root,"장v2",name+".md"),encoding='utf-8'):
        m=CH_RE.match(line)
        if m: chapter=int(m.group(1)); sec=None
        m=SEC_RE.match(line)
        if m: sec=m.group(1)
        m=HEAD_RE.match(line)
        if m:
            kind,labch,lab=m.groups(); key=f"{labch}:{lab}"
            rest=line[m.end():]
            nm=None
            if rest.startswith(" ("):
                depth=0
                for idx,ch in enumerate(rest[1:],1):
                    if ch=="(": depth+=1
                    elif ch==")":
                        depth-=1
                        if depth==0: nm=rest[2:idx].strip(); rest2=rest[idx+1:]; break
            else: rest2=rest
            status=None; rids=[]
            mb=re.match(r"\s*\[(.*?)\]\s*\.?\*\*", rest2)
            if mb:
                inside=mb.group(1)
                if ';' in inside:
                    status=inside.split(';')[0].strip(); rids=RID.findall(inside.split(';',1)[1])
                else:
                    if RID.search(inside): status=None; rids=RID.findall(inside)
                    else: status=inside.strip()
            if kind=="정의" and status is None: status="정의"
            headlabs=[f"{a}:{b}" for a,b in LAB.findall(line) if f"{a}:{b}"!=key]
            cur[key]=dict(kind=kind,sec=sec,name=nm,status=status,rids=sorted(set(rids)),head=headlabs,body=[],file=name)
            orderkeys.append(key); curkey=key
        elif line.startswith("#"):
            curkey=None
        elif curkey or re.match(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(\([^)]*\))?의 증명", line):
            md=re.match(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}", line)
            if md and line[md.end():].lstrip("(").split(")")[-1].startswith("의 증명") or (md and "의 증명" in line[md.end():md.end()+12]):
                curkey=f"{md.group(2)}:{md.group(3)}"
            if curkey is None: continue
            for a,b in LAB.findall(line):
                k2=f"{a}:{b}"
                if k2!=curkey and k2 not in cur[curkey]['body'] and k2 not in cur[curkey]['head']: cur[curkey]['body'].append(k2)
# 지도 읽기
dep={}
with open(os.path.join(root,"의존지도_v2.md"),encoding='utf-8') as f:
    insec1=False
    for line in f:
        if line.startswith("## 1."): insec1=True
        elif line.startswith("## 2."): insec1=False
        if not insec1: continue
        m=re.match(r"^\| `\{\{(\d+):([^}]+)\}\}` \| (.*) \|\s*$", line)
        if m:
            cells=[c.strip() for c in m.group(3).split(" | ")]
            dep[f"{m.group(1)}:{m.group(2)}"]=cells
print("지도 1절 행", len(dep), "장 머리", len(cur))
for k in cur:
    if k not in dep: print("지도에 없음", k)
for k in dep:
    if k not in cur: print("장에 없음", k)
for k in cur:
    if k not in dep: continue
    c=cur[k]; d=dep[k]
    sec,old,gist,status,inputs,rids,lit,appD,note = d[:9] if len(d)>=9 else d+['']*(9-len(d))
    if not (sec==c['sec'] or (c['sec'] or '').startswith(sec+'.')): print("절 다름",k,"지도",sec,"장",c['sec'])
    if c['name'] and gist!=c['name']: print("요지 다름",k,"| 지도:",gist,"| 장:",c['name'])
    st=re.sub(r"\{\{(\d+):([^}]+)\}\}",r"{{\1:\2}}",status)
    cst=(c['status'] or '')
    cst_n=re.sub(r"`","",cst)
    if re.sub(r"\s+"," ",st)!=re.sub(r"\s+"," ",cst_n): print("지위 다름",k,"| 지도:",status,"| 장:",c['status'])
    # 입력 라벨
    hl=[]; bl=[]
    part=inputs.split("본문 인용:")
    hl=[f"{a}:{b}" for a,b in LAB.findall(part[0])]
    if len(part)>1: bl=[f"{a}:{b}" for a,b in LAB.findall(part[1])]
    if set(hl)!=set(c['head']): print("머리 인용 다름",k,"| 지도:",hl,"| 장:",c['head'])
    if set(bl)!=set(c['body']): print("본문 인용 다름",k,"| 지도만:",sorted(set(bl)-set(c['body'])),"| 장만:",sorted(set(c['body'])-set(bl)))
    drids=sorted(set(RID.findall(rids)))
    if drids!=c['rids'] and not (c['kind']=="정의" and not c['rids']): print("기록 식별자 다름",k,"| 지도:",drids,"| 장:",c['rids'])
