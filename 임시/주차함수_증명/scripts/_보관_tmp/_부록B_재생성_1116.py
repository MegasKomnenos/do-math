# -*- coding: utf-8 -*-
"""부록 B만 생성기(부록_v2.py)로 다시 만든다(열 이름 「제목」; 부록 A·C는 손 편집본이라 건드리지 않음). 2026-11-16."""
import io, os, sys
ROOT = r"C:\math\임시\주차함수_증명"
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib
mod = importlib.import_module("부록_v2")
texts = mod.chapter_texts()
texts_all = dict(texts)
texts_all["부록A.md"] = io.open(os.path.join(ROOT, "장v2", "부록A.md"), encoding="utf-8").read()
texts_all["부록C.md"] = io.open(os.path.join(ROOT, "장v2", "부록C.md"), encoding="utf-8").read()
B, rows_B, missing_B = mod.build_B(texts_all, "415", "438", "2026-11-13")
old = io.open(os.path.join(ROOT, "장v2", "부록B.md"), encoding="utf-8").read()
print("식별자", len(rows_B), "폴더 없음", missing_B)
old_rows = [l for l in old.split("\n") if l.startswith("| r")]
new_rows = [l for l in B.split("\n") if l.startswith("| r")]
print("행 수 옛/새", len(old_rows), len(new_rows), "행 집합 같음:", set(old_rows) == set(new_rows))
diff = [l for l in old.split("\n") if l not in B.split("\n")]
print("옛 판에만 있는 줄:", [d[:120] for d in diff][:5])
io.open(os.path.join(ROOT, "장v2", "부록B.md"), "w", encoding="utf-8", newline="\n").write(B)
print("written 부록B.md", len(B))
