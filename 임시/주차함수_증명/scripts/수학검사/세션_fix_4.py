# -*- coding: utf-8 -*-
"""사용자 승인(「권고대로」) 뒤 적용: (ㄱ) 장부 3절에 「가운데 비교」·「가운데 증가」 등재(장1 1.4절 99행이 「이 비교를 가운데 비교, 이 증가를 가운데 증가라 부르자」로 정의;
본문 27곳이 씀 — 통일 대신 등재가 맞음), (ㄴ) 장11 11.3 표 120행에서 「·정리 {{9:old-7-35}}의 증명」 제거(9.5절은 명제 9-6만 인용),
(ㄷ) 11.4 Robbins 행의 「7.2절」 제거(장7A에 Robbins 언급 없음), Ahlfors 행에 7.3·7.4절의 Cauchy 부등식 사용처 추가. 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# (ㄱ) 장부 3절
p = os.path.join(ROOT, "장부_v2.md")
L = io.open(p, encoding="utf-8").read().split("\n")
idx = next(i for i, l in enumerate(L) if l.startswith("| 한가운데 | 행 $n$을 고정했을 때"))
rows = [
    "| 가운데 비교 | 한가운데 위치의 비교 $b_{n,k_n-1}\\le b_{n,k_n}$ | 1.4 | 중앙 비교 |",
    "| 가운데 증가 | 가운데 비교가 엄격 부등식으로 성립함($b_{n,k_n-1}<b_{n,k_n}$; 정리 4.5) | 1.4 | 중앙 증가, 중앙 틈(명제·정리 이름으로는 그대로) |",
]
if not any(l.startswith("| 가운데 비교 |") for l in L):
    L[idx + 1:idx + 1] = rows
    print("장부 3절: 가운데 비교·가운데 증가 등재")
io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(L))

# (ㄴ)(ㄷ) 장11
q = os.path.join(ROOT, "장v2", "장11.md")
s = io.open(q, encoding="utf-8").read(); n = 0
for old, new in [
    ("명제 {{9:old-7-6}}·정리 {{9:old-7-35}}의 증명(명제 {{2:old-2-41}})", "명제 {{9:old-7-6}}(명제 {{2:old-2-41}})"),
    ("보조정리 {{6:lemma-Hprime}}, 6.6절, 7.2절, 7.4절, 보조정리 {{7:vertical-nu}}", "보조정리 {{6:lemma-Hprime}}, 6.6절, 7.4절, 보조정리 {{7:vertical-nu}}"),
    ("| 4.3절(Lagrange 계수의 윤곽 적분 표현), 보조정리 {{4:correction-contour}} |", "| 4.3절(Lagrange 계수의 윤곽 적분 표현), 보조정리 {{4:correction-contour}}, 7.3절·7.4절(Cauchy 부등식) |"),
    ("| Proposition 5.3.2(Cayley 공식) | 2.4절, 2.5절, 정리 {{2:chain-expansion}}, 명제 {{6:chain-count}}, 보조정리 {{6:split-mass}}·{{6:lemma-O}} |", "| Proposition 5.3.2(Cayley 공식) | 2.4절, 2.5절, 정리 {{2:chain-expansion}}, 보조정리 {{5:stop-lower}}, 명제 {{6:chain-count}}, 보조정리 {{6:split-mass}}·{{6:lemma-O}} |"),
    ("보조정리 {{4:correction-contour}}·{{4:two-corrections}}, 보조정리 {{5:inverse-renewal}}", "보조정리 {{4:correction-contour}}, 보조정리 {{5:inverse-renewal}}"),
]:
    c = s.count(old)
    if c == 1:
        s = s.replace(old, new); n += 1
    elif new in s:
        pass
    else:
        print("앵커 수", c, ":", old[:50])
io.open(q, "w", encoding="utf-8", newline="\n").write(s)
print("장11 고침", n)
