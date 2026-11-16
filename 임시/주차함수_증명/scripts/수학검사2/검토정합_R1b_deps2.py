# -*- coding: utf-8 -*-
"""R1b: (1) 「…에 의존」 목록의 라벨 가운데 외부 입력(계산 보조·계산 증거·문헌 인용·에 의존)이 없는 진술; (2) 계산 보조·계산 증거 머리 ↔ 의존지도 1절 「부록 D 계산」 열. 읽기만."""
import io, os, re, sys
sys.path.insert(0, r"C:\math\임시\주차함수_증명\scripts")
from _의존_도달 import parse_chapters
ROOT = r"C:\math\임시\주차함수_증명"
stmts = parse_chapters()
KEY = ("계산 보조", "계산 증거", "문헌 인용", "에 의존")
def status(s):
    m = re.search(r"\[(.*?)\]\.\*\*", s["head"]); st = m.group(1) if m else ""
    return st.rsplit(";", 1)[0] if ";" in st else st
tainted = {k for k, s in stmts.items() if any(x in status(s) for x in KEY)}
print("== 의존 목록에 든 비오염 진술 (장6·7) ==")
for k, s in stmts.items():
    if not (k.startswith("6:") or k.startswith("7:")): continue
    st = status(s)
    m = re.search(r"((?:[^\[\]]*?)에 의존)", st)
    if not m: continue
    deps = set(re.findall(r"\{\{(\d+:[A-Za-z0-9\-]+)\}\}", m.group(1)))
    bad = [d for d in deps if d not in tainted]
    if bad:
        print(f"  {{{{{k}}}}} ({s['file']}:{s['line']}): 비오염 의존 {bad} — 그 머리: " + "; ".join(f"{{{{{d}}}}}=[{status(stmts[d])}]" for d in bad))
print("\n== 의존지도 1절 「부록 D 계산」 열 대조 ==")
rows = {}
for ln in io.open(os.path.join(ROOT, "의존지도_v2.md"), encoding="utf-8").read().split("\n"):
    m = re.match(r"\| `\{\{((6|7):[A-Za-z0-9\-]+)\}\}` \|", ln)
    if m:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows[m.group(1)] = cells
for k, s in stmts.items():
    if not (k.startswith("6:") or k.startswith("7:")): continue
    st = status(s)
    has_calc = ("계산 보조" in st) or ("계산 증거" in st)
    cells = rows.get(k)
    if cells is None:
        print(f"  !! 의존지도에 행 없음: {k}"); continue
    dcol = cells[8] if len(cells) > 8 else "?"
    if has_calc and dcol.strip() in ("없음", "—", ""):
        print(f"  !! 계산 표지 있으나 의존지도 D열 비어 있음: {k} | {dcol}")
    if (not has_calc) and dcol.strip() not in ("없음", "—", ""):
        print(f"  ?? 계산 표지 없는데 의존지도 D열 있음: {k} | {dcol}")
    if cells[4].strip() != st.strip():
        print(f"  !! 의존지도 지위 열 ≠ 머리: {k} | 지도 「{cells[4]}」 / 머리 「{st}」")
print("끝")
