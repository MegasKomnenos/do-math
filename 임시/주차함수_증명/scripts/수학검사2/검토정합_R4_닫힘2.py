# -*- coding: utf-8 -*-
"""R4 보조 2: strict 본문(첫 ∎까지) + 10.7절 고리 산문을 정리 {{10:old-8-37}}의 증명으로 귀속한 닫힘으로 11.3절 세 표의 소속을 검사한다(읽기만)."""
import io, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); SCRIPTS = os.path.dirname(HERE); ROOT = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
import _의존_도달 as DEP
LABEL_RE = DEP.LABEL_RE
stmts = DEP.parse_chapters(strict=True)
t10 = io.open(os.path.join(DEP.BASE, "장10.md"), encoding="utf-8").read().split("\n")
s = next(i for i, l in enumerate(t10) if l.startswith("### 10.7"))
e = next(i for i, l in enumerate(t10) if l.startswith("**정리 {{10:old-8-37}}"))
extra = {f"{a}:{b}" for ln in t10[s:e] for a, b in LABEL_RE.findall(ln)} - {"9:old-7-46"}  # 「정리 9.56의 증명 마지막 고리와 같다」는 비교 언급이라 뺀다
stmts["10:old-8-37"]["body_labels"] |= extra
print("10.7 고리 산문이 인용하는 라벨:", sorted(extra))
r1, _ = DEP.reach(stmts, ["9:old-7-46"]); r2, _ = DEP.reach(stmts, ["10:old-8-37"])
r1 &= set(stmts); r2 &= set(stmts)
shared, only1, only2 = r1 & r2, r1 - r2, r2 - r1
print(f"첫째 {len(r1)}, 둘째 {len(r2)}, 공유 {len(shared)}, 첫째만 {len(only1)}, 둘째만 {len(only2)}, 어느 쪽도 아님 {len(set(stmts)-r1-r2)}")
def where(l): return "공유" if l in shared else "첫째만" if l in only1 else "둘째만" if l in only2 else "어느 쪽도 아님"
text = io.open(os.path.join(ROOT, "장v2", "장11.md"), encoding="utf-8").read().split("\n")
on = False; cur = None; rows = {"공유 입력": [], "첫째 증명의 고유 입력": [], "둘째 증명의 고유 입력": []}
for i, ln in enumerate(text, 1):
    if ln.startswith("### 11.3"): on = True; continue
    if ln.startswith("### 11.4"): break
    if on and ln.startswith("**") and ln.endswith("**"): cur = ln.strip("*").rstrip(".")
    if on and cur in rows and ln.startswith("| ") and not ln.startswith("|---"):
        cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
        if cells[0] != "입력": rows[cur].append((i, cells))
def labs(s): return [f"{a}:{b}" for a, b in LABEL_RE.findall(s)]
print("\n== 1열·2열 라벨의 소속이 표와 다른 것 ==")
for tbl, want in [("공유 입력", "공유"), ("첫째 증명의 고유 입력", "첫째만"), ("둘째 증명의 고유 입력", "둘째만")]:
    for i, cells in rows[tbl]:
        for col in (0, 1):
            for l in labs(cells[col]):
                w = where(l)
                if w != want:
                    print(f"  장11:{i} [{tbl}] {col+1}열 {{{{{l}}}}}({stmts[l]['kind']} {stmts[l]['name'][:28]}) → 실제 {w}")
print("\n== 닫힘에 들고 머리에 계산 보조·증거가 있으나 11.3 2열에 없는 것 ==")
listed2 = set(); listed_all = set()
for tbl in rows:
    for i, cells in rows[tbl]:
        listed2 |= set(labs(cells[1])); listed_all |= set(labs(" | ".join(cells)))
for k in sorted(r1 | r2, key=lambda k: stmts[k]["order"]):
    m = re.search(r"\[([^\]]*)\]\.\*\*", stmts[k]["head"]); tag = m.group(1) if m else ""
    if re.search(r"계산 (보조|증거)\(", tag) and k not in listed2:
        print(f"  {{{{{k}}}}} {stmts[k]['kind']} {stmts[k]['name'][:40]} [{where(k)}] ({stmts[k]['file']}:{stmts[k]['line']})")
print("\n== 11.3에 들었으나 어느 닫힘에도 없는 것 ==")
for l in sorted(listed_all, key=lambda k: stmts[k]["order"] if k in stmts else 0):
    if l in stmts and l not in r1 and l not in r2:
        print(f"  {{{{{l}}}}} {stmts[l]['kind']} {stmts[l]['name'][:40]} 절 {stmts[l]['section']}")
print("\n== 닫힘(1–8장, 정의 제외)에 들지만 11.3 어느 열에도 없는 것 ==")
for k in sorted(r1 | r2, key=lambda k: stmts[k]["order"]):
    if k not in listed_all and not k.startswith(("9:", "10:")) and stmts[k]["kind"] != "정의":
        print(f"  {{{{{k}}}}} {stmts[k]['kind']} {stmts[k]['name'][:36]} [{where(k)}] 절 {stmts[k]['section']}")
print("\n== 9장·10장 진술 가운데 닫힘에 들고 머리에 계산 보조가 있는 것(11.3 고유 표 대조용) ==")
for k in sorted(r1 | r2, key=lambda k: stmts[k]["order"]):
    if k.startswith(("9:", "10:")):
        m = re.search(r"\[([^\]]*)\]\.\*\*", stmts[k]["head"]); tag = m.group(1) if m else ""
        if "계산 보조" in tag: print(f"  {{{{{k}}}}} [{where(k)}] {'11.3에 있음' if k in listed2 else '11.3 2열에 없음'}: {tag[:90]}")
