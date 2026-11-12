# -*- coding: utf-8 -*-
"""대조 보고 `대조/의존지도_대조_P.md`의 정정 제안(5절)을 의존지도.md 2절에 반영한다. 2절 전체를 교체한다."""
import io

p = "임시/주차함수_증명/의존지도.md"
s = io.open(p, encoding="utf-8").read()
a = s.index("## 2. P◇ 경로(7장)의 행")
b = s.index("## 3. Q⋆₂ 경로(8장)의 행")

new2 = r"""## 2. P◇ 경로(7장)의 행

대조 보고 `대조/의존지도_대조_P.md`(2026-11-12, 프런티어 판 382 기준)를 반영한 판. 36행 모두 기록 원문으로 판정되었고(일치 17, 정정 19, 미확인 0), 미지지 입력과 철회·우려는 없다. "진술" 열은 새 원고의 기호로 적었다(장부 1절). 기호가 기록과 다른 자리는 비고에 적는다.

| 새 글의 자리 | 진술 | 입력(기록/주장 또는 글 안의 번호) | 지위 | 비고 |
|---|---|---|---|---|
| 2.10 | 다섯 조각 분해 $d_n=-\Theta_n+FL^{(5)}_n+BV_n+KD_n+PAIR_n$, $2k+1\le n\le3k-1$ | [r6f5f48f]/pr-five-pieces; 지수 공식 $F_\ell=\exp T_\ell$([r0ee343a]/p-exp-form; 글 안 2.6 명제 2.16의 증명) | 증명 | 기존 6.8절 문단을 옮김 |
| 2.10 | 쌍 항의 정수 꼴과 비음성, 확률 꼴 | [rae1f209]/c-pair-explicit(§1, §2.3) | 증명(재유도) | |
| 2.10 | 한 블록 꼴 $PAIR_n=\frac12\sum_s\binom ns[v_sb_{n-s,k-1}+u_sb_{n-s,k}]$, $\Theta_n=\binom nk v_kA_{n-k,k-1}$, $2k\le n\le3k-1$ | [r5909c9e]/c-pair-marginal-identity(§4.4) | 증명(정확) | 검토가 $3\le k\le8$에서 정수 확인. 기록은 이 식에 (E1) 표지를 붙였으나 새 원고에서 (E1)은 6.9의 한 블록 재귀만 가리킨다 |
| 2.8 | 크기 결합: 결합 $\tilde M_n\le\tilde M_{n+1}\le\tilde M_n+1$(최대 변위는 크기가 하나 늘 때 0 또는 1 오름)과 두 부등식 (SM) $s_{N+1}(y)\le s_N(y)$, (DM0) $s_{m-1}(k)\le s_m(k+1)$, 그리고 (SC) $A_{N,\ell}/p_N\le A_{N+1,\ell+1}/p_{N+1}$ | [r60a6f55]/size-coupling(문헌 Fleurat 위), 재진술 [r207f124]/diag-lossless((SM)·(DM0)), 두 부등식의 초등 증명 [r79ee9e0]/c-lemma-sh | (SM)·(DM0): 증명([r79ee9e0]/c-lemma-sh); 결합(0 또는 1 증가): 비형식(문헌) | 기존 6.6절. 새 원고는 두 부등식을 c-lemma-sh의 증명으로 세우고 결합 진술은 문헌 위 비형식으로 둔다 |
| 2.8 | 보조정리 C(수준 방문 보존): $\sum_{N=c+1}^K c_N(c)\ge1-s_K(c)$와 Abel 판 | [rae1f209] §3.3 보조정리 C(p-visit-conservation); 입력 (DM0)=[r207f124]/diag-lossless | 증명 | 전역 용어 '수준 방문 보존 하계'. 검토의 귀속 정정: 무게 없는 꼴은 [re597c0e]/c-sojourn-identity에서 머묾 항을 버린 것이고, 이 기록의 새 몫은 Abel 판과 정리 F′의 결합 |
| 2.9 | 정리 T (i)–(iv), 따름 (a)(b)(c)(d) | [r4868e30] §3.3–3.4(c-threshold-subtree, c-inner-head-sum); 입력: 숲 표현(2.4), Cayley 공식, Stirling, [r33475a7]/p-heavy-path-ratio((iii)의 사슬 구조), [r2ec875c]/c-psi-correction((d)의 $\Psi(J)\le0.7979\sqrt J$) | 증명((a)–(d) 지지; 바깥 층과의 맞물림은 발견적이므로 넣지 않음) | (i)의 점별 부호와 (ii)의 첫 층 판은 [r52e9c83]/c-lemma4-chain·c-lemma5-neg-bound와 같음. 기록의 $c_N(\kappa)=\min(N,\kappa)A_{N-1,\kappa-1}$(나무 개수)는 새 원고의 허용 나무 수 $\mathcal N_{\kappa-1}(N)$, $c_0:=1$은 $\mathrm{Ren}(0):=1$ |
| 7.1 | 보조정리 1: $k+2\le N\le2k+1$에서 $A^\circ_N/p_N=\pi^0_N(k)+\frac{k}{k+1}\pi_N(k+1)$, $\Theta^\circ_n/\Theta_n$의 꼴 | [rae1f209] §2.1(c-theta0-closed-form) | 증명 | $\pi^0_N(k)$의 Borel 상계: 무게중심 정지 확률 [r2fe0259]/p-centroid-stop의 숲 꼴 $(1-\pi_2(F+1))/(F+1)$ |
| 7.1 | 병합 항등식 $2k+2\le n\le3k-1$에서 $\Theta_n=\Theta^\circ_n+\sum_{m=2k+1}^{n-1}K_n(m)\gamma_m\Theta_m$; $BV_n=\sum_mK_n(m)b^{(2)}_m$은 $BV$의 정의 | [r6f5f48f]/pr-merge-identity | 증명 | 검토가 $k=3$–$11$에서 정확 유리수 확인. 4-1 확인(판 382, supported) |
| 7.1 | 보조정리 T(잘린 병합 항등식): $\Theta_n-\sum_{m\ge2k+1+T}K_n(m)\gamma_m\Theta_m=\binom nk k^{k-2}A^{(k+T+1)}_N$ | [rae1f209] §5.1 보조정리 T(p-truncated-merge) | 증명 | $k=3$–$8$, $0\le T\le k-1$ 정확 확인 |
| 7.1 | 보조정리 4(덮인 문턱의 꼴): $k+1\le N\le2k-1$에서 $A^\diamond_N/p_N=\pi^0_N(k)+\sum_{g=k+1}^{\min(N,k+103)}\pi_N(g)(k/g)s_{g-1}(k)$ | [r5909c9e] §3.2 보조정리 4(c-pdiamond-theorem 안) | 증명 | |
| 7.1 | 정리 A: $\mathcal D_n:=BV_n-(\Theta_n-\Theta^\circ_n)=\sum_mK_n(m)\gamma_m\Theta_m(\mathcal Q_m-1)$; (가)(나) | [rae1f209] §2.2 정리 A(c-reduction-theorem-A); 입력 병합 항등식([r6f5f48f]/pr-merge-identity) | 증명 | 기록의 $X_n$ |
| 7.2 | 명제 B(행 조건의 정확한 식) | [rae1f209] §3.1(c-row-identity-B); 입력 (OB)=[r77e234e]/ob-identity | 증명 | 4-2 확인 |
| 7.2 | 보조정리 V: $2k\le m\le3k-1$에서 $\mathcal V_m=b_{m,k-1}+\mathcal P^-_m$; $2k+1\le m\le3k-1$에서 $b^{(2)}_m\ge(1-\mathfrak d_k/2)(\cdots)$ | [rae1f209] §3.2(p-lemma-V); 입력 보조정리 P=[r77e234e]/lemma-P($\mathcal P^-_m\le(\mathfrak d_k/2)\mathcal V_m$) | 증명 | 4-3 확인. 기록의 $V_m$, $M_2$, $\delta_k$ |
| 7.2 | 명제 R(행 조건의 귀납) | [rae1f209] §3.2(p-row-criterion); 입력 보조정리 V, 정리 A, 보조정리 1, 명제 B, $\Theta^\circ_n/\Theta_n\le1-W_0'(n-k)$([r77e234e]/p-theta-circ-kernel-bound), (SM) | 증명 | $W_0'(N)=\sum_{g=k+2}^N\pi_N(g)k/g$ |
| 7.2 | 정리 AR 네 단계 | [rae1f209] §5.1(p-analytic-row-theorem; (1) p-landing-minorant, (2) p-delta-bound); 입력: Robbins 부등식, 정리 F′([r7e03176]/p-thmF-prime), 크기 결합 (SM)·(DM0), 보조정리 C(수준 방문 보존), 보조정리 F([r77e234e]/lemma-F)·P([r77e234e]/lemma-P), 정리 B‴([r030ffae]/theorem-B-triple), 무게중심 정지 확률, 보조정리 V(p-lemma-V), 보조정리 T(p-truncated-merge), 명제 B/(OB)(c-row-identity-B), 초등 경계 $\pi_2(M)\le(8/(\pi M))^{1/2}$, $L_*(6668)=1.206$의 구적 | 증명(공표 입력 위; 정리 B‴는 컴퓨터 보조) | 검토 단서: 띠 행의 $6668\le k\le9948$에서 band 노드 범위 밖 행 $m<20001$까지 theorem-B-triple 자체를 씀. 상수 확인: $L_*(6668)=1.206$, $\mathfrak d_k\le6.62/\sqrt k$, 띠 행 $\le1.0845$, 벌크 행 $\le1.0786$ |
| 7.2 | 따름정리: 모든 벌크 $n$에서 P◇이면 $B^+$ | [rae1f209] §5.1 따름정리(관계 주장은 p-pair-node-relation) | 증명 | |
| 7.3 | 명제 2.1(분해 $\tilde\sigma_n=(FL_n-\Theta_n)+BV_n+\mathcal X_n$, $2k+1\le n\le3k+1$) | [rb6a2cd0] §2(c-structure); 입력 (S)=[r05cf8c9]/c-rel-onelevel-fs, c-renewal-identity, c-lemma1, c-X-nonneg | 증명 | 재생 원천 $\tilde\sigma_n$의 정의는 용어집 '숲–나무 재생 원천'([r05cf8c9]의 용어집 항목 fs-source) |
| 7.3 | 두 나무 꼴 $\mathcal T_n(s)=n!e^{n+1}\mathrm{Bor}(s)\mathrm{Bor}(n+1-s)s_{n-s}(k)$ | [rb6a2cd0] §2(c-two-tree-form) | 증명 | 기록의 $\varpi_n$은 새 원고 $\mathcal T_n$(표시 나무 무게) |
| 7.3 | 정리 L(표시 나무 무게의 증가 $\mathcal T_n(s+1)/\mathcal T_n(s)=e^{g(s)}/\mathfrak r_{n-s-1}\ge1$, 등호는 $(s,n)=(k,2k)$뿐)과 보조정리 R($\mathcal T_n(k+1)\le(1-1/k)^{-\nu}\mathcal T_n(k)$) | (L)=[rcb2e2d4]/c-weight-monotone(입력 [r051bfe1]/c-sharp); 보조정리 R=[rb6a2cd0]/c-ratio(입력 size-coupling, lemma-cap-shift (a)=[r030ffae]/lemma-cap-shift, c-weight-monotone) | 증명 | (CS) (a): $k\le N\le2k-1$에서 $s_N(k-1)/s_N(k)\ge(1-1/k)^{N-k+1}$ |
| 7.3 | 정리 10 (a)(b)(c) | [rb6a2cd0] §3.2(c-flat-tails); 입력 (D)=[r696d62c]/p-lemmaD-sharp($kD_k\ge-1-\Upsilon_k$), (Υ)=[r29b01e8]/p-ups-bound($\Upsilon_k\le\hat\Upsilon_k<0.198$, $k\ge3131$), ($H^*_+$)=[r33475a7]/c-hplus, $m_1(k)$ | 증명(공표 입력 위; ($H^*_+$)는 구간 산술 인증, (Υ)는 [r7e03176]/p-row-averaging-e3를 거쳐 $n\le20000$ 인증·right-bulk-increase에 기댐) | |
| 7.3 | 정리 11, (3.2)·(3.3), $\varrho^H$·$\varrho^L$ | [rb6a2cd0] §3.3–3.5; 입력 (Hz)=[r051bfe1]/c-hazard, c-hazard-implies-published (b)($\kappa_N\ge0.307$, $k\ge2000$), (V)의 $c(k)$=[r317d678]/c-vcore-quant, 정리 L(c-weight-monotone), 정리 10(c-flat-tails) | 증명(공표 입력 위; (V)=c-vcore-quant는 비형식, 정리 10을 거쳐 $H^*_+$ 구간 산술) | |
| 7.3 | 보조정리 4.1($\mathcal Y_k(n)$의 모양과 $\nu_0(k)$), 따름정리 12·13 | [rb6a2cd0] §4.1–4.2(c-x-shape, c-cor12, c-cor13); 입력 정리 11, (V), 정리 L; 따름정리 12는 [r030ffae]/band-node | 증명(공표 입력 위; 보조정리 4.1의 경계값은 binary64·50자리 mpmath) | |
| 7.3 | 정리 P | [rb6a2cd0] §4.5(c-band-thmP); 입력 정리 11, 보조정리 R, 보조정리 4.1, (B′)=[r030ffae]/theorem-B-prime, (B‴)=[r030ffae]/theorem-B-triple | 증명(공표 입력 위; $38887\le k\le48965$는 닫힌 꼴 $F_k(103)$의 $k$별 계산, binary64·50자리 mpmath) | $k\ge38887$에서 $\nu_1=103$ |
| 7.3 | 보조정리 C(꼬리의 상한), 정리 11′, 정리 P⁺ | [rb6a2cd0] §4.7(c-tail-cap, c-fl-lower-loc, c-band-thmP-plus); 입력 정리 T 따름 (a)([r4868e30]/c-inner-head-sum), (B′), 보조정리 R, (V), (Hz), 정리 P | 보조정리 C·정리 11′: 증명(공표 입력 위); 정리 P⁺: 비형식($9467\le k\le38886$ binary64 블록 확인, 구간 산술 아님, 최소 여유 $4.6\cdot10^{-9}$, 경계 $k$는 30자리 mpmath) | 문턱 9467 |
| 7.3 | 정리 11″(LP), 정리 P⁺⁺ | [rb6a2cd0] §4.8(c-band-thmP-pp); 입력 (Hz), 정리 T, (V), (B′), 보조정리 R, 보조정리 C(꼬리 상한), 정리 10, 정리 P·P⁺ | 비형식(binary64 LP 확인, $6668\le k\le9466$의 2799개 $k$) | 점별 최솟값 $F^{LP}=0.0056$($k=6668$, $\nu=103$), 블록 경계 최소 여유 $3.1\cdot10^{-7}$ |
| 7.3 | 따름정리 P′⁺⁺ | [rb6a2cd0] §4.9(c-lrp2-band-pp); 입력 finite-P-20000, integer-certificate, theorem-S, theorem-4B, P⁺⁺ | 비형식 | |
| 7.4 | 보조정리 1–3(쌍의 무게, 창 블록의 수준 질량 $k\ge6668$, $1\le b\le4k^{2/3}$, 나머지의 Borel 인자 $\ge((N+1)/(\nu+1))^{3/2}(1-2.3\cdot10^{-4})$, $a\ge366$) | [r5909c9e] §3.1(c-pdiamond-theorem 안); 입력 정리 W([r030ffae]/theorem-W), Robbins; 사소한 입력 p-exp-form·p-capacity-differences([r0ee343a]), largest-tree-facts([r030ffae])는 2.10 행으로 대신 | 증명(정리 W 위; 정리 W는 컴퓨터 보조) | 기록의 $y=b/k^{2/3}$는 새 원고 $\xi$ |
| 7.4 | 보조정리 5–6($\pi^{0,up}$, merge$^{up}$) | [r5909c9e] §3.2 | 증명(Robbins와 Borel 초등 합) | |
| 7.4 | 보조정리 7–8(칸 인자, 칸 합의 적분 하계), (3.2)와 $k$-단조성, 정리 P◇ | [r5909c9e] §3.3(c-pdiamond-theorem) | 비형식(한 변수 격자 평가 binary64, 5200 구간, 50칸; 40자리 재평가) | 정리의 상수 1.149(격자 최솟값 1.14936, 40자리 1.149357). $\Psi^{low}$는 정수 $b$의 함수 $\Psi^{low}(d)=0.3989(2\sqrt d-1.678)$ |
| 7.4 | 정리 P◇′ | [r5909c9e] §3.4(c-pdiamond-giant-bound); 입력 정리 W([r030ffae]/theorem-W), 한 블록 꼴(c-pair-marginal-identity), 보조정리 4–6, heavy path 점화식([r39ea75d]/heavy-path-recurrence = 기존 정리 2.13), 크기 단조성([r79ee9e0]/c-lemma-sh) | 비형식(정리 W 위) | 정리의 상수 2.27(격자 최솟값 2.274, $\theta'\approx0.567$). 증명이 쓰는 $W_0''(N)=\sum_{g=k+104}^N\pi_N(g)k/g$는 [rae1f209] §5.1의 $W_0''$이며 기록 [r5909c9e]는 이를 $W_0'$로 적음 |
| 7.5 | 정리 Q: $B^+\Rightarrow LRP_2$ | [rb6a2cd0] §4.9(c-rel-bplus-lrp2); 입력 다섯 조각, 따름정리 13, 정리 P⁺⁺, 중앙 띠(theorem-S, theorem-4B), 인증(finite-P-20000, integer-certificate), c-bplus-bulk, [rae1f209]/c-pair-explicit | 비형식(입력 P⁺⁺의 binary64 유한 확인, $n\le20000$ 인증, 중앙 띠의 컴퓨터 보조 정리를 물려받음) | 관계 승인 사유: "근거는 컴퓨터 보조 공표 입력과 binary64 유한 확인이다" |
| 7.5 | P◇∧띠⇒B⁺ | [rae1f209]/p-pair-node-relation(관계 sbc38cd…-rel-pairnode-band-implies-bplus); 입력 정리 AR(p-analytic-row-theorem), 노드 bvtheta-band([r030ffae]/band-node = B‴에 $n\ge20001$ 바닥) | 증명(공표 입력 위; 정리 AR·B‴, B‴는 컴퓨터 보조) | 검토 단서: AR의 띠 행은 $6668\le k\le9948$에서 band 노드 범위 밖 행 $m<20001$까지 theorem-B-triple 자체를 씀. B‴ 철회 시 재검토 |
| 7.5 | $LRP_2\Rightarrow W_L^\flat$ | [r317d678]/c-rel-v-lrp2-wlflat(관계 s5a4a753…-rel-v-lrp2-implies-wlflat); 입력 V, source-side, Q⋆(2001–3130)(판 382에서 모두 established) | 증명 | 기존 정리 6.21 |
| 7.5 | $W_L^\flat\Rightarrow W_L\Rightarrow L\Rightarrow T$, 네 위치쌍 ⇒ 뿌리 | [r7c26b8b]/rel-claim-wlflat-implies-wl(관계 rel-wlflat-implies-wl), [rb6423c6]/wl-implies-left-interior(관계 rel-wl-implies-left-interior), [rce3dc75]/left-implies-cross(관계 left-implies-cross-rel), [rce3dc75]/four-part-cover(관계 split-four-position-pairs); 전제 central-gap·right-interior(established) | 증명(공표 입력 위; wl-implies-left-interior는 공표 비형식 정리 사용) | 기존 6.2, 4.1 |
| 7.6 | 명제 A(조각남 확률의 점근) | [r5909c9e] §4.1(c-fragmentation-asymptotic); = [r39ea75d]/bulk-first-order의 둘째 진술 | 증명 | |
| 7.6 | 명제 B·C, 수준 위험률 극한 | [r5909c9e] §4.2–4.4(c-pair-vs-fragmentation-limit, c-pair-theta-asymptotics) | 비형식 유도(창 국소 극한 위) | 읽기. 검토 단서: 명제 B의 수치 확인은 $\theta'=0.8$에서 극한 쪽으로 움직이지 않음 |

같은 이름이 다른 진술을 가리키는 자리(새 번호를 붙일 때 구별): 보조정리 C([rae1f209] 수준 방문 보존 2.8 / [rb6a2cd0] 꼬리 상한 7.3), 보조정리 1·4([rae1f209] / [r5909c9e]), (E1)([r030ffae] 한 블록 재귀 6.9 / [r5909c9e] 한 블록 꼴 2.10), 명제 B([rae1f209] 행 조건 식 7.2 / [r5909c9e] 창×창 극한 7.6), 정리 T([r4868e30] 2.9)·보조정리 T([rae1f209] 7.1), 정리 P([rb6a2cd0] 7.3)·명제 P([r5909c9e] §6.3, 새 원고에 없음).

"""
s = s[:a] + new2 + s[b:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("의존지도 2절 교체 완료")
