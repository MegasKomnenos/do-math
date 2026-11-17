## 부록 A. 기호표

변수와 지표 글자를 먼저 적고, 본문에 나오는 전역 기호를 장별로 처음 정의된 절의 순서로 적는다. 열은 기호, 뜻, 처음 정의된 절, 그리고 같은 양을 연구 기록이 다른 글자로 적은 경우 그 글자와 식별자다. 증명 안에서만 쓰이는 국소 기호는 그 증명이 정의한다.

### 변수와 지표 글자

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $n$ | 행의 크기(주차함수의 「길이」 $n$, 숲의 「크기」 $n$; 낱말은 대상마다 그렇게 쓴다); 둘째 층의 행은 $n=2k+\nu$로 적는다(1.5) | 1.1 | — |
| $m$ | 둘째 크기 변수(부분 숲·나무·환경·행의 크기를 $n$과 함께 적을 때; 합의 지표) | 1.5 | — |
| $t$ | 나무의 크기 변수 | 2.2 | — |
| $N:=n-k$ | 환경(표시한 나무를 뺀 나머지 숲)의 크기; 8·9장에서는 문턱 나무를 덜어 낸 $N=n-k=k+\nu$, 6장에서는 일반 환경 크기 $N\ge0$ | 1.5 | — |
| $k$ | 열의 용량 $\ell+1$(고정) | 1.5 | — |
| $\ell=k-1$ | 수준(최대 변위의 값) | 1.3 | — |
| $y$ | 용량 변수(움직일 때) | 2.1(뜻은 2.6) | — |
| $Y$ | 수준 변수(움직이는 수준; 정의 {{2:old-2-25}}는 일반 $Y\ge0$; 5.5절은 생존 확률의 수준 $Y\in\{y-1,y,y+1\}$과 착지 창의 수준 $Y\ge1$(착지 질량 $\widehat\Lambda(Y)$와 정리 {{5:old-5-33}}부터는 $Y\ge25000$) — 따름정리 {{5:old-5-34}}의 증명에서는 $Y\in\{y-1,y\}$) | 2.6 | — |
| $i$, $j$ | 자리·차·항의 지표; 층 번호(1.5의 「$j$째 층」)도 $j$ | 1.1 | — |
| $u$, $v$ | 꼭짓점 지표 | 2.2($v$), 6.6($u$) | — |
| $r:=n-\ell-1$ | 꼬리 좌표(오른쪽 끝에서 잰 위치; 위치 $\ell$은 끝에서 $r+1$번째 칸); $n-k$와 같은 수 | 1.5 | — |
| $\nu:=n-2k$ | 두 중앙 행 가운데 첫 행 $n=2k$에서 아래로 잰 행의 위치(둘째 층 안에서는 $1\le\nu\le k$; 행의 한가운데에서는 $\nu\in\{-1,0\}$(4.3절)) | 1.5 | — |
| $d$ | 결손(크기−최대 변위; 결손 좌표 $d=m-M$, 크기 $y+d-1$; 2.12절과 3장은 자리 하나를 더한 $n+1-M$으로 센다 — 1.5절이 두 셈법의 관계를 적는다) | 1.5 | — |
| $q$ | 초과(크기−용량) 변수: 무거운 사슬 $i$째 꼭짓점의 초과 $q_i:=S_i-y$, 사슬이 지나는 초과 $q_0>q_1>\dots>q_L$, 착지 창 안의 크기 $k+q$; 둘째 초과 변수는 $q^\prime$ | 1.5 | — |

### 1장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $a_i$ | 차 $i$의 선호 자리 | 1.1 | — |
| $p_n$ | 주차함수의 수 $(n+1)^{n-1}$, $p_0=1$ | 1.1 | 같음; 지수 생성함수 $e^{T(x)}=\sum_np_nx^n/n!$는 $P$ ([rba2ecf4], [r37c204b], [rce3dc75], [rda45d0e], [r708d99c], [r4daca3d], [r475ada3], [ra7615a0], [r8d6850a]) |
| $\alpha$ | 주차함수(선호 수열) $\alpha=(a_1,\dots,a_n)$ | 1.1 | — |
| $\mathrm{PF}_n$ | 길이 $n$ 주차함수 전체의 집합 | 1.1 | — |
| $d_i$ | 차 $i$의 변위 $\mathrm{pos}_i-a_i$; 마지막 차의 변위 $d_n$. 자리 $i$에 선 차의 변위는 $d_{\sigma_i}$ | 1.2 | — |
| $M(\alpha), M_n, M$ | 최대 변위; 균등 주차함수(또는 균등 숲)의 최대 변위($M_0=0$) | 1.2 | 문헌: Petersson의 학위논문 Theorem 2.1은 $D$(3.1절이 인용하는 모형의 최대 변위) |
| $\mathrm{pos}_i$ | 차 $i$가 실제로 선 자리; 마지막 차의 자리 $\mathrm{pos}_n$ | 1.2 | — |
| $b_{n,\ell}$ | 최대 변위가 $\ell$인 길이 $n$ 주차함수의 수 | 1.3 | 같음 ([r15df76b], [r19de912], [r6373c70]) |
| $\ell^\ast$ | 단봉성의 증인(봉우리 첨자); 행 $n$의 것은 가장 작은 증인 $\ell^\ast_n$ | 1.3 | $\ell^*$ ([r7e03176], [r19de912]); $\ell_n$ ([r19de912]; 최빈 위치) |
| $A_{n,\ell}$ | 최대 변위가 $\ell$ 이하인 누적 개수($A_{0,\ell}=1$, $A_{n,-1}=0$); 약기 없이 늘 두 첨자로 적는다 | 1.3 | 같음 ([r15524fd], [r15df76b], [r19de912], [r6373c70]); $A_s:=A_{s-1,k-1}$ ([r475ada3], 한 칸 어긋남) |
| $\mathsf P, \mathsf P(n)$ | 문제 $\mathsf P$(모든 행이 단봉인가)와 그 긍정 진술인 명제 $\mathsf P$(4.1절); 행 $n$의 명제 $\mathsf P(n)$ | 1.3, 4.1 | $P$, $P(n)$ ([r15524fd], [r15df76b]) |
| $d_{n,k}$ | 한 칸 차분 $b_{n,k}-b_{n,k-1}=A_{n,k}-2A_{n,k-1}+A_{n,k-2}$; 확률판은 $d_{n,k}/p_n$ | 1.5 | $\Delta_{n,k}$ ([r37c204b]); $\delta_0$ ([r708d99c]; $\delta_1=d_{n,k+1}$); $\delta_{n,c}$ ([ra4c01fc]; $c\to k$); 같음 ([r13b0b8f]; $E_n=d_{n,c}/p_n$); $\Delta\pi_m$ ([r3d0856b]); $d_n$ ([rcb2e2d4]; 기록 줄임); 같음 ([r6373c70]); $\delta_{n,k}$ ([ra7615a0]); $d_m$ ([r6f5f48f]; 둘째 첨자 생략); [r7c079be]의 $d_{n,k}$는 소인 질량 $C_{n,k}e^{-n}/n!$ |
| $k_n$ | 행 $n$의 한가운데 용량 $\lceil n/2\rceil$(비교 $b_{n,k_n-1}$ 대 $b_{n,k_n}$) | 1.5 | $m=\lceil n/2\rceil$ ([r15df76b], [r6373c70]) |
| $x, \hat x$ | 임계 창 좌표 $x=(n-k)/n^{2/3}$, $\hat x=(n-\ell)(\ell+1)^{-2/3}$($=r/n^{2/3}$, $=(r+1)(\ell+1)^{-2/3}$)(3장은 $x$만, 6장은 $\hat x$만 쓴다) | 1.5 | $\hat x=(Y+1)u^2$, $Qk^{-2/3}$, $(n-y+1)/y^{2/3}$ ([ra4c01fc], [r5f5cf73], [r8a9b11e]); $X=(n-y)/y^{2/3}$ ([r23f10e9], [r58b4caa]; $X=\hat x-(\ell+1)^{-2/3}$) |
| $\lambda$ | 용량과 행 크기의 비 $k/n$(움직이는 용량이면 $y/n$) | 1.5 | 같음 ([r23f10e9], [r58b4caa], [r8a9b11e]); $\lambda=k/N$ ([r8456f59]; 이 글은 풀어 적는다) |

