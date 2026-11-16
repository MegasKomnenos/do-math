# -*- coding: utf-8 -*-
"""장부·의존지도·구조표·장 파일이 부르는 라벨이 현행 머리에 있는지 본다."""
import re, sys, os, io, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:\math\임시\주차함수_증명"
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
DHEAD_RE = re.compile(r"^### D\.\{\{D:([A-Za-z][A-Za-z0-9\-]*)\}\}")
LAB = re.compile(r"\{\{(\d+|D):([A-Za-z][A-Za-z0-9\-]*)\}\}")
heads=set(); dheads=set()
for p in glob.glob(os.path.join(root,"장v2","*.md")):
    for line in open(p,encoding='utf-8'):
        m=HEAD_RE.match(line)
        if m: heads.add(f"{m.group(2)}:{m.group(3)}")
        m=DHEAD_RE.match(line)
        if m: dheads.add(m.group(1))
print("머리", len(heads), "D 항목", len(dheads))
targets = [os.path.join(root,f) for f in ["장부_v2.md","의존지도_v2.md","구조표_v2.md"]] + sorted(glob.glob(os.path.join(root,"장v2","*.md")))
for p in targets:
    bad={}
    for ln_no,line in enumerate(open(p,encoding='utf-8'),1):
        for m in LAB.finditer(line):
            key = m.group(2) if m.group(1)=="D" else f"{m.group(1)}:{m.group(2)}"
            ok = (key in dheads) if m.group(1)=="D" else (key in heads)
            if not ok: bad.setdefault(m.group(0),[]).append(ln_no)
    if bad:
        print("==", os.path.basename(p))
        for k,v in bad.items(): print("  없는 라벨", k, "행", v[:8], ("…" if len(v)>8 else ""))
