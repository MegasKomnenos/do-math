# -*- coding: utf-8 -*-
"""R4 보조: strict(첫 ∎까지) 닫힘, 두 뿌리 사이의 경로, 장별 인용 집합으로 도입 문장의 주장을 검증한다(읽기만)."""
import io, os, re, sys
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__)); SCRIPTS = os.path.dirname(HERE); ROOT = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
import _의존_도달 as DEP
LABEL_RE = DEP.LABEL_RE
def path(stmts, a, b):
    prev = {a: None}; q = deque([a])
    while q:
        x = q.popleft()
        if x == b: break
        for y in stmts[x]["head_labels"] | stmts[x]["body_labels"]:
            if y in stmts and y not in prev:
                prev[y] = x; q.append(y)
    if b not in prev: return None
    out = []; x = b
    while x is not None: out.append(x); x = prev[x]
    return list(reversed(out))
for strict in (False, True):
    stmts = DEP.parse_chapters(strict=strict)
    r1, _ = DEP.reach(stmts, ["9:old-7-46"]); r2, _ = DEP.reach(stmts, ["10:old-8-37"])
    r1 &= set(stmts); r2 &= set(stmts)
    print(f"\n######## strict={strict}: 첫째 {len(r1)}, 둘째 {len(r2)}, 공유 {len(r1&r2)}, 첫째만 {len(r1-r2)}, 둘째만 {len(r2-r1)}")
    print("  첫째만:", sorted(r1 - r2, key=lambda k: stmts[k]['order']))
    print("  둘째만:", sorted(r2 - r1, key=lambda k: stmts[k]['order']))
    for a, b in [("10:old-8-37", "9:old-7-16"), ("10:old-8-37", "7:old-6-22"), ("9:old-7-46", "10:old-8-36"), ("9:old-7-46", "10:old-8-23"), ("10:old-8-37", "9:head-sum-2")]:
        p = path(stmts, a, b)
        print(f"  경로 {a} → {b}: {p}")
    if strict:
        # 계산 보조/증거 머리 중 닫힘에 들고 11.3 2열에 없는 것, 등 재계산
        text = io.open(os.path.join(ROOT, "장v2", "장11.md"), encoding="utf-8").read().split("\n")
        on = False; listed2 = set(); listed_all = set()
        for ln in text:
            if ln.startswith("### 11.3"): on = True; continue
            if ln.startswith("### 11.4"): break
            if on and ln.startswith("| ") and not ln.startswith("|---"):
                cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
                if cells[0] != "입력":
                    listed2 |= {f"{a}:{b}" for a, b in LABEL_RE.findall(cells[1])}
                    listed_all |= {f"{a}:{b}" for a, b in LABEL_RE.findall(" | ".join(cells))}
        print("\n  [strict] 닫힘에 들고 계산 보조·증거가 있으나 11.3 2열에 없는 것:")
        for k in sorted(r1 | r2, key=lambda k: stmts[k]["order"]):
            m = re.search(r"\[([^\]]*)\]\.\*\*", stmts[k]["head"]); tag = m.group(1) if m else ""
            if re.search(r"계산 (보조|증거)\(", tag) and k not in listed2:
                print(f"    {{{{{k}}}}} {stmts[k]['kind']} {stmts[k]['name'][:40]} [{tag[:80]}]")
        print("\n  [strict] 11.3에 들었으나 어느 닫힘에도 없는 것:")
        for l in sorted(listed_all, key=lambda k: stmts[k]["order"] if k in stmts else 0):
            if l in stmts and l not in r1 and l not in r2:
                print(f"    {{{{{l}}}}} {stmts[l]['kind']} {stmts[l]['name'][:40]} 절 {stmts[l]['section']}")
        # 장별 인용 집합
        by_file = {}
        for k, s in stmts.items():
            by_file.setdefault(s["file"], set()).update(s["head_labels"] | s["body_labels"])
        def users_by_chapter(target):
            return sorted({s["file"] for k, s in stmts.items() if target in (s["head_labels"] | s["body_labels"])})
        print("\n  [strict] 도입 주장 검증: 대상 ← 인용하는 장 파일")
        for t in ["2:old-2-34", "2:old-2-40", "2:old-2-41", "2:old-2-46", "2:old-2-44", "4:old-4-6", "4:old-4-7", "6:cor-L", "5:witness-position-bound", "5:old-5-13", "5:old-5-28", "5:zeta-constants", "6:V-all", "6:old-6-19", "6:old-7-13", "6:old-8-11", "6:old-7-21", "6:old-7-24", "6:D-bound", "6:increment-bounds", "6:old-8-13", "6:old-8-12", "6:DD-lower-bound", "6:diag-first-layer", "7:old-6-15", "7:old-6-20", "7:old-6-13", "7:qstar-columns", "7:old-6-22", "7:qstar-implies-wlflat", "7:src-plus", "7:old-6-14", "7:old-6-21", "8:old-6-33", "8:old-6-28", "8:old-6-29", "3:old-3-6", "9:old-7-46", "10:old-8-37", "1:old-1-2", "2:old-2-11", "2:old-2-5", "2:old-2-20", "3:old-3-4", "3:old-3-1", "3:old-3-2", "3:old-3-3"]:
            users = [(k, stmts[k]["file"]) for k, s in stmts.items() if t in (s["head_labels"] | s["body_labels"])]
            print(f"    {{{{{t}}}}} ← " + ", ".join(f"{k}({f})" for k, f in sorted(users, key=lambda u: stmts[u[0]]['order'])))
        # 5장 파일이 뒤 장(6–10) 라벨을 인용하는 자리
        print("\n  [strict] 5장 진술이 6장 이후 라벨을 인용:")
        for k, s in stmts.items():
            if s["file"].startswith("장5"):
                later = [l for l in (s["head_labels"] | s["body_labels"]) if int(l.split(":")[0]) >= 6]
                if later: print(f"    {k} → {later}")
        print("\n  [strict] 4장 진술이 5장 이후 라벨을 인용:")
        for k, s in stmts.items():
            if s["file"].startswith("장4"):
                later = [l for l in (s["head_labels"] | s["body_labels"]) if int(l.split(":")[0]) >= 5]
                if later: print(f"    {k} → {later}")
