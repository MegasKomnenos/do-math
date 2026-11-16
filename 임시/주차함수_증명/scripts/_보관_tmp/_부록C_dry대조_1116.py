# -*- coding: utf-8 -*-
"""AL(11차): 부록_v2.py가 만드는 부록 C(건조)와 현행 장v2/부록C.md를 절·행 단위로 대조한다(읽기 전용). 2026-11-16."""
import io, os, sys
ROOT = r"C:\math\임시\주차함수_증명"
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib
mod = importlib.import_module("부록_v2")
ledger = io.open(mod.LEDGER, encoding="utf-8").read()
C_gen = mod.build_C(ledger)
C_cur = io.open(os.path.join(ROOT, "장v2", "부록C.md"), encoding="utf-8").read()


def sections(text):
    out, cur = {}, None
    for ln in text.split("\n"):
        if ln.startswith("### "):
            cur = ln.strip()
            out[cur] = []
        elif cur and ln.startswith("|") and not set(ln.replace("|", "").strip()) <= set("-: "):
            out[cur].append(ln.rstrip())
    return out


g, c = sections(C_gen), sections(C_cur)
for sec in g:
    rg, rc = g[sec], c.get(sec, [])
    print("==", sec, "생성", len(rg), "현행", len(rc))
    only_g = [r for r in rg if r not in rc]
    only_c = [r for r in rc if r not in rg]
    print("  생성에만:", len(only_g))
    for r in only_g:
        print("   G|", r[:400])
    print("  현행에만:", len(only_c))
    for r in only_c:
        print("   C|", r[:400])
