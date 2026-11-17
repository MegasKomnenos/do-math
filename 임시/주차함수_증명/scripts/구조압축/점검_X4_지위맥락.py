# -*- coding: utf-8 -*-
"""X4 (ㅂ) 보조: 점검_X4_지위.py가 「빠짐」으로 색인한 (진술, 라벨) 쌍마다 그 진술 블록에서 라벨을 인용하는 문장을 찍는다(읽을 자리 안내)."""
import glob, io, os, re
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CH = os.path.join(ROOT, "장v2")
files = sorted(glob.glob(os.path.join(CH, "장*.md")))
HEAD0 = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}(?!의 증명)")
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}(?!의 증명)(.*?)\[(.*?)\]\.\*\*")
PROOF_OF = re.compile(r"^\*\*(?:정의|정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}의 증명")
CITE = re.compile(r"\{\{([^}]+)\}\}")
status = {}; kind = {}; blocks = defaultdict(list)
for p in files:
    lines = io.open(p, encoding="utf-8").read().split("\n"); cur = None
    for i, ln in enumerate(lines):
        m = HEAD0.match(ln)
        if m:
            cur = m.group(2); kind[cur] = m.group(1); m2 = HEAD.match(ln); status[cur] = m2.group(4) if m2 else ""
        m = PROOF_OF.match(ln)
        if m: cur = m.group(1)
        if ln.startswith("###"): cur = None
        if cur: blocks[cur].append((os.path.basename(p), i+1, ln))
def external(lab): return bool(re.search(r"계산 증거|계산 보조|문헌 인용|에 의존|시작점 비명시", status.get(lab, "")))
def deps(lab):
    out = []
    for dep in re.findall(r"((?:[^\[\];]*?)에 의존)", status.get(lab, "")): out += CITE.findall(dep)
    return out
for lab in status:
    if kind[lab] == "정의": continue
    dl = set(deps(lab))
    for f, no, ln in blocks[lab]:
        for c in set(CITE.findall(ln)) - {lab}:
            if c in status and external(c) and c not in dl and kind.get(c) != "정의":
                i = ln.find("{{" + c + "}}")
                print(f"{lab} [{status[lab][:50]}] ← {c} [{status[c][:40]}] @ {f}:{no}\n      …{ln[max(0,i-140):i+80]}…")
