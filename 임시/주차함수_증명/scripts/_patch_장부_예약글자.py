# -*- coding: utf-8 -*-
"""작업 장부: 예약 글자 잔존 검사 결과(장별 재개 때 포함할 지적)를 더한다."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "작업_장부.md")
s = io.open(P, encoding="utf-8").read()

ENTRY = (
    "- 2026-11-12 23:3x 예약 바탕 글자 잔존 검사(`scripts/_scan_예약글자.py`; 수식 안의 맨 이탤릭 $h$·$a$·$b$·$c$·$l$, $\\delta_t$ 가족 밖의 $\\delta$): 1·2·3·4·8·9장 0. "
    "**재개 때 포함할 지적(추가)**: 5A — 94행 평행이동 변수 $a$($\\xi\\mapsto\\xi+a$), 381–385행 구간 끝점 $a<b$·$(a,b]$, 567–575행 상수 $c=1/44$·$1/24$; "
    "5B — 292행부터 척도 $h:=Y^{-1/3}$(167회; 5A는 같은 종류의 척도를 $\\mathfrak z$로 적었으므로 같은 양이면 $\\mathfrak z$, 다른 양이면 5장 여유 글자), 264행 $a:=\\sqrt{\\sigma\\cdots}$·$b:=\\sqrt{\\tau/\\cdots}$, 483행 맨 $\\delta$; "
    "6장 — 171행 합의 끝 $j=a,\\dots,b$($a=N-k+1$, $b=k-1$), 1040행 $H_b-H_a$, 805행 맨 $l$; "
    "7A — 105행 $h=\\mathfrak g_j$, 783행 $\\mathfrak i_{j+1}h/2$, 581행 $(a+c)^+\\le a+c+(-a)^+$, 886행 $a<b<c$·$\\psi(a)$, 458–460행 맨 $\\delta$($z'=z+1+\\delta$); "
    "7B — 27행 $\\prod\\min(h,k)$(선호 용량의 값 변수면 $h_i$ 꼴로), 854행 $L=h$, 74행 $a+b=n-1$, 655행 $\\sqrt a$, 548–554행 $A_{l,y-1}\\rho_y^l/l!$·$\\varepsilon_y(l)$(라틴 소문자 엘), 67–76행 $\\delta_i$(상대 오차); "
    "10장(완료) — 705행 $0.5a^2\\theta-2a<0$의 맨 $a$와 같은 줄의 문턱 $h_0=m^{\\mathrm{hit}}_{\\mathrm L}$(바탕 글자 $h$)는 세션 일관성 검토에서 고친다. "
    "부록 D 조각에도 잔존: 5A(11행 $(k+h+1)s_h$·$1\\le a\\le300$, 74행 $a/b$, 154행 $h/2$), 5B(9행 $a',b'$, 39행 척도 $h$, 41행 $\\delta$), 7A(17행 $[l,r)$, 55행 합 지표 $\\delta$, 75행 $h/2$, 95행 $a$·$c$), 7B(27행 $\\delta=0.0037$, 49행 $l$) — 각 조각의 재개 지적에 넣는다(코드 변수 이름이면 결정 40의 「코드의 변수 …」 꼴로 적고 수식 글자로는 쓰지 않는다)."
)
old = "\n## 재개 기록\n"
assert s.count(old) == 1
if "예약 바탕 글자 잔존 검사" not in s:
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched 작업_장부.md (예약 글자 검사)")