### 2장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $h_i$ | 자리 $i$의 선호 용량 $i-\max(\{j<i:\sigma_j>\sigma_i\}\cup\{0\})$ | 2.1 | 같음 ([r88bed8a], [r631b0f4], [r8d6850a], [rdc27681], [ra7615a0]); $h_p$ ([r1892593]; 지표 $p\to i$); $t_i$ ([r15524fd]; 선호 용량 — [r631b0f4]의 $t_i=i-h_i$와 다른 뜻) |
| $A^\sigma_\ell$ | 섬유 $\sigma$의 누적 개수 $\prod_i\min(h_i,\ell+1)$ | 2.1 | $C_{\sigma,\ell}$ ([r15524fd]); $\prod_p\min(h_p,k)$ ([r1892593]; 글자 없음); $F_\sigma(k)=\prod_i\min(h_i,k)/h_i$ ([r88bed8a]; 정규화 $1/\prod h_i$, 인수는 용량) |
| $\sigma, \sigma_i$ | 결과 순열; 자리 $i$에 선 차 | 2.1 | — |
| $\mathfrak S_n$ | $n$차 대칭군 | 2.1 | — |
| $b^\sigma_\ell$ | 섬유 $\sigma$의 행 $A^\sigma_\ell-A^\sigma_{\ell-1}$ | 2.1 | — |
| $H_k(\sigma), H_k(F)$ | 용량이 정확히 $k$인 자리의 수(문턱 자리 수); 숲·나무에서는 크기가 정확히 $k$인 부분나무의 수(문턱 부분나무 수) | 2.1($\sigma$), 2.2($F$) | $H_a$ ([r1892593]; 문턱 $a$); $H$ ([r8d6850a]) |
| $Z_k(\sigma), Z_k(F)$ | 용량이 $k$를 넘는 자리의 수(무거운 자리 수); 숲·나무에서는 부분나무 크기가 $k$를 넘는 꼭짓점의 수(무거운 꼭짓점 수) | 2.1($\sigma$), 2.2($F$) | $Z$ ([r5f5cf73], [r8d6850a], [rdc27681]); $Z_a$ ([r1892593]; 문턱 $a$); $J^{cap}_k$ ([ra7615a0]) |
| $\mathfrak v_k(Z,H)$ | 섬유 부호식 $(1+1/k)^Z+(1-1/k)^{Z+H}-2$(보조정리 {{2:capacity-ratio}}의 진술이 정의한다) | 2.1 | $g(x; \eta)$ ([r7c26b8b], [rb7effe0], [r89eb039]); $g(Z,H)$ ([r88bed8a]) |
| $t_v$ | 꼭짓점 $v$의 부분나무 크기(나무 크기 변수 $t$를 꼭짓점으로 첨자한 것; 7.5의 토막 나무에서는 꼭짓점 $v$의 토막 크기) | 2.2 | $s_v$ ([rbeae3a3], [r42d9a17], [r88bed8a], [r3172894], [rdc27681]); $s_w$ ([r2ec875c]; $w\to v$) |
| $F$ | 라벨 뿌리 숲(변수) | 2.2 | — |
| $I_v$ | 꼭짓점 $v$의 국소 역전 수 | 2.2 | — |
| $M(F)$ | 숲 $F$의 최대 국소 역전 수(정리 {{2:old-2-10}}으로 최대 변위와 분포가 같다) | 2.2 | — |
| $\tau$ | 뿌리 라벨 나무(변수); 토막 나무의 모양 | 2.2 | — |
| $A_\ell(x)$ | 누적 개수의 지수 생성함수 $\sum_nA_{n,\ell}x^n/n!$ | 2.3 | $F_\ell(z)$ ([rf09e7ef], [r58b4caa]); $F(x)=F^{(k)}$ ([rbeae3a3]; $=A_{k-1}$); $D(x)$ ([rb7effe0], $=A_{k-1}$); $F_c=\exp T_c$ ([r05cf8c9]; 용량→수준); $F_\ell(x)$ ([r15524fd]) |
| $A_n[\mathrm{wg}], A[\mathrm{wg}](x)$ | 가중 분배함수 $\sum_{\sigma\in\mathfrak S_n}\prod_i\mathrm{wg}_{h_i}$와 그 지수 생성함수(정리 {{2:weighted-partition}}; $A_{n,\ell}$ 가족의 범함수 변형 — 무게 $\mathrm{wg}_t=\min(t,\ell+1)$에서 $A_{n,\ell}$, $A_\ell(x)$) | 2.3 | — |
| $Q_\ell(x)$ | 역수 미분방정식의 적분 다항식 $\sum_{j<\ell}(\ell-j)p_jx^{j+1}/(j+1)!$; 열 $k$에서는 $Q_{k-1}$ | 2.3 | 같음 ([r15524fd]; $Q^\prime_\ell$, $H_\ell=1/F_\ell$); $\Pi_k(x)$ ([rb7effe0]); $Q_k(x)$ ([r7c079be], [r89eb039], [rf451d83], [rbeae3a3]; 첨자 용량); $H_\ell=Q^\prime_\ell$ ([rf09e7ef]); [r37c204b]의 $Q_k=(1-T)(P-P_{<k})$는 다른 양 |
| $\mathrm{wg}_t, \mathrm{wg}(t,I)$ | 가중 분배함수의 무게 — 크기 $t$ 부분나무의 무게 $\mathrm{wg}_t=\sum_{I<t}\mathrm{wg}(t,I)$와 국소 역전 수 $I$에 따른 세분(정리 {{2:weighted-partition}}; 둘째 인수는 국소 역전 수 $I_v$(2.2절)의 값) | 2.3 | — |
| $T_\ell(x)$ | 허용 나무 생성함수 $\sum_t\mathcal N_\ell(t)x^t/t!$($A_\ell=\exp T_\ell$; 나무 함수의 허용판) | 2.4 | — |
| $U_v$ | 꼭짓점 $v$의 독립 균등 변수(변위 표현) | 2.4 | — |
| $\mathcal N_\ell(t)$ | 크기 $t$의 허용 나무 수 $\min(t,\ell+1)A_{t-1,\ell}$ | 2.4 | $c_N(\kappa)=\mathcal N_{\kappa-1}(N)$ ([r4868e30]); $\mathcal T_\ell(s)$ ([rcb2e2d4]); $t_s(c)$ ([r05cf8c9]; 용량 $c\to$ 수준) |
| $G$ | 숲의 가장 큰 나무의 크기($=S_1$) | 2.5 | 같음 ([r8456f59]); $G_N$ ([r030ffae], [r5bbc534]); $S_0$ ([r88bed8a]) |
| $L$ | 가장 큰 나무 사슬에서 문턱을 넘는 항의 수(사슬 길이; $S_1>\dots>S_L$, 마지막 초과 $q_L$) | 2.5 | $J$ ([re71a735]); $J_d$ ([r845b205]); $Z$ ([r8a9b11e], [r23f10e9], [r29c10cd], [r696d62c], [rb1d8cd5]) |
| $S_1>S_2>\cdots$ | 문턱 $y$의 가장 큰 나무 사슬(가장 큰 자식 쪽으로 내려가며 읽은 부분나무 크기 수열) | 2.5 | $S_0>S_1>\cdots$ ([r88bed8a]; 기록 $S_j$는 이 글의 $S_{j+1}$); $s_j$ ([r29c10cd]); $s_i$ ([r42d9a17], [r1aa0be6]) |
| $T(x)$ | 나무 함수 $\sum_tt^{t-1}x^t/t!$ | 2.5 | 같음 ([rba2ecf4], [ra4c01fc], [r475ada3], [ra7615a0]; $T=xP=xe^T$); $P=e^T$ ([r37c204b]; 주차함수 지수 생성함수) |
| $\pi^0_n(y)$ | 쪼개짐 확률 $\Pr_n(G\le y)$(크기 $y$를 넘는 나무가 없을 확률; 2.5절의 낱말 「쪼개짐」) | 2.5 | $P_0(N)$ ([rae1f209]; 인수 $k$ 고정); $\mathcal N(j,y)$ ([r29c10cd]); $\mathcal N(L,c)$ ([r696d62c]); $\mathcal N(F,Y)$ ([r8a9b11e], [r23f10e9]); $\mathrm{stop}_N(h)=\pi^0_{N-h-1}(x-1)$ ([rb1d8cd5]); $f_N(y)=p_N\pi^0_N(y)$ ([r39ea75d]); $q_N=\pi^0_N(k)$ ([r8456f59]); [r030ffae] 보고서 L260(보조정리 H-G)의 $q_N=1-\sum_j\mathrm{Bor}(j)\rho_j$는 $\pi^0_N(k+1)$(보고서 L25·exposition L42의 $q_N$은 $s_N(k+1)$); L226의 「모든 나무 크기 $<k$」 확률은 $\pi^0_{N^\prime}(k-1)$(글자 없음); $\Pi_n(\le c)$ ([r59c82d7]; $c\to y$) |
| $\pi_n(m)$ | 크기 $n$ 균등 뿌리 숲에서 크기 $m$ 나무 수의 기댓값 $\binom nmm^{m-1}p_{n-m}/p_n$; $m>n/2$에서는 가장 큰 나무의 법칙 $\Pr_n(G=m)$(가장 큰 나무 핵) | 2.5 | $\varpi_N(s)$, $\varpi_L(s)$ ([rae1f209], [r030ffae]); $\pi_N(m)$ ([r39ea75d], [r8456f59], [r13b0b8f]); $\pi_F(t)$, $\pi_n(t)$ ([r8a9b11e], [r23f10e9], [r58b4caa]); $\gamma_L(j)$, $\gamma_N(t)$ ([r5bbc534]); $G_N(s)$ ([r207f124]); $\beta_c(d,a)=\pi_{c+d-1}(c+a)$, $K_c(d,a)$ ([r98fb348]); $w_{m,s}=\pi_m(m-s)$ ([r6b37c7e]); $\varpi_m(s)$ ([r6f5f48f]); 같음 ([r59c82d7]; 인수 $s$) |
| $\mathrm{Bor}(m)$ | Borel 질량 $e^{-m}m^{m-1}/m!$ | 2.5 | 같음 ([r13b0b8f], [r8a9b11e], [rae1f209], [r845b205]); $\beta_j$, $\beta_d$ ([r4868e30], [r7e03176], [r79ee9e0]); $\beta_m$, $\beta_s$ ([rb7effe0], [r5bbc534]); $\beta_n$ ([r2ec875c]); $\tau_j$, $\tau_k$, $\tau_m$ ([ra4c01fc], [r5f5cf73], [r475ada3], [r39ea75d], [r8456f59], [r7c079be], [r89eb039], [r207f124]); $\mathrm{Bo}(n)$ ([r051bfe1]); $q_s=\mathrm{Bor}(s+1)$ ([r6b37c7e]); $\beta_h$ ([r6a8c8b6]); $\beta_g$ ([r3172894]); $\tau_s$ ([ra7615a0]); $\tau_m$ ([r8d6850a]); 같음 ([r6f5f48f], [r59c82d7]) |
| $\mathrm{Bor}^{*j}(m)$ | Borel–Tanner 질량(독립 Borel 변수 $j$개의 합이 $m$일 확률) | 2.5 | $BT$ ([r8a9b11e]); $BT_n(j)$ ([re71a735]); $BT_j(J)$ ([r58b4caa]; 누적); $\beta^{*j}(h)$ ([r6a8c8b6]) |
| $\Pr_n, \mathbb E_n$ | 크기 $n$ 균등 뿌리 숲의 법칙(=길이 $n$ 균등 주차함수의 법칙)과 그 기댓값 | 2.5 | — |
| $\Psi(q)$ | Borel 갱신함수 $\sum_{j=1}^q\mathrm{Ren}(j)$ | 2.5 | $U(D)=1+\Psi(D)$ ([r4868e30]); $\Psi(d)$ ([r5bbc534], [r9bf2dc6], [r2ec875c]); $\Psi(b)$ ([r030ffae]); $\bar\Psi$ ([r030ffae], 다른 양) |
| $\theta_t(k)$ | 크기 $t$ 균등 나무의 문턱 부분나무 기대 수 $\mathbb E^T_t[H_k]=\mathrm{Ren}(t-k)\mathrm{Bor}(k)/\mathrm{Bor}(t)=\binom tk\frac{k^{k-1}(t-k)^{t-k}}{t^{t-1}}$(정리 {{2:chain-law}}(라)가 정의; 크기 $N$ 숲에서 부분나무 크기가 $m$인 꼭짓점의 기대 수는 같은 (라)의 $\mathbb E_N[H_m(F)]=\theta_{N+1}(m)$) | 2.5 | $\theta_N(k)$ ([rb6a2cd0]; $N\to t$) |
| $\mathrm{Ren}(j)$ | 갱신 방문 핵 $j^je^{-j}/j!=j\,\mathrm{Bor}(j)$, $\mathrm{Ren}(0):=1$; 하계 함수는 $\mathrm{Ren}_*(j)$ | 2.5 | $c_j$, $c_h$, $c_0=1$ ([r4868e30]); $u(j)$, $u(r)$, $u(n)$, $u(q)$ ([r030ffae], [re71a735], [r2ec875c], [r98fb348], [r8456f59], [r5bbc534]); $c_d$ ([r79ee9e0]); $c_j$, $c_g$, $c_h$ ([r42d9a17], [r1aa0be6], [r13b0b8f], [r7798355], [r690be93]); $c_h=h\beta_h$ ([r6a8c8b6]) |
| $\Pr^{T}_t, \mathbb E^{T}_t$ | 크기 $t$ 균등 뿌리 라벨 나무의 법칙과 기댓값 | 2.5 | — |
| $c_m(Y)$ | 수준 질량 $b_{m,Y}/p_m=\Pr_m(M=Y)$ | 2.6 | $\pi_m(\ell)$ ([r845b205], [r3d0856b], [re71a735]); $\beta_m(c)=b_{m,c}/p_m$ ([r13b0b8f]); $q_m$, $q^+_m$ ([r79ee9e0]; 수준 $k-1$·$k$); $r_N,r^\prime_N$ ([rae1f209], [r030ffae]); $f_N=c_N(k-1)$ ([r77e234e], [rae1f209]); $V_c(d)$ ([re71a735]); $c_m(\ell)$ ([r2ec875c]); 같음 ([r8a9b11e], [r23f10e9], [r58b4caa]); $\pi_m(\ell)$ ([raad7e6d]); $\beta_n(c)$ ([r59c82d7]; $c\to y$) |
| $g(x)$ | $(x-1)\log(1+1/x)$(Borel 이웃비와 자유 비의 로그) | 2.6 | $g(j)$, $g(n)$ ([rb6a2cd0], [rcb2e2d4], [raad7e6d]); $f(x)$ ([r207f124], [r23f10e9], [r58b4caa]); $\mathfrak f(q)$ ([r5bbc534]) |
| $s^{T}_t(y)$ | 크기 $t$ 균등 뿌리 나무가 용량 $y$ 아래 살아남을 확률 $\Pr^T_t(M^T_t\le y-1)$(나무 생존 확률) | 2.6 | $\chi(g)$, $\chi^+(g)$ ([r030ffae]; 용량 $k$, $k+1$) |
| $s_m(y)$ | 생존 확률 $A_{m,y-1}/p_m=\Pr_m(M\le y-1)$, $s_m(0):=0$ | 2.6 | $F_m(y)$ ([r317d678], [r845b205]); $F_m(\ell)=s_m(\ell+1)$ ([r3d0856b], [re71a735]); $s_N,q_N,t_N$ ([rae1f209], [r030ffae]); $\mathfrak s_N$ ([rb6a2cd0], [r051bfe1], [r5bbc534], [rcb2e2d4]); $s_n$ ([r7e03176]); $q_y(N)$ ([r207f124]); $s_c(d)$ ([r98fb348]); $\sigma_\ell(m)=s_m(\ell+1)$ ([r79ee9e0]); $\alpha_m(c)=s_m(c+1)$ ([r13b0b8f]); $u_m(Y)$, $u_n(y)$ ([r8a9b11e], [r23f10e9], [r58b4caa]); $Q_c=s_{k+c}(k+1)$ ([r030ffae]); $\alpha_{N,\ell}=s_N(\ell+1)$ ([r39ea75d]); $s_N$ ([r6f5f48f]); $s_m$ ([r3172894]); $F_m(\ell)=s_m(\ell+1)$ ([raad7e6d]); $a_n(c)$ ([r59c82d7]; $c\to y$) |
| $\Pr_{\mathrm B}$ | 임계 볼츠만 법칙 | 2.6 | — |
| $e_n$ | $\mathcal K^{\prime\prime}_{n,k}(k)=2E2_{n,k}$ | 2.7 | 같음 ([ra4c01fc], [r5f5cf73]); $\mathscr K^{\prime\prime}_{(n,k)}(k)$ ([r8d6850a]) |
| $B_{n,\ell}$ | 최댓값이 용량에 막힌 주차함수의 수(막힌 주차함수 수; 첨자는 수준 $\ell$ — 정의 {{2:old-2-27}}) | 2.7 | 같음(첨자는 수준; [r37c204b], [rce3dc75], [ra4c01fc], [rda45d0e], [r5f5cf73], [r631b0f4], [r8d6850a]) |
| $E_{n,k}, E2_{n,k}$ | 짝수 동률 수, 두 차 동률 수 | 2.7 | 같음 ([r631b0f4]; $E_{n,k}$); $E2_{n,c}$ ([ra4c01fc]; $c\to k$); $V_{n,k}=2E_{n,k}$ ([ra7615a0]) |
| $J_n(z)$ | 경계 다항식 $\sum_{\sigma\in\mathfrak S_n}H_k\,k^{H_k-1}\,z^{Z_k}\prod_{i:\,h_i<k}h_i$(문턱 $k$ 고정; $z$는 무게 변수); 열 $k$의 비교에 쓰는 값은 $J_n(k-1)$ | 2.7 | $J_n(k)$ ([r475ada3]; 무게 $k$의 값); $J_n(c)$, $B^G=J_n(k-1)$ ([r37c204b], [r5f5cf73]); $J_n(k-1)$ ([r8d6850a]; 값); $B^G_{n,k}$ ([ra7615a0]; 중앙 행의 $J_n(k-1)$) |
| $M^{\#}(\alpha)$ | 최대 변위를 달성하는 차의 수($M^\#\ge2$인 주차함수가 동률) | 2.7 | $K_M$ ([ra4c01fc], [r5f5cf73], [r631b0f4]) |
| $T^{\le k}, T^{>k}$ | 나무 함수의 절단 $\sum_{t\le k}t^{t-1}x^t/t!$와 나머지 $T-T^{\le k}$(2.7절 보조 급수 문단; 7.4절도 씀) | 2.7 | $T_{\le k}$, $T_{>k}$ ([r475ada3]); $T_c(x)$ ([ra4c01fc]; 아래 첨자, 용량 $c\to k$) |
| $\Xi_{2k,k}$ | $B_{2k,k-1}=J_{2k}(k-1)-\Xi_{2k,k}$의 보정 $\binom{2k-1}{k-1}p_{k-1}^2$(행 $n=2k$에서만 정의한다) | 2.7 | $C^{ev}_{n,k}=\mathbf 1_{n=2k}\binom{2k-1}{k-1}k^{2k-4}$, $C_{n,k}$ ([rba2ecf4], [r37c204b], [rce3dc75], [ra7615a0]; $k^{2k-4}=p_{k-1}^2$) |
| $\mathcal E_{<k}(x)$ | 절단 급수 $\sum_{j<k}p_jx^j/j!$(2.7절 보조 급수 문단; 4.3·5.2.1·7.4절도 쓴다) | 2.7 | $P_{<k}$, $P_k$ ([r37c204b], [ra7615a0]) |
| $\mathcal K_{n,k}(y)$ | 얼린 용량 다항식(인자를 $h_i$로 고정하고 용량을 실수 $y$로 둔 것); 두 변수 판 $\mathcal K_{n,k}(\eta,y)$(문턱 자리의 무게를 $\eta$로 따로 둔 것)와 그 지수 생성함수 $\mathcal K_k(\eta,y; x)$, 얼린 지수 생성함수 $\mathcal K_k(y; x):=\mathcal K_k(k,y; x)$(2.7절; 따름정리 {{2:two-variable-frozen}}·{{2:volterra-residual}}가 쓰고 7.4절이 받는다) | 2.7 | $\mathcal K(\cdot)$ ([rce3dc75]); $Z_{n,k}(u)$ ([rda45d0e]; $y=k+u$); $\mathcal A_{n,k}(\gamma)$ ([r708d99c]); $\mathcal A(c)$ ([r5ddf8a8]); $\mathcal K_{n,k}(c)$ ([r475ada3]); 같음 ([r5f5cf73]); $E_{k,n}(c)$ ([ra7615a0]; 첨자 순서·$c\to y$); $f_{n; k}(y)$ ([rdc27681]) |
| $\mathcal X(y;x)$ | 잔차 $\mathcal K_k(y; x)-\mathcal G_\ast(y; x)$(2.7절 Green 응답 뒤 문단; 따름정리 {{2:volterra-residual}}; 7.4절도 쓴다) | 2.7 | $X$ ([r475ada3]) |
| $\mathrm{Gr}(x)$ | Green 적분인자의 지수 $T(x)-T(x)^2/2$ | 2.7 | $U=T-T^2/2$ ([rba2ecf4], [r37c204b], [rce3dc75], [ra4c01fc], [rda45d0e], [r4daca3d], [r475ada3], [ra7615a0], [r8d6850a]) |
| $\mathrm{pd}(y;x), \mathrm{pd}_t(y)$ | 조각 차이 $\mathrm{pd}_t(y):=y\mathcal K_{t-1,k}(y)-t^{t-1}$와 그 지수 생성함수($\mathcal K_k(y; x)=e^{T}e^{\mathrm{pd}}$ — 2.7절 Green 응답 뒤 문단, 따름정리 {{2:volterra-residual}}; 7.4절도 쓴다) | 2.7 | — |
| $\mathrm{sm}_k(x)$ | 작은 나무 급수 $(1-T)(e^T-\mathcal E_{<k})$(2.7절 보조 급수 문단; $\mathcal E_{<k}+\mathrm{sm}_k=e^T(1-T^{>k})$; 4.3·5.2.1절도 쓴다) | 2.7 | $Q_k$ ([r37c204b]) |
| $\mathcal G_{z,i,n}$ | Green 응답: 2.7의 일차 선형 미분방정식에서 원천항 $e^{T}x^i/i!$ 하나가 내는 해의 몫의 계수 $n!\,[x^n]\,e^{T(x)}e^{z\mathrm{Gr}(x)}\int_0^xe^{-z\mathrm{Gr}(\varsigma)}\frac{\varsigma^i}{i!}\,d\varsigma$($z$의 다항식; 5.2.1은 매개변수를 $y$로 두어 $\mathcal G_{y,i,n}$이라 적는다; 연쇄 해 $\mathcal G_\ast(y; x):=\mathcal E_{<k}+\mathrm{sm}_k+y\,e^{T}e^{y\mathrm{Gr}}\int_0^x\mathrm{sm}_k\,e^{-y\mathrm{Gr}}$는 같은 가족의 변형 — 2.7절 Green 응답 뒤 문단이 정의하고 4.3·7.4절이 쓴다) | 2.7 | $G_{c,h,n}$ ([rba2ecf4], [r4daca3d]); $\mathcal G_{c,h}$ ([rda45d0e]) |
| $\mathcal P_m(j)$ | 마지막 차 자리 법칙 $\Pr_m(\mathrm{pos}_m=j)=j\binom{m-1}{j-1}p_{j-1}p_{m-j}/p_m$ | 2.8 | $\Pi_m(j)$ ([r79ee9e0], [r7e03176], [r8456f59] L32, [r3172894]); $\Pi_L(j)$ ([r5bbc534]); [r79ee9e0]의 $\pi_m(j)$·$p_j$는 다른 양 |
| $x_t(y)$ | 나무 곡률 $s^T_t(y+1)-2s^T_t(y)+s^T_t(y-1)$; 열 $k$에서는 $x_t(k)$ | 2.9 | 같음 ([r58b4caa], [r8a9b11e], [r23f10e9]); $x_N(k)$ ([r4868e30]) |
| $M^{T}_t$ | 크기 $t$ 균등 뿌리 나무의 최대 변위 | 2.9 | — |
| $\Pi$ | 사슬 생존 곱: 나무(사슬) 전체의 $\prod_{S_i>y}y/S_i=\prod_i y/(y+q_i)$ | 2.9 | $W_v=\prod_{S_j>v}v/S_j$ ([r23f10e9]; 용량 $v$) |
| $\Psi^{\mathrm{low}}_{(\varkappa)}$ | 갱신함수 하계의 실수 인수 정밀판 $(2\pi)^{-1/2}(2\sqrt\varkappa-\mathsf c_\Psi+\frac1{2\sqrt\varkappa}-\frac1{24}\varkappa^{-3/2})$($\varkappa\ge1$; $\varkappa<1$에서 $0$; 보조정리 {{2:power-sum-renewal}}(ㄴ)이 정의하고 8.2절 보조정리 {{8:envelope-H}}와 (8.18)이 쓴다; 인수 $\varkappa$는 실수이고 8장은 제 인수를 넣어 부른다; 6.6절 보조정리 {{6:lemma-Hprime}}의 증명은 (ㄴ)의 하계 $(2\pi)^{-1/2}(2\sqrt d-\mathsf c_\Psi)$를 받는다) | 2.9 | $\Psi_{(r)}$ ([r030ffae]); $\Psi_\flat(r)$ ([rfc69320]) |
| $\mathsf c_\Psi$ | 갱신함수 하계의 상수 $-\mathsf z_{1/2}+\mathsf z_{3/2}/12$($\in(\frac32,1.6781)$; 명명 상수; $\Psi^{\mathrm{low}}_{(\varkappa)}$의 식에 든다 — 보조정리 {{2:power-sum-renewal}}(ㄴ); 6.6절 보조정리 {{6:lemma-Hprime}}의 증명도 부른다) | 2.9 | $C_\Psi$ ([rfc69320]); $-\zeta(\frac12)+\zeta(\frac32)/12$로 풀어 적음 ([r030ffae]) |
| $\mathsf z_{1/2}, \mathsf z_{-1/2}, \mathsf z_{3/2}$ | Riemann 제타 함수의 $\tfrac12$, $-\tfrac12$, $\tfrac32$에서의 값(명명 상수; 수치와 인증 구간은 부록 D; 2.9가 정의하고 6.6절·8장이 받는다) | 2.9 | $\zeta(\frac12)$, $\zeta(-\frac12)$, $\zeta(\frac32)$ ([r8a9b11e], [r030ffae], [rfc69320]) |
| $\mathrm{rb}_m$ | Robbins 나머지 $\log m!-(m+\tfrac12)\log m+m-\tfrac12\log(2\pi)$ | 2.9 | $\rho_m$ ([rae1f209]); $\lambda_q$ ([r5bbc534]); $r_n$ ([r9bf2dc6]); $\varepsilon_h$ ([r7798355]); $\theta_n$ ([r29c10cd]) |
| $b^{(2)}_m$ | 두 수준 개수 $b_{m,k}+b_{m,k-1}$ | 2.10 | $L_m$ ([rae1f209]); $bb_m$ ([rcb2e2d4]); $b^+_m+b^-_m$ ([r6f5f48f]; 글자 없음) |
| $b^{T}_{t,\ell}$ | 크기 $t$, 최대 변위 $\ell$인 뿌리 나무의 수 $\mathcal N_\ell(t)-\mathcal N_{\ell-1}(t)$ | 2.10 | — |
| $c^{(2)}_m$ | 두 수준 질량 $c_m(k)+c_m(k-1)=b^{(2)}_m/p_m$ | 2.10 | $\ell_N$ ([rae1f209]); $s_m$ ([r3d0856b]); 나무판 $\tilde u_s,\tilde v_s$·$C^\pm_s$([rae1f209])는 $b^T_{t,k}/p_{t-1}$, $b^T_{t,k-1}/p_{t-1}$로 풀어 적음 |
| $\delta_t$ | 나무 한 칸 차분 $b^T_{t,k}-b^T_{t,k-1}$; $t\ge k+1$에서 $=(k+1)b_{t-1,k}-(k-1)b_{t-1,k-1}=t^{t-1}x_t(k)$ | 2.10 | $\hat\delta_s$, $\delta_s$ ([rcb2e2d4], [r05cf8c9], [r6f5f48f]; $s\to t$); 같음 ([raad7e6d]; $\delta_{m+1}$) |
| $\Theta_n$ | 문턱 나무 손실 $\binom nkk^{k-2}A_{n-k,k-1}$ | 2.10 | 같음 ([r6f5f48f]); $\mathrm{thr}_n=\varpi_n(k)/k$ ([rcb2e2d4]); $K_n=-\Theta_n$ ([r05cf8c9]) |
| $\mathcal B_\ell(x)$ | 나무 수준 개수의 지수 생성함수 $\sum_tb^T_{t,\ell}x^t/t!=T_\ell-T_{\ell-1}$ | 2.10 | $a=T_{k+1}-T_k$, $b=T_k-T_{k-1}$ ([r05cf8c9]; 첨자 용량) |
| $\mathrm{BV}_n$ | 줄기 이득(정의 {{2:old-2-40}}; 문턱 나무 손실 $\Theta_n$과 견주는 양) | 2.10 | $BV_n$ ([r6f5f48f]; 이탤릭) |
| $R_j$ | 자유 Borel 보행의 부분합($R_0=0$) | 2.11 | $R_j$ ([r8a9b11e]); $T_k$(iid Borel 합; [r8a9b11e]); $S_j=g_1+\dots+g_j$ ([r845b205]); $S_j$ ([ra7615a0]) |
| $\beta_i$ | 독립 Borel 변수(자유 Borel 보행의 걸음; 사슬에서는 $q_{i-1}-q_i$) | 2.11 | $Y$ ([r8a9b11e]); $g_i$ ([r845b205]); $B$ ([r7e03176], [r79ee9e0]) |
| $\mathrm{tilt}_q(q^\prime)$ | 기울임 인자 $\mathrm{Bor}(y+q^\prime)/\mathrm{Bor}(y+q)$($q^\prime<q$; 용량 $y$는 문맥의 것); 6.5절·9장은 출발 초과를 결손 $d$로 두어 $\mathrm{tilt}_d(q)$로 적는다(같은 글자의 첨자 변형) | 2.11 | $\tau_d(b)$ ([re71a735]); $r_j(t)$ ([r845b205]; 실수 연장); $\rho_h$, $\rho_j$ ([r030ffae]), $\omega_N(r)$ ([r5bbc534])는 $\mathrm{Bor}(N+1-r)/\mathrm{Bor}(N+1)$ 꼴 |
| $\Pr^y(q\to q^\prime)$ | 초과 $q$에서 $q^\prime<q$로 내려갈 확률 $\mathrm{Bor}(q-q^\prime)\mathrm{Bor}(y+q^\prime)/\mathrm{Bor}(y+q)$(사슬의 전이 확률) | 2.11 | — |
| $\Pr^y, \mathbb E^y$ | 용량 $y$의 무거운 사슬 법칙과 기댓값; 기준 용량 $y_0$의 것(얼린 법칙; 6.5절이 정의)은 $\Pr^{y_0}$, $\mathbb E^{y_0}$ | 2.11 | — |
| $W_n(\gamma)$ | 간격 수열 $\gamma$(지정 사슬 크기 $\mathfrak t_1>\dots>\mathfrak t_j$, 길이 $j$)의 사슬 가중치 $\mathrm{nf}(n,\,n-\mathfrak t_j)\prod_{i<j}n/\mathfrak t_i$; $1/n$ 전개의 계수 $W^{[s]}(\gamma)$($W_n(\gamma)=\sum_{s\ge0}W^{[s]}(\gamma)n^{-s}$ — 정리 {{5:chain-weight-all-orders}}가 5.2에서 정의하는 같은 양의 변형) | 2.12 | $W_n(g)=\mathcal R(n,d_k-1)\prod_{i<k}n/s_i$ ([r1aa0be6], [r13b0b8f], [r690be93]; $k$는 사슬 길이, $d_k=n+1-s_k$); [r42d9a17]에는 글자가 없음(식 (20)만) |
| $\mathrm{lc}_i(d)$ | 정규화 인자의 로그 계수 $\frac1i\bigl[\frac{d^{i+1}}{i+1}+2d^i-\sum_{\rho<d}\rho^i\bigr]$($\log\mathrm{nf}(n,d)=\sum_{i\ge1}\mathrm{lc}_i(d)n^{-i}$; 보조정리 {{2:nf-log-coefficients}}(가); 5.2.3절의 전차수 전개가 받는다) | 2.12 | $\lambda_h(d)$ ([r13b0b8f]) |
| $\mathrm{nf}(n,d)$ | 사슬 전개의 정규화 인자 $e^d\frac{n!}{(n-d)!}\frac{(n-d)^{n-d-2}}{n^{n-2}}$ | 2.12 | $\mathcal R(n,d)$ ([r1aa0be6], [r42d9a17], [r13b0b8f]) |

### 3장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $f$ | 극한 $X$의 밀도(8.3절이 항등식 $f=-\frac d{dx}\Pr(X\ge x)$로 한 번 부른다; 2·4·5·6·7장 증명 안의 일반 함수 글자 $f$는 이 양이 아니다) | 3.1 | 같음 ([r1aa0be6]); $f_X$ ([r81e7051]) |
| $X_n, X$ | 정규화 결손 $(n+1-M_n)/(n+1)^{2/3}$과 그 극한(해싱 극한); 분포함수·생존함수는 $\Pr(X\le x)$, $\Pr(X\ge x)$로 적는다 | 3.1 | 같음 ([r81e7051]; 그 기록의 문헌 이름 $\mathcal M$은 극한 $X$); [rae1f209]의 $X_n$은 다른 양이고 이 글이 쓰지 않는다 |
| $x_\ast$ | 밀도 $f$의 최빈점(임계 창 좌표의 특정값) | 3.2 | $m$ ([r1aa0be6], [r81e7051]); $m_f$ ([r690be93]); $x_*$ ([r0dc57fa]); $\mathfrak m$ ([r29c10cd]) |
| $\ell_n$ | 행 $n$의 임의의 증인(수준 변수 $\ell$의 특정값; 따름정리 {{3:peak-asymptotics}}의 진술과 증명 — 어떻게 골라도 결론이 선다; 가장 작은 증인은 위 $\ell^\ast_n$) | 3.4 | — |

### 4장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $\mathsf{LH}^+(n)$ | 왼쪽 절반의 증가 명제 $b_{n,0}\le\dots\le b_{n,k_n-1}\le b_{n,k_n}$(한가운데까지의 판; 정리 {{4:old-4-8}}가 $\mathsf P_L(n)$과의 동치를 준다) | 4.1 | $LH^+(n)$ ([r15df76b], [rdc27681]) |
| $\mathsf P_L, \mathsf P_X, \mathsf P_C, \mathsf P_R$ | 네 위치쌍 명제(모든 $n$의 연언); 행별 명제는 $\mathsf P_L(n)$ 등 | 4.1 | cross, $P_X$ ([rce3dc75]); $P_L$, $P_R$ ([rdc27681]); [r5f5cf73] §6.2의 $P_R$은 다른 양 |
| $\Gamma^{\pm}$ | 경계 응답의 두 경계항 $p_k\Gamma_{r-1}(k+2; n)$, $p_{k-1}\Gamma_{r}(k-1; n)$ | 4.2 | $B_\pm$ ([r708d99c]) |
| $\Gamma_d(y;n)$ | 경계 응답 다항식(첫 인수 $y$는 용량 변수 — 4.2절은 다항식 변수로, 5장은 실수 값으로 쓴다) | 4.2 | $\Gamma_m(c; n)$, $\Gamma_d(c; n)$ ([rda45d0e], [r708d99c], [r5ddf8a8], [r19de912]; 인수 글자 $c\to y$, 첨자 $m$은 이 글의 $r$ — [r708d99c]는 용량 $k$로 $m=n-k$, [rda45d0e]는 수준 $k$로 $m=n-k-1$, 둘 다 $n-\ell-1$) |
| $\mathcal S_{n,k}$ | 경계 응답 부등식의 양 $\Gamma^+d_{n,k}-\Gamma^-d_{n,k+1}$ | 4.2 | $S$ ([r708d99c], [r5ddf8a8]) |
| $\mathsf Q(n,\ell), \mathsf Q_R(n), \mathsf Q_R$ | 감소 뒤의 로그오목성(조건부 로그오목성)의 위치별 명제, 오른쪽 절반의 행별 명제와 그 연언(정의 {{4:old-4-3}}) | 4.2 | $Q$, $Q_L$, $Q_R$, $Q(n,\ell)$ ([r15524fd], [rdc27681], [r19de912], [r59c82d7]) |
| $V(x)$ | $(1-x)^2/2$(중앙 틈의 피적분 인자) | 4.3 | 같음 ([rce3dc75], [ra4c01fc], [r475ada3]) |
| $\Phi, \Phi^{\mathrm{aux}}$ | 중앙 틈의 생성함수($e_n/n!=[x^n]\Phi(T(x))$)와 위 끝을 $1$로 바꾼 것 | 4.3 | $\Phi(t)$, $\Phi_{aux}$ ([rce3dc75]; 아래첨자 — 이 글은 윗첨자 로마체); $\Phi(t)$ ([ra4c01fc]) |
| $\mathcal A_{k,n}$ | 중앙 틈의 계수 $\frac{n!}{p_n}[x^n]\Phi^{\mathrm{aux}}(T)$ | 4.3 | 같음 ([rce3dc75], [ra4c01fc], [r5f5cf73]) |
| $\mathcal D(\beta)$ | Dawson 함수 $\mathcal D(\beta)=e^{-\beta^2/2}\int_0^\beta e^{v^2/2}\,dv$ | 4.3 | 같음 ([rce3dc75], [r5f5cf73]) |
| $\mathcal I_k$ | Gauss형 적분(중앙 틈) $\int_0^1\frac v{1-v}e^{-v^2/2}e^{-k\eta(v)}dv$, $\eta(v)=-\log(1-v)-v-\frac{v^2}2$ | 4.3 | 같음 ([rce3dc75], [r5f5cf73]; 지수의 $\varrho(v)$는 이 글의 $\eta(v)$); $J_c$ ([ra4c01fc]) |
| $\mathcal M_i$ | Gauss형 계수(중앙 틈의 실수 비교; 차수 지표 $i\ge0$; 쓰이는 값 $0,2,4$); $(y,n)$-판은 $\mathcal M^{(y,n)}_i$ | 4.3 | $M_r=M^{(k,n)}_r$, $M^{(c,n)}_r$ ([rce3dc75], [ra4c01fc], [r5f5cf73]; 글자체, $c\to y$, 지표 $r\to i$) |
| $\mathsf a_j$ | 적분 상수 $\int_0^\infty w^je^{-w^3/3}\,dw$ | 4.3 | $C_0$, $I$ ([rce3dc75], [r5f5cf73], [ra4c01fc], [r475ada3]); $I$ ([ra7615a0]); $M_m$ ([ra4c01fc]); $C_A$ ([rb7effe0]) |
| $\mathsf b_D, \mathsf b_J$ | 상쇄 분해의 두 보정 계수 | 4.3 | $c_D$, $c_J$ ([rce3dc75], [ra4c01fc], [r5f5cf73]) |
| $\mathsf g_k$ | 중앙 틈의 선도 상수 $2-k\mathcal M_2/\mathcal M_0$ | 4.3 | $\lambda_k=2-kM_2/M_0$ ([rce3dc75], [r475ada3]); $\lambda_n$ ([ra4c01fc], [r5f5cf73]) |
| $\mathsf n_k, \mathsf n_\infty$ | 중앙 틈 증명의 정규화 상수 $\frac{n!}{p_n}\frac{e^{n+1}}{2\pi k^{3/2}}$와 그 극한 $2/\sqrt\pi$ | 4.3 | $N_k$, $N_0$ ([rce3dc75]); $N_k=N_nk^{-3/2}$ ([r5f5cf73]) |
| $\mathrm{Bor}^{\mathrm{tail}}_k(\mathfrak Z)$ | Borel 꼬리(중앙 틈 증명의 꼬리 함수; 정의 자리의 인수는 $\mathfrak Z$이고 쓰는 자리는 그때의 인수를 넣는다) | 4.3 | $H_k(t)$, $H_k(s)$, $H_c(s)$ ([r37c204b], [rce3dc75], [ra4c01fc], [r5f5cf73], [r475ada3]; 인수 글자 $t,s\to\mathfrak Z$, $c\to k$) |
| $\mathrm{He}_j$ | Hermite 수 — $\exp(\mathfrak N\mathfrak Y-y\mathfrak Y^2/2)=\sum_j\mathrm{He}_j\mathfrak Y^j/j!$의 계수($\mathfrak N=n+y+1$); Gauss형 계수 $\mathcal M_i$를 적는 데 쓴다 | 4.3 | $H_j=j![t^j]\exp(At-ct^2/2)$, $A=n+c+1$ ([rce3dc75]) |

### 5장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $A^{c}_{n,\ell}$ | 넘는 수 $p_n-A_{n,\ell}$(최대 변위가 $\ell$을 넘는 주차함수의 수); 꼬리 좌표로는 $A^c_{n,n-r-1}$ | 5.1 | $D_{n,\ell}$, $\mathscr D_n(r)$ ([r42d9a17], [r1aa0be6]; 기록 $r=n-\ell$은 이 글의 $r+1$); $\Delta_n=p_n-A_{n,c-1}$ ([rba2ecf4]); $D_{n,\ell}$ ([r15524fd]; [r15524fd]의 $D_{n,n-r}$의 $r$은 이 글의 $r+1$); $D_{n,c}$ ([r19de912]; 첨자 용량 $c\to$ 수준 $c-1$); $D_{n,n-u}$ ([ra88ba51]; $u=n-\ell$은 이 글의 $r+1$) |
| $\mathfrak a_n$ | 지수 생성함수 계수 $A_{n,k-1}/n!$ | 5.1 | $a_m$ ([rb7effe0], [r207f124]); $a_n$ ([r7c26b8b], [rf451d83]); $a_N$ ([r051bfe1]); $f_j$ ([rbeae3a3]); $\tilde a_m$ ([r207f124]); $a^{(k)}_n$ ([r15df76b]); $\tilde a_n$ ([r6f5f48f]; 볼츠만판) |
| $\mathfrak m(n)$ | 꼬리 칸 수: 정리 {{5:old-5-5}}의 두 분기가 오른쪽 끝에서부터 덮는 칸 수 $\max(\{170\}\cup\{m\ge171:m^{3/2}+9m\le n\})$($n\ge20001$; 성질은 보조정리 {{5:tail-cells}}) | 5.2 | 같음 ([r2ec875c], [r23f10e9]) |
| $(\mathrm G)_d$ | 경계 응답 부등식을 합 지표 $d$별로 쪼갠 조각 | 5.2 | (G) ([r708d99c], [r5ddf8a8]; 기록의 이름은 「원천별 비교」) |
| $\mathsf W, \mathsf W^\sharp$ | 오른쪽 벌크 증가 명제; 임계 창 잔여 명제 | 5.3, 5.4 | — |
| $\mathrm{rq}$ | 사슬 가중치의 전개에 쓰는 꼬리 좌표와 행 크기의 비 $\mathrm{rq}:=r/n$(5.4절) | 5.4 | — |
| $q_{\max}(Y)$ | 착지 창의 폭(창 끝) $\lfloor6Y^{2/3}\rfloor$; 열 $k$에서는 $q_{\max}=\lfloor6k^{2/3}\rfloor$ | 5.5 | $B$ ([r030ffae]); $R_\ell$ ([r8a9b11e]) |
| $t_0(y), \mathrm{wid}$ | 이음 행 $1+\min\{m\ge y+1:\ m-y\ge\mathfrak m(m)+1\}$(나무 크기 변수의 특정값; 정의 {{5:old-5-21}})과 꼬리 창의 폭 $\mathrm{wid}:=t_0(y)-1-y$(같은 정의) | 5.5 | 글자는 같음; 기록의 식은 $\min\{t\ge y+2:\ y\le(t-1)-\lfloor\frac34(t-1)^{2/3}\rfloor\}$ ([r58b4caa], [r8a9b11e], [r23f10e9]) |
| $\widehat\Lambda(Y)$ | 착지 질량 $\sum_{q=1}^{q_{\max}(Y)}\frac Y{Y+q+1}c_{Y+q}(Y)$(착지 창 열 값의 가중 합; 보조정리 {{5:landing-mass}}가 정의하고 $\ge\mathsf w_0=\frac45$를 준다) | 5.5 | $\Lambda_w(\ell,R)$ ([r8a9b11e]; 창 끝 $R$ 명시 — 그 기록은 닫힌 꼴 하계 $\mathrm{Lc}$를 거친다) |
| $\mathsf w_0$ | 착지 질량의 균일 하계 $\frac45$(보조정리 {{5:landing-mass}}) | 5.5 | $s_0$ ([r8a9b11e]; 기록의 검토가 바로잡은 값 $0.71216$) |
| $\mathrm{IH}(n,y)$ | 귀납 가정 | 5.5 | $H(n,y)$ ([r58b4caa], [r8a9b11e], [r23f10e9]) |
| $P_n(y)$ | 기저량 $\sum_{t=y}^{n}x_t(y)$(5.5절 Abel 재배열의 기저 — 명제 {{5:old-5-22}} 첫 항의 인자; 따름정리 {{6:cor-L}}가 아래에서 막는다) | 5.5 | $D2S_n(y)$ ([r23f10e9], [r58b4caa]) |
| $\mathrm{POS}_0, \mathrm{POS}^\prime_0, \mathrm{POS}^{\prime-}_0$ | 환원 $(5.1)$의 꼭대기(원천) 항; 흡수 뒤의 원천 항과 그 하계 | 5.5 | $\mathrm{POS}_\alpha$ ([r58b4caa]; 기울임 매개변수 $\alpha=0$); (R₀), $\mathrm{POS}_0$, $\mathrm{POS}^\prime_0$, $\mathrm{POS}^{\prime-}_0$, (CF₀′) ([r8a9b11e] L238·250·254) |
| $\mathrm{tail}_s(y)$ | 나무 곡률의 꼬리합 $\sum_{t=s+1}^nx_t(y)$(바깥 지표는 $s$; 안쪽 합의 지표가 나무 크기 $t$다) | 5.5 | $\mathcal T_s(y)$ ([r58b4caa], [r8a9b11e], [r23f10e9]) |
| $\mathrm{top}, \mathrm{top}_\pi$ | 꼭대기 보정 $y(y-1)c_{n-1}(y-1)/n$; 가장 큰 나무 핵판 $(y-1)\pi_n(y)$ | 5.5 | — |
| $\mathrm{WIN}_0, \mathrm{WIN}^{\mathrm V}_0$ | 환원 $(5.1)$의 창 항(꼬리 창의 음의 질량); 그 방문 확률 상계 | 5.5 | $\mathrm{WIN}_\alpha$, $\mathrm{WIN}^V_\alpha$ ([r58b4caa]; $\alpha=0$) |

### 6장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $\mathrm{Bor}_{>}(q)$ | Borel 꼬리 $\sum_{d>q}\mathrm{Bor}(d)$ | 6.1 | $T(b)$ ([r030ffae]) |
| $\mathfrak s_d(y)$ | 결손 좌표의 생존 확률 $s_{y+d-1}(y)$(같은 양의 좌표 변환 약기) | 6.1 | $s_d(y)$ ([re71a735]); $s_c(d)$ ([r98fb348]) |
| $\mathfrak s^{\mathrm{up}}_d(y)$ | 첫 층 생존의 상계(자유 Borel 재귀의 상위해) $\min(1,\mathsf m_{\mathrm S}(y+d)/d^{3/2})$(정리 {{6:old-8-25}}) | 6.1 | $\phi_C(m)=\min(1,C(y+m)/m^{3/2})$ ([re71a735]; 인수 $m\to d$) |
| $\mathsf m_{\mathrm S}$ | 상위해 상수 $1.15$(정리 {{6:old-8-25}}) | 6.1 | $C=1.15$ ([re71a735]) |
| $\kappa_N$ | 위험률 하계(보조정리 {{6:old-7-24}})의 상수($k\ge2000$에서 $\ge0.307$) | 6.2 | 같음 ([r051bfe1]); [r030ffae] 보고서의 $\kappa_N$은 다른 양 |
| $\epsilon_N$ | 위험률 하계(보조정리 {{6:old-7-24}})의 지수 $g(N+1)-g(k)$($0\le\epsilon_N\le3/(2k)$; 진술의 머리 문장·(가)의 (6.18)·항목 (다)의 글자) | 6.2 | $\delta_N$, $\delta$ ([r051bfe1]) |
| $\mathfrak r_N$ | 제한 성장비 $A_{N+1,k-1}/((N+1)A_{N,k-1})$ | 6.2 | $r_N$ ([rb6a2cd0], [r3d0856b], [rcb2e2d4], [raad7e6d]); $\rho_N$ ([r051bfe1]; $\rho^*=\rho_{k-1}=1/x^*$는 $\mathfrak r_{k-1}=1/\mathsf x_k$) |
| $\mathfrak w_n(t)$ | 표시 나무 무게 $\binom ntt^{t-1}A_{n-t,k-1}$(크기 $t$ 나무를 표시하고 환경을 용량 $k$ 아래에서 센 수); 정규화 $\tilde{\mathfrak w}_n(t)=\mathfrak w_n(t)/p_n$ | 6.2 | $\varpi_n(s)$ ([rb6a2cd0], [rcb2e2d4]); $\varpi_n(N)$ ([r4868e30]; 인수 글자 $N$); $\mathcal T_n(t)$, $\tilde\pi_n(t)$ ([r33475a7]); $\varpi_t(s)$ ([raad7e6d]) |
| $\mathsf x_k$ | 임계 기울임 $(k/(k+1))^{k-1}$(보조정리 {{6:old-7-20}}의 상수) | 6.2 | $x^*$ ([r051bfe1], [rcb2e2d4]); $\rho_k$ ([rbeae3a3]); $x_k$ ([raad7e6d]) |
| $\mathrm{hz}_k(N)$ | 크기 방향 생존 위험률 $1-s_{N+1}(k)/s_N(k)$; 위험률 합은 $\sum_N\mathrm{hz}_k(N)$으로 적고 8장의 명시 하계는 $\mathfrak h(k,\nu)$(보조정리 {{8:hazard-H1}}) | 6.2 | $h_k(N)$ ([r030ffae], [rb6a2cd0], [r051bfe1], [r5bbc534]); $h_m$ ([r79ee9e0]); $h_y(N)$ ([r207f124]; 용량 $y$) |
| $\varsigma_m(\ell)$ | 머묾 질량 $s_{m+1}(\ell+1)-s_m(\ell)$(크기 $m\to m+1$에서 최대 변위가 수준 $\ell$에 머무는 몫); 결손 좌표로는 $\varsigma_{y+d-1}(y)=\mathfrak s_d(y+1)-\mathfrak s_d(y)$ | 6.3 | $\sigma_n(\ell)=\varsigma_n(\ell+1)$ ([r3d0856b]; 인수 하나 어긋남); $W^{(\ell)}_n=\varsigma_{n-1}(\ell)$ ([r3d0856b], [re71a735]; 첨자 하나 어긋남); $W_c(d)$ ([re71a735]); $\sigma_m(\ell)$ ([r845b205]) |
| $\mathfrak W_0$ | 첫 층 질량 $\sum_{n=k+1}^{2k}\mathrm{Bor}(n)\,c_{n-1}(k-1)$(따름정리 {{6:first-layer-mass}}; 6.6절 명제 {{6:prop-R}}가 쓴다) | 6.4 | $W_0$ ([r29c10cd]) |
| $\mathsf u(k), \mathsf u^\flat(k)$ | 중앙 행 수준 질량 상계의 함수(따름정리 {{6:old-8-11}}(가)(나)) $\frac3{0.35}(1.35+\frac1k)(0.65-\frac1k)^{-3/2}k^{-1/2}$와 따름정리 {{6:old-8-11}}(라)의 $1.15$ 꼴 상계 $\frac{1.15}{0.35}(2+\frac1k)(0.65-\frac1k)^{-3/2}k^{-1/2}$ | 6.4 | $g(k)$ ([r7e03176], [rb1d8cd5]); $\tilde g(k)$ ([rb6a2cd0]) |
| $\mathrm{loss}_{n,k}$ | 한 칸 손실 $(k+1)\mathrm{Bor}(n+1)c_n(k)-(k-1)\mathrm{Bor}(n)c_{n-1}(k-1)$(따름정리 {{6:one-step-loss}}; 6.6절 명제 {{6:prop-R}}가 쓴다) | 6.4 | — |
| $y_0$ | 기준 용량(용량 변수의 특정값; 6.5절 얼린 법칙 $\Pr^{y_0}$의 용량 — 정수 $y_0\ge2$이고 정리 {{6:old-8-22}}부터는 $y_0=k$) | 6.5 | — |
| $\Pi_j(y)$ | 사슬 생존 곱의 $j$번째까지의 부분곱 $\prod_{i\le j}y/(y+q_i)$(6.5절 머리 문단이 정의한다) | 6.5 | $\Pi_j(t)$ ([r845b205]); $\Pi_J(y)$ ([re71a735]) |
| $\mathcal U_k(m)$ | 볼츠만 꼬리합 $\sum_{m^\prime=m}^{2k}\mathfrak b_{m^\prime}$(볼츠만 무게의 꼬리합; 명제 {{6:old-6-18}}의 사다리가 그 양성을 확률 꼬리합 $\mathcal V_k(m)$의 양성으로 옮긴다) | 6.5 | $U_k(L)$ ([r7e03176], [r6f5f48f], [raad7e6d]); [r29c10cd]의 $\mathcal U_k=\sum_{m\ge k}V_m$은 $2k$ 절단이 없는 다른 양 |
| $\mathcal V_k(m)$ | 확률 꼬리합 $\sum_{m^\prime=m}^{2k}\mathfrak p_{m^\prime}$(판정 V의 꼬리합; V-핵심은 $\mathcal V_k(k)$) | 6.5 | $\tilde U(L)$, $\tilde U(k)$ ([r845b205], [r3d0856b], [r23f10e9], [rb6a2cd0], [raad7e6d]) |
| $\mathfrak A_j, \mathfrak A^{\mathrm{crit}}_d(q), \mathfrak A^{\mathrm{up}}_{q_0}(q)$ | 경로의 면적 $\sum_{i\le j}q_i/(y_0+1+q_i)$; 임계 면적(6.5절 젊은 사슬 문단); 조건부 면적 상계 $\frac{\sqrt{2\pi}}4e^{1/(12(q_0-q))}(q_0+q)\sqrt{q_0-q}$(9.6절 보조정리 {{9:old-8-31}}의 진술) | 6.5($\mathfrak A_j$·$\mathfrak A^{\mathrm{crit}}$), 9.6($\mathfrak A^{\mathrm{up}}$) | $\tilde X_j$, $X^{crit}_d(b)$ ([re71a735]) |
| $\mathfrak b_m$ | 볼츠만 무게의 항 $\delta_{m+1}e^{-m}/m!$(볼츠만 꼬리합 $\mathcal U_k(m)$의 항) | 6.5 | $V_m$ ([r29c10cd], [r9bf2dc6], [r6f5f48f]) |
| $\mathfrak H_d$ | 정리 {{6:old-8-22}}의 수준별 손실 합(결손 $d$의 몫; $\mathrm{DDL}_2(k)=2\sum_{d=2}^{k+1}\mathfrak H_d$) | 6.5 | $H_2(d)$ ([re71a735]) |
| $\mathfrak k_d(q)$ | 젊은 사슬 정리의 계수 $e^{\mathrm{inc}^-_q}+e^{-\mathrm{inc}^+_q}-2$ | 6.5 | $\Sigma_d(b)$ ([re71a735]; $b\to q$) |
| $\mathfrak p_m$ | 확률 무게의 항 $\delta_{m+1}/p_m$(판정 V의 항) | 6.5 | $v_m$ ([r3d0856b], [raad7e6d]) |
| $\mathfrak s^{\mathrm{fr}}_d(y)$ | 얼린 생존 $\mathbb E^{y_0}[\Pi_L(y)]$ | 6.5 | $V_y(d)$ ([re71a735]) |
| $\mathsf V$ | 첫 층 꼬리합 판정의 이름(확률 무게: 모든 $k\le m\le2k$에서 $\mathcal V_k(m)\ge0$); 꼬리표는 (V) | 6.5 | (V) ([raad7e6d]) |
| $\mathsf v(k)$ | V-핵심의 하계 함수 $2-\frac{4.6}{\sqrt{k+1}}-2\,\mathsf u^\flat(k)-\frac12\mathrm{DDL}^\natural(k)$($k\ge2001$; 정리 {{6:old-6-19}}; $k$에 증가, $\mathsf v(6667)>1.549$) | 6.5 | — |
| $\mathrm{Bd}^{\mathrm V}_k$ | 망원 항등식의 경계항 가족 가운데 V-핵심 머묾 꼴의 경계항 $2-2s_{2k+1}(k+1)-(k-1)\varsigma_{2k}(k)-(k-1)c_{2k}(k-1)$ | 6.5 | $B_k$ ([r845b205]) |
| $\mathrm{DD}(m,y)$ | 대각선 둘째 차분 $(y+2)s_{m+2}(y+2)-2(y+1)s_{m+1}(y+1)+ys_m(y)$; 9장의 약기 $\mathrm{DD}_m:=\mathrm{DD}(m-1,k-1)$ | 6.5 | $DD_m$ ([re71a735], [r3d0856b]); $D_d$ ([r98fb348]) |
| $\mathrm{DDL}_2(k), \mathrm{DDL}^\natural(k)$ | 대각선 손실의 명시 상계 $2\sum_{d=2}^{k+1}\mathfrak H_d$(정리 {{6:old-8-22}})와 그 닫힌 꼴 상계 $\frac{14(\log3k-1)}{5\sqrt{\pi k}}+\frac{37.6}{5\sqrt\pi\,k}$(명제 {{6:old-8-23}}; $k\ge7$에서 감소) | 6.5 | $DDL_2$, $CF^\natural$ ([re71a735]) |
| $\mathrm{hf}_y(q)$ | 얼린 법칙의 $h$-변환 몫 $\mathrm{Bor}(y+q)/\mathrm{Bor}(y_0+q)$(6.5절 머리 문단; 보조정리 {{2:h-transform}}(가)의 $h$-함수 $\mathrm{hf}$를 이 사슬에서 읽은 것) | 6.5 | $h_y$ ([re71a735]) |
| $\mathrm{inc}^{\pm}_q$ | 기울임 증분 $g(y_0+d)-g(y_0+q)$, $g(y_0-1+d)-g(y_0-1+q)$ | 6.5 | $u_b$, $v_b$ ([re71a735]) |
| $\mathrm{Res}_d$ | 기울임 나머지(얼린 볼록 몫을 뺀 나머지) | 6.5 | 같음 ([re71a735]) |
| $\mathrm{stp}_q$ | 젊은 걸음 수 상계 $\mathfrak A^{\mathrm{crit}}_d(q)(y_0+1+q)/q$(보조정리 {{6:old-8-20}}(나)의 진술; 실수 변수 판 $\mathrm{stp}$는 보조정리 {{6:old-8-21}}의 진술 국소) | 6.5 | — |
| $\mathrm{vm}_y(q)$ | 얼린 법칙 $\Pr^{y_0}$ 아래 수준 $q$의 생존 가중 방문 질량 $\mathbb E^{y_0}[\Pi_j(y); \ q_j=q]$(6.5절 머리 문단의 수준별 공식 (6.35); 보조정리 {{2:h-transform}}(가)의 생존 가중 방문 측도 $\mathrm{vm}$을 이 사슬에서 읽은 것). 9.6절 보조정리 {{9:old-8-31}} 증명의 $\mathfrak M^y(q)$는 참 법칙 $\Pr^y$ 아래의 같은 꼴 다른 양(그 증명의 국소 기호) | 6.5 | $G_y(b)$ ([re71a735]) |
| $\mathsf s_{\mathrm B}$ | Borel 상수 $e/\sqrt{2\pi}$ | 6.6 | $B$ ([r7e03176], [r29c10cd], [r9bf2dc6]) |

### 7장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $\mu_n(k)$ | 상대 둘째 차분 $d_{n,k}/A_{n,k-1}=\mathbb E^\sigma_{n,k}[\mathfrak v_k(Z_k,H_k)]$ | 7.1 | 같음 ([r88bed8a]); $\hat\delta_m$ ([r207f124]); $r_m$ ([r79ee9e0], [r3d0856b], [r3172894], [raad7e6d]); [r39ba7c1]의 $\mu_T$는 다른 양 |
| $\mathcal T_k(\sigma), \mathcal T_{n,k}$ | 모멘트 판정의 통계 $Z_k(Z_k-1)-kH_k$; 그 합 $\sum_{\alpha\in\mathrm{PF}_n,\ M(\alpha)\le k-1}\mathcal T_k(\sigma(\alpha))=A_{n,k-1}\mathbb E^\sigma_{n,k}[\mathcal T_k]$(주차함수에 걸친 합이라 결과 순열 $\sigma$마다 섬유 크기 $\prod_i\min(h_i,k)$의 가중이 붙는다) | 7.1 | $LM_{n,k}$ ([r475ada3]); $T_n=S_n-kh_n$ ([r10ff8c2]; 기댓값판); $T_k$, $\mathcal S_{n,k}(k)$ ([r1892593]) |
| $\mathsf t_k$ | 반감 경계 지표 $\min\{j\ge0:(k+1)^jk^{j+1}+(k-1)^{2j+1}\ge2k^{2j+1}\}$ | 7.1 | $t_k$ ([r39ba7c1], [rb6423c6]) |
| $\Pr^{\sigma}_{n,k}, \mathbb E^{\sigma}_{n,k}$ | 용량 가중 결과 순열 법칙 $\prod_i\min(h_i,k)/A_{n,k-1}$($\mathfrak S_n$ 위; 균등 주차함수를 $M\le k-1$로 조건화한 결과 순열의 법칙)과 그 기댓값 | 7.1 | $\nu_{n,k}$ ([r3172894]); $\nu_{n,y}$, $E_y$ ([r1892593]; $y=k$); $\nu_{n; k,y}$ ([rdc27681]) |
| $n^\sharp_k$ | 열 $k$의 반감 경계 $k+(k+1)\mathsf t_k$(행 크기의 특정값; 정리 {{7:old-6-8}} — 열 $2\le k\le140$에서 $n^\sharp_k\le k^2+2k\le19880<20001$이라 명제 {{7:old-6-9}}의 증명이 그 열을 이 경계로 닫는다) | 7.2 | $N^\sharp_k$ ([rb6423c6]); [r39ba7c1]의 $N^\#_k$(기록의 경계)·[rc9aee43]의 $N_k=\lceil k^2/4\rceil$는 보조정리 {{7:column-lemma}}(다)의 정수 $n_\ast=\lceil k^2/4\rceil$ |
| $C_k(x), C_{n,k}$ | 용량 $k$ 아래 소인 주차함수의 지수 생성함수와 그 계수 $n!\,[x^n]C_k$ | 7.2 | $C_k$, $c_{n,k-1}$ ([rf451d83], [r7c079be]); $C_\ell(z)$, $c_{d,\ell}$ ([rf09e7ef]; 첨자 수준) |
| $\rho_k$ | 열 $k$의 극 | 7.2 | 같음 ([rb7effe0], [rf451d83]); $\rho_\ell$ ([rf09e7ef], 첨자는 수준); [r39ba7c1] 검토 파일의 $\rho_k$(영점)와 [r051bfe1]의 $\rho^*=\rho_{k-1}$($=\mathfrak r_{k-1}$)은 다른 양 |
| $\mathcal W$ | 왼쪽 창(한 걸음 판정 $\mathsf Q^\star$를 묻는 위치 집합) $\{(n,k):\ k\ge2001,\ n\ge\max(2k+103,20001)\}$(7.2절이 정의한다) | 7.2 | $\mathcal W^{(>102)}$ ([r6b37c7e], [r3172894]); $\mathcal W$ ([r89eb039]; $2k+41$판) |
| $\mathfrak a^\rho_m$ | 극 정규화 갱신열 $\mathfrak a_m\rho_k^m$(보조정리 {{7:supermultiplicative}}(나)가 정의) | 7.2 | $f(l)$ ([rb7effe0], [r89eb039]); $u_l$ ([rf451d83]); $u^{(y)}_l$ ([r207f124]) |
| $\mathfrak P_k(n)$ | 문턱 자리 밀도 $\mathbb E^\sigma_{n,k}[kH_k]/n$ | 7.2 | 같음 ([rb7effe0]) |
| $\mathsf Q^\star, \mathsf Q^\star_2$ | 한 걸음 판정 명제와 그 둘째 층 판 | 7.2($\mathsf Q^\star$), 9.1($\mathsf Q^\star_2$ — 정의 {{9:old-8-1}}) | $Q^\star$ ([r3172894]) |
| $\mathsf W_L$ | 왼쪽 잔여 증가 명제(왼쪽 창 $\mathcal W$의 모든 위치에서 $b_{n,k-1}\le b_{n,k}$; 7.2절) | 7.2 | $W_L^\flat$ ([r3172894]) |
| $\mathfrak a^\circ_n$ | 용량 제한 없는 지수 생성함수 계수 $p_n/n!$($=[x^n]e^{T(x)}$; 7.3절 꼬리 핵 $K$ 앞 문단이 정의한다) | 7.3 | $a^\circ_m$ ([rb7effe0]); $a_m$ ([r475ada3]); $a_n$ ([r8d6850a]) |
| $\mathfrak P_k(\infty)$ | 문턱 자리 밀도의 $n\to\infty$ 극한 | 7.3 | 같음 ([rb7effe0]) |
| $n^{\mathrm G}_k$ | 열 $k$의 전달 문턱 $\max(n^{\mathrm{bis}}_0,n^\psi_k)$(행 크기의 특정값; 7.3절 끝 문단이 정의 — 열별 갱신 인증서(정리 {{7:theorem-G-prime}}(나))가 열 $k$의 비교를 닫기 시작하는 행이며 열 $501\le k\le840$에서 $\le20000$, $841\le k\le2000$에서 $\ge20001$; 부록 D.{{D:column-certificates-501-2000}}·{{D:moment-certification}}이 받는다) | 7.3 | — |
| $J^{\mathrm G}_n(z)$ | Green 표현을 모든 $n$으로 연장한 경계 다항식의 상계(Green 원자 $J^{\mathrm G}_n(z):=p_{k-1}\mathcal G_{z,k-1,n}$ — 2.7절 Green 응답의 값; $z$는 무게 변수) | 7.4 | $J^G_n(c)$ ([r475ada3]); $J^G_n$ ([r8d6850a]; 무게 $k-1$의 값) |
| $\mathcal P^{(k)}_m(j)$ | 용량 $k$ 아래의 뿌리 자리 법칙 $\min(j,k)\binom{m-1}{j-1}A_{j-1,k-1}A_{m-j,k-1}/A_{m,k-1}=\Pr_m(\mathrm{pos}_m=j\mid M\le k-1)$(마지막 차 자리 법칙을 $M\le k-1$로 조건화한 것) | 7.4 | $P_m(j)$, $P_N(J=j)$ ([r051bfe1] L68·163); $P_t(j)$, $\theta_N(j)$ ([r79ee9e0] L52·171; $N$은 행 크기); $\pi_n(s)$ ([r207f124]); $\pi_n(p)$ ([r10ff8c2] L72); $P_m(j)$ ([r3172894]); $P_t(j)$ ([raad7e6d]) |
| $\chi_m(j)$ | 원천 함수(뿌리 자리 $j$의 원천 몫) | 7.5 | $\varphi_t(j)$ ([r79ee9e0]) |
| $\mathcal Z$ | $\mu_m(k)\ge0$이 알려진 크기 $m$의 집합(흡수 귀납의 입력 집합; 5.2.3절의 국소 생성함수 $\mathcal Z^{(\iota)}_j(z)$와 다른 양) | 7.5 | — |
| $\mathrm{cl}^+_m, \mathrm{cl}^-_m$ | 정규화 수준 질량 $c_m(k)/s_m(k)$, $c_m(k-1)/s_m(k)$(생존 확률 $s_m(k)$로 정규화한 수준 $k$·$k-1$의 질량; $\mathrm{cl}^-_m$만 조건부확률) | 7.5 | $\beta^\pm_m$ ([r207f124]); $g^\pm(m)$ ([r79ee9e0], [r3d0856b], [r3172894], [raad7e6d]) |
| $\mathrm{inh}_k(n), \mathrm{inh}^{\mathrm{lin}}_k(n)$ | 첫 층 상속(첫 층 자식에서 상속되는 차분)과 그 선형 몫 | 7.5($\mathrm{inh}_k$), 7.6($\mathrm{inh}^{\mathrm{lin}}_k$) | $\mathrm{FLlin}_k(t)$ ([r79ee9e0]); $FL(t)$ ([r3172894]) |
| $\mathrm{src}_k(m)$ | 토막 원천 $\sum_j\mathcal P^{(k)}_m(j)\,\chi_m(j)$(크기 $m$ 토막이 내는 원천) | 7.5 | $\mathrm{src}_k(t)$ ([r79ee9e0], [r3172894]; $t\to m$); $\hat\sigma_n$ ([r207f124]); [r10ff8c2]의 $\mathrm{src}_m$은 다른 양 |
| $(\star)(n)$ | 한 걸음 양 $\mathrm{src}_k(n)+\mathrm{inh}_k(n)$ | 7.5 | — |
| $\mathrm{apex}^{\mathrm H}_k(n)$ | 꼭대기 뿌리 순상환 $\frac1k\bigl[\sum_{j=n-k+1}^n\mathcal P^{(k)}_n(j)(\mathrm{cl}^++\mathrm{cl}^-)_{j-1}-\mathcal P^{(k)}_n(k)(1-\mathrm{cl}^-_{n-k})\bigr]$(7.6절 정의 문단; 정리 {{7:top-roots}}·{{7:apex-positive}}·명제 {{7:src-plus}}가 쓴다) | 7.6 | $\mathrm{Top}_k(t)$ ([r79ee9e0]) |
| $w_m$ | 분할 무게 $\binom{n-1}mp_mA_{n-1-m,k-1}/A_{n,k-1}$ | 7.7 | 같음 ([r3d0856b], [re71a735]) |
| $\mathfrak u_n$ | 문턱 단위 $w_{n-k}s_{n-k}(k+1)$ | 7.7 | $N_{thr}$ ([r3d0856b], [re71a735]) |
| $\mathrm{Left}_n$ | 왼쪽 항 $\sum_{m=k}^{2k}w_m\mathfrak p_m$ | 7.7 | — |
| $\mathrm{Quad}_n, \mathrm{Stem}_n$ | 둘째 층 한 걸음 항등식의 이차 몫; 깊은 자식 몫 | 7.7 | — |
| $\mathrm{KD}^\prime_n$ | 둘째 층 크기의 자식에서 물려받는 상속 몫 $\mathrm{KD}^\prime_n=\sum_{m=2k+1}^{n-1}(k+n-m)\binom{n-1}mp_{n-1-m}d_{m,k}$(정리 {{7:old-6-21}}의 항등식 $A_{n,k-1}(\star)(n)=d_{n,k}-\mathrm{KD}^\prime_n$의 항; 9장이 받아 쓴다) | 7.7 | — |
| $\mathcal R_2$ | 실질 잔여 $\{(n,k):k\ge6668,\max(2k+103,20001)\le n\le3k-1\}$ — 7장의 환원이 주 정리에 남긴 위치의 집합(그 모든 위치에서 $(\star)(n)\ge0$을 9장이 보인다) | 7.8 | — |

### 8장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $s^{\mathrm{low}}_q$ | 원천의 생존 하계 수열(착지 창 크기 $k+q$의 생존 확률 $s_{k+q}(k+1)$을 아래에서 막는 임의의 수열; $s^{\mathrm{low}}_0=1$) | 8.1 | $Q^{\mathrm{low}}_c$ ([r030ffae] L94); [r030ffae]·[rfc69320]의 $Q_c$는 정확 생존 $s_{k+c}(k+1)$ |
| $\Omega(\xi), \Omega_q$ | 모양 함수(상위해를 $\mathfrak E_q=\Psi(q)(1-\Omega_q)$ 꼴로 잡는 감소 함수)와 그 값 $\Omega_q:=\Omega(\xi_q)$(첨자는 정수 초과 $q$) | 8.1 | $W$, $W_c$ ([r030ffae]) |
| $\xi$ | 창 좌표 $q/k^{2/3}$(초과를 $k^{2/3}$ 눈금으로 잰 것; 정수 초과 $q$의 것은 $\xi_q:=q/k^{2/3}$); 9장에서 시작 초과 $q_0$의 것은 $\xi=q_0/y^{2/3}$(다른 절들이 국소 글자로 쓰는 $\xi$와 다른 양 — 국소 글자는 그 자리가 정의한다) | 8.1 | $x_b$, $x$, $y$ ([r030ffae]); $y$ ([rfc69320]); $x$ ([re71a735] §4); $x=d/k^{2/3}$ ([r9bf2dc6]) |
| $\mathfrak D^{\mathrm{src}}_q$ | 부족량의 원천 항 $\frac q{k+q}\Psi(q)+\frac k{k+q}\sum_{m=1}^q\mathrm{Bor}(m)(1-s^{\mathrm{low}}_{q-m})$ | 8.1 | $\sigma_b$ ([r030ffae]) |
| $\mathfrak D_q$ | 부족량 $\Psi(q)-\mathfrak R_q$(창의 수준 질량이 극한값에서 모자라는 양; $\mathfrak D_0=0$) | 8.1 | $D_b$ ([r030ffae]) |
| $\mathfrak E_q$ | 부족량의 상위해(부족량 부등식을 만족하는 수열) | 8.1 | $E_b$ ([r030ffae]) |
| $\mathfrak R_q$ | 착지 창의 수준 질량 $k\,c_{k+q}(k)$ | 8.1 | $R_b=k\,r_{k+b}$ ([r030ffae]) |
| $\mathrm{Bor}_\le(q)$ | $\sum_{m\le q}\mathrm{Bor}(m)=1-\mathrm{Bor}_>(q)$(8.1절 보조정리 {{8:old-6-25}}의 증명이 정의하고 8.2절·8.4절이 받는다) | 8.1 | $S_0(b)$ ([r030ffae]); $S_0(d)$ ([r5bbc534]); $\beta(m)$ ([r29c10cd]) |
| $\mathrm{dup}_m$ | 한 나무 재귀의 중복 몫 | 8.1 | $\mathrm{rem}_L$ ([r030ffae]) |
| $\mathrm{Flow}_q$ | 부족량의 흐름 항 | 8.1 | $G_b$ ([r030ffae]) |
| $s^{\mathrm{cf}}(\xi)$ | 닫힌 꼴 봉투 $\max\{e^{-\mathsf j_\infty(\xi)}\ (\xi\le2.1),\ \mathrm{Esc}_{6600}(\xi)\ (\xi\ge2)\}$(저장된 봉투 표가 참 생존 확률의 하계임을 인증하는 장치; $\mathrm{Esc}_{6600}$은 8.2절 (8.14)의 탈출 봉투 몫의 $k=6600$ 값) | 8.2 | $Q^{\mathrm{cf}}$ ([rfc69320]) |
| $\mathsf j_\infty(\xi)$ | Jensen 봉투 지수의 $k\to\infty$ 극한 $\frac43(2\pi)^{-1/2}\xi^{3/2}$ | 8.2 | $B_\infty(y)$ ([rfc69320]) |
| $\mathrm{km}_N$ | 정리 {{8:escape-lower}}의 사슬 질량 $\sum_{m=y+1}^N\pi_N(m)\,y/m$ | 8.2 | $\kappa_N$ ([r8456f59], [r030ffae]; 6.2의 위험률 하계 상수 $\kappa_N$과 다른 양) |
| $\mathrm{Lip}$ | 정리 {{8:old-6-28}} 증명 (나)의 (8.19)·(8.20) 셀 검사에서 좌변 빼기 우변 $\Phi$의 도함수 크기를 위에서 막는 상수(Lipschitz 하계 $\Phi\ge\min(\text{양 끝})-\mathrm{Lip}\cdot0.001$) | 8.2 | — |
| $\mathfrak c_0(N)$ | 용량 이동 비 $s_N(k-1)/s_N(k)$의 하계 — 보조정리 {{2:capacity-shift-ratio}}의 하계와 보조정리 {{8:old-6-30}}(나)의 하계 가운데 큰 쪽 $\max\{(1-1/k)^{N-k+1},\,1-e^{7/6}N^{3/2}/(4(2\pi)^{-1/2}k(2k-1-N))\}$($k\le N\le2k-2$; 그 보조정리 뒤에 정의) | 8.3 | $c_0$ ([r030ffae]; 보조정리 $C_0$의 최댓값) |
| $m_{\mathrm{fb}}$ | 되먹임 시작 $\lceil5k/4\rceil+q_{\max}$(크기 변수의 특정값) | 8.4 | $L_0$ ([r030ffae]) |
| $q_{\mathrm{fb}}$ | 되먹임 폭 $\lfloor(3(k-1)/4-q_{\max}-3)/8\rfloor$(한 걸음에서 줄어드는 부분나무 크기의 상한; 정리 {{8:old-6-33}}; 초과 변수의 특정값) | 8.4 | $G$ ([r030ffae]; 두 정의 L241·L191) |
| $\mathfrak R^{\mathrm{low}}_k$ | 띠 정리 조립의 창 합 하계 — 창 착지 항 $q=1,\dots,q_{\mathrm w}$(나무 크기 $k+q$, 내부 숲 크기 $k+q-1$)의 생존과 수준 질량의 괄호 $[s_{k+q-1}(k+1)+\mathfrak R_{q-1}]$를 아래에서 막아 더한 합((8.23); 8장 머리가 밝힌 셈법대로 착지 창 $k+1,\dots,k+q_{\max}$보다 내부 숲 크기가 하나 아래) | 8.4 | $\hat S_k$ ([r030ffae]) |
| $\mathrm{fb}(\lambda)$ | 되먹임 인자 $\mathrm{fb}(\lambda):=\sum_{i<8}(\lambda\,\mathrm{Bor}_\le(q_{\mathrm{fb}}))^i$(되먹임 기하합; 인수는 1.5절의 비 $\lambda=k/n$이고 수준 $k-1$의 항에서는 $(k-1)/n$을 넣는다) | 8.4 | $F(\theta)$ ([r030ffae]) |
| $\mathrm{LB}^{\mathrm{mono}}, \mathrm{LB}^{\mathrm{low}}, \mathrm{LOW}_k$ | 띠 정리 조립의 두 명시 하계와 생존 $1$ 착지 항 | 8.4 | $\rho_{\mathrm{mono}}$, $\rho_{\mathrm{low}}$, $\mathrm{LOW}_k$ ([r030ffae]) |

### 9장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $\varkappa_m$ | 장부 계수 $2$($m\le N$) 또는 $1+(n-m)/k$($m>N$) | 9.1 | $c_m$ ([r3d0856b], [re71a735]) |
| $\mathfrak f_m$ | $1/p$ 장부의 항 $\varkappa_mk\,d_{m,k}/p_m+(2-\mathbf 1\{m>N\})c^{(2)}_m$ | 9.1 | $f_m$ ([r3d0856b], [re71a735]) |
| $\mathfrak T_m$ | 장부 항의 꼬리합 $\sum_{i=m}^{2k}\mathfrak f_i$, $\mathfrak T_{2k+1}:=0$ | 9.1 | $T_m$ ([r3d0856b], [re71a735]) |
| $m_0$ | 장부 꼬리합 $\mathfrak T_{m_0}$의 시작 크기; 미결 범위의 $m_0$에 대해 시작 초과는 $q_0=m_0-k$ | 9.2 | — |
| $m^\flat$ | 머묾 꼴 (나)의 반사 크기 $3k+\nu-m_0$($=n+k-m_0$; 명제 {{9:old-8-8}}(나)의 $N<m_0\le2k$ 경우) | 9.2 | — |
| $\omega_m, \omega_y(d), \tilde\omega(d)$ | 꺾인 무게 $2$($k<m\le N+1$), $2-(m-N)/k$($N+2\le m\le2k$); 결손 좌표의 같은 무게; $\nu$에 무관한 변형 | 9.2($\omega_m$), 9.5($\omega_y$), 9.6($\tilde\omega$) | — |
| $\mathrm{Bd}^{\mathrm S}$ | 머묾 꼴(명제 {{9:old-8-8}})의 중앙 경계항(경계항 가족) | 9.2 | — |
| $\mathrm{Stays}, \mathrm{Stays}^{\mathrm{vis}}, \mathrm{Stays}_{\mathrm{PM}}$ | 문턱 뒤 머묾 질량 $2\varsigma_{N+1}(k)+\sum_{m=N+2}^{2k}\omega_m[\varsigma_m(k)+\varsigma_{m-1}(k-1)]$; 그것을 머묾 법칙(정리 {{6:old-8-13}})으로 수준 질량의 결손 가중합에 넘긴 꼴; 거기에 정리 {{6:old-8-12}}(벌크 수준 질량의 상계)를 넣은 것 | 9.2($\mathrm{Stays}$), 9.4($\mathrm{Stays}^{\mathrm{vis}}$·$\mathrm{Stays}_{\mathrm{PM}}$) | `Stays` ([r3d0856b]); `Stays_θ` ([r3d0856b])는 $\mathrm{Stays}^{\mathrm{vis}}$ |
| $\nu_{\min}(k), \bar\nu$ | FLQ 범위의 실제 하한 $\max(103,20001-2k)$; $\nu$의 상한(둘째 층 위치의 특정값) | 9.3($\nu_{\min}$), 9.6($\bar\nu$) | — |
| $\vartheta, \vartheta_0$ | 띠 인자 $2(1+\frac1k)A_{N,k-1}/A_{N,k}-1$(띠), $-1$(벌크); 상수 $(2e^{-0.48}-1)e^{-0.48}$(명제 {{9:old-8-35}}의 진술이 정의) | 9.3($\vartheta$), 9.6($\vartheta_0$) | $\theta$ ([r3d0856b]); $\theta_0$ ([re71a735] L317) |
| $\mathsf{FLQ}$ | 첫 층 열 값만의 두 부등식 명제(정의 {{9:old-8-9}}) | 9.3 | — |
| $s^{\mathrm W}_{\nu-1}(N,k+1)$ | 착지 창의 생존 상계 — 보조정리 {{2:supersolution}}(나)의 상위해 $\phi_1$을 용량 $k+1$, 초과 $\nu-1$에서 읽은 값 $1-\sum_{j=1}^{\nu-1}\mathrm{Bor}(j)\frac{\nu-j}{k+\nu+1-j}$(9.4절 준비 문단이 정의) | 9.4 | $W_b$ ([r3d0856b]) |
| $\pi^{\mathrm{two}}_N$ | 크기 $N-1$ 숲이 크기 $k$, $\nu-1$의 두 나무뿐일 확률 $\binom{N-1}kk^{k-1}(\nu-1)^{\nu-2}/N^{N-2}=\mathrm{Bor}(k)\mathrm{Bor}(\nu-1)/(e\,\mathrm{Bor}(N))$ | 9.4 | $\lambda$ ([r3d0856b] L343, [re71a735] L318) |
| $\vartheta_{\mathrm{lb}}$ | 띠 인자의 하계 $2(1+\frac1k)^{1-\nu}-1$ | 9.4 | $\theta_{lb}$ ([r3d0856b]) |
| $\vartheta^{\mathrm T}(k,\nu)$ | 허용 상계 $\mathrm{Stays}^{\mathrm{adm}}(k,\nu)$에 드는 띠 인자 항: 띠 $\nu\le0.48k$에서 $\vartheta_{\mathrm{lb}}(1+\frac1{k-1})^{-(\nu-1)}$, 벌크 $\nu>0.48k$에서 $-e^{3/(2k)}\mathsf r_\ast$ | 9.4 | $\Theta(k,\nu)$ ([re71a735]) |
| $\mathsf r_\ast$ | 벌크 상수(9.4절 준비 문단이 정의한다; $\vartheta^{\mathrm T}(k,\nu)$의 벌크 값 $-e^{3/(2k)}\mathsf r_\ast$에 든다) | 9.4 | $\rho^*$ ([r3d0856b]) |
| $\mathrm{Bd}^{\mathrm T}(k,\nu)$ | 명제 {{9:reduction-na}}의 경계항 상계(경계항 가족) | 9.4 | $BD(k,\nu)$ ([r3d0856b], [re71a735]) |
| $\mathrm{PM}_y(d)$ | 벌크 수준 질량의 상계 $16.54(y+1+\frac{d-1}3)(d-1)^{-5/2}$(정리 {{6:old-8-12}}를 용량 $y+1$, 초과 $d-1$에 쓴 $c_{y+d}(y)$의 상계) | 9.4 | $PM_c(d)$ ([re71a735]); $16.54(k+a/3)a^{-5/2}$ ([r7e03176]; $k=y+1$, $a=d-1$) |
| $\Pi^{\mathrm{up}}_j$ | 길이 $j$의 무거운 사슬 위에서 잰 생존 곱의 상계 계수 $\prod_{i=1}^{j}\frac{k+1}{k+i}$(9.4절 준비 문단; 명제 {{9:reduction-na}} 증명 (5)·명제 {{9:old-8-35}} 증명이 쓴다) | 9.4 | $\tau_h$ ([r3d0856b]; 첨자 $h\to j$) |
| $\mathrm{Stays}^{\mathrm{adm}}(k,\nu)$ | 머묾 질량의 허용 상계(머묾 질량이 그 이하이면 $\mathsf{FLQ}$의 (나)가 서는 값 — 명제 {{9:reduction-na}}(나)가 세운다; 머묾 질량 자체의 상계가 아님): 띠·벌크 공통의 한 식 $4-3\min\bigl(s^{\mathrm W}_{\nu-1}(N,k+1),\mathfrak s^{\mathrm{up}}_{\nu+1}(k+1)\bigr)-\mathrm{Bd}^{\mathrm T}(k,\nu)-\mathrm{DDL}^\natural(k)+\vartheta^{\mathrm T}(k,\nu)$ | 9.4 | $S^*(k,\nu)$ ([r3d0856b]); $S^*_{new}$ ([re71a735]) |
| $d^\star$ | 나눔점 $\lfloor0.6y\rfloor$($y\in\{k-1,k\}$는 용량; 결손의 특정값; 명제 {{9:old-8-33}}이 정의한다) | 9.6 | $D_1=\lfloor0.6c\rfloor$ ([re71a735] L274; $c\to y$); [r030ffae]의 $D_1$은 다른 양 |
| $k_0, k^\ast$ | 가족이 비지 않는 가장 작은 $k$(가족의 첫 열); 단계 (b)의 최소 열(용량의 특정값) | 9.6 | — |
| $\mathfrak Q(y,\xi)$ | 두 부분 적분 꼴의 수준 질량 하계(보조정리 {{9:old-8-32}}(i)가 세우는 $k\,c_{k+q_0}(k)$의 하계) | 9.6 | $Q_2(y,x)$ ([re71a735]) |
| $\mathfrak s^{\mathrm{low}}_d(y)$ | 착지 창의 생존 하계(보조정리 {{9:old-8-30}}) | 9.6 | — |
| $\mathsf f_1$ | 극한 결손 법칙의 첫 계수 $4/(3\sqrt{2\pi})=0.53192\ldots$ | 9.6 | $I_1$ ([re71a735]) |
| $\mathrm{Stays}^{\mathrm{up}}(k;\bar\nu), \mathrm{Stays}^{\mathrm{up}}_F, \mathrm{Stays}^{\mathrm{up}}_\circ$ | 머묾 질량 $\mathrm{Stays}$의 상계들: $\nu$에 무관한 상계(명제 {{9:old-8-33}}); 가족별 상계(명제 {{9:check-na}}); 임의의 상계(명제 {{9:reduction-ga}}(ii) — 9.4절) | 9.6($\mathrm{Stays}^{\mathrm{up}}_\circ$는 9.4) | $U(k; \bar\nu)$, $U_F(k)$ ([re71a735]) |

