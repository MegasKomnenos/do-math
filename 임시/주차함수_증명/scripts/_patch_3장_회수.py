# -*- coding: utf-8 -*-
"""3장 집필 회수 뒤 세션 판단: 1.3 3.1 묶음의 Gamma(5/6) 변수 Γ→H, 최빈점·x_*의 정의 절 3.2, 지침 7.3 보강."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rw(path, fn):
    s = io.open(path, encoding="utf-8").read()
    t = fn(s)
    if t != s:
        io.open(path, "w", encoding="utf-8", newline="\n").write(t)
        print("patched", os.path.relpath(path, ROOT))
    else:
        print("unchanged", os.path.relpath(path, ROOT))


def patch_ledger(s):
    a = "| $E$, $\\Gamma$, $V$; $\\mathrm B(\\cdot,\\cdot)$ | 곱 표현의 세 독립 변수 Gamma(1), Gamma(5/6), Beta(1/2,1/6)와 베타 함수(명제 3.2) |"
    assert s.count(a) == 1, "3.1 묶음"
    s = s.replace(a, "| $E$, $H$, $V$; $\\mathrm B(\\cdot,\\cdot)$ | 곱 표현의 세 독립 변수 Gamma(1), Gamma(5/6), Beta(1/2,1/6)와 베타 함수(명제 3.2; Gamma(5/6) 변수는 감마 함수 $\\Gamma(\\cdot)$와 겹치지 않게 $H$) |")
    a = "| 최빈점 | 밀도 $f$의 최댓값 자리 $x_\\ast$ | 3.1 |"
    assert s.count(a) == 1, "최빈점"
    s = s.replace(a, "| 최빈점 | 밀도 $f$의 최댓값 자리 $x_\\ast$(유일성은 정리 3.3에 기댄다) | 3.2 |")
    a = "| 밀도 $f$의 최빈점 $0.5996\\ldots$(임계 창 좌표의 특정값) | 3.1 |"
    assert s.count(a) == 1, "x_*"
    s = s.replace(a, "| 밀도 $f$의 최빈점(임계 창 좌표의 특정값) | 3.2 |")
    return s


rw(os.path.join(ROOT, "장부_v2.md"), patch_ledger)


def patch_guide(s):
    a = "덧붙임은 「계산 보조(산술 등급)」, 「작성자 판단」, 「시작점 비명시」(문턱 $N_0$를 명시하지 않는 점근 진술에만), 「X에 의존」(라벨로)뿐이다."
    assert s.count(a) == 1
    add = (" 문헌의 정리(Stirling·Robbins 부등식 같은 표준 부등식을 포함)를 인용해 쓰는 단계가 있으면 그 증명의 지위는 「비형식 증명」이고, 식별자 자리는 그 결과를 세운 기록의 식별자(결과 자체가 문헌의 것이면 「표준」)다. "
           "어느 문헌에 기댔는지는 증명의 그 단계에서 저자·연도로 적는다.")
    if "Stirling·Robbins 부등식 같은 표준 부등식을 포함" not in s:
        s = s.replace(a, a + add)
    return s


rw(os.path.join(ROOT, "파견", "집필_공통지침_v2.md"), patch_guide)
