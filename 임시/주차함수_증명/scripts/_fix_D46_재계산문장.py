# -*- coding: utf-8 -*-
"""D.46(대각선 손실 닫힌 꼴의 두 적분값)의 독립 재계산 줄에서 기록의 옛 상수·값 언급을 걷어 내고 현재 사실만 남긴다. 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "장v2", "부록D_장10.md")
OLD1 = r"기록의 검토가 기록의 상수 $0.708345$, $2.528570$으로 두 적분을 따로 적분해 $0.7998520$, $2.7171423$을 얻었고, "
NEW1 = r"기록의 검토가 두 적분을 따로 적분해 "
OLD2 = r" 이 글은 두 상수를 위로 반올림한 $0.70836$, $2.528571$로 두 적분을 소수 30자리 tanh-sinh 구적과 치환 $\rho=\sigma^2$ 꼴로 다시 계산해 위의 값을 얻었다("
NEW2 = r" 이 글의 두 적분값은 상수 $0.70836$, $2.528571$로 소수 30자리 tanh-sinh 구적과 치환 $\rho=\sigma^2$ 꼴로 계산한 것이다("
OLD3 = r"); 네 $\mathrm{DDL}^\natural$ 값은 소수 넷째 자리까지 같다."
NEW3 = r")."

s = io.open(P, encoding="utf-8").read()
changed = False
for old, new in ((OLD1, NEW1), (OLD2, NEW2), (OLD3, NEW3)):
    n = s.count(old)
    if n == 1:
        s = s.replace(old, new)
        changed = True
    elif n == 0 and new in s:
        pass
    else:
        raise SystemExit(f"앵커 {n}곳: {old[:50]}")
if changed:
    io.open(P, "w", encoding="utf-8", newline="\n").write(s)
    print("D.46 독립 재계산 줄 정리")
else:
    print("이미 반영")
