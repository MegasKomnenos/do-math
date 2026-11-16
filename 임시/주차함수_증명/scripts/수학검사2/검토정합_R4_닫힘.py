# -*- coding: utf-8 -*-
"""R4 보조: 두 증명 각각의 의존 닫힘을 계산해 11.3절 세 표와 대조한다(읽기만).
뿌리: 첫째 증명 = 정리 {{9:old-7-46}}, 둘째 증명 = 정리 {{10:old-8-37}}. 주 정리의 머리는 둘에 의존하므로 1.4절 산문은 뿌리에서 뺀다.
"""
import io, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); SCRIPTS = os.path.dirname(HERE); ROOT = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
import _의존_도달 as DEP
LABEL_RE = DEP.LABEL_RE
stmts = DEP.parse_chapters()
r1, _ = DEP.reach(stmts, ["9:old-7-46"])
r2, _ = DEP.reach(stmts, ["10:old-8-37"])
r1 &= set(stmts); r2 &= set(stmts)
shared = r1 & r2; only1 = r1 - r2; only2 = r2 - r1
print(f"첫째 증명 닫힘 {len(r1)}, 둘째 증명 닫힘 {len(r2)}, 공유 {len(shared)}, 첫째만 {len(only1)}, 둘째만 {len(only2)}, 어느 쪽도 아님 {len(set(stmts)-r1-r2)}")
def grades(k):
    m = re.search(r"\[([^\]]*)\]\.\*\*", stmts[k]["head"]); tag = m.group(1) if m else ""
    return re.findall(r"계산 (?:보조|증거)\(([^)]*)\)", tag)
# 11.3 표 읽기
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
print("\n== 1열 입력의 소속 검사 ==")
for tbl, want in [("공유 입력", shared), ("첫째 증명의 고유 입력", only1), ("둘째 증명의 고유 입력", only2)]:
    for i, cells in rows[tbl]:
        for l in labs(cells[0]):
            where = "공유" if l in shared else "첫째만" if l in only1 else "둘째만" if l in only2 else "어느 쪽도 아님"
            if l not in want:
                print(f"  장11:{i} [{tbl}] 1열 {{{{{l}}}}}({stmts[l]['kind']} {stmts[l]['name'][:30]}) → 실제 {where}")
        for l in labs(cells[1]):
            where = "공유" if l in shared else "첫째만" if l in only1 else "둘째만" if l in only2 else "어느 쪽도 아님"
            if l not in want:
                print(f"  장11:{i} [{tbl}] 2열 {{{{{l}}}}}({stmts[l]['kind']} {stmts[l]['name'][:30]}) → 실제 {where}")
print("\n== 닫힘에 들고 머리에 계산 보조·계산 증거가 있는데 11.3 2열 어디에도 없는 진술 ==")
listed = set()
for tbl in rows:
    for i, cells in rows[tbl]: listed |= set(labs(cells[1]))
for k in sorted(r1 | r2, key=lambda k: stmts[k]["order"]):
    if grades(k) and k not in listed:
        where = "공유" if k in shared else "첫째만" if k in only1 else "둘째만"
        print(f"  {{{{{k}}}}} {stmts[k]['kind']} {stmts[k]['name'][:40]} [{where}] 등급 {grades(k)} ({stmts[k]['file']}:{stmts[k]['line']})")
print("\n== 닫힘에 들지만 11.3 어느 열에도 라벨로 안 나오는 앞 장(1–8장) 진술(참고; 묶음 행이 덮는지 손으로 볼 것) ==")
all_listed = set()
for tbl in rows:
    for i, cells in rows[tbl]: all_listed |= set(labs(" | ".join(cells)))
for k in sorted(r1 | r2, key=lambda k: stmts[k]["order"]):
    if k not in all_listed and not k.startswith(("9:", "10:")) and stmts[k]["kind"] != "정의":
        where = "공유" if k in shared else "첫째만" if k in only1 else "둘째만"
        print(f"  {{{{{k}}}}} {stmts[k]['kind']} {stmts[k]['name'][:40]} [{where}] 절 {stmts[k]['section']}")
print("\n== 어느 증명 닫힘에도 없는 진술이 11.3에 든 경우 ==")
for tbl in rows:
    for i, cells in rows[tbl]:
        for l in labs(" | ".join(cells)):
            if l not in r1 and l not in r2:
                print(f"  장11:{i} [{tbl}] {{{{{l}}}}} {stmts[l]['kind']} {stmts[l]['name'][:40]}")
print("\n== 특정 진술을 인용하는 진술 ==")
for target in ["2:old-2-41", "9:old-7-6", "6:log-derivative", "6:insertion", "6:trapezoid", "7:old-6-14", "6:old-7-24", "6:cor-L", "6:diag-first-layer", "5:old-5-28", "3:old-3-6", "2:old-2-34", "6:increment-bounds", "6:D-bound", "2:old-2-46", "2:old-2-44", "6:DD-lower-bound", "6:old-8-12", "6:old-8-13"]:
    users = [k for k, s in stmts.items() if target in (s["head_labels"] | s["body_labels"])]
    print(f"  {{{{{target}}}}} ← {users}")
print("\n== 9장 뿌리와 10장 뿌리의 머리 ==")
for k in ["9:old-7-46", "10:old-8-37", "1:main-theorem"]:
    print(" ", stmts[k]["head"][:700])
