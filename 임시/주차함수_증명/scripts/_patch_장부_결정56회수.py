# -*- coding: utf-8 -*-
"""작업 장부: 결정 56 글자 정리 회수(5A·5B·6·7B·9·10), Gr 치환의 중괄호 결함과 복구, 4절 새 생성기."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "작업_장부.md")
s = io.open(P, encoding="utf-8").read()

ENTRY = (
    "- 2026-11-13 02:5x **결정 56 글자 정리 회수(여섯 장)**: 5A($g^\\pm_j\\to\\mathrm{Lp}^\\pm_j$, $f_{\\mathrm{ws}}\\to\\mathrm{Fs}$, $\\mathfrak g_i(d)\\to\\mathrm{lc}_i(d)$, FKG 절단점 $S\\to\\mathrm{Cut}$); 5B(5.28 $\\sigma$·$\\tau$ 풀어 씀, $Z_{\\mathrm{cut}}\\to\\mathfrak S_{\\mathrm{cut}}$, $Z\\to\\mathfrak S$(68곳), $\\Phi_i\\to\\mathfrak L_i$, $\\hat\\eta$ 풀어 씀, $\\tau=1+\\eta\\to\\mathfrak l$, $\\hat H\\to\\mathrm{bt}$, 부록 D $X\\to\\mathrm{ex}$·$u$, $\\mathfrak I_i(\\tau)\\to\\mathfrak I_i(\\upsilon)$); 6장($\\tau$ 네 뜻을 $\\mathcal J$·$\\sigma$·$t$·$\\mathrm{tp}$·$\\mathcal M$으로; $\\theta$·$a_0$는 현행 파일에 없음); 7B($\\Phi_\\ast\\to\\mathcal G_\\ast$, $\\mathcal K^\\sharp\\to\\mathcal D$, $\\hat\\pi_q\\to\\hat{\\mathfrak n}_q$, 윤곽 $\\tau\\to\\xi$, $T_0\\to U_0$, $h_0\\to j_0$, $\\Omega\\to\\omega$(4장 글자), 7.6 지표 $R\\to U$ 32곳; 7A 표 미도착으로 $\\mathfrak U_1$ 추종은 대기); 9장($\\sigma\\to\\varsigma$, $\\tau\\to\\mathfrak t$, $\\mathcal K(n,m)\\to\\mathrm{Kr}(n,m)$; $S_k$는 본문에 없음); 10장($\\tau\\to\\rho$ 124곳, $\\eta\\to\\mathfrak y$, $\\mathfrak w(q)\\to\\mathfrak o(q)$, $\\mathfrak w^\\sharp\\to\\mathfrak y^\\sharp$). 7A 진행 중. "
    "**세션 결함과 복구**: 결정 54의 일괄 치환 정규식이 `…G}}`에서 닫는 중괄호 하나를 삼켰다(5A 10곳은 5A 집필자가 복구; 4장 1·7B 3곳은 커밋 0030d15f와의 문맥 대조 스크립트 `_fix_Gr_km_braces.py`로, 2장 4·7B 1곳은 정확 문자열 `_fix_Gr_braces2.py`로 복구). 수식 구간 중괄호 균형 검사기 `_check_math_braces.py`(전 장 불균형 0)를 두었다 — 조립 전 상시 검사에 넣는다. 교훈: 정규식 치환은 `\\}?\\}` 같은 선택 괄호를 두지 말고, 치환 뒤 수식 균형 검사를 바로 돌린다. 또 5B의 `\\mathcal T^{\\mathrm G}` 4곳도 치환이 건드려 집필자가 `\\mathcal`을 지웠다(뜻 같음). "
    "4절: 모집단을 라벨 등록부 1절(첫 판 진술)에서 장 파일의 진술 머리 전부로 바꾼 새 생성기 `scripts/장부v2_4절_재생성2.py`(머리 441개 = 첫 판 226 + 새 진술 215; 세션 손질 이름 유지; 뺌 행 유지)로 재생성."
)
old = "\n## 재개 기록\n"
assert s.count(old) == 1
if "**결정 56 글자 정리 회수(여섯 장)**" not in s:
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched 작업_장부.md")
