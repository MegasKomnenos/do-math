# 부록 D 7A–10 항목의 「자료」 줄에 적힌 경로가 실제로 있는지 확인한다(records/… 와 원고_자료/…).
import re, os, sys, io, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:/math/임시/주차함수_증명/장v2/"
rec = r"C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/"
mroot = r"C:/math/임시/주차함수_증명/"
files = ["부록D_장7A.md","부록D_장7B.md","부록D_장8.md","부록D_장9.md","부록D_장10.md"]
recdirs = os.listdir(rec)
def expand(p):
    # records/r475ada3…/x  -> find dir starting with prefix
    m = re.match(r'records/(r[0-9a-f]+)…?/(.*)', p)
    if m:
        pre, rest = m.group(1), m.group(2)
        cands = [d for d in recdirs if d.startswith(pre)]
        if len(cands)!=1: return None, f"record prefix {pre} -> {cands}"
        return os.path.join(rec, cands[0], rest), None
    if p.startswith('원고_자료/'):
        return os.path.join(mroot, p), None
    return None, None
for f in files:
    txt = open(root+f, encoding='utf-8').read()
    for lab, body in re.findall(r'### D\.\{\{D:([^}]+)\}\}(.*?)(?=\n### D\.|\Z)', txt, flags=re.S):
        m = re.search(r'\*\*자료\.\*\*(.*)', body)
        if not m: continue
        paths = re.findall(r'`([^`]+)`', m.group(1))
        missing = []
        for p in paths:
            if ' ' in p and not p.startswith('records') and not p.startswith('원고'): continue
            full, err = expand(p)
            if err: missing.append((p, err)); continue
            if full is None: continue
            if '*' in full:
                if not glob.glob(full): missing.append((p,'glob none'))
            elif not os.path.exists(full): missing.append((p,'missing'))
        print("==", f, lab, "paths:", len(paths), "missing:", len(missing))
        for p,e in missing: print("   ", p, e)
