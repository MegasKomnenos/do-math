# -*- coding: utf-8 -*-
"""외부 피드백 넷째 묶음(실제 확인된 오류 3.1–3.7) 가운데 세션이 원문 대조로 확인한 항목을 본문·부록 D·장부에 반영한다. 멱등.
각 치환은 기대 횟수를 적고 어긋나면 멈춘다."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry" in sys.argv
SESS_Z = "`원고_자료/세션_재계산/zeta_constants/sum100_iv.py`, `원고_자료/세션_재계산/zeta_constants/sum100_iv_out.txt`"
SESS_M = "`원고_자료/세션_재계산/M_natural/j_integrals.py`, `원고_자료/세션_재계산/M_natural/j_integrals_out.txt`"

EDITS = [
    # ---- 3.1 생략한 사슬 길이의 꼬리 (나): 거짓인 j=1 계수별 부등식 삭제(쓰이는 곳 없음)
    ("장v2/장5A.md",
     r"$\mathcal Z^{(2)}_j\preceq\mathrm{dc}'_j(1-z)^{-\vartheta'_j}$($j\ge2$)이고, $\mathcal Z^{(2)}_1=zC\preceq\frac34(1-z)^{-1/2}$이다.",
     r"$\mathcal Z^{(2)}_j\preceq\mathrm{dc}'_j(1-z)^{-\vartheta'_j}$($j\ge2$)이다.", 1),
    ("장v2/장5A.md",
     r"(나) 보조정리 {{5:parity-tail}}(나)다. $j=1$은 (가)에서 $zC\preceq\frac34z(w^{-1}-1)\preceq\frac34w^{-1}$이다.",
     r"(나) 보조정리 {{5:parity-tail}}(나)다.", 1),
    # ---- 3.4 사전 오차 상계의 귀납 (나) 증명: 1.01s를 실제로 주는 경계
    ("장v2/장7B.md",
     r"$|\log(1+\mathrm w)|\le|\mathrm w|/(1-|\mathrm w|)\le|\mathrm w|/0.991$이므로 그 절댓값은 $s/0.991\le1.0091s$ 이하다. $|x|\le1.0091s\le0.0091$에서 $e^x\le1+x+x^2/(2(1-|x|/3))\le1+1.0091s+0.0046\cdot1.0091s<1+1.01s$이고 $e^{x}\ge1+x\ge1-1.01s$다.",
     r"$|\log(1+\mathrm w)-\mathrm w|=\bigl|\sum_{j\ge2}(-1)^{j+1}\mathrm w^j/j\bigr|\le\frac{\mathrm w^2}{2(1-|\mathrm w|)}\le0.0046|\mathrm w|$이므로 그 절댓값 $|x|$는 $1.0046s\le0.00905$ 이하다. $e^x\le1+x+x^2/(2(1-|x|/3))\le1+1.0046s+0.00454\cdot1.0046s<1+1.01s$이고 $e^{x}\ge1+x\ge1-1.01s$다.", 1),
    # ---- 3.2 꼬리 상계를 넣은 쌍별 판정: 분모의 양성을 주는 가정
    ("장v2/장7B.md",
     r"(7.13)가 확인된 $(K_1,\mathfrak M,\mathcal C)$에 대해 $\hat{\mathfrak n}_1:=0$",
     r"(7.13)가 확인되고 $\mathcal C\mathfrak M^{3/2}<K_1$인 $(K_1,\mathfrak M,\mathcal C)$에 대해 $\hat{\mathfrak n}_1:=0$", 1),
    ("장v2/장7B.md",
     r"**증명.** 보조정리 {{7:heavy-block}}(나)에서 $\mathrm{ex}_{k+q}$는 $1-\mathfrak s_q(k)$에 대해 증가하므로 보조정리 {{7:tail-bound}}에서 $\mathrm{ex}_{k+q}\le\hat{\mathrm{ex}}_q$다.",
     r"**증명.** 가정 $\mathcal C\mathfrak M^{3/2}<K_1$에서 모든 $k\ge K_1$과 $2\le q\le\mathfrak M$에 $\hat{\mathfrak n}_q<1$이다. 보조정리 {{7:heavy-block}}(나)에서 $\mathrm{ex}_{k+q}=q+(k+q)x/(1-x)$, $x:=1-\mathfrak s_q(k)\in[0,1)$이고 이 함수는 $[0,1)$에서 $x$에 증가하므로, 보조정리 {{7:tail-bound}}의 $x\le\hat{\mathfrak n}_q<1$에서 $\mathrm{ex}_{k+q}\le\hat{\mathrm{ex}}_q$다.", 1),
    ("장v2/장7B.md",
     r"$(10^6,700,0.519)$은 꼬리 삼중이다. 곧 각각에서 $2\le q\le\mathfrak M$인 모든 $q$에 (7.13)가 성립한다.",
     r"$(10^6,700,0.519)$은 꼬리 삼중이다. 곧 각각에서 $2\le q\le\mathfrak M$인 모든 $q$에 (7.13)가 성립한다. 여섯 묶음과 (나)의 표의 열한 열은 모두 보조정리 {{7:pair-criterion-sharp}}의 가정 $\mathcal C\mathfrak M^{3/2}<K_1$을 만족한다($\mathcal C\mathfrak M^{3/2}$의 최댓값은 $(700,0.519)$의 $9612$, 그 다음은 $(450,0.548)$의 $5231$).", 1),
    # ---- 3.7 이름: 조건부 → 정규화 (정의 자리에 설명)
    ("장v2/장7B.md",
     r"크기 $m$의 조건부 수준 질량을 $\mathrm{cl}^+_m:=c_m(k)/s_m(k)=b_{m,k}/A_{m,k-1}$, $\mathrm{cl}^-_m:=c_m(k-1)/s_m(k)=b_{m,k-1}/A_{m,k-1}$로 두면",
     r"크기 $m$의 정규화 수준 질량을 $\mathrm{cl}^+_m:=c_m(k)/s_m(k)=b_{m,k}/A_{m,k-1}$, $\mathrm{cl}^-_m:=c_m(k-1)/s_m(k)=b_{m,k-1}/A_{m,k-1}$로 두면(생존 확률 $s_m(k)$로 정규화한 수준 $k$·$k-1$의 질량이다. $\mathrm{cl}^-_m$은 조건부확률 $\Pr_m(M=k-1\mid M\le k-1)$이지만, $\mathrm{cl}^+_m$은 서로소인 두 사건의 확률의 비라 조건부확률이 아니다)", 1),
    ("장v2/장7B.md", "조건부 수준 질량", "정규화 수준 질량", 1),
    ("장v2/장9.md", "조건부 수준 질량", "정규화 수준 질량", 3),
    ("장v2/장10.md", "조건부 수준 질량", "정규화 수준 질량", 1),
    ("장부_v2.md", "(생존을 조건으로 한 수준 $k$·$k-1$의 질량)", "(생존 확률 $s_m(k)$로 정규화한 수준 $k$·$k-1$의 질량; $\\mathrm{cl}^-_m$만 조건부확률)", 1),
    ("장부_v2.md", "조건부 수준 질량", "정규화 수준 질량", 6),
    # ---- 3.3 열 1차 모멘트의 균일 상수: 적분 범위 [0,40], 상계의 반올림 방향, 상수 7.7149
    ("장v2/장5B.md", r"$\mathsf C_E=7.7148$이다.", r"$\mathsf C_E=7.7149$이다.", 1),
    ("장v2/장5B.md", r"\mathfrak A\int_0^{\infty}\!\!\int_{(\mathfrak k_i-\mathfrak h_0^2)_+}^{\mathfrak k_{i+1}}",
     r"\mathfrak A\int_0^{40}\!\!\int_{(\mathfrak k_i-\mathfrak h_0^2)_+}^{\mathfrak k_{i+1}}", 1),
    ("장v2/장5B.md", r"$C_{\mathrm I}\le6.0961$이고, 이 부등식은", r"$C_{\mathrm I}\le6.09612$이고, 이 부등식은", 1),
    ("장v2/장5B.md", r"$C_{\mathrm{II}}:=e^{\mathfrak h_0^3/12}\int_0^\infty(\theta+\mathfrak h_0)", r"$C_{\mathrm{II}}:=e^{\mathfrak h_0^3/12}\int_0^{40}(\theta+\mathfrak h_0)", 1),
    ("장v2/장5B.md", r"$\mathfrak h_0C_{\mathrm{II}}\le0.1153$은 부록", r"$\mathfrak h_0C_{\mathrm{II}}\le0.11531$은 부록", 1),
    ("장v2/장5B.md", r"(6.0961+0.1153+1.5034+10^{-9})\,w^{-1/3}\ \le\ 7.7148\,w^{-1/3}", r"(6.09612+0.11531+1.5034+10^{-9})\,w^{-1/3}\ \le\ 7.7149\,w^{-1/3}", 1),
    ("장v2/부록D_장5B.md",
     r"$C_{\mathrm I}\le6.0961$, $\mathfrak h_0C_{\mathrm{II}}\le0.1153$, $C_{\mathrm{III}}\le1.5034$, 따라서 $C_{\mathrm I}+\mathfrak h_0C_{\mathrm{II}}+C_{\mathrm{III}}+2\times10^{-10}\le7.7148$",
     r"$C_{\mathrm I}\le6.09612$, $\mathfrak h_0C_{\mathrm{II}}\le0.11531$, $C_{\mathrm{III}}\le1.5034$, 따라서 $C_{\mathrm I}+\mathfrak h_0C_{\mathrm{II}}+C_{\mathrm{III}}+2\times10^{-10}\le7.7149$", 1),
    ("장v2/부록D_장5B.md", r"\mathfrak A\int_0^{\infty}\!\!\int_{(\mathfrak k_i-\mathfrak h_0^2)_+}^{\mathfrak k_{i+1}}",
     r"\mathfrak A\int_0^{40}\!\!\int_{(\mathfrak k_i-\mathfrak h_0^2)_+}^{\mathfrak k_{i+1}}", 1),
    ("장v2/부록D_장5B.md",
     r"$C_{\mathrm{II}}=e^{\mathfrak h_0^3/12}\int_0^\infty(\theta+\mathfrak h_0)\sup_{[\theta,\theta+\mathfrak h_0]}\bar{\mathcal P}_{\mathrm{II}}\cdot\mathfrak L_{\mathrm{II}}(\theta+\mathfrak h_0)\,d\theta$. 영역 III.",
     r"$C_{\mathrm{II}}=e^{\mathfrak h_0^3/12}\int_0^{40}(\theta+\mathfrak h_0)\sup_{[\theta,\theta+\mathfrak h_0]}\bar{\mathcal P}_{\mathrm{II}}\cdot\mathfrak L_{\mathrm{II}}(\theta+\mathfrak h_0)\,d\theta$. 두 영역의 $\theta>40$ 꼬리는 정리 {{5:old-5-37}} 증명 셋째 단계의 손 경계 $10^{-27}\mathfrak h$로 따로 막는다. 영역 III.", 1),
    ("장v2/부록D_장5B.md", r"합 $\le7.7148$.", r"합 $\le7.71482$.", 1),
    ("장부_v2.md", r"열 1차 모멘트 상수 $7.7148$", r"열 1차 모멘트 상수 $7.7149$", 1),
    # ---- 3.5 D 보정의 나머지 무게: Gauss 인자 중복 제거
    ("장v2/장5B.md",
     r"무게는 $\upsilon^4\rho^2Q_0e^{-\eta\upsilon^2/2}e^{-\varrho^2/2}(1+\epsilon_{\mathfrak f})$, $\epsilon_{\mathfrak f}:=",
     r"무게는 $\upsilon^4\rho^2Q_0e^{-\eta\upsilon^2/2}(1+\epsilon_{\mathfrak f})$(Gauss 인자 $e^{-\varrho^2/2}$는 $\mathcal Q_j$ 쪽에 이미 들어 있다), $\epsilon_{\mathfrak f}:=", 1),
    # ---- 3.4 100항 합
    ("장v2/장7A.md", r"처음 $100$항의 합 $2.41287$ 이하에", r"처음 $100$항의 합 $2.41288$ 이하에", 1),
    ("장v2/부록D_장7A.md", r"$\sum_{j=1}^{100}j^{-3/2}\le2.41287$.", r"$\sum_{j=1}^{100}j^{-3/2}\le2.41288$.", 1),
    ("장v2/부록D_장7A.md",
     r"(4) $\sum_{j\le100}j^{-3/2}$는 $j^{-3/2}\le$ 유리수 상계(이진 유리수로 위에서 반올림)의 합으로 확인한다.",
     r"(4) $\sum_{j\le100}j^{-3/2}$는 항마다 소수 30자리 방향 반올림 구간으로 감싸 더한다(`원고_자료/세션_재계산/zeta_constants/sum100_iv.py`).", 1),
    ("장v2/부록D_장7A.md",
     r"정확 정수·유리수(세 층의 상수, 따름정리의 세 값, (4))와 방향 반올림 구간($e^{-i}$와 $k=6098$의 평가)",
     r"정확 정수·유리수(세 층의 상수, 따름정리의 세 값)와 방향 반올림 구간($e^{-i}$, $k=6098$의 평가, (4))", 1),
    ("장v2/부록D_장7A.md", r"$\sum_{j\le100}j^{-3/2}=2.41286\ldots\le2.41287$.",
     r"$\sum_{j\le100}j^{-3/2}\in[2.4128740987,2.4128740988]$, 따라서 $\le2.41288$.", 1),
    ("장v2/부록D_장7A.md", r"(4)는 이 글을 쓰며 더한 확인이며 아직 다시 돌리지 않았다.",
     r"(4)는 이 글을 쓰며 더한 확인이고, 그 구간 계산과 출력이 자료에 있다.", 1),
    # ---- 3.5 극 영역 입력 (ㄹ)의 지표: 코드의 지표와 유도의 지표
    ("장v2/부록D_장7A.md",
     r"(ㄹ) 처음 $60$항: $m=i+\ell$($\ell=0,\dots,59$), $j:=k+i-\ell\in[k_1+i-\ell,k_2+i-\ell]$에서",
     r"(ㄹ) 처음 $60$항: $m=i+\ell$($\ell=0,\dots,59$), $j:=k+i-\ell\in[k_1+i-\ell,k_2+i-\ell]$(코드의 지표. 원천 합의 $\theta$ 지표는 $k+i-m=k-\ell$이므로 코드는 $\theta_j$의 두 경계를 $i$만큼 큰 $j$에서 읽는다. 하계 $e^{5/(12j)}$는 그래서 더 작아 그대로 하계이고, 상계 $1+0.7/j$는 참 지표의 것보다 상대 $0.7i/((k-\ell)(k+i-\ell))\le0.6/k$만큼 작을 수 있다. 이 차이가 블록의 결정 여유 안에 드는지는 이 글에서 확인하지 않았다)에서", 1),
    # ---- 3.4 u(3131)
    ("장v2/장6.md", r"$\mathsf u$는 $k$에 대해 감소하고 $\mathsf u(3131)=0.395$다.", r"$\mathsf u$는 $k$에 대해 감소하고 $\mathsf u(3131)<0.3951$이다.", 1),
    ("장v2/장6.md", r"$\mathsf u(3131)=8.5714\cdot1.35032\cdot1.9096\cdot0.017872=0.395$다. ∎",
     r"$\mathsf u(3131)\le8.5715\cdot1.35032\cdot1.9097\cdot0.017872<0.3951$이다. ∎", 1),
    ("장v2/장6.md", r"$\hat\Upsilon_k<\mathsf u(3131)/2=0.1975<0.198$", r"$\hat\Upsilon_k<\mathsf u(3131)/2<0.1976<0.198$", 1),
    ("장v2/장6.md", r"$kc_{2k}(k-1)\le\mathsf u(k)\le\mathsf u(3131)=0.395$이므로 $E_3\le0.0514",
     r"$kc_{2k}(k-1)\le\mathsf u(k)\le\mathsf u(3131)<0.3951$이므로 $E_3\le0.0514", 1),
    # ---- 3.4 50.600
    ("장v2/장6.md", r"\le\frac{14.652+35.948}{\sqrt t}=\frac{50.600}{\sqrt t}\le\frac{50.62}{\sqrt t}",
     r"\le\frac{14.653+35.952}{\sqrt t}=\frac{50.605}{\sqrt t}\le\frac{50.62}{\sqrt t}", 1),
    ("장v2/부록D_장6.md", r"\le14.652+35.948=50.600\le50.62", r"\le14.653+35.952=50.605\le50.62", 1),
    ("장v2/부록D_장6.md",
     r"상수 $50.600$과 진술의 $50.62$ 사이에 $0.02$의 여유를 두었다. 칸을 두 배로 늘리면 위합은 $50.571$로 내려간다.",
     r"상수 $50.605$와 진술의 $50.62$ 사이에 $0.015$의 여유를 두었다. 칸을 두 배로 늘리면 네 위합은 더 내려간다(기록이 보고한 합 $50.571$).", 1),
    ("장v2/부록D_장6.md", r"합 $50.600$.", r"합 $50.605$(네 상계를 위로 반올림해 더한 값).", 1),
    # ---- 3.4 10장 상수와 두 적분값
    ("장v2/장10.md", r"상수 $0.708345=3\sqrt2\cdot0.16696$, $2.528570=2.5-\log2-\log0.485917$이다.",
     r"상수 $0.70836$과 $2.528571$은 각각 $3\sqrt2\cdot0.16696$과 $2.5-\log2-\log0.485917$을 위로 반올림한 값이다.", 1),
    ("장v2/장10.md", r"$\gamma^\natural_d$는 $\gamma^2/2-\sqrt2\mathfrak c_d\log\gamma$를 최소로 하는 값이다.",
     r"$\gamma^\natural_d$는 $\gamma^2/2-\sqrt2\mathfrak c_d\log\gamma$를 최소로 하는 값을 반올림한 것이다.", 1),
    ("장v2/장10.md", r"=2.7171423\ldots", r"=2.7171999\ldots", 1),
    ("장v2/장10.md", r"=0.7998520\ldots", r"=0.7998717\ldots", 1),
    ("장v2/장10.md", "0.708345", "0.70836", 6),
    ("장v2/장10.md", "2.528570", "2.528571", 3),
    ("장v2/부록D_장10.md",
     r"상수 $0.708345=3\sqrt2\cdot0.16696$, $2.528570=2.5-\log2-\log0.485917$은 명제 {{10:old-8-23}}의 증명 3단계의 것이다.",
     r"상수 $0.70836$과 $2.528571$($3\sqrt2\cdot0.16696$과 $2.5-\log2-\log0.485917$을 위로 반올림한 값)은 명제 {{10:old-8-23}}의 증명 3단계의 것이다.", 1),
    ("장v2/부록D_장10.md", "0.708345", "0.70836", 3),
    ("장v2/부록D_장10.md", "2.528570", "2.528571", 1),
    ("장v2/부록D_장10.md",
     r"기록의 검토가 두 적분을 따로 적분해 같은 값 $0.7998520$, $2.7171423$을 얻었고, $\mathrm{DDL}^\natural(6668,8065,9551,9705)=0.1324,0.1223,0.1140,0.1133$을 독립 재현했다.",
     r"기록의 검토가 기록의 상수 $0.708345$, $2.528570$으로 두 적분을 따로 적분해 $0.7998520$, $2.7171423$을 얻었고, $\mathrm{DDL}^\natural(6668,8065,9551,9705)=0.1324,0.1223,0.1140,0.1133$을 독립 재현했다. 이 글은 두 상수를 위로 반올림한 $0.70836$, $2.528571$로 두 적분을 소수 30자리 tanh-sinh 구적과 치환 $\rho=\sigma^2$ 꼴로 다시 계산해 위의 값을 얻었다(" + SESS_M + r"); 네 $\mathrm{DDL}^\natural$ 값은 소수 넷째 자리까지 같다.", 1),
    ("장v2/부록D_장10.md", r"=2.7171423\ldots", r"=2.7171999\ldots", 1),
    ("장v2/부록D_장10.md", r"=0.7998520\ldots", r"=0.7998717\ldots", 1),
    # ---- 3.6 한 변수 하계 보조정리의 정의역
    ("장v2/장9.md", r"(가) $\vartheta\in(0,1]$을 고정하면", r"(가) $\vartheta\in[0.48,1]$을 고정하면", 1),
    # ---- 3.6 시험 함수 Ω의 보정 규칙·연장
    ("장v2/장8.md",
     r"를 곱한 표 $(1-\mathfrak g(\xi^{\mathsf K}_i))\mathfrak w_i$를 비증가로 보정하고, 그 표를 지나는 단조 $C^1$ 3차 Hermite 보간을 $\Omega$로 둔다. $\Omega$는 감소하는 $C^1$ 함수이고, $\Omega(0)=0.96$,",
     r"를 곱한 표 $(1-\mathfrak g(\xi^{\mathsf K}_i))\mathfrak w_i$를 왼쪽부터의 누적 최솟값으로 바꾸어 비증가로 만들고(이 표에서는 바뀌는 항이 없다), 그 표를 지나는 단조 3차 Hermite 보간(내부 절점의 기울기는 이웃한 두 할선 기울기의 조화평균, 끝점은 한쪽 세 점 공식에 모양 보존 제한을 둔 것)을 $[0,\xi^{\mathsf K}_{12926}]$에서 쓰고, $\xi^{\mathsf K}_{12926}=5.9997$ 오른쪽 $(5.9997,6]$에서는 마지막 표 값 $0.00229$로 상수 연장한 함수를 $\Omega$로 둔다. $\Omega$는 비증가 연속 함수이고 $5.9997$을 뺀 곳에서 $C^1$이며(그 점에서 $\Omega'$은 $-0.0020$에서 $0$으로 뛴다), $\Omega(0)=0.96$,", 1),
    ("장v2/장8.md",
     r"$\Omega'$이 도약하면 도약마다 $\sqrt q$ 크기의 항이 남아 큰 $q$에서 셀 경계가 쓸모없어진다.",
     r"$\Omega'$이 도약하면 도약마다 $\sqrt q$ 크기의 항이 남아 큰 $q$에서 셀 경계가 쓸모없어진다. $5.9997$의 한 도약은 (나)의 셀 가운데 $[5.999,6]$ 하나에만 닿고, 거기서 남는 항은 도함수 경계에 $0.19$ 이하, 셀 폭 $0.001$을 곱해 $2\times10^{-4}$ 이하이며, 그 셀의 여유($2.9\times10^{-4}$ 이상)가 이를 덮는다(부록 D.{{D:window-mass-env}}).", 1),
    ("장v2/부록D_장8.md",
     r"를 곱한 표를 비증가로 보정한 뒤 Fritsch–Carlson 기울기의 단조 $C^1$ 3차 Hermite 보간으로 $\Omega$를 정의한다. 보간 구간마다 $|\Omega'|$, $|\Omega''|$의 닫힌 꼴 상계를 함께 저장한다.",
     r"를 곱한 표를 왼쪽부터의 누적 최솟값으로 바꾸어 비증가로 만든 뒤(바뀌는 항 없음) Fritsch–Carlson 기울기(내부 절점은 이웃 할선 기울기의 조화평균, 끝점은 한쪽 세 점 공식에 모양 보존 제한)의 단조 3차 Hermite 보간으로 $[0,\xi^{\mathsf K}_{12926}]$에서 $\Omega$를 정의하고, $(\xi^{\mathsf K}_{12926},6]=(5.9997,6]$에서는 마지막 표 값으로 상수 연장한다(코드의 평가 함수가 마지막 구간의 끝값을 돌려준다). 보간 구간마다 $|\Omega'|$, $|\Omega''|$의 닫힌 꼴 상계를 함께 저장한다.", 1),
    ("장v2/부록D_장8.md",
     r"(`rv_checks.out`; 증명이 아니라 대조).",
     r"(`rv_checks.out`; 증명이 아니라 대조). 이 글을 쓰며 확인한 것: 상수 연장 때문에 $\Omega'$은 $5.9997$에서 $-0.0020$에서 $0$으로 뛰고, (나)의 셀 Lipschitz 경계(부분적분 꼴 $\int\tau\,d[\varsigma'|\Omega'|]$)는 이 도약의 원자 $5.9997\cdot0.0020=0.0123$을 넣지 않았다. 원자가 닿는 셀은 $[5.999,6]$ 하나이고 그 무게는 $\frac2\pi\cdot\frac1{5.999}\cdot(1-5.9997/6+1/J_i)^{-1/2}\le15.5$라 빠진 몫은 $15.5\cdot0.0123\cdot0.001<2\times10^{-4}$인데, 그 셀의 여유는 우변 $\ge6^{3/2}\cdot0.78\cdot0.00229=0.0262$의 $1.125\%$ 이상, 곧 $2.9\times10^{-4}$ 이상이다.", None),
]


def append_to_자료(lines, after_idx, extra):
    """after_idx 다음의 첫 「**자료.**」 줄 끝에 extra를 덧붙인다(이미 있으면 그대로)."""
    for i in range(after_idx, min(after_idx + 12, len(lines))):
        if lines[i].startswith("**자료.**"):
            if extra.split(",")[0].strip("` ") in lines[i]:
                return False
            lines[i] = lines[i].rstrip().rstrip(".") + ", " + extra + "."
            return True
    raise SystemExit(f"자료 줄 없음 (after {after_idx})")


def main():
    texts = {}
    for rel, old, new, expect in EDITS:
        p = os.path.join(ROOT, rel)
        s = texts.get(rel)
        if s is None:
            s = io.open(p, encoding="utf-8").read()
        n = s.count(old)
        if n == 0:
            if new in s:
                print(f"{rel}: 이미 반영 — {old[:40]}")
                continue
            print(f"{rel}: 원문 없음 — {old[:70]}")
            sys.exit(1)
        if expect is not None and n != expect:
            print(f"{rel}: 횟수 어긋남 {n}≠{expect} — {old[:70]}")
            sys.exit(1)
        if expect is None and n != 1:
            # 부록D_장8 rv_checks 앵커: 대조 문장이 정확히 한 번이어야 한다
            print(f"{rel}: 앵커 {n}곳 — {old[:70]}")
            sys.exit(1)
        texts[rel] = s.replace(old, new)
        print(f"{rel}: {n}곳 — {old[:48]}")
    # 자료 줄 보강: D.30(자기일관 상계의 상수)과 D.46(두 적분값)
    for rel, marker, extra in [
        ("장v2/부록D_장7A.md", "(4)는 이 글을 쓰며 더한 확인이고", SESS_Z),
        ("장v2/부록D_장10.md", "이 글은 두 상수를 위로 반올림한", SESS_M),
    ]:
        s = texts.get(rel) or io.open(os.path.join(ROOT, rel), encoding="utf-8").read()
        lines = s.split("\n")
        idx = [i for i, l in enumerate(lines) if marker in l]
        if not idx:
            print(f"{rel}: 표지 없음 — {marker}")
            sys.exit(1)
        if append_to_자료(lines, idx[0], extra):
            print(f"{rel}: 자료 줄에 세션 파일 추가")
        texts[rel] = "\n".join(lines)
    if DRY:
        print("(dry) 쓰지 않음")
        return
    for rel, s in texts.items():
        io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n").write(s)
    print("기록함:", ", ".join(texts))


if __name__ == "__main__":
    main()
