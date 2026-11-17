# -*- coding: utf-8 -*-
"""X4 (ㅁ) 보조: 인용의 종류 낱말(정의·정리·명제·보조정리·따름정리)이 그 라벨의 머리 종류와 같은가. 「정리 {{A}}·{{B}}·보조정리 {{C}}」 사슬은 종류 낱말이 바뀔 때까지 앞 낱말을 잇는다. 읽기 전용."""
import glob, io, os, re
from collections import Counter
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CH = os.path.join(ROOT, "장v2")
files = sorted(glob.glob(os.path.join(CH, "장*.md"))) + sorted(glob.glob(os.path.join(CH, "부록D_장*.md")))
others = [os.path.join(ROOT, "장부_v2.md"), os.path.join(ROOT, "구조표_v2.md")] + [os.path.join(CH, f"부록{x}.md") for x in "ABC"]
def rel(p): return os.path.relpath(p, ROOT)
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}(?!의 증명)")
kind = {}
for p in files:
    for ln in io.open(p, encoding="utf-8").read().split("\n"):
        m = HEAD.match(ln)
        if m: kind[m.group(2)] = m.group(1)
    for m in re.finditer(r"^### D\.\{\{([^}]+)\}\}", io.open(p, encoding="utf-8").read(), re.M):
        kind[m.group(1)] = "D"
CHAIN = re.compile(r"(정의|정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}((?:\s*·\s*\{\{[^}]+\}\})*)")
n = 0; bad = []; nolabel = Counter()
for p in files + others:
    for no, ln in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
        if HEAD.match(ln) or ln.startswith("### D."): pass
        for m in CHAIN.finditer(ln):
            k = m.group(1); labs = [m.group(2)] + re.findall(r"\{\{([^}]+)\}\}", m.group(3))
            # 머리 자체는 건너뛴다
            if HEAD.match(ln) and m.start() == 2: labs = labs[1:]
            for L in labs:
                n += 1
                if L in kind and kind[L] != k:
                    bad.append((rel(p), no, k, L, kind[L], ln[max(0,m.start()-40):m.end()+30]))
        # 종류 낱말 없이 맨 {{라벨}}만 있는 인용(「D.{{」·「{{…}}의 증명」 머리 제외)
        for m in re.finditer(r"(?<![·\s])\{\{([^}]+)\}\}|(?<=\s)\{\{([^}]+)\}\}", ln):
            L = m.group(1) or m.group(2)
            pre = ln[max(0, m.start()-8):m.start()]
            if re.search(r"(정의|정리|명제|보조정리|따름정리) $", pre) or pre.endswith("D.") or pre.endswith("·"): continue
            nolabel[(rel(p), no)] += 1
print("## 종류 낱말 붙은 인용(사슬 풀어 센 것):", n)
print("## 종류 어긋남:", len(bad))
for b in bad: print("  ", b)
print()
print("## 종류 낱말·D. 없이 선 라벨 인용(자리별 수; 표 셀 등 — 읽어 가른다):", sum(nolabel.values()))
for (f, no), c in sorted(nolabel.items()):
    print(f"   {f}:{no} x{c}")
