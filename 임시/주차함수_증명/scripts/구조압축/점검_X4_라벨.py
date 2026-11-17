# -*- coding: utf-8 -*-
"""X4 (ㄱ) 라벨 전수: 장v2/장*.md·부록D_장*.md의 머리 정의와 {{장:라벨}} 인용을 전수로 뽑아
미정의 인용·중복 정의·인용 0인 정의·꺾쇠 밖의 맨 라벨을 적는다. 읽기 전용.
장부_v2.md·구조표_v2.md·부록A·B·C는 장 파일 정본에 대한 인용 쪽만 본다(V6 몫).
"""
import glob, io, os, re, sys
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CH = os.path.join(ROOT, "장v2")
chap_files = sorted(glob.glob(os.path.join(CH, "장*.md")))
appD_files = sorted(glob.glob(os.path.join(CH, "부록D_장*.md")))
other_files = [os.path.join(ROOT, "장부_v2.md"), os.path.join(ROOT, "구조표_v2.md")] + \
    [os.path.join(CH, f"부록{x}.md") for x in "ABC"]
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}(?!의 증명)")
DHEAD = re.compile(r"^### D\.\{\{([^}]+)\}\}")
CITE = re.compile(r"\{\{([^}]+)\}\}")
BARE = re.compile(r"(?<![{A-Za-z0-9])((?:[1-9]|10|11|D):[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])(?![}A-Za-z0-9])")

def rel(p): return os.path.relpath(p, ROOT)

defs = {}            # label -> (file, line, kind)
dupes = []
cites = defaultdict(list)   # label -> [(file,line)]
bare = []
for p in chap_files + appD_files:
    lines = io.open(p, encoding="utf-8").read().split("\n")
    for no, ln in enumerate(lines, 1):
        m = HEAD.match(ln) or DHEAD.match(ln)
        if m:
            lab = m.group(m.lastindex)
            kind = m.group(1) if m.re is HEAD else "D"
            if lab in defs:
                dupes.append((lab, defs[lab], (rel(p), no)))
            else:
                defs[lab] = (rel(p), no, kind)
        for c in CITE.finditer(ln):
            cites[c.group(1)].append((rel(p), no))
        # 꺾쇠 밖 맨 라벨
        stripped = CITE.sub("", ln)
        for b in BARE.finditer(stripped):
            bare.append((rel(p), no, b.group(1), stripped[max(0,b.start()-30):b.end()+30]))

print("## 정의 수(장 파일 머리):", len(defs), " | 종류별:", dict(Counter(v[2] for v in defs.values())))
print("## 인용 토큰 수:", sum(len(v) for v in cites.values()), " | 서로 다른 라벨:", len(cites))
print("## 접두별 정의 수:", dict(sorted(Counter(l.split(':')[0] for l in defs).items())))
print()
print("## 중복 정의:", len(dupes))
for d in dupes: print("  ", d)
print()
undefined = {l: v for l, v in cites.items() if l not in defs}
print("## 미정의 인용(장·부록 D):", len(undefined))
for l, v in sorted(undefined.items()):
    print(f"  {l}  x{len(v)}  ", ", ".join(f"{f}:{n}" for f, n in v[:8]))
print()
# 인용 수 (자기 머리 제외)
selfhead = {l: (f, n) for l, (f, n, k) in defs.items()}
uncited = []
for l, (f, n, k) in defs.items():
    others = [(ff, nn) for ff, nn in cites.get(l, []) if not (ff == f and nn == n)]
    if not others:
        uncited.append((l, f, n, k))
print("## 머리 밖 인용 0인 정의:", len(uncited))
for t in sorted(uncited): print("  ", t)
print()
print("## 꺾쇠 밖 맨 라벨(장·부록 D):", len(bare))
for t in bare: print("  ", t)
print()
# 다른 파일(장부·구조표·부록 A·B·C)의 인용 가운데 장 파일에 정의 없는 것
print("## 장부·구조표·부록 A·B·C의 인용 가운데 장 파일 머리에 없는 라벨(V6 몫; 읽기만)")
for p in other_files:
    if not os.path.exists(p): continue
    cnt = Counter(); where = defaultdict(list)
    for no, ln in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
        for c in CITE.finditer(ln):
            if c.group(1) not in defs:
                cnt[c.group(1)] += 1; where[c.group(1)].append(no)
    print(f"  {rel(p)}: 미정의 라벨 {len(cnt)}종 {sum(cnt.values())}회")
    for l, k in sorted(cnt.items()):
        print(f"     {l} x{k} 행 {where[l][:6]}")
