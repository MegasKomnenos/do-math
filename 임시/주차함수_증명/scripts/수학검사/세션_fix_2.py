# -*- coding: utf-8 -*-
"""장11 검사의 발견: 정리 {{7:polar-PD}}는 머리에 「계산 보조」가 있고 11.3 표에 등급이 적혀 있으나 어느 부록 D 항목 머리에도 없어 11.2 표에 행이 없다.
D.31 이식 보고가 polar-PD의 계산 몫이 D.xcert-partAB에서만 옴을 확인했으므로 그 항목 머리와 11.2 표의 같은 행에 polar-PD를 더한다. 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "장v2", "부록D_장7A.md")
Q = os.path.join(ROOT, "장v2", "장11.md")

s = io.open(P, encoding="utf-8").read()
old = "### D.{{D:xcert-partAB}} 유한 크기 전달 $\\mathsf X'$의 다섯 층 인증 (정리 {{7:old-6-12}})\n"
new = "### D.{{D:xcert-partAB}} 유한 크기 전달 $\\mathsf X'$의 다섯 층 인증 (정리 {{7:old-6-12}}, 정리 {{7:polar-PD}})\n"
if old in s:
    s = s.replace(old, new, 1); io.open(P, "w", encoding="utf-8", newline="\n").write(s); print("부록D_장7A 머리 고침")
elif new in s:
    print("부록D_장7A 이미")
else:
    print("부록D_장7A 앵커 없음")

t = io.open(Q, encoding="utf-8").read()
lines = t.split("\n"); n = 0
for i, l in enumerate(lines):
    if l.startswith("| 부록 D.{{D:xcert-partAB}} |"):
        cells = l.split("|")
        if cells[2].strip() == "정리 {{7:old-6-12}}":
            cells[2] = " 정리 {{7:old-6-12}}, 정리 {{7:polar-PD}} "
            lines[i] = "|".join(cells); n += 1
        else:
            print("11.2 행 진술 열:", cells[2].strip())
io.open(Q, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("장11 11.2 행 고침", n)
