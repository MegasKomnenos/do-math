# -*- coding: utf-8 -*-
"""부록 D 장7A·7B·8·9·10의 「자료」 줄이 가리키는 기록 경로와 원고_자료 경로가 실제로 있는지 센다. python -I"""
import re, os, glob, json
ROOT = r"C:\math\임시\주차함수_증명"
REC = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
files = ["부록D_장7A.md","부록D_장7B.md","부록D_장8.md","부록D_장9.md","부록D_장10.md"]
missing = []; total = 0
for f in files:
    txt = open(os.path.join(ROOT,"장v2",f),encoding="utf-8").read()
    for m in re.finditer(r"`(records/[^`]+|원고_자료/[^`]+)`", txt):
        p = m.group(1)
        if "*" in p or "<" in p or "…/" not in p and p.endswith("/") is False and False: pass
        total += 1
        if p.startswith("records/"):
            rest = p[len("records/"):]
            rid, _, tail = rest.partition("/")
            rid = rid.replace("…","")
            cands = glob.glob(os.path.join(REC, rid+"*"))
            if not cands: missing.append((f,p,"record dir")); continue
            full = os.path.join(cands[0], tail.replace("/", os.sep))
            if "*" in full:
                if not glob.glob(full): missing.append((f,p,"glob empty"))
            elif not os.path.exists(full.rstrip(os.sep)):
                missing.append((f,p,"no file"))
        else:
            full = os.path.join(ROOT, p.replace("/", os.sep))
            if "*" in full:
                if not glob.glob(full): missing.append((f,p,"glob empty"))
            elif not os.path.exists(full.rstrip(os.sep)):
                missing.append((f,p,"no file"))
print("checked", total, "paths; missing", len(missing))
for x in missing: print(x)
# seed certificate counts
cnt_seed = cnt_init = cnt_coef = 0
keys=set()
for k in range(2,121):
    fp = glob.glob(os.path.join(REC,"r9e782f5*","producer",f"certificate-k{k}.json"))[0]
    d = json.load(open(fp,encoding="utf-8"))
    keys |= set(d.keys())
    cut = d.get("cut"); r = d.get("r")
    cnt_seed += (r + k + 1) - cut
    cnt_init += r + k + 2
print("seed keys:", sorted(keys)[:30])
print("씨앗 수 Σ(r+k+1-cut) =", cnt_seed, "(글 34,571); 초기값 수 Σ(r+k+2) =", cnt_init, "(글 49,372)")
d=json.load(open(glob.glob(os.path.join(REC,"r9e782f5*","producer","certificate-k2.json"))[0],encoding="utf-8"))
print({k:(v if not isinstance(v,(list,dict)) else type(v).__name__+str(len(v))) for k,v in d.items()})
