# -*- coding: utf-8 -*-
"""R1b: 머리 괄호의 「기록 […]의 이름」 ↔ 장부 4절 ↔ 부록 C 기록 이름 표 대조(장6·7A·7B). 읽기만."""
import io, os, re
ROOT = r"C:\math\임시\주차함수_증명"
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{((6|7):[A-Za-z0-9\-]+)\}\}(?: \((.*?)\))?(?: \[(.*?)\])?[.．]?\*\*")
heads = {}
for f in ["장6.md", "장7A.md", "장7B.md"]:
    for i, ln in enumerate(io.open(os.path.join(ROOT, "장v2", f), encoding="utf-8").read().split("\n"), 1):
        m = HEAD.match(ln)
        if m:
            kind, lab, _, name, st = m.groups()
            name = name or ""
            if "; 기록" in name:
                title, rec = name.split("; ", 1)
            else:
                title, rec = name, ""
            heads[lab] = dict(kind=kind, title=title, rec=rec, where=f"{f}:{i}")
# 장부 4절
ledger = io.open(os.path.join(ROOT, "장부_v2.md"), encoding="utf-8").read().split("\n")
L = {}
for i, ln in enumerate(ledger, 1):
    m = re.search(r"\{\{((6|7):[A-Za-z0-9\-]+)\}\}", ln)
    if 706 <= i < 1147 and ln.startswith("|") and m:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        L[m.group(1)] = (cells, i)
# 부록 C 이름표
C = io.open(os.path.join(ROOT, "장v2", "부록C.md"), encoding="utf-8").read().split("\n")
Crows = []
for i, ln in enumerate(C, 1):
    if 154 <= i < 432 and ln.startswith("|"):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        Crows.append((cells, i))
print("부록 C 이름표 머리:", Crows[0][0] if Crows else None)
print("장부 4절 머리:", [c.strip() for c in ledger[706:712] if c.startswith("|")][:2])
for lab, h in heads.items():
    cells, li = L.get(lab, (None, None))
    if cells is None:
        print(f"!! 장부 4절에 없음: {lab}")
        continue
    # 장부: | 첫판번호 | 종류 | 제목 | 기록이름 | 절 | 라벨 |
    if cells[1] != h["kind"]: print(f"!! 종류 불일치 {lab}: 머리 {h['kind']} / 장부 {cells[1]} (장부:{li})")
    if cells[2] != h["title"]: print(f"!! 제목 불일치 {lab}: 머리 「{h['title']}」 / 장부 「{cells[2]}」 (장부:{li})")
    if cells[3] != h["rec"]: print(f"!! 기록 이름 불일치 {lab}: 머리 「{h['rec']}」 / 장부 「{cells[3]}」 (장부:{li})")
    # 부록 C: 라벨 또는 기록 이름으로 찾기
    hit = [(c, i) for c, i in Crows if any(f"{{{{{lab}}}}}" in x for x in c)]
    if not hit and h["rec"]:
        hit = [(c, i) for c, i in Crows if h["rec"] in " ".join(c)]
    if h["rec"] and not hit:
        print(f"?? 부록 C 이름표에 없음: {lab} 「{h['rec']}」")
    elif hit:
        for c, i in hit:
            joined = " | ".join(c)
            if h["rec"] and h["rec"] not in joined and h["rec"].replace("기록 ", "") not in joined:
                print(f"?? 부록 C 행과 기록 이름 다름 {lab}: 머리 「{h['rec']}」 / C:{i} 「{joined[:200]}」")
