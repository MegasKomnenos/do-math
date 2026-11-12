# -*- coding: utf-8 -*-
"""명세v2_META.py에 장별 추가 지시(사전 설계의 세션 결정 2·3·7·9·11·14·15·16·17)를 넣는다.

EXTRA_NOTES 사전을 apply() 앞에 두고, apply()가 notes 뒤에 그 장의 항목을 잇게 한다.
"""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "scripts", "명세v2_META.py")
s = io.open(P, encoding="utf-8").read()

EXTRA = '''
# 사전 설계의 세션 결정(대조v2/장부_설계_세션결정.md)에서 온 장별 지시
EXTRA_NOTES = {
    1: [
        "1.4 개관의 왼쪽·오른쪽 절반은 1.5의 위치 기준($n\\\\le2k$ / $n\\\\ge2k+1$)으로 적는다. 첫 판 1.4의 첨자 기준 문장은 위치 기준으로 고쳐 쓰되, 고친 문장이 참인지 확인한다(두 기준은 중앙의 한 칸에서만 다르다).",
    ],
    2: [
        "2.1의 선호 용량은 $h_i:=i-\\\\max(\\\\{j<i:\\\\sigma_j>\\\\sigma_i\\\\}\\\\cup\\\\{0\\\\})$로 바로 정의한다. 첫 판의 $t_i$는 전역 기호가 아니다: 그 자리는 $i-h_i$로 적고(정리 2.3의 범위 $i-h_i<a_{\\\\sigma_i}\\\\le i$, 보조정리 2.15의 용량 구간 $(i-h_i,\\\\,i]$), 증명 안에서 이름이 꼭 필요하면 장부 1.3의 국소 기호 $z_i$를 쓴다.",
        "자리 $i$에 선 차의 변위는 $d_{\\\\sigma_i}$로 적는다($d_i$는 차 $i$의 변위). 결과 순열 $\\\\sigma_i$의 정의(자리 $i$에 선 차)와 맞는지 확인하고 어긋나면 반환에 적는다.",
    ],
    5: [
        "첫 판 5.5.4(정리 5.28 등)의 보조 변수 $v=m-d$와 $\\\\mathrm{EB}(v)$의 인수는 장부 1.3이 정한 5장 국소 글자로 적는다(꼭짓점 지표 $v$는 쓰지 않는다). 5.5.7–5.5.8의 척도 변수도 장부 1.3의 글자대로($\\\\zeta$는 1.5의 중앙 창 좌표이므로 쓰지 않는다).",
    ],
    7: [
        "7.5의 뿌리 자리 법칙 $\\\\mathcal P^{(k)}_m(j)$는 마지막 차 자리 법칙 $\\\\mathcal P_m(j)$의 용량판이다. 정의 문장에 $\\\\mathcal P^{(k)}_m(j)=\\\\Pr_m(s_m=j\\\\mid M\\\\le k-1)$을 적고 그 등식을 한 줄로 확인한다(마지막 차의 선호 $\\\\min(j,k)$가지, 두 조각 $A_{j-1,k-1}A_{m-j,k-1}$).",
    ],
    9: [
        "첫 판 7.1의 $A^{(G)}_N$의 위첨자 $G$는 가장 큰 나무의 크기 $G$가 아니라 「모든 나무의 크기가 이 값 이하」라는 문턱 매개변수다. 장부대로 나무 크기 변수 $t$로 $A^{(t)}_N$이라 적고 $A^\\\\circ_N=A^{(k+1)}_N$, $A^\\\\diamond_N=A^{(k+103)}_N$으로 둔다. 7.1의 합 지표 $g$도 나무 크기 변수 $t$ 또는 묶인 지표로 바꾼다.",
        "평평한 꼬리는 $\\\\mathrm{flat}_k(t)$다(첫 판 7.3의 $\\\\mathfrak t_k(s)$). $\\\\varphi^\\\\flat_k=1+kD_k=k\\\\,\\\\mathrm{flat}_k(k+1)$.",
    ],
    10: [
        "첫 판 8.3의 「창 안」($m_0$의 미결 범위)은 장부 3절의 「미결 범위」로 적는다. 다만 첫 판 8.3·3372와 8.6·3724의 그 범위가 착지 창($k<m\\\\le k+q_{\\\\max}$)과 같으면 「착지 창 안」으로 적고 반환에 어느 쪽을 택했는지 적는다.",
    ],
}

'''

anchor = "def apply(ch):"
assert s.count(anchor) == 1
if "EXTRA_NOTES" not in s:
    s = s.replace(anchor, EXTRA + anchor)
old = 'spec["notes"] = m["notes"]'
assert s.count(old) == 1
s = s.replace(old, 'spec["notes"] = m["notes"] + EXTRA_NOTES.get(ch, [])')
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched", P)
