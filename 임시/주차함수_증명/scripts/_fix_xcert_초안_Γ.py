# -*- coding: utf-8 -*-
"""D.31(xcert-partAB) 구간 이식 초안의 층 A″-2 [Γ] 식 줄: $\\mathfrak v\\to0^+$에서 발산하는 꼴이므로, 기록의 코드와 이 글의 재계산이 실제로 한 대로
「$\\mathfrak v>0$; $\\mathfrak v=0$에서는 $\\max$ 대신 $0.55$」를 적는다(이식 보고 주의 4, 세션 판단). 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "원고_자료", "세션_재계산", "xcert_iv", "D항목_초안.md")

OLD = r"3k^{-1/2}\max(0.55,0.55\mathfrak v^{-3/2}k^{-1/2}e^{\mathfrak v})]$, $g_{\mathfrak s}:="
NEW = r"3k^{-1/2}\max(0.55,0.55\mathfrak v^{-3/2}k^{-1/2}e^{\mathfrak v})]$($\mathfrak v>0$; $\mathfrak v=0$에서는 $\max$ 대신 $0.55$), $g_{\mathfrak s}:="

s = io.open(P, encoding="utf-8").read()
c = s.count(OLD)
if c == 1:
    s = s.replace(OLD, NEW, 1)
    io.open(P, "w", encoding="utf-8", newline="\n").write(s)
    print("고침 1")
elif NEW in s:
    print("이미")
else:
    print("앵커 수", c)
