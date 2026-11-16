# -*- coding: utf-8 -*-
"""V5 (ㄴ): 11.4 표의 행마다 「쓰인 자리」의 라벨·절 번호를 장 파일 위치로 바꾸어 첫 등장 위치를 구하고, 행 순서가 「본문에 처음 나오는 차례」인지 본다.
또 본문에서 저자 이름이 나오는 자리를 감싸는 진술·절과 11.4의 쓰인 자리를 견준다."""
import io, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORDER = ["장1", "장2", "장3", "장4", "장5A", "장5B", "장6", "장7A", "장7B", "장8", "장9", "장10", "장11"]
HEAD = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}")
SEC = re.compile(r"^### (\d+\.\d+)")
CH = re.compile(r"^## (\d+)\.")
labelpos = {}; secpos = {}; lines_by = {}
for ci, name in enumerate(ORDER):
    L = io.open(os.path.join(ROOT, "장v2", name + ".md"), encoding="utf-8").read().split("\n")
    lines_by[name] = L
    for i, l in enumerate(L):
        m = HEAD.match(l)
        if m: labelpos.setdefault(f"{m.group(2)}:{m.group(3)}", (ci, i))
        m = SEC.match(l)
        if m: secpos.setdefault(m.group(1), (ci, i))
# 11.4 표
L11 = lines_by["장11"]
i0 = next(i for i, l in enumerate(L11) if l.startswith("### 11.4"))
rows = [l for l in L11[i0:] if l.startswith("| ") and not l.startswith("| 문헌 |")]
prev = None
for r in rows:
    c = [x.strip() for x in r.strip()[1:-1].split("|")]
    if len(c) < 3: continue
    name = c[0][:28]; place = c[2]
    poss = []
    for m in re.finditer(r"\{\{(\d+:[A-Za-z][A-Za-z0-9\-]*)\}\}", place):
        k = m.group(1)
        if k.startswith("D:"): poss.append(((12, 10**6), "부록 D")); continue
        if k in labelpos: poss.append((labelpos[k], k))
        else: print("  !! 라벨 없음", k, "in", name)
    for m in re.finditer(r"(\d+\.\d+)절", place):
        s = m.group(1)
        if s in secpos: poss.append((secpos[s], s + "절"))
        else: print("  !! 절 없음", s, "in", name)
    if not poss: print("  ?? 자리 없음", name, place[:60]); continue
    first = min(poss)
    flag = "" if prev is None or first[0] >= prev[0] else "  <-- 앞 행보다 먼저 나옴"
    print(f"{ORDER[first[0][0]]}:{first[0][1]+1:5d} {first[1]:28s} | {name}{flag}")
    prev = first
# 저자 이름 자리
AUTH = ["Konheim", "Foata", "Pollak", "Celano", "Aguilar", "Stanley", "Knuth", "Flajolet", "Robbins", "Petersson", "Janson", "Ibragimov", "Ahlfors", "Graham", "Euler–Maclaurin", "Fortuin", "FKG", "Jensen 부등식", "Wallis", "Corless", "Lambert", "Tanner", "OEIS", "Grimmett", "Harris", "Comtet", "Faà", "Apostol", "Titchmarsh", "편각 원리", "coth", "Cauchy"]
print("\n== 본문의 저자 이름 자리(감싸는 진술/절) ==")
for ci, name in enumerate(ORDER[:-1]):
    L = lines_by[name]; cur = None; sec = None
    for i, l in enumerate(L):
        m = HEAD.match(l)
        if m: cur = f"{m.group(1)} {m.group(2)}:{m.group(3)}"
        m = SEC.match(l)
        if m: sec = m.group(1); cur = None
        if l.startswith("**증명.**") is False and HEAD.match(l) is None and l.startswith("### "): cur = None
        for a in AUTH:
            if a in l:
                print(f"  {a:14s} {name}:{i+1:5d}  {cur or ('절 ' + str(sec))}")
