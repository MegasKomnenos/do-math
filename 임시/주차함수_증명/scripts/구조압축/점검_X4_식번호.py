# -*- coding: utf-8 -*-
"""X4 (ㄷ) 식 번호: \\tag{n.m} 정의와 (n.m) 참조를 맞춘다(태그 있는 장 4·5B·6·7B·8의 번호). 읽기 전용."""
import glob, io, os, re
from collections import Counter, defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CH = os.path.join(ROOT, "장v2")
files = sorted(glob.glob(os.path.join(CH, "장*.md"))) + sorted(glob.glob(os.path.join(CH, "부록D_장*.md")))
others = [os.path.join(ROOT, "장부_v2.md"), os.path.join(ROOT, "구조표_v2.md")] + [os.path.join(CH, f"부록{x}.md") for x in "ABC"]
def rel(p): return os.path.relpath(p, ROOT)
BS = chr(92)
TAG = re.compile(BS + BS + r"tag\*?\{([^}]*)\}")
tags = {}   # "6.12" -> (file,line)
dup = []
for p in files:
    for no, ln in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
        for m in TAG.finditer(ln):
            t = m.group(1)
            if t in tags: dup.append((t, tags[t], (rel(p), no)))
            else: tags[t] = (rel(p), no)
bychap = defaultdict(list)
for t in tags:
    m = re.match(r"(\d+)\.(\d+)$", t)
    if m: bychap[int(m.group(1))].append(int(m.group(2)))
    else: bychap["기타"].append(t)
print("## 태그 수:", len(tags), "| 중복:", dup)
for c in sorted(bychap, key=str):
    v = bychap[c]
    if c == "기타": print("   기타:", v); continue
    v = sorted(v); gaps = [i for i in range(1, max(v)+1) if i not in v]
    print(f"   {c}장: ({c}.1)–({c}.{max(v)}) {len(v)}개, 빠진 번호 {gaps}")
tagged_chaps = {c for c in bychap if c != "기타"}
REF = re.compile(r"\((\d{1,2})\.(\d{1,2})\)")
print()
print("## (n.m) 참조 가운데 태그 있는 장 번호(4·5B·6·7B·8)를 가리키면서 태그에 없는 것")
bad = []; ok = Counter(); okwhere = defaultdict(list)
for p in files + others:
    for no, ln in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
        if BS + "tag" in ln: continue
        for m in REF.finditer(ln):
            c = int(m.group(1)); key = f"{c}.{int(m.group(2))}"
            if c in tagged_chaps:
                if key in tags:
                    ok[key] += 1; okwhere[key].append(f"{os.path.basename(p)}:{no}")
                else: bad.append((rel(p), no, m.group(0), ln[max(0,m.start()-60):m.end()+40]))
print("   참조 토큰(태그 있음):", sum(ok.values()), "| 서로 다른 식:", len(ok))
print("   어긋남:", len(bad))
for b in bad: print("    ", b)
print()
print("## 다른 장·파일에서 부르는 식 번호(장 경계를 넘는 참조 — 번호 재부여의 여파 자리)")
for t in sorted(tags, key=lambda x: [int(s) if s.isdigit() else 0 for s in x.split('.')]):
    own = os.path.basename(tags[t][0])
    outside = [w for w in okwhere.get(t, []) if not w.startswith(own.split('.')[0])]
    if outside: print(f"   ({t}) 정의 {tags[t][0]}:{tags[t][1]} ← {outside}")
print()
print("## 태그마다 참조 수(장·부록 D·장부·구조표·부록 A·B·C; 0이면 참조 없는 번호)")
for t in sorted(tags, key=lambda x: [int(s) if s.isdigit() else 0 for s in x.split('.')]):
    print(f"   ({t}) x{ok.get(t,0)}  정의 {tags[t][0]}:{tags[t][1]}")
