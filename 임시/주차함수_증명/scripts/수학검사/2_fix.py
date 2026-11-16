# -*- coding: utf-8 -*-
"""수학 검사(태그 2) 수정 스크립트. 멱등. 앵커가 파일 안에 정확히 한 번 있을 때만 치환한다."""
import sys, io
P = r"C:\math\임시\주차함수_증명\장v2\장2.md"
FIXES = [
    # 2장 도입부(9행): 보조정리 {{2:old-2-34}}의 우변 1-s_K(Y)=Pr_K(M>=Y)는 수준 Y 「이상」의 질량이다.
    # 이 장은 「위」를 엄격한 뜻(문턱 위의 초과 q=S-y>0 등)으로 쓰므로 「위에」는 경계가 어긋난다. 2.8절 549행의 「수준 Y 이상에 두는 질량」과 맞춘다.
    ("큰 크기에서 그 수준 위에 있는 질량 이상이라는 부등식",
     "큰 크기에서 그 수준 이상에 있는 질량 이상이라는 부등식"),
]
s = io.open(P, encoding="utf-8").read()
changed = 0
for old, new in FIXES:
    c = s.count(old)
    if c == 1:
        s = s.replace(old, new); changed += 1; print("치환:", old[:40], "->", new[:40])
    elif c == 0 and s.count(new) == 1:
        print("이미 적용됨:", new[:40])
    else:
        print("앵커 수 이상(", c, "):", old[:40]); sys.exit(1)
if changed:
    io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("수정", changed)
