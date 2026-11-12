# -*- coding: utf-8 -*-
"""세션 결정 38: 교과서 수준의 표준 결과 인용은 지위를 바꾸지 않는다(지침 7.3 재정의). 식별자 rba2ecf→rba2ecf4(세션 소유 파일)."""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rw(path, fn):
    s = io.open(path, encoding="utf-8").read()
    t = fn(s)
    if t != s:
        io.open(path, "w", encoding="utf-8", newline="\n").write(t)
        print("patched", os.path.relpath(path, ROOT))
    else:
        print("unchanged", os.path.relpath(path, ROOT))


def patch_guide(s):
    old = (" 문헌의 정리(Stirling·Robbins 부등식 같은 표준 부등식을 포함)를 인용해 쓰는 단계가 있으면 그 증명의 지위는 「비형식 증명」이고, 식별자 자리는 그 결과를 세운 기록의 식별자(결과 자체가 문헌의 것이면 「표준」)다. "
           "어느 문헌에 기댔는지는 증명의 그 단계에서 저자·연도로 적는다.")
    new = (" 문헌 인용의 지위 규칙(세션 결정 38): 교과서 수준의 **표준 결과**(지수 공식, Lagrange 역변환, Cayley 공식, Stirling·Robbins 부등식, Jensen·Hermite–Hadamard 부등식, Euler–Maclaurin 공식, Borel·Borel–Tanner 분포의 기본 성질 등 조합론·확률론·해석학 교과서에 증명이 실린 것)은 진술과 출처(저자·연도 또는 교과서)를 적고 쓰며 지위를 바꾸지 않는다. "
           "**연구 문헌의 정리**(Petersson, Janson, Fleurat 등 특정 논문의 결과)에 기대는 단계가 있으면 「비형식 증명」이다. 다른 진술(라벨)에 기대는 것은 지위를 바꾸지 않으며 11장 입력표가 적는다. 계산 증거나 계산 보조 진술에 기대면 덧붙임 「X에 의존」(라벨)을 둔다. "
           "식별자 자리는 그 결과를 세운 기록의 식별자이고, 결과 자체가 문헌의 것이면 「표준」이다.")
    assert s.count(old) == 1, "7.3 문장"
    return s.replace(old, new)


rw(os.path.join(ROOT, "파견", "집필_공통지침_v2.md"), patch_guide)


def patch_decisions(s):
    add = r"""
## 8. 집필 중 세션 결정(결정 38–39)

38. **표준 결과 인용과 지위(지침 7.3의 재정의; 2026-11-12 밤).** 2장 2차 대조가 지침 7.3을 글자대로 읽으면 지수 공식·Lagrange 역변환·Stirling 부등식을 인용한 2.10·2.37–2.39가 「비형식 증명」이 되고 2장 거의 전부와 뒤 장들이 연쇄로 내려감을 보였다. 합의 v2 결정 9의 「문헌의 정리」는 이 연구 밖의 **연구 문헌** 결과(Petersson, Janson, Fleurat 등 특정 논문)를 뜻하는 것으로 읽고, 교과서 수준의 표준 결과(지수 공식, Lagrange 역변환, Cayley 공식, Stirling·Robbins, Jensen·Hermite–Hadamard, Euler–Maclaurin, Borel 분포의 기본 성질)는 진술과 출처를 적고 쓰되 지위를 바꾸지 않는다. 다른 진술에 기대는 것도 지위를 바꾸지 않고 11장 입력표가 적으며, 계산 증거·계산 보조에 기대면 「X에 의존」을 덧붙인다. 이 결정으로 3장 정리 3.6(Robbins)과 10장의 다섯 진술은 「증명됨」으로 되돌리고, 8장의 `{{8:explicit-bounds}}`(「증명됨; 표준」)는 그대로다. 사용자에게 보고하며, 사용자가 글자대로의 규칙을 원하면 지위 표지만 일괄로 되돌린다.
39. **식별자 자릿수.** 기록 [rba2ecf…]의 7자리 식별자는 `rba2ecf4`다(설계 문서·명세·장부가 6자리 `rba2ecf`로 적었음). 조립 전 전 파일에서 `rba2ecf`(뒤에 16진수가 없는 것)를 `rba2ecf4`로 바꾼다.
"""
    if "## 8. 집필 중 세션 결정" not in s:
        s = s.rstrip("\n") + "\n" + add
    return s


rw(os.path.join(ROOT, "대조v2", "장부_설계_세션결정.md"), patch_decisions)

ID_RE = re.compile(r"rba2ecf(?![0-9a-f])")
for rel in ("구조표_v2.md", os.path.join("scripts", "명세v2_수정.py"), "의존지도_v2.md", "설계_재구성.md", os.path.join("대조", "자족성_조사4.md")):
    p = os.path.join(ROOT, rel)
    if os.path.exists(p):
        rw(p, lambda s: ID_RE.sub("rba2ecf4", s))
