# -*- coding: utf-8 -*-
"""장3 퇴고 최종 반환(02:3x) 뒤 세션 후속 셋: (1) 3.4 끝 「길이가 천 이상인 행」을 정리 old-3-6의 조건 $n\\ge1000$으로,
(2) 장 머리 둘째 문단의 「두 명제가 서로 동치라는 것」 되풀이 제거, (3) 3.3 도입의 「반례」에 장부 3절의 뜻을 괄호로 되살림. 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "장v2", "장3.md")

EDITS = [
    ("해싱 극한을 쓰지 않고도, 길이가 천 이상인 행이 단봉이라면 그 봉우리는 오른쪽 절반에 있다.",
     "해싱 극한을 쓰지 않고도, $n\\ge1000$에서 행이 단봉이라면 그 봉우리는 오른쪽 절반에 있다."),
    ("다른 하나는 왼쪽 절반 안에서 줄었다가 다시 느는 일이 없다는 명제(왼쪽 내부)다. 두 명제가 서로 동치라는 것이 정리 {{4:old-4-8}}의 내용이다. 그 동치의 증명 가운데",
     "다른 하나는 왼쪽 절반 안에서 줄었다가 다시 느는 일이 없다는 명제(왼쪽 내부)다. 이 동치가 정리 {{4:old-4-8}}이고, 그 증명 가운데"),
    ("계산으로 확인된 첫 반례는 $n=80$에 있다.",
     "계산으로 확인된 첫 반례(로그오목성이 깨지는 행)는 $n=80$이다."),
]

s = io.open(P, encoding="utf-8").read()
n = 0
for old, new in EDITS:
    if old in s:
        s = s.replace(old, new, 1); n += 1
    elif new in s:
        pass
    else:
        print("앵커 없음:", old[:50])
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("고침", n)
