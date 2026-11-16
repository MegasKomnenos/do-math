# -*- coding: utf-8 -*-
"""E12 검산 4: 부록 D(장2~장6) 「자료」 줄의 경로가 실제로 있는지 확인한다."""
import re, os, glob, sys
REPO=r"C:\math\임시\주차함수_증명"
REC=r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
files=["부록D_장2.md","부록D_장3.md","부록D_장4.md","부록D_장5A.md","부록D_장5B.md","부록D_장6.md"]
def recdir(idx):
    g=glob.glob(os.path.join(REC,idx+"*"))
    return g[0] if g else None
missing=[]; checked=0
for f in files:
    txt=open(os.path.join(REPO,"장v2",f),encoding="utf-8").read()
    item=None
    for line in txt.split("\n"):
        if line.startswith("### D."): item=line.split()[1]
        if not line.startswith("**자료.**"): continue
        cur=None
        for tok in re.findall(r"`([^`]+)`",line):
            tok=tok.strip()
            if tok.endswith("/"): tok=tok[:-1]
            m=re.match(r"records/(r[0-9a-f]{7})…/(.*)",tok)
            if m:
                d=recdir(m.group(1))
                if d is None: missing.append((f,item,tok,"record dir missing")); continue
                p=os.path.join(d,m.group(2)); cur=os.path.dirname(p)
            elif tok.startswith("원고_자료/"):
                p=os.path.join(REPO,tok); cur=os.path.dirname(p); base=REPO
            elif "/" in tok and cur is not None and "원고_자료" in cur:
                # relative to the 원고_자료 run directory (two levels up if cur is .../code)
                root=cur
                while root and os.path.basename(root) in ("code","indep","logs"): root=os.path.dirname(root)
                p=os.path.join(root,tok)
                cands=[p,os.path.join(cur,tok)]
                if not any(os.path.exists(c) for c in cands):
                    missing.append((f,item,tok,"rel path")); continue
                checked+=1; continue
            elif cur is not None and "/" not in tok and not tok.startswith("--"):
                p=os.path.join(cur,tok)
            else:
                continue
            checked+=1
            if "*" in p:
                if not glob.glob(p): missing.append((f,item,tok,"glob empty"))
            elif not os.path.exists(p): missing.append((f,item,tok,p))
print("checked",checked)
for m in missing: print("MISSING",m)
