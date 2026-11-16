# 부록 D(2~6장) 자료 줄의 경로 존재 확인
import re, os, glob, sys
root=r"C:\math\임시\주차함수_증명"
rec=r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
files=["부록D_장2.md","부록D_장3.md","부록D_장4.md","부록D_장5A.md","부록D_장5B.md","부록D_장6.md"]
def expand(pth):
    # records/rXXXX…/ -> glob
    pth=pth.replace("records/","")
    m=re.match(r"(r[0-9a-f]+)…/(.*)",pth)
    if m:
        g=glob.glob(os.path.join(rec,m.group(1)+"*"))
        if not g: return None
        return os.path.join(g[0],m.group(2))
    return os.path.join(rec,pth)
for f in files:
    txt=open(os.path.join(root,"장v2",f),encoding="utf-8").read()
    for item in txt.split("### D.")[1:]:
        title=item.split("\n")[0][:60]
        m=re.search(r"\*\*자료\.\*\*(.*)",item)
        if not m: print("NO 자료:",title); continue
        paths=re.findall(r"`([^`]+)`",m.group(1))
        missing=[]; curdir=None
        for pth in paths:
            if pth.startswith("records/"):
                full=expand(pth); curdir=os.path.dirname(full) if full else None
            elif pth.startswith("원고_자료/"):
                full=os.path.join(root,pth); curdir=os.path.dirname(full)
            elif "/" in pth or pth.endswith((".py",".txt",".json",".c",".log",".tsv",".out",".jsonl",".bat",".md",".gz",".bin",".sh",".part")) or pth.endswith("/"):
                full=os.path.join(curdir,pth) if curdir else None
            else:
                continue  # variable names etc
            if full is None or not (os.path.exists(full) or glob.glob(full.replace("*","*"))):
                missing.append(pth)
        print(f, "|", title, "| paths", len(paths), "| missing:", missing)
