# -*- coding: utf-8 -*-
"""수학 검사(태그 5B) 수정 스크립트. 멱등. 앵커가 파일 안에 정확히 한 번 나타날 때만 치환한다.
사용: python -I scripts/수학검사/5B_fix.py"""
import io, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')

def apply(rel, pairs):
    path = os.path.join(ROOT, rel)
    with io.open(path, encoding='utf-8', newline='') as f:
        s = f.read()
    n = 0
    for old, new in pairs:
        c = s.count(old)
        if c == 0 and s.count(new) >= 1:
            continue  # 이미 적용됨(멱등)
        assert c == 1, (rel, old[:70], c)
        s = s.replace(old, new)
        n += 1
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(s)
    print(rel, '치환', n)

# 1. 장5B.md 127행: Robbins 나머지 \epsilon_m(버린 이름) -> \mathrm{rb}_m(장부 634행 정본). 네 곳 모두 같은 양.
apply('장v2/장5B.md', [
    (r"$m!=\sqrt{2\pi m}\,(m/e)^me^{\epsilon_m}$",
     r"$m!=\sqrt{2\pi m}\,(m/e)^me^{\mathrm{rb}_m}$"),
    (r"$\frac1{12m+1}<\epsilon_m<\frac1{12m}$",
     r"$\frac1{12m+1}<\mathrm{rb}_m<\frac1{12m}$"),
    (r"$\mathrm{Bor}(m)=(2\pi)^{-1/2}m^{-3/2}e^{-\epsilon_m}$",
     r"$\mathrm{Bor}(m)=(2\pi)^{-1/2}m^{-3/2}e^{-\mathrm{rb}_m}$"),
    (r"$0<\epsilon_m<1/(12m)$",
     r"$0<\mathrm{rb}_m<1/(12m)$"),
])

# 2. 부록D_장5B.md: 부록 항목 안의 자기 지시(「이 절」·「다음 절」·「앞 절」) -> 부록 항목 번호(D.{{D:…}}; 같은 파일 153·155행의 참조 꼴)
apply('장v2/부록D_장5B.md', [
    # 3행 (D.window-mass-constant)
    ("두 함수의 적분으로 적혔고 이 절에서는 그 두 함수를 단봉 계단 함수로",
     "두 함수의 적분으로 적혔고 D.{{D:window-mass-constant}}에서는 그 두 함수를 단봉 계단 함수로"),
    # 69행 (D.band-check)
    ("모든 위치에서 성립해야 하고 이 절에서는 그 범위를 소구간으로 잘라",
     "모든 위치에서 성립해야 하고 D.{{D:band-check}}에서는 그 범위를 소구간으로 잘라"),
    # 119행 (D.lemma-H-interval)
    ("부호 조건으로 귀결되었다. 이 절에서는 그 영역을 상자로 덮어",
     "부호 조건으로 귀결되었다. D.{{D:lemma-H-interval}}에서는 그 영역을 상자로 덮어"),
    # 121행 (D.lemma-H-interval -> 다음 항목 D.lemma-V-coefficients)
    ("그 관계식은 다음 절의 식 항목에 적는다.",
     "그 관계식은 D.{{D:lemma-V-coefficients}}의 식 항목에 적는다."),
    # 139행 (D.lemma-V-coefficients; 앞 절 = D.lemma-H-interval)
    ("**확인하는 진술.** 앞 절의 상자 평가에 드는 두 보정의 경계는",
     "**확인하는 진술.** D.{{D:lemma-H-interval}}의 상자 평가에 드는 두 보정의 경계는"),
    (r"항들로 이루어진다. 이 절에서는 그 항 $\mathrm{Main}_D$",
     r"항들로 이루어진다. D.{{D:lemma-V-coefficients}}에서는 그 항 $\mathrm{Main}_D$"),
    # 141행 (앞 절 = D.lemma-H-interval)
    (r"$\mathfrak K$이고 앞 절의 식에 나온 보조 변수들은",
     r"$\mathfrak K$이고 D.{{D:lemma-H-interval}}의 식에 나온 보조 변수들은"),
])
