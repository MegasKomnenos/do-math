# -*- coding: utf-8 -*-
"""R1b: 머리 괄호의 [r…] 기록 ↔ 쌍반점 뒤 식별자 목록 ↔ 부록 B 등재 대조(장6·7A·7B). 읽기만."""
import io, os, re
ROOT = r"C:\math\임시\주차함수_증명"
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{((6|7):[A-Za-z0-9\-]+)\}\}(?: \((.*?)\))?(?: \[(.*?)\])?[.．]?\*\*")
B = io.open(os.path.join(ROOT, "장v2", "부록B.md"), encoding="utf-8").read()
Bids = set(re.findall(r"\br[0-9a-f]{7}\b", B))
print("부록 B 식별자 수:", len(Bids))
allids = set()
for f in ["장6.md", "장7A.md", "장7B.md"]:
    for i, ln in enumerate(io.open(os.path.join(ROOT, "장v2", f), encoding="utf-8").read().split("\n"), 1):
        m = HEAD.match(ln)
        if not m: continue
        kind, lab, _, name, st = m.groups()
        name = name or ""; st = st or ""
        ids = set(re.findall(r"\br[0-9a-f]{7}\b", st.rsplit(";", 1)[1])) if ";" in st else set(re.findall(r"\br[0-9a-f]{7}\b", st))
        pids = set(re.findall(r"\br[0-9a-f]{7}\b", name))
        allids |= ids | pids
        if pids - ids:
            print(f"!! 괄호 기록이 식별자 목록에 없음: {f}:{i} {{{{{lab}}}}} 괄호={sorted(pids)} 식별자={sorted(ids)}")
        for r in (ids | pids):
            if r not in Bids:
                print(f"!! 부록 B에 없는 식별자: {f}:{i} {{{{{lab}}}}} {r}")
print("장6·7 머리의 식별자 수:", len(allids))
