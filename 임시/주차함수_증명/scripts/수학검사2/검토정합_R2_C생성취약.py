# -*- coding: utf-8 -*-
"""R2 (ㄷ): 장부 3절 넷째 열(첫 판의 낱말)에 생성기 clean()이 메모로 보고 지우는 조각이 있어 재생성 때 부록 C 행이 사라지거나 바뀌는 행을 찾는다(읽기 전용)."""
import io, os, sys, importlib.util
ROOT = r"C:\math\임시\주차함수_증명"
spec = importlib.util.spec_from_file_location("buro", os.path.join(ROOT, "scripts", "부록_v2.py"))
buro = importlib.util.module_from_spec(spec); spec.loader.exec_module(buro)
L = io.open(os.path.join(ROOT, "장부_v2.md"), encoding="utf-8").read().split("\n")
out = io.StringIO()
for n in range(502, 706):
    ln = L[n]
    if not ln.startswith("|") or ln.startswith("|---"): continue
    c = [x.strip() for x in ln.strip().strip("|").split(" | ")]
    if len(c) < 4 or c[0] == "낱말": continue
    raw, cl = c[3], buro.clean(c[3])
    if raw != cl:
        out.write(f"[{n+1}] {c[0][:30]} | 원문: {raw[:120]} | 정제: {cl[:120]}\n")
sys.stdout.buffer.write(out.getvalue().encode("utf-8"))
