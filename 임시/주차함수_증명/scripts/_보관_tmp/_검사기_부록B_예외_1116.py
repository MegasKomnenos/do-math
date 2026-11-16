# -*- coding: utf-8 -*-
"""`_tex_outside_math_check.py` (나) 규칙에 부록 B 기록 제목 행 예외를 넣는다(결정 122-3: 제목은 record.json의 평문 그대로). 2026-11-16."""
import io
p = r"C:\math\임시\주차함수_증명\scripts\_tex_outside_math_check.py"
s = io.open(p, encoding="utf-8").read()
old = '''        plain = re.sub(r"`[^`\\n]*`", "¶", nomath)  # (나)
        m = TEX_IN_TEXT.search(plain)
        if m:'''
new = '''        plain = re.sub(r"`[^`\\n]*`", "¶", nomath)  # (나)
        m = TEX_IN_TEXT.search(plain)
        if m and BOOKB_ROW.match(line):  # 2026-11-16 결정 122-3: 부록 B의 기록 제목은 record.json의 평문 그대로(`r^{3/2}` 등) — (나)의 대상이 아니다
            m = None
        if m:'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
anchor = "def scan_text(text, name):"
assert s.count(anchor) == 1
s = s.replace(anchor, 'BOOKB_ROW = re.compile(r"^\\| r[0-9a-f]{7} \\| \\d\\d-\\d\\d \\d\\d:\\d\\d \\| ")\n\n\n' + anchor)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("checker ok")
