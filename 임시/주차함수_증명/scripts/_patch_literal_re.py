# -*- coding: utf-8 -*-
"""조립.py의 LITERAL_RE 오탐 수정: 「따름정리 5.34」 안의 「정리 5.3」, 「5.32」의 앞부분 매치를 막는다."""
import io

p = "임시/주차함수_증명/scripts/조립.py"
s = io.open(p, encoding="utf-8").read()
old = 'LITERAL_RE = re.compile(r"(?<!\\{\\{old:)(정리|명제|보조정리|따름정리|정의) \\d+\\.\\d+(?!\\}\\})")'
assert s.count(old) == 1, s.count(old)
new = 'LITERAL_RE = re.compile(r"(?<![가-힣{:])(정리|명제|보조정리|따름정리|정의) \\d+\\.\\d+(?![\\d}])")'
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("LITERAL_RE fixed")
