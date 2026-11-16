# L13: 부록 D 7A·7B·8·9·10 자료 줄의 경로 존재 확인
import re,os,glob,sys
REC=r"C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records"
BASE=r"C:/math/임시/주차함수_증명"
files=["부록D_장7A","부록D_장7B","부록D_장8","부록D_장9","부록D_장10"]
miss=[]; ok=0
for f in files:
    txt=open(f"{BASE}/장v2/{f}.md",encoding="utf-8").read()
    for m in re.finditer(r"`([^`]+)`",txt):
        p=m.group(1).strip()
        if p.startswith("python") or " " in p or p.startswith("--") or "(" in p: continue
        if p.startswith("records/"):
            q=p[len("records/"):]
            if "…" in q:
                head,tail=q.split("…",1)
                dirs=glob.glob(f"{REC}/{head}*")
                cand=[d+tail for d in dirs]
            else: cand=[f"{REC}/{q}"]
            cand=[c.rstrip("/") for c in cand]
            found=any(os.path.exists(c) or glob.glob(c) for c in cand)
            if not found: miss.append((f,p))
            else: ok+=1
        elif p.startswith("원고_자료/"):
            c=f"{BASE}/{p}".rstrip("/")
            if not (os.path.exists(c) or glob.glob(c)): miss.append((f,p))
            else: ok+=1
print("ok",ok)
for m in miss: print("MISSING",m)
