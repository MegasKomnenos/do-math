# -*- coding: utf-8 -*-
"""_sync_11_2행.py의 cell()에 11.2절 머리말의 약속(「이 문단 머리의 꺾쇠 괄호」→「「재계산」 열의 꺾쇠 괄호」)을 넣는다. 2026-11-15 (9차 O11 3항)."""
import io
p = r"C:\math\임시\주차함수_증명\scripts\_sync_11_2행.py"
s = io.open(p, encoding="utf-8").read()
old = "def cell(s):\n    return re.sub("
new = ("def cell(s):\n"
       "    # 11.2절 머리말의 약속: 부록 D 줄이 표 안의 자리를 가리키는 말은 표의 자리로 바꾼다.\n"
       "    s = s.replace(\"이 문단 머리의 꺾쇠 괄호\", \"「재계산」 열의 꺾쇠 괄호\")\n"
       "    return re.sub(")
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
