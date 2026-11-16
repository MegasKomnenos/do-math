# -*- coding: utf-8 -*-
"""_check_조사.py의 정규식에 식 번호 「(7.21)」 뒤 조사도 넣는다(10차 R7 인계). 2026-11-16."""
import io
p = r"C:\math\임시\주차함수_증명\scripts\_check_조사.py"
s = io.open(p, encoding="utf-8").read()
old = 'r"(?:(?:정의|정리|명제|보조정리|따름정리) \\d+\\.\\d*(\\d)|부록 D\\.\\d*(\\d))"'
new = 'r"(?:(?:정의|정리|명제|보조정리|따름정리) \\d+\\.\\d*(\\d)|부록 D\\.\\d*(\\d)|\\(\\d+\\.\\d*(\\d)\\))"'
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)
old2 = "            digit = m.group(1) or m.group(2)\n            particle = m.group(3)"
new2 = "            digit = m.group(1) or m.group(2) or m.group(3)\n            particle = m.group(4)"
assert s.count(old2) == 1
s = s.replace(old2, new2)
s = s.replace('"""조립본에서 진술 번호·부록 D 번호 바로 뒤의 조사가', '"""조립본에서 진술 번호·부록 D 번호·식 번호 「(7.21)」 바로 뒤의 조사가')
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
