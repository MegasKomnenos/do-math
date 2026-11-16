# -*- coding: utf-8 -*-
"""사용자 결정(2026-11-16 11:0x, 결정 122-3): 부록 B의 기록 제목은 record.json의 평문 그대로 적는다 — 두 행(r690be93·r13b0b8f)의 `$…$` 감쌈을 거둔다.
`부록_v2.py`의 title_tex_to_math를 항등으로 바꾸고 부록 B만 다시 만든다(손 편집 머리말 1–4행은 현행 파일에서 유지)."""
import io, os, sys, importlib
ROOT = r"C:\math\임시\주차함수_증명"
G = os.path.join(ROOT, "scripts", "부록_v2.py")
g = io.open(G, encoding="utf-8").read()
old = '''    def wrap(m):
        s = m.group(0)
        if "$" in s:
            return s
        s = s.replace("≥", r"\\ge ").replace("≤", r"\\le ")
        return "$" + s + "$"
    return _TEX_RUN.sub(wrap, title)
'''
new = '''    # 2026-11-16 결정 122-3(사용자): 기록 제목은 고유명이라 평문 그대로 둔다(검색 가능성; 한 표 안의 한 규칙). 감싸지 않는다.
    return title
'''
assert g.count(old) == 1, g.count(old)
io.open(G, "w", encoding="utf-8", newline="\n").write(g.replace(old, new))
print("부록_v2.py ok")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
mod = importlib.import_module("부록_v2")
texts = mod.chapter_texts()
texts_all = dict(texts)
texts_all["부록A.md"] = io.open(os.path.join(ROOT, "장v2", "부록A.md"), encoding="utf-8").read()
texts_all["부록C.md"] = io.open(os.path.join(ROOT, "장v2", "부록C.md"), encoding="utf-8").read()
B, rows_B, missing_B = mod.build_B(texts_all, "415", "438", "2026-11-13")
pB = os.path.join(ROOT, "장v2", "부록B.md")
old_lines = io.open(pB, encoding="utf-8").read().split("\n")
new_lines = B.split("\n")
assert old_lines[4].startswith("| 식별자") and new_lines[4].startswith("| 식별자"), (old_lines[4][:30], new_lines[4][:30])
merged = old_lines[:4] + new_lines[4:]
diff = [(i + 1, a[:90], b[:90]) for i, (a, b) in enumerate(zip(old_lines, merged)) if a != b]
print("식별자", len(rows_B), "폴더 없음", missing_B, "행 수 옛/새", len(old_lines), len(merged))
for d in diff:
    print("  바뀐 행", d[0], "|", d[1], "→", d[2])
assert len(diff) <= 3, "예상 밖의 변경"
assert "$" not in "\n".join(merged[4:]), "표에 $ 남음"
io.open(pB, "w", encoding="utf-8", newline="\n").write("\n".join(merged))
print("부록B.md ok")
