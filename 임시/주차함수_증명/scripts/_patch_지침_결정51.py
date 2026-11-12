# -*- coding: utf-8 -*-
"""집필 공통 지침 v2에 세션 결정 51의 두 문장(계산 증거 괄호 꼴·등급 둘 나열; #### 소절 머리 허용)을 더한다."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "파견", "집필_공통지침_v2.md")
s = io.open(P, encoding="utf-8").read()

a = "장 머리는 `## N. 제목`, 절 머리는 `### N.m 제목`."
assert s.count(a) == 1
if "`####`" not in s:
    s = s.replace(a, a + " 절 안의 소절 머리가 필요하면 `#### 제목`을 쓴다(번호 없음; 조립은 `##`·`###`만 번호에 쓴다; 세션 결정 51).")

b = "산술 등급의 이름은 「정확 정수·유리수」, 「방향 반올림 구간」, 「binary64 사전 오차 해석」, 「<정밀도> 평가, 인증 아님」(예 「배정밀도 평가, 인증 아님」)의 넷뿐이다."
assert s.count(b) == 1
if "계산만으로 선 진술은 「계산 증거(등급); r…」" not in s:
    s = s.replace(b, b + " 계산만으로 선 진술은 「계산 증거(등급); r…」로 적고 「계산 보조」를 함께 적지 않는다. 등급이 둘이면 괄호 안에 쉼표로 나열한다(「계산 보조(정확 정수·유리수, 방향 반올림 구간)」). 괄호 안에 설명 문구를 두지 않는다(세션 결정 51).")

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched 집필_공통지침_v2.md")
