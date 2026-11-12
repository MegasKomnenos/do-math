# -*- coding: utf-8 -*-
"""11장 집필자가 조립본에서 발견한 다른 장의 어긋남 다섯을 고친다(정확한 문자열 치환; 건수 확인).
1) 10.7 셋째 고리: 명제 {{7:old-6-17}}(나) → {{7:src-plus}}(7B가 (나)를 분리한 라벨).
2) 9.6: 정리 {{6:old-6-19}}로 판정 V → 정리 {{6:V-all}}.
3) 10.38·old-8-10 머리: 손 조립 증명의 「비형식 증명」→「증명됨」(결정 38).
4) 명제 {{10:old-8-14}} 머리: 「비형식 증명」→「증명됨」(입력이 모두 증명됨).
5) 산술 등급 서식: 「와」→쉼표(7A), 괄호 안 쌍반점→쉼표(6장), 「계산 증거, 계산 보조」→「비형식 증명, 계산 보조」(7B).
"""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(ROOT, "장v2")


def rep(path, pairs):
    p = os.path.join(CH, path)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        n = s.count(a)
        print(f"{path}: {n}건 | {a[:70]!r}")
        if n == 1:
            s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


# src-plus의 종류 확인
s7b = io.open(os.path.join(CH, "장7B.md"), encoding="utf-8").read()
m = re.search(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{7:src-plus\}\}", s7b, re.M)
kind = m.group(1) if m else "명제"
print("src-plus 종류:", kind)

rep("장10.md", [
    ("명제 {{7:old-6-20}}가 명제 {{7:old-6-17}}(나)와 (V) 위에서", f"명제 {{{{7:old-6-20}}}}가 {kind} {{{{7:src-plus}}}}와 (V) 위에서"),
    ("**정리 {{10:old-8-37}} (주 정리의 둘째 증명) [비형식 증명, 정리 {{10:old-8-36}}", "**정리 {{10:old-8-37}} (주 정리의 둘째 증명) [증명됨, 정리 {{10:old-8-36}}"),
    ("q-flq-relation) [비형식 증명, 정리 {{8:old-6-33}}에 의존; r3d0856b]", "q-flq-relation) [증명됨, 정리 {{8:old-6-33}}에 의존; r3d0856b]"),
    ("명제 T) [비형식 증명, 따름정리 {{6:old-8-11}}·따름정리 {{6:DD-lower-bound}}에 의존; r3d0856b]", "명제 T) [증명됨, 따름정리 {{6:old-8-11}}·따름정리 {{6:DD-lower-bound}}에 의존; r3d0856b]"),
])
rep("장9.md", [
    ("정리 {{6:old-6-19}}로 판정 $\\mathsf V$가 성립하므로", "정리 {{6:V-all}}로 판정 $\\mathsf V$가 성립하므로"),
])
rep("장7A.md", [
    ("계산 보조(정확 정수·유리수와 방향 반올림 구간)", "계산 보조(정확 정수·유리수, 방향 반올림 구간)"),
])
rep("장6.md", [
    ("계산 보조(정확 정수·유리수; 40자리 평가, 인증 아님)", "계산 보조(정확 정수·유리수, 40자리 평가, 인증 아님)"),
])
rep("장7B.md", [
    ("[계산 증거, 계산 보조(방향 반올림 구간); r475ada3, r6b37c7e]", "[비형식 증명, 계산 보조(방향 반올림 구간); r475ada3, r6b37c7e]"),
])
