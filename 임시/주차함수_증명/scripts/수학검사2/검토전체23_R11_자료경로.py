# -*- coding: utf-8 -*-
"""부록 D(장2·3·4·5A)의 「자료」 줄 경로가 기록·자료 묶음에 실제로 있는지 본다(읽기 전용)."""
import re, os, sys, glob
BASE = r"C:\math\임시\주차함수_증명"
REC = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
files = ["부록D_장2.md", "부록D_장3.md", "부록D_장4.md", "부록D_장5A.md"]
recdirs = {d[:8]: d for d in os.listdir(REC)}
def resolve_rec(p):
    m = re.match(r"records/(r[0-9a-f]{7})…/(.*)", p)
    rid, rest = m.group(1), m.group(2)
    full = os.path.join(REC, recdirs.get(rid, rid + "??"), *rest.split("/"))
    return rid, rest, full
for f in files:
    txt = open(os.path.join(BASE, "장v2", f), encoding="utf-8").read()
    item = None
    for line in txt.split("\n"):
        if line.startswith("### "):
            item = re.search(r"\{\{D:([^}]*)\}\}", line).group(1)
        if not line.startswith("**자료.**"):
            continue
        cur_rec = None; cur_dir = None; cur_sess = None; rid = None
        for tok in re.findall(r"`([^`]*)`", line):
            if tok.startswith("records/"):
                rid, rest, full = resolve_rec(tok)
                cur_rec = os.path.dirname(full); cur_sess = None
                ok = os.path.exists(full) or bool(glob.glob(full))
                # 묶음 사본
                bn = os.path.basename(rest.rstrip("/"))
                bundle = os.path.join(BASE, "원고_자료", rid)
                inb = os.path.isdir(bundle) and any(x == bn or x.endswith("__" + bn) for x in os.listdir(bundle)) if bn and "*" not in bn else None
                print(f"[{item}] REC {'OK ' if ok else 'MISSING'} bundle={inb} {tok}")
            elif tok.startswith("원고_자료/"):
                full = os.path.join(BASE, *tok.split("/"))
                cur_sess = full if os.path.isdir(full) else os.path.dirname(full); cur_rec = None
                ok = os.path.exists(full) or bool(glob.glob(full))
                print(f"[{item}] SES {'OK ' if ok else 'MISSING'} {tok}")
            else:
                cands = []
                base = cur_rec or cur_sess
                if base is None:
                    print(f"[{item}] ??? no base {tok}"); continue
                b = base
                for up in range(4):
                    cands.append(os.path.join(b, *tok.split("/")))
                    b = os.path.dirname(b)
                hit = None
                for c in cands:
                    if os.path.exists(c) or glob.glob(c):
                        hit = c; break
                if hit and cur_rec:
                    cur_rec = os.path.dirname(hit) if not os.path.isdir(hit) else cur_rec
                inb = None
                if cur_rec and rid and "*" not in tok:
                    bn = os.path.basename(tok.rstrip("/"))
                    bundle = os.path.join(BASE, "원고_자료", rid)
                    inb = os.path.isdir(bundle) and any(x == bn or x.endswith("__" + bn) for x in os.listdir(bundle))
                kind = "rec" if cur_rec else "ses"
                print(f"[{item}] {kind} {'OK ' if hit else 'MISSING'} bundle={inb} {tok}" + ("" if hit else f"   (base {base})"))
