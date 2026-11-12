# -*- coding: utf-8 -*-
"""명세 META에 11장 추가 지시(EXTRA_NOTES)를 더한다: 조립본 기반 입력표·문헌 목록 전수·표 틀·출력 한도."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "scripts", "명세v2_META.py")
s = io.open(P, encoding="utf-8").read()
MARK = "# --- 11장 추가 지시(세션, 2026-11-13) ---"
if MARK not in s:
    add = '''
''' + MARK + '''
EXTRA_NOTES.setdefault(11, []).append("11장은 1–10장이 모두 조립된 뒤에 쓴다. 전체 흐름과 번호는 조립본 `원고.md`에서 읽고, 다른 장의 진술을 가리킬 때는 라벨(`장v2/장N.md`의 진술 머리에 있는 `{{N:이름}}`)로 적는다(조립이 번호로 바꾼다). 11장에는 진술이 없으므로 라벨을 새로 만들지 않는다.")
EXTRA_NOTES.setdefault(11, []).append("11.3의 공유 입력·고유 입력 표는 첫 판 표를 옮기지 않고 조립본에서 다시 만든다: 7.8·9.6·10.7의 고리 문장, 9장·10장 닫는 정리의 머리에 적힌 「…에 의존」과 증명이 부르는 라벨을 읽어, 두 증명이 함께 기대는 입력과 각각만 기대는 입력을 라벨로 적는다(근거 열에 그 입력을 쓰는 자리의 라벨). 지위 낱말은 1.5의 정의와 지침 7.3 현행(세션 결정 38: 라벨 의존은 지위를 바꾸지 않고, 계산 진술에 기댈 때만 「X에 의존」)대로 적고 되풀이해 설명하지 않는다.")
EXTRA_NOTES.setdefault(11, []).append("11.2는 표의 틀(열: 부록 D 항목 라벨 `부록 D.{{D:이름}}`, 확인하는 진술의 라벨, 산술 등급, 쓰인 곳(장·절), 독립 재계산)과 머리 산문만 쓰고 행 자리에 `<!-- 세션 채움 -->` 한 줄을 둔다. 산술 등급의 이름은 넷뿐이다(지침 7.3).")
EXTRA_NOTES.setdefault(11, []).append("11.4의 문헌 목록은 첫 판 목록을 베끼지 않는다. 조립본 1–10장(과 부록 D 조각)에서 실제로 인용된 학술 문헌을 전부 찾아(저자·연도·제목·정리 번호를 적은 자리를 grep으로 모은다) 저자·제목·판·정리 번호·이 글에서 쓰인 자리(라벨)를 적는다. 예상되는 것: Konheim–Weiss, Pollak, Petersson, Janson, Cayley, Stanley *Enumerative Combinatorics* 2권(Prop. 5.3.2, Thm 5.4.2), Flajolet–Sedgewick *Analytic Combinatorics*, Robbins 1955, Fortuin–Kasteleyn–Ginibre 1971·Harris 1960·Grimmett *Percolation* Thm 2.4, Fekete, Tanner(Borel–Tanner), Faà di Bruno, Hermite–Hadamard, Jensen, Euler–Maclaurin(Apostol), Corless 외 1996(Lambert W), Wallis. 본문에 없는 문헌은 적지 않고, 본문에 있는데 목록에 빠진 것이 없게 한다.")
EXTRA_NOTES.setdefault(11, []).append("11.1은 연구 체계를 출처를 읽는 데 필요한 만큼만 말한다: 식별자 [r…]는 결과를 처음 세운 연구 기록이고 각 기록은 작성과 독립된 검토를 거쳤으며 이 글의 진술과 상수는 그 검토가 확인한 것이라는 일반 문장. 개별 정정·운영 경위·세션은 적지 않는다. 지위 낱말의 뜻은 1.5를 가리키지도 되풀이하지도 않는다.")
EXTRA_NOTES.setdefault(11, []).append("한 번의 도구 호출로 쓰는 분량은 12,000 토큰 이하로 나눈다(장 파일은 절 단위로 나누어 쓴 뒤 이어 붙인다). 반환문도 6,000 토큰 이하.")
'''
    anchor = '\nif __name__ == "__main__":'
    assert s.count(anchor) == 1
    s = s.replace(anchor, add + anchor)
    io.open(P, "w", encoding="utf-8", newline="\n").write(s)
    print("patched 명세v2_META.py (11장 EXTRA_NOTES)")
else:
    print("unchanged")
