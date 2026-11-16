# -*- coding: utf-8 -*-
"""수학 검사 7A: 장v2/장7A.md의 토큰 수정(멱등). 앵커가 정확히 한 번 나타날 때만 치환한다.
실행: python -I scripts/수학검사/7A_fix.py"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "장v2", "장7A.md")

# (앵커, 치환) — 한 수정은 한 토큰.
FIXES = [
    # 7.2 보조정리 prime-decomposition 증명 (라): C_∞의 멱급수는 수렴반경 1/e, T(x)의 실수 가지도 [0,1/e]까지이므로
    # 급수 비교의 범위를 「x≥0」에서 「0≤x≤1/e」로 좁힌다(외부 검토 지적). 증명이 쓰는 값은 x=1/e뿐이다.
    (r"$C_{n,k}\le C_{n,n}$이므로 $x\ge0$에서 $C_k(x)\le C_\infty(x)=1-e^{-T(x)}$이고",
     r"$C_{n,k}\le C_{n,n}$이므로 $0\le x\le1/e$에서 $C_k(x)\le C_\infty(x)=1-e^{-T(x)}$이고"),
]

s = io.open(PATH, encoding="utf-8").read()
orig = s
for old, new in FIXES:
    c_old, c_new = s.count(old), s.count(new)
    if c_old == 0 and c_new == 1:
        print("이미 적용됨:", new[:60])
        continue
    if c_old != 1:
        print(f"앵커가 {c_old}번 나타남, 건너뜀:", old[:60]); sys.exit(1)
    s = s.replace(old, new)
    print("치환:", old[:60], "->", new[:60])
if s != orig:
    io.open(PATH, "w", encoding="utf-8", newline="").write(s)
    print("저장:", PATH)
else:
    print("변경 없음")

# --- 부록 D 조각: 비트 표기 통일(코디네이터 추가 과제). 7장 조각의 다른 표기 「$64$비트」·「$128$비트」와 같은 꼴로 맞춘다.
PATH_D = os.path.join(ROOT, "장v2", "부록D_장7A.md")
FIXES_D = [
    (r"방향 반올림 구간. 144비트 고정소수점 정수 구간이고", r"방향 반올림 구간. $144$비트 고정소수점 정수 구간이고"),
    (r"기록의 독립 재계산은 160비트, 이 글의 재계산은", r"기록의 독립 재계산은 $160$비트, 이 글의 재계산은"),
    (r"\mathfrak e_{n-1-j}$를 160비트 정수 구간으로 직접 계산하는", r"\mathfrak e_{n-1-j}$를 $160$비트 정수 구간으로 직접 계산하는"),
]
s = io.open(PATH_D, encoding="utf-8").read()
orig = s
for old, new in FIXES_D:
    c_old, c_new = s.count(old), s.count(new)
    if c_old == 0 and c_new == 1:
        print("이미 적용됨:", new[:60]); continue
    if c_old != 1:
        print(f"앵커가 {c_old}번 나타남, 건너뜀:", old[:60]); sys.exit(1)
    s = s.replace(old, new); print("치환:", old[:60], "->", new[:60])
if s != orig:
    io.open(PATH_D, "w", encoding="utf-8", newline="").write(s); print("저장:", PATH_D)
else:
    print("변경 없음(부록 D)")
