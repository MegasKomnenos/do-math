# -*- coding: utf-8 -*-
"""X4 (ㅂ) 지위 표지·의존 목록: 머리 대괄호의 「…에 의존」 라벨이 정의되어 있는가, 외부 입력(계산 증거·계산 보조·문헌 인용·의존) 있는 진술만 드는가,
증명 본문이 인용하는 외부 입력 진술이 의존 목록에 빠져 있는가(연쇄). 읽기 전용. 색인이지 판정이 아니다."""
import glob, io, os, re
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CH = os.path.join(ROOT, "장v2")
files = sorted(glob.glob(os.path.join(CH, "장*.md")))
def rel(p): return os.path.relpath(p, ROOT)
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}(?!의 증명)(.*?)\[(.*?)\]\.\*\*")
HEAD0 = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}(?!의 증명)")
PROOF_OF = re.compile(r"^\*\*(?:정의|정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}의 증명")
CITE = re.compile(r"\{\{([^}]+)\}\}")
status = {}; kind = {}; where = {}
blocks = defaultdict(list)   # label -> list of text (statement+proof)
for p in files:
    lines = io.open(p, encoding="utf-8").read().split("\n")
    cur = None
    for i, ln in enumerate(lines):
        m = HEAD0.match(ln)
        if m:
            cur = m.group(2); kind[cur] = m.group(1); where[cur] = (rel(p), i+1)
            m2 = HEAD.match(ln)
            status[cur] = m2.group(4) if m2 else ""
        m = PROOF_OF.match(ln)
        if m: cur = m.group(1)
        if ln.startswith("###"): cur = None
        if cur: blocks[cur].append(ln)
def external(lab):
    s = status.get(lab, "")
    return bool(re.search(r"계산 증거|계산 보조|문헌 인용|에 의존|시작점 비명시", s))
def deps(lab):
    s = status.get(lab, "")
    out = []
    for dep in re.findall(r"((?:[^\[\];]*?)에 의존)", s):
        out += CITE.findall(dep)
    return out
print("## 진술 수:", len(status), "| 외부 입력 표지 있는 진술:", sum(external(l) for l in status))
print()
print("## 의존 목록의 라벨 가운데 정의 없는 것")
for lab in status:
    for d in deps(lab):
        if d not in status: print(f"   {where[lab]} {lab} → {d} (정의 없음)")
print()
print("## 의존 목록이 외부 입력 없는 진술을 드는 자리(1.5절: 의존은 계산·문헌·의존 가진 진술만)")
for lab in status:
    for d in deps(lab):
        if d in status and not external(d): print(f"   {where[lab]} {lab} → {d} [{status[d][:60]}]")
print()
print("## 의존 목록의 라벨 가운데 그 진술·증명 블록이 인용하지 않는 것(색인; 블록 경계는 근사)")
for lab in status:
    txt = "\n".join(blocks[lab])
    cited = set(CITE.findall(txt)) - {lab}
    for d in deps(lab):
        if d not in cited: print(f"   {where[lab]} {lab} → {d} 블록 인용 없음")
print()
print("## 증명 블록이 외부 입력 진술을 인용하는데 머리에 「…에 의존」이 없거나 그 라벨이 빠진 자리(색인)")
for lab in status:
    if kind[lab] == "정의": continue
    txt = "\n".join(blocks[lab])
    cited = set(CITE.findall(txt)) - {lab}
    dl = set(deps(lab))
    miss = [c for c in sorted(cited) if c in status and external(c) and c not in dl and kind.get(c) != "정의"]
    if miss:
        print(f"   {where[lab]} {lab} [{status[lab][:70]}] ← 빠짐: {miss}")
print()
print("## 지위 표지 전수(라벨 | 표지)")
for lab in status:
    print(f"   {where[lab][0]}:{where[lab][1]} {kind[lab]} {lab} | {status[lab]}")
