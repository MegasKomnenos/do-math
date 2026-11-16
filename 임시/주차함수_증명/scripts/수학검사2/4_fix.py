# -*- coding: utf-8 -*-
"""수학검사2 태그 4 수정 스크립트 (멱등). python -I scripts/수학검사2/4_fix.py
보조정리 gauss-contraction (나) 잔차 상계: 글에 적힌 네 항의 합
(1/3+4e-5)*11328660 + 468018 + 291 + 1 = 4244983.1464 이므로 상계 정수 4244983은 내림이다.
가장 가까운 바른 방향의 값 4244984로 고친다(뒤의 4.25e6 상계는 그대로 선다).
"""
import io, sys
PATH = r"C:\math\임시\주차함수_증명\장v2\장4.md"
FIXES = [
    (r"모두 더하면 $|\mathcal R(\iota)|\le4244983\,\mathfrak x^4\le4.25\cdot10^6\mathfrak x^4$다.",
     r"모두 더하면 $|\mathcal R(\iota)|\le4244984\,\mathfrak x^4\le4.25\cdot10^6\mathfrak x^4$다."),
]
s = io.open(PATH, encoding="utf-8").read()
changed = 0
for old, new in FIXES:
    c_old, c_new = s.count(old), s.count(new)
    if c_old == 0 and c_new == 1:
        print("이미 적용됨:", new[:40]); continue
    if c_old != 1:
        print("앵커 수가 1이 아님(%d): %s" % (c_old, old[:60])); sys.exit(1)
    s = s.replace(old, new); changed += 1
if changed:
    io.open(PATH, "w", encoding="utf-8", newline="\n").write(s)
print("적용한 치환 수:", changed)
