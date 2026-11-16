# -*- coding: utf-8 -*-
"""V4: 부록_v2.py의 build_A·build_C를 import해 건조 실행하고 현재 판과 행 단위로 대조한다. 파일을 쓰지 않는다."""
import io, os, sys, difflib
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib
gen = importlib.import_module("부록_v2")
ledger = io.open(gen.LEDGER, encoding="utf-8").read()
texts = gen.chapter_texts()
body = "\n".join(texts.values())
A, missing = gen.build_A(ledger, body)
C = gen.build_C(ledger)
curA = io.open(os.path.join(ROOT, "장v2", "부록A.md"), encoding="utf-8").read()
curC = io.open(os.path.join(ROOT, "장v2", "부록C.md"), encoding="utf-8").read()
print("부록 A: 본문에 바탕 토큰 없는 1.2 행", len(missing), missing)
for name, g, c in (("A", A, curA), ("C", C, curC)):
    gl = [l for l in g.split("\n")]
    cl = [l for l in c.split("\n")]
    print(f"\n===== 부록 {name}: 생성본 {len(gl)}행, 현재 {len(cl)}행 =====")
    gs, cs = set(gl), set(cl)
    only_gen = [l for l in gl if l not in cs and l.strip()]
    only_cur = [l for l in cl if l not in gs and l.strip()]
    print(f"-- 생성본에만 있는 행 {len(only_gen)}")
    for l in only_gen: print("G>", l)
    print(f"-- 현재 판에만 있는 행 {len(only_cur)}")
    for l in only_cur: print("C>", l)
