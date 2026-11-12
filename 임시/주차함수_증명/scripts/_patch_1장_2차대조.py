# -*- coding: utf-8 -*-
"""1장 2차 대조 뒤 세션 결정(다른 장과 맞출 열 가지)의 반영: 장부 v2, 구조표, 지침 v2, META."""
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
    # 5절 1장 행: 「수열」 제거(일반어)
    lines = s.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("| 1 | $\\mathrm{PF}_n$"):
            cells = ln.split(" | ")
            cells[2] = cells[2].replace("열; 수열; 수준", "열; 수준")
            lines[i] = " | ".join(cells)
        if ln.startswith("| 열 | 수준 $\\ell$을 고정한 수열"):
            cells = ln.split(" | ")
            cells[3] = "1.3(열), 1.5(열 $k$)"
            lines[i] = " | ".join(cells)
        if ln.startswith("| 중앙 띠 |"):
            lines[i] = ln.replace("$\\nu\\le102$(정리 6.13의 두 띠는", "$1\\le\\nu\\le102$(정리 6.13의 두 띠는").replace("$\\nu\\le40$, $\\nu\\le102$", "$1\\le\\nu\\le40$, $1\\le\\nu\\le102$")
        if ln.startswith("| $n$ | 행(주차함수·숲)의 크기"):
            lines[i] = ln.replace("행(주차함수·숲)의 크기;", "행의 크기(주차함수의 「길이」 $n$, 숲의 「크기」 $n$; 낱말은 대상마다 그렇게 쓴다);")
        if ln.startswith("| $\\ell^\\ast$ |"):
            lines[i] = ln.replace("행 $n$의 것은 $\\ell^\\ast_n$(3.4의 봉우리 위치, 첫 판 8.4의 최빈 위치)", "행 $n$의 것은 가장 작은 증인 $\\ell^\\ast_n$(증인이 여럿이면 가장 작은 첨자; 3.4의 봉우리 위치, 첫 판 8.4의 최빈 위치)")
    s = "\n".join(lines)
    # 3절 주차함수 행: 영어 병기 씨앗
    a = "| 주차함수 | 모든 차가 자리를 얻는 선호 수열 | 1.1 |"
    if s.count(a) == 1:
        s = s.replace(a, "| 주차함수 | 모든 차가 자리를 얻는 선호 수열(영어 병기 parking function; 선형 탐사 linear probing도 1.1에서 한 번) | 1.1 |")
    return s


rw(os.path.join(ROOT, "장부_v2.md"), patch_ledger)


def patch_struct(s):
    lines = s.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("| 1.4 주 정리와 증명의 지도 |") and "{{1:main-theorem}}" not in ln:
            cells = ln.split(" | ")
            cells[1] = "주 정리 `{{1:main-theorem}}`(정리; 지위 비형식 증명; 식별자는 9.6·10.7의 두 닫는 정리의 기록) " + cells[1]
            lines[i] = " | ".join(cells)
    return "\n".join(lines)


rw(os.path.join(ROOT, "구조표_v2.md"), patch_struct)


def patch_guide(s):
    a = "**4.8 경중.**"
    assert s.count(a) == 1
    add = ("**4.7′ 표준 증명의 전개.** 문헌의 표준 증명(Pollak의 순환 논법, Cayley 공식의 증명 등)을 이 글이 전개한 단계에는 「작성자 판단」 표지를 붙이지 않는다. 집필 대조 파일에 「표준 증명 전개」로 적고 문헌을 든다. "
           "「작성자 판단」은 기록에도 문헌에도 없는 단계에만 붙인다. 본문의 수치 표(작은 $n$의 개수 등)는 그 값을 확인한 부록 D 항목(예 `{{D:exact-n20000}}`)을 한 문장으로 가리킨다.\n\n")
    if "4.7′ 표준 증명의 전개" not in s:
        s = s.replace(a, add + a)
    return s


rw(os.path.join(ROOT, "파견", "집필_공통지침_v2.md"), patch_guide)


def patch_meta(s):
    block = r'''
# 2026-11-12 밤: 1장 2차 대조 뒤 세션 결정
EXTRA_NOTES.setdefault(1, []).append("주 정리는 라벨 `{{1:main-theorem}}`의 정리로 세우고 지위는 「비형식 증명」, 식별자는 9.6·10.7의 두 닫는 정리의 기록이다(구조표 9.6·10.7 행). 1.3의 작은 $n$ 표는 부록 D `{{D:exact-n20000}}`을 한 문장으로 가리킨다. 1.5는 뒤 장이 정의하는 낱말(해싱 극한, 극)을 쓰지 않고 좌표의 정의만 적는다. 행 $n$의 증인 $\\ell^\\ast_n$은 가장 작은 증인이다.")

'''
    anchor = "def apply(ch):"
    if "1장 2차 대조 뒤 세션 결정" not in s:
        s = s.replace(anchor, block + anchor)
    return s


rw(os.path.join(ROOT, "scripts", "명세v2_META.py"), patch_meta)
