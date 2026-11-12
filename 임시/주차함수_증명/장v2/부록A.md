## 부록 A. 기호표

본문에 나오는 전역 기호를 처음 정의된 절의 순서로 적는다. 열은 기호, 뜻, 처음 정의된 절, 그리고 같은 양을 연구 기록이 다른 글자로 적은 경우 그 글자와 식별자다. 증명 안에서만 쓰이는 국소 기호는 그 증명이 정의한다.

### 변수와 지표 글자

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $n$ | 행의 크기(주차함수의 「길이」 $n$, 숲의 「크기」 $n$; 낱말은 대상마다 그렇게 쓴다); 7–10장에서는 둘째 층 행 $n=2k+\nu$ | 1.5 | — |
| $m$ | 둘째 크기 변수(부분 숲·블록·환경·행의 크기를 $n$과 함께 적을 때; 합의 지표) | 1.5 | — |
| $t$ | 나무(블록)의 크기 변수 | 1.5 | — |
| $N:=n-k$ | 환경(표시한 나무를 뺀 나머지 숲)의 크기(7–10장); $N=k+\nu$ | 1.5 | — |
| $k$ | 열의 용량 $\ell+1$(고정) | 1.5 | — |
| $\ell=k-1$ | 수준(최대 변위의 값) | 1.5 | — |
| $y$ | 용량 변수(움직일 때) | 1.5 | — |
| $Y$ | 수준 변수 $Y\in\{y-1,y,y+1\}$ | 1.5 | — |
| $i$, $j$ | 자리·차·항의 지표; 층 번호(1.5의 「$j$째 층」)도 $j$ | 1.5 | — |
| $u$, $v$ | 꼭짓점 지표 | 1.5 | — |
| $r:=n-\ell-1$ | 꼬리 좌표(오른쪽 끝에서 잰 위치; 위치 $\ell$은 끝에서 $r+1$번째 칸); $n-k$와 같은 수 | 1.5 | — |
| $\nu:=n-2k$ | 둘째 층 안의 오프셋(중앙에서 잰 행의 위치) | 1.5 | — |
| $d$ | 결손(크기−최대 변위; 결손 좌표 $d=m-M$, 크기 $y+d-1$) | 1.5 | — |
| $q$ | 초과(크기−용량) 변수: 무거운 사슬 $i$째 꼭짓점의 초과 $q_i:=S_i-y$, 사슬이 지나는 초과 수준 $q_0>q_1>\dots>q_J$, 착지 창 안의 크기 $k+q$; 둘째 초과 변수는 $q^\prime$ | 1.5 | — |

### 1장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $a_i$ | 차 $i$의 선호 자리 | 1.1 | — |
| $p_n$ | 주차함수의 수 $(n+1)^{n-1}$, $p_0=1$ | 1.1 | — |
| $\alpha$ | 주차함수(선호 수열) $\alpha=(a_1,\dots,a_n)$ | 1.1 | — |
| $\mathrm{PF}_n$ | 길이 $n$ 주차함수 전체의 집합 | 1.1 | — |
| $d_i$ | 차 $i$의 변위 $\mathrm{pos}_i-a_i$; 마지막 차의 변위 $d_n$. 자리 $i$에 선 차의 변위는 $d_{\sigma_i}$ | 1.2 | — |
| $M(\alpha), M_n, M$ | 최대 변위; 균등 주차함수(또는 균등 숲)의 최대 변위($M_0=0$) | 1.2 | $D$ (Petersson 모형, 3.1) |
| $\mathrm{pos}_i$ | 차 $i$가 실제로 선 자리; 마지막 차의 자리 $\mathrm{pos}_n$ | 1.2 | — |
| $b_{n,\ell}$ | 최대 변위가 $\ell$인 길이 $n$ 주차함수의 수 | 1.3 | — |
| $\ell^\ast$ | 단봉성의 증인(봉우리 첨자); 행 $n$의 것은 가장 작은 증인 $\ell^\ast_n$ | 1.3 | $\ell^*$ ([r7e03176]) |
| $A_{n,\ell}$ | 최대 변위가 $\ell$ 이하인 누적 개수($A_{0,\ell}=1$, $A_{n,-1}=0$); 약기 없이 늘 두 첨자로 적는다 | 1.3 | $A_s:=A_{s-1,k-1}$ ([r475ada3], 한 칸 어긋남) |
| $\mathsf P, \mathsf P(n)$ | 문제 P(모든 행이 단봉); 행 $n$의 명제 | 1.3 | — |
| $d_{n,k}$ | 한 칸 차분 $b_{n,k}-b_{n,k-1}=A_{n,k}-2A_{n,k-1}+A_{n,k-2}$; 확률판은 $d_{n,k}/p_n$ | 1.5 | $\Delta\pi_m$ ([r3d0856b]); $d_n$(기록 줄임); [r7c079be]의 $d_{n,k}$는 소인 질량 $C_{n,k}e^{-n}/n!$ |
| $k_n$ | 행 $n$의 한가운데 용량 $\lceil n/2\rceil$(비교 $b_{n,k_n-1}$ 대 $b_{n,k_n}$) | 1.5 | — |
| $x, \hat x$ | 임계 창 좌표 $x=(n-k)/n^{2/3}$, $\hat x=(n-\ell)(\ell+1)^{-2/3}$($=r/n^{2/3}$, $=(r+1)(\ell+1)^{-2/3}$) | 1.5 | — |
| $\lambda$ | 용량과 행 크기의 비 $k/n$(움직이는 용량이면 $y/n$) | 1.5 | — |
| $\zeta$ | 중앙 창 좌표 $\nu/k^{2/3}=(n-2k)/k^{2/3}$ | 1.5 | $x$ ([r3d0856b]) |

### 2장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $h_i$ | 자리 $i$의 선호 용량 $i-\max(\{j<i:\sigma_j>\sigma_i\}\cup\{0\})$ | 2.1 | — |
| $A^\sigma_\ell$ | 섬유 $\sigma$의 누적 개수 $\prod_i\min(h_i,\ell+1)$ | 2.1 | — |
| $\sigma, \sigma_i$ | 결과 순열; 자리 $i$에 선 차 | 2.1 | — |
| $\mathfrak S_n$ | $n$차 대칭군 | 2.1 | — |
| $b^\sigma_\ell$ | 섬유 $\sigma$의 행 $A^\sigma_\ell-A^\sigma_{\ell-1}$ | 2.2 | — |
| $A_\ell(x)$ | 누적 개수의 지수 생성함수 $\sum_nA_{n,\ell}x^n/n!$ | 2.3 | $D(x)$ ([rb7effe0], $=A_{k-1}$) |
| $Q_\ell(x)$ | 역수 미분방정식의 적분 다항식 $\sum_{j<\ell}(\ell-j)p_jx^{j+1}/(j+1)!$; 열 $k$에서는 $Q_{k-1}$ | 2.3 | $\Pi_k(x)$ ([rb7effe0]); $Q_k(x)$ ([r7c079be], [r89eb039], [rf451d83]; 첨자 용량); $H_\ell=Q^\prime_\ell$ ([rf09e7ef]); [r37c204b]의 $Q_k=(1-T)(P-P_{<k})$는 다른 양 |
| $t_v$ | 꼭짓점 $v$의 부분나무 크기(나무 크기 변수 $t$를 꼭짓점으로 첨자한 것; 7.5의 토막 나무에서는 꼭짓점 $v$의 토막 크기) | 2.4 | — |
| $F$ | 라벨 뿌리 숲(변수) | 2.4 | — |
| $I_v$ | 꼭짓점 $v$의 국소 역전 수 | 2.4 | — |
| $M(F)$ | 숲 $F$의 최대 국소 역전 수(정리 `{{2:old-2-10}}`으로 최대 변위와 분포가 같다) | 2.4 | — |
| $T_\ell(x)$ | 허용 나무 생성함수 $\sum_t\mathcal N_\ell(t)x^t/t!$($A_\ell=\exp T_\ell$; 나무 함수의 허용판) | 2.4 | — |
| $U_v$ | 꼭짓점 $v$의 독립 균등 변수(변위 표현) | 2.4 | — |
| $\tau$ | 뿌리 라벨 나무(변수); 블록 나무의 모양 | 2.4 | — |
| $\mathcal N_\ell(t)$ | 크기 $t$의 허용 나무 수 $\min(t,\ell+1)A_{t-1,\ell}$ | 2.4 | $c_N(\kappa)=\mathcal N_{\kappa-1}(N)$ ([r4868e30]); $T_\ell(s)$ ([r5909c9e]) |
| $G$ | 숲의 가장 큰 나무의 크기($=S_1$) | 2.5 | $G_N$ ([r030ffae], [r5bbc534]); $S_0$ ([r88bed8a]) |
| $H_k(\sigma), H_k(F)$ | 용량이 정확히 $k$인 자리의 수(문턱 자리 수); 숲·나무에서는 크기가 정확히 $k$인 부분나무의 수(문턱 부분나무 수) | 2.5 | — |
| $L$ | 최대 나무 사슬에서 문턱을 넘는 항의 수(사슬 길이; $S_1>\dots>S_L$, 마지막 초과 $q_L$) | 2.5 | $J$ ([re71a735]); $J_d$ ([r845b205]); $Z$ ([r8a9b11e], [r23f10e9], [r29c10cd], [r696d62c], [rb1d8cd5]) |
| $S_1>S_2>\cdots$ | 문턱 $y$의 최대 나무 사슬(가장 큰 자식 쪽으로 내려가며 읽은 부분나무 크기열) | 2.5 | $S_0>S_1>\cdots$ ([r88bed8a]; 기록 $S_j$는 사전 $S_{j+1}$); $s_j$ ([r29c10cd]); $s_i$ ([r42d9a17], [r1aa0be6]) |
| $T(x)$ | 나무 함수 $\sum_tt^{t-1}x^t/t!$ | 2.5 | $P=e^T$ ([r37c204b], 주차함수 지수 생성함수) |
| $Z_k(\sigma), Z_k(F)$ | 용량이 $k$를 넘는 자리의 수(무거운 자리 수); 숲·나무에서는 부분나무 크기가 $k$를 넘는 꼭짓점의 수(무거운 꼭짓점 수) | 2.5 | $Z$ ([r5f5cf73]) |
| $\pi^0_n(y)$ | 쪼개짐 확률 $\Pr_n(G\le y)$(크기 $y$를 넘는 나무가 없을 확률; 3절 낱말 「쪼개짐」); 상계는 $\pi^{0,\mathrm{up}}$ | 2.5 | $P_0(N)$ ([rae1f209], [r5909c9e]; 인수 $k$ 고정); $P^{up}_0$ ([r5909c9e]); $q_F=\pi^0_F(F/2)$ ([r2fe0259]); $\mathcal N(j,y)$ ([r29c10cd]); $\mathcal N(L,c)$ ([r696d62c]); $q_N=\pi^0_N(k)$ ([r8456f59]); [r030ffae] 보고서 L260(보조정리 H-G)의 $q_N=1-\sum_j\mathrm{Bor}(j)\rho_j$는 $\pi^0_N(k+1)$(보고서 L25·exposition L42의 $q_N$은 $s_N(k+1)$); L226의 「모든 나무 크기 $<k$」 확률은 $\pi^0_{N^\prime}(k-1)$(글자 없음) |
| $\pi_n(m)$ | 크기 $n$ 균등 뿌리 숲에서 크기 $m$ 나무 수의 기댓값 $\binom nmm^{m-1}p_{n-m}/p_n$; $m>n/2$에서는 가장 큰 나무의 법칙 $\Pr_n(G=m)$(가장 큰 나무 핵) | 2.5 | $\varpi_N(s)$, $\varpi_L(s)$ ([rae1f209], [r5909c9e], [r030ffae]); $\pi_N(m)$ ([r39ea75d], [r8456f59], [r13b0b8f]); $\pi_F(t)$ ([r8a9b11e], [r23f10e9]); $\gamma_L(j)$, $\gamma_N(t)$ ([r5bbc534]); $G_N(s)$ ([r207f124]); $\beta_c(d,a)=\pi_{c+d-1}(c+a)$, $K_c(d,a)$ ([r98fb348]); $w_{m,s}=\pi_m(m-s)$ ([r6b37c7e]) |
| $\mathfrak v_k(Z,H)$ | 섬유 부호식 $(1+1/k)^Z+(1-1/k)^{Z+H}-2$(둘째 차분 함수 $G_k(a,h)=k\,\mathfrak v_k(a,h)$는 풀어 적는다) | 2.5 | $g(x; \eta)$ ([r7c26b8b], [rb7effe0], [r89eb039]); $g(Z,H)$ ([r88bed8a]) |
| $\mathrm{Bor}(m)$ | Borel 질량 $e^{-m}m^{m-1}/m!$ | 2.5 | $\beta_j$, $\beta_d$ ([r4868e30], [r7e03176], [r79ee9e0]); $\beta_n$ ([r2ec875c]); $\tau_m$ ([r8456f59]); $\mathrm{Bo}(n)$ ([r051bfe1]); $q_s=\mathrm{Bor}(s+1)$ ([r6b37c7e]) |
| $\mathrm{Bor}^{*j}(m)$ | Borel–Tanner 질량(독립 Borel 변수 $j$개의 합이 $m$일 확률) | 2.5 | $BT$ ([r8a9b11e]); $B^{(*n)}(\ell)$ ([r5909c9e]); $BT_n(j)$ ([re71a735]) |
| $\Pr_n, \mathbb E_n$ | 크기 $n$ 균등 뿌리 숲의 법칙(=길이 $n$ 균등 주차함수의 법칙)과 그 기댓값 | 2.5 | — |
| $c_m(Y)$ | 수준 질량 $b_{m,Y}/p_m=\Pr_m(M=Y)$ | 2.6 | $\pi_m(\ell)$ ([r3d0856b], [re71a735]); $r_N,r^\prime_N$ ([rae1f209], [r030ffae]); $c^\pm_m$ ([r5909c9e]); $V_c(d)$ ([re71a735]); $c_m(\ell)$ ([r2ec875c]) |
| $g(x)$ | $(x-1)\log(1+1/x)$(Borel 이웃비와 성장률의 로그; Q22·Q63) | 2.6 | $g(j)$ ([rb6a2cd0]); $f(x)$ ([r207f124]) |
| $s^{T}_t(y)$ | 크기 $t$ 균등 뿌리 나무가 용량 $y$ 아래 살아남을 확률 $\Pr^T_t(M^T_t\le y-1)$(나무 생존 확률) | 2.6 | $\chi(g)$, $\chi^+(g)$ ([r030ffae]; 용량 $k$, $k+1$) |
| $s_m(y)$ | 생존 확률 $A_{m,y-1}/p_m=\Pr_m(M\le y-1)$, $s_m(0):=0$ | 2.6 | $F_m(y)$ ([r317d678], [r845b205]); $F_m(\ell)=s_m(\ell+1)$ ([r3d0856b], [re71a735]); $s_N,q_N,t_N$ ([rae1f209], [r030ffae]; [r5909c9e]는 $s_m$만); $\mathfrak s_N$ ([rb6a2cd0], [r051bfe1], [r5bbc534]); $q_y(N)$ ([r207f124]); $s_c(d)$ ([r98fb348]); $\sigma_\ell(m)=s_m(\ell+1)$ ([r79ee9e0]); $a_m(\ell)=s_m(\ell+1)$ ([r60a6f55]); $Q_c=s_{k+c}(k+1)$ ([r030ffae]); $\alpha_{N,\ell}=s_N(\ell+1)$ ([r39ea75d]) |
| $\Pr_{\mathrm B}$ | 임계 볼츠만 법칙 | 2.6 | — |
| $e_n$ | $\mathcal K^{\prime\prime}_{n,k}(k)=2E2_{n,k}$ | 2.7 | — |
| $B_{n,m}$ | 최댓값이 용량에 막힌 주차함수의 수(막힌 목록 수) | 2.7 | — |
| $E_{n,k}, E2_{n,k}$ | 짝수 동률 수, 두 차 동률 수 | 2.7 | — |
| $J_n(z)$ | 경계 다항식 $\sum_{\sigma\in\mathfrak S_n}H_k\,k^{H_k-1}\,z^{Z_k}\prod_{i:\,h_i<k}h_i$(문턱 $k$ 고정; $z$는 무게 변수); 열 $k$의 비교에 쓰는 값은 $J_n(k-1)$ | 2.7 | $J_n(k)$ ([r475ada3]; 무게 $k$의 값); $J_n(c)$, $B^G=J_n(k-1)$ ([r37c204b], [r5f5cf73]) |
| $M^{\#}(\alpha)$ | 최대 변위를 달성하는 차의 수(동률 수) | 2.7 | $K_M$ ([ra4c01fc], [r5f5cf73]) |
| $\Xi_{n,k}$ | $B_{n,k-1}=J_n(k-1)-\Xi_{n,k}$의 보정 $\mathbf 1_{n=2k}\binom{2k-1}{k-1}p_{k-1}^2$ | 2.7 | — |
| $\mathcal K_{n,k}(y)$ | 얼린 용량 다항식(인자를 $h_i$로 고정하고 용량을 실수 $y$로 둔 것) | 2.7 | — |
| $\mathrm{Gr}(x)$ | Green 적분인자의 지수 $T(x)-T(x)^2/2$ | 2.7 | $U=T-T^2/2$ ([rba2ecf4], [r37c204b], [rce3dc75], [ra4c01fc], [rda45d0e]) |
| $\mathcal P_m(j)$ | 마지막 차 자리 법칙 $\Pr_m(\mathrm{pos}_m=j)=j\binom{m-1}{j-1}p_{j-1}p_{m-j}/p_m$ | 2.8 | $\Pi_m(j)$ ([r79ee9e0], [r7e03176], [r8456f59] L32); $\Pi_L(j)$ ([r5bbc534]); [r79ee9e0]의 $\pi_m(j)$·$p_j$는 다른 양 |
| $x_t(y)$ | 나무 곡률 $s^T_t(y+1)-2s^T_t(y)+s^T_t(y-1)$; 열 $k$에서는 $x_t(k)$ | 2.9 | — |
| $M^{T}_t$ | 크기 $t$ 균등 뿌리 나무의 최대 변위 | 2.9 | — |
| $P_t(k)$ | 머리 합 $\sum_{t^\prime=k}^{t}x_{t^\prime}(k)$(첫 항 $x_k(k)=-1/k$가 출발 빚) | 2.9 | — |
| $\Pi$ | 사슬 생존 곱: 나무(사슬) 전체의 $\prod_{S_i>y}y/S_i=\prod_i y/(y+q_i)$ | 2.9 | — |
| $\Psi(q)$ | Borel 갱신함수 $\sum_{j=1}^q\mathrm{Ren}(j)$ | 2.9 | $U(D)=1+\Psi(D)$ ([r4868e30]); $\bar\Psi$ ([r030ffae], 다른 양); $\Psi(d)$ ([r2ec875c]) |
| $\theta_t(k)$ | 크기 $t$ 균등 나무의 문턱 부분나무 기대 수 $\mathbb E^T_t[H_k]=\binom tk\frac{k^{k-1}(t-k)^{t-k}}{t^{t-1}}$ | 2.9 | — |
| $\mathrm{Ren}(j)$ | 갱신 방문 핵 $j^je^{-j}/j!=j\,\mathrm{Bor}(j)$, $\mathrm{Ren}(0):=1$; 하계 함수는 $\mathrm{Ren}_*(j)$ | 2.9 | $c_j$, $c_h$, $c_0=1$ ([r4868e30]); $u(j)$, $u(r)$, $u(n)$, $u(q)$ ([r030ffae], [re71a735], [r2ec875c], [r98fb348], [r8456f59], [r5bbc534]); $c_d$ ([r79ee9e0]); $c_j$, $c_g$ ([r42d9a17], [r1aa0be6]) |
| $\Pr^{T}_t, \mathbb E^{T}_t$ | 크기 $t$ 균등 뿌리 라벨 나무의 법칙과 기댓값 | 2.9 | — |
| $b^{(2)}_m$ | 두 수준 개수 $b_{m,k}+b_{m,k-1}$ | 2.10 | $L_m$ ([rae1f209]) |
| $b^{T}_{t,\ell}$ | 크기 $t$, 최대 변위 $\ell$인 뿌리 나무의 수 $\mathcal N_\ell(t)-\mathcal N_{\ell-1}(t)$(다섯 몫의 계수 $u_s=b^T_{t,k}$, $v_s=b^T_{t,k-1}$) | 2.10 | — |
| $c^{(2)}_m$ | 두 수준 질량 $c_m(k)+c_m(k-1)=b^{(2)}_m/p_m$ | 2.10 | $\ell_N$ ([rae1f209]); $s_m$ ([r3d0856b]); 나무판 $\tilde u_s,\tilde v_s$·$C^\pm_s$([rae1f209], [r5909c9e])는 $b^T_{t,k}/p_{t-1}$, $b^T_{t,k-1}/p_{t-1}$로 풀어 적음 |
| $\delta_t$ | 나무 한 칸 차분 $b^T_{t,k}-b^T_{t,k-1}$; $t\ge k+1$에서 $=(k+1)b_{t-1,k}-(k-1)b_{t-1,k-1}=t^{t-1}x_t(k)$ | 2.10 | — |
| $\Theta_n$ | 문턱 나무 손실 $\binom nkk^{k-2}A_{n-k,k-1}$ | 2.10 | — |
| $\mathcal B_\ell(x)$ | 나무 수준 개수의 지수 생성함수 $\sum_tb^T_{t,\ell}x^t/t!=T_\ell-T_{\ell-1}$ | 2.10 | — |
| $\mathrm{BV}_n$ | 줄기 이득(다섯 조각) | 2.10 | — |
| $\mathrm{FL}_n$ | 첫 층 선속(다섯 조각) | 2.10 | $FL_n$ |
| $\mathrm{KD}_n$ | 둘째 층 상속(다섯 조각); 상속 몫 $\mathrm{KD}^\prime_n=\sum_{m=2k+1}^{n-1}(k+n-m)\binom{n-1}mp_{n-1-m}d_{m,k}$ | 2.10 | — |
| $\mathrm{PAIR}_n$ | 두 수준 블록 쌍(다섯 몫; 숲–나무 분해의 음 아닌 나머지) | 2.10 | $\mathcal X_n$ ([rb6a2cd0], 같은 범위) |
| $R_j$ | 자유 Borel 보행의 부분합($R_0=0$) | 2.11 | $R_j$ ([r8a9b11e]); $T_k$(iid Borel 합; [r8a9b11e]); $S_j=g_1+\dots+g_j$ ([r845b205]) |
| $\beta_i$ | 독립 Borel 변수(자유 Borel 보행의 걸음; 사슬에서는 $q_{i-1}-q_i$) | 2.11 | $Y$ ([r8a9b11e]); $g_i$ ([r845b205]); $B$ ([r7e03176], [r79ee9e0]) |
| $\mathcal H_{\mathrm B}(q)$ | Borel 갱신 집합 $\{R_j\le q\}$ | 2.11 | — |
| $\mathrm{tilt}_q(q^\prime)$ | 기울임 인자 $\mathrm{Bor}(y+q^\prime)/\mathrm{Bor}(y+q)$($q^\prime<q$; 용량 $y$는 문맥의 것) | 2.11 | $\tau_d(b)$ ([re71a735]); $r_j(t)$ ([r845b205]; 실수 연장); $\rho_h$, $\rho_j$ ([r030ffae]), $\omega_N(r)$ ([r5bbc534])는 $\mathrm{Bor}(N+1-r)/\mathrm{Bor}(N+1)$ 꼴 |
| $\Pr^y(q\to q^\prime)$ | 초과 $q$에서 $q^\prime<q$로 내려갈 확률 $\mathrm{Bor}(q-q^\prime)\mathrm{Bor}(y+q^\prime)/\mathrm{Bor}(y+q)$(사슬의 전이 확률) | 2.11 | $p(y\to z)$ ([rad00a59], 다른 사슬) |
| $\Pr^y, \mathbb E^y$ | 용량 $y$의 무거운 사슬 법칙과 기댓값; 기준 용량 $y_0:=k$의 것(얼린 법칙)은 $\Pr^{y_0}$, $\mathbb E^{y_0}$ | 2.11 | — |
| $W_n(\gamma)$ | 간격 수열 $\gamma$(지정 사슬 크기 $\mathfrak t_1>\dots>\mathfrak t_j$, 길이 $j$; 1.3 2.12 묶음)의 사슬 가중치 $\mathrm{nf}(n,\,n-\mathfrak t_j)\prod_{i<j}n/\mathfrak t_i$ | 2.12 | $W_n(g)=\mathcal R(n,d_k-1)\prod_{i<k}n/s_i$ ([r1aa0be6]; $k$는 사슬 길이, $d_k=n+1-s_k$); [r42d9a17] |
| $\mathrm{nf}(n,d)$ | 사슬 전개의 정규화 인자 $e^d\frac{n!}{(n-d)!}\frac{(n-d)^{n-d-2}}{n^{n-2}}$ | 2.12 | $\mathcal R(n,d)$ ([r1aa0be6], [r42d9a17], [r13b0b8f]) |

### 3장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $f$ | 극한 $X$의 밀도 | 3.1 | — |
| $X_n, X$ | 정규화 결손 $(n+1-M_n)/(n+1)^{2/3}$과 그 극한(해싱 극한); 분포함수·생존함수는 $\Pr(X\le x)$, $\Pr(X\ge x)$로 적는다 | 3.1 | [rae1f209]의 $X_n$은 $\mathcal C_n$ |
| $x_\ast$ | 밀도 $f$의 최빈점(임계 창 좌표의 특정값) | 3.2 | $m$ ([r1aa0be6], [r81e7051]); $m_f$ ([r690be93]); $x_*$ ([r0dc57fa]); $\mathfrak m$ ([r29c10cd]) |

### 4장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $\mathsf{LH}(n), \mathsf{LH}^+(n)$ | 왼쪽 절반의 증가 명제 $b_{n,0}\le\dots\le b_{n,k_n-1}$과 $b_{n,k_n}$까지의 판 | 4.1 | — |
| $\mathsf P_L, \mathsf P_X, \mathsf P_C, \mathsf P_R$ | 네 위치쌍 명제(모든 $n$의 연언); 행별 명제는 $\mathsf P_L(n)$ 등 | 4.1 | $T(n)$, $L(n)$ ([r656206c]); cross, $P_X$ ([rce3dc75]); [r5f5cf73] §6.2의 $P_R$은 다른 양 |
| $\Gamma^{\pm}$ | 경계 응답의 두 경계항 $p_k\Gamma_{r-1}(k+2; n)$, $p_{k-1}\Gamma_{r}(k-1; n)$ | 4.2 | $B_\pm$ ([r708d99c]) |
| $\Gamma_d(\ell;n)$ | 경계 응답 다항식 | 4.2 | 「경계 응답」 |
| $\mathcal S_{n,k}$ | 경계 응답 부등식의 양 $\Gamma^+d_{n,k}-\Gamma^-d_{n,k+1}$ | 4.2 | — |
| $\mathsf Q, \mathsf Q_L, \mathsf Q_R, \mathsf Q(n,\ell)$ | 감소 뒤의 로그오목성(조건부 로그오목성)과 두 반쪽, 위치별 명제 | 4.2 | — |
| $\mathsf S_R$ | 경계 응답 부등식 $\mathcal S_{n,k}\ge0$의 명제 | 4.2 | — |
| $V(x)$ | $(1-x)^2/2$(중앙 틈의 피적분 인자) | 4.3 | — |
| $\Phi, \Phi^{\mathrm{aux}}$ | 중앙 틈의 생성함수($e_n/n!=[x^n]\Phi(T(x))$)와 위끝을 $1$로 바꾼 것 | 4.3 | — |
| $\mathcal A_{k,n}$ | 중앙 틈의 계수 $\frac{n!}{p_n}[x^n]\Phi^{\mathrm{aux}}(T)$ | 4.3 | — |
| $\mathcal D(\beta)$ | Dawson 함수 | 4.3 | — |
| $\mathcal I_k$ | Gauss형 적분(중앙 틈) $\int_0^1\frac v{1-v}e^{-v^2/2}e^{-k\varrho(v)}dv$ | 4.3 | 같음 ([rce3dc75], [r5f5cf73]); $J_c$ ([ra4c01fc]) |
| $\mathcal M_r$ | Gauss형 계수(중앙 틈의 실수 비교); $(y,n)$-판은 $\mathcal M^{(y,n)}_r$ | 4.3 | — |
| $\mathsf a_j$ | 적분 상수 $\int_0^\infty y^je^{-y^3/3}\,dy$ | 4.3 | $C_0$, $I$ ([rce3dc75], [r5f5cf73], [ra4c01fc]); $M_m$ ([ra4c01fc]); $C_A$ ([rb7effe0]) |
| $\mathsf b_D, \mathsf b_J$ | 상쇄 분해의 두 보정 계수 | 4.3 | — |
| $\mathsf g_k$ | 중앙 틈의 선도 상수 $2-k\mathcal M_2/\mathcal M_0$; $n$-판은 $\mathsf g_{k}(n)$ | 4.3 | — |
| $\mathsf n_k, \mathsf n_\infty$ | 중앙 틈 증명의 정규화 상수 $\frac{n!}{p_n}\frac{e^{n+1}}{2\pi k^{3/2}}$와 그 극한 $2/\sqrt\pi$ | 4.3 | $N_k$, $N_0$ ([rce3dc75]); $N_k=N_nk^{-3/2}$ ([r5f5cf73]) |
| $\mathrm{Bor}^{\mathrm{tail}}_k(s)$ | Borel 꼬리(중앙 틈 증명의 꼬리 함수) | 4.3 | — |
| $\mathrm{He}_j$ | Hermite 수(중앙 틈의 두 보정) | 4.3 | — |

### 5장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $A^{c}_{n,\ell}$ | 미달 수 $p_n-A_{n,\ell}$(최대 변위가 $\ell$을 넘는 주차함수의 수); 꼬리 좌표로는 $A^c_{n,n-r-1}$ | 5.1 | $D_{n,\ell}$, $\mathscr D_n(r)$ ([r42d9a17], [r1aa0be6]; 기록 $r=n-\ell$은 사전 $r+1$); $\Delta_n=p_n-A_{n,c-1}$ ([rba2ecf4]) |
| $\mathfrak a_n$ | 지수 생성함수 계수 $A_{n,k-1}/n!$; 볼츠만판 $\tilde{\mathfrak a}_n=e^{-n}\mathfrak a_n$ | 5.1 | $a_m$ ([rb7effe0], [rad00a59], [r207f124]); $f_n$ ([r60a6f55]); $\tilde a_m$ ([r207f124]) |
| $b^\circ_{n,\ell}$ | 막히지 않은 수준 개수 $b_{n,\ell}-B_{n,\ell}$(최대 변위가 $\ell$인 주차함수 가운데 용량에 막히지 않은 것의 수) | 5.2 | $\Phi_{n,k}$ ([rda45d0e]; 첨자는 수준) |
| $\mathfrak m(n)$ | 꼬리 정리들이 덮는 꼬리 길이 $\max(\{170\}\cup\{m\ge171:m^{3/2}+9m\le n\})$ | 5.2 | 같음 ([r2ec875c], [r23f10e9]) |
| $\mathrm{rb}_m$ | Robbins 나머지 $\log m!-(m+\tfrac12)\log m+m-\tfrac12\log(2\pi)$ | 5.2 | $\rho_m$ ([r5909c9e], [rae1f209]); $\lambda_q$ ([r5bbc534]); $r_n$ ([r9bf2dc6]); $\varepsilon_h$ ([r7798355]); $\theta_n$ ([r29c10cd]) |
| $(\mathrm G)_d$ | 경계 응답 부등식을 합 지표 $d$별로 쪼갠 조각 | 5.2 | source-wise comparison |
| $r_0(n)$ | 진입 지표 $\lfloor\frac34n^{2/3}\rfloor$(꼬리 좌표의 특정값); 진입 위치는 $n-r_0(n)-1$ | 5.3 | — |
| $\mathsf W, \mathsf W^\sharp$ | 오른쪽 벌크 증가 명제; 임계 창 잔여 명제 | 5.3 | — |
| $\mathsf X$ | 오른쪽 두 항 부등식 명제 | 5.4 | — |
| $q_{\max}(Y)$ | 착지 창의 폭(창 끝) $\lfloor6Y^{2/3}\rfloor$; 열 $k$에서는 $q_{\max}=\lfloor6k^{2/3}\rfloor$ | 5.5 | $B$ ([r030ffae]); $R_\ell$ ([r8a9b11e]) |
| $t_0(y)$ | 이음 행(나무 크기 변수의 특정값; 정의 `{{5:old-5-21}}`) | 5.5 | 같음 ([r58b4caa]) |
| $\Lambda_{\mathrm w}(Y)$ | 가중 창 질량 $\sum_{r=1}^{q_{\max}(Y)}\frac{Y}{Y+r+1}\mathrm{Lc}(Y,r)$ | 5.5 | $\Lambda_w(\ell,R)$ ([r8a9b11e]; 창 끝 $R$ 명시) |
| $\mathcal E, \mathcal E^+, \mathcal E^\ast(y)$ | 열 사이 보정 $y\sum_m\mathfrak e_mc_m(y-1)$; 그 상계 $\mathsf C_E(y-1)^{-1/3}$; $n$에 무관한 상계 | 5.5 | — |
| $\mathfrak e_m$ | 열 사이 보정의 보정 무게 $\frac{(y-1)(m+2)-(y+1)(m+1)(1-\mathfrak z_m(d))}{(m+1)(m+2)}$ | 5.5 | $e_m$ ([r8a9b11e], [r23f10e9]) |
| $\mathfrak g(\theta)$ | 정리 `{{5:old-5-32}}`의 피적분함수(인수 $\theta$는 5.5.6–5.5.8의 국소 척도 변수 $z/Y^{1/3}$) | 5.5 | $g$ ([r8a9b11e]) |
| $\mathfrak z_m(d)$ | 크기 방향 손실률 $\frac{e^{(d-1)/w}}{w+1}+\frac{3d}{2(w+1)(m+1)}$($w=m-d$는 수준 좌표; 5.5의 국소 글자) | 5.5 | $\beta_m(d)$ ([r29c10cd], [r23f10e9]; 기록의 $v=m-d$) |
| $\mathsf C_E$ | 열 1차 모멘트 상수 $7.7148$(정리 `{{5:old-5-37}}`) | 5.5 | $C_E$ ([r8a9b11e]; review 정정값) |
| $\mathsf w_0$ | 가중 창 질량의 균일 하계 $0.71216$(정리 `{{5:old-5-32}}`) | 5.5 | $s_0$ ([r8a9b11e]; review 정정값) |
| $\mathsf z_{1/2}, \mathsf z_{-1/2}, \mathsf z_{3/2}$ | Riemann 제타 함수의 $\tfrac12$, $-\tfrac12$, $\tfrac32$에서의 값 | 5.5 | $\zeta(\frac12)$, $\zeta(-\frac12)$, $\zeta(\frac32)$ ([r030ffae], [rfc69320]) |
| $\mathrm{EB}(w)$ | $\mathcal E^\ast$의 닫힌 꼴 상계(인수 $w$는 수준 좌표 $m-d$) | 5.5 | $EB(v)$ ([r8a9b11e]) |
| $\mathrm{IH}(n,y)$ | 귀납 가정 | 5.5 | $H(n,y)$ ([r8a9b11e]) |
| $\mathrm{Lc}(Y,r)$ | 착지 창 열 값 $c_{Y+r}(Y)$의 닫힌 꼴 하계 | 5.5 | $\mathrm{Lc}(\ell,r)$ ([r8a9b11e]) |
| $\mathrm{POS}_0, \mathrm{POS}^\prime_0, \mathrm{POS}^{\prime-}_0$ | 환원 (R₀)의 꼭대기(원천) 항; 흡수 뒤의 원천 항과 그 하계 | 5.5 | $\mathrm{POS}_\alpha$ ([r58b4caa]; 기울임 매개변수 $\alpha=0$); (R₀), $\mathrm{POS}_0$, $\mathrm{POS}^\prime_0$, $\mathrm{POS}^{\prime-}_0$, (CF₀′) ([r8a9b11e] L238·250·254) |
| $\mathrm{tail}_t(y)$ | 나무 곡률의 꼬리합 $\sum_{t^\prime=t+1}^nx_{t^\prime}(y)$ | 5.5 | $\mathcal T_s(y)$ ([r58b4caa]) |
| $\mathrm{top}, \mathrm{top}_\pi$ | 꼭대기 보정 $y(y-1)c_{n-1}(y-1)/n$; 가장 큰 나무 핵판 $(y-1)\pi_n(y)$ | 5.5 | — |
| $\mathrm{WIN}_0, \mathrm{WIN}^{\mathrm V}_0$ | 환원 (R₀)의 창 항(꼬리 창의 음의 질량); 그 방문 확률 상계 | 5.5 | $\mathrm{WIN}_\alpha$, $\mathrm{WIN}^V_\alpha$ ([r58b4caa]; $\alpha=0$) |
| $\eta$ | 임계 창의 척도 매개변수 $(r+1)/k$($\hat x=\eta k^{1/3}$) | 5.6 | $\eta=Q/k$ ([r5f5cf73]); [ra4c01fc] §10.3의 $\eta=Y/k$는 사전 $\eta-1/k$ |

### 6장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $s^{\mathrm F}(k,\nu)$ | 첫 층 생존의 상계 함수 $\min(1,3(k+1)(\nu-1)^{-3/2})$(정리 F′의 창 읽기) | 6.1 | $\psi(a)=\min(1,3ka^{-3/2})$ ([r7e03176]; 일반판 — 사전은 용량 $k+1$, $a=\nu-1$의 특수화); $F^\prime(k,\nu)$ ([r3d0856b] L340 정의; [re71a735]는 사용) |
| $\mathrm{Bor}_{>}(q)$ | Borel 꼬리 $1-\mathrm{Bor}_\le(q)$ | 6.1 | $T(b)$ ([r030ffae]) |
| $\kappa_N$ | 위험률 하계 (Hz)의 상수($\ge0.307$) | 6.2 | 같음 ([r051bfe1]); [r030ffae] 보고서의 $\kappa_N$은 다른 양 |
| $\varrho_t, \varrho^{\mathrm H}, \varrho^{\mathrm L}, \varrho_{\min}$ | 표시 나무 무게의 증분 $\mathfrak w_n(t)/\mathfrak w_n(t-1)-1$과 그 하계들; 크기별 하계 $\varrho^{\mathrm{lb}}_t$ | 6.2 | $\rho_s,\rho^H,\rho^L,\rho_{\min}$ ([rb6a2cd0]) |
| $\mathfrak r_N$ | 제한 성장비 $A_{N+1,k-1}/((N+1)A_{N,k-1})$ | 6.2 | $r_N$ ([rb6a2cd0], [r3d0856b], [rcb2e2d4]); $\rho_N$ ([r051bfe1]; $\rho^*=\rho_{k-1}=1/x^*$는 $\mathfrak r_{k-1}=1/\mathsf x_k$) |
| $\mathfrak w_n(t)$ | 표시 나무 무게 $\binom ntt^{t-1}A_{n-t,k-1}$(크기 $t$ 나무를 표시하고 환경을 용량 $k$ 아래에서 센 수); 정규화 $\tilde{\mathfrak w}_n(t)=\mathfrak w_n(t)/p_n$ | 6.2 | $\varpi_n(s)$ ([rb6a2cd0], [rcb2e2d4]); $\varpi_n(N)$ ([r4868e30]; 인수 글자 $N$) |
| $\mathrm{dec}_N$ | 감소율 $k(1-\log\mathfrak r_N)$ | 6.2 | $\eta(N)$ ([r051bfe1], [r207f124], [rb6a2cd0]) |
| $\mathrm{hz}_k(N)$ | 크기 방향 생존 위험률 $1-s_{N+1}(k)/s_N(k)$; 위험률 합은 $\Sigma_{\mathrm{hz}}$ | 6.2 | $h_k(N)$ ([r030ffae], [rb6a2cd0], [r051bfe1], [r5bbc534]); $h_m$ ([r79ee9e0]) |
| $\varsigma_m(\ell)$ | 머묾 질량 $s_{m+1}(\ell+1)-s_m(\ell)$(크기 $m\to m+1$에서 최대 변위가 수준 $\ell$에 머무는 몫); 결손 좌표로는 $\varsigma_{y+d-1}(y)=\mathfrak s_d(y+1)-\mathfrak s_d(y)$ | 6.3 | $\sigma_n(\ell)=\varsigma_n(\ell+1)$ ([r3d0856b]; 인수 하나 어긋남); $W^{(\ell)}_n=\varsigma_{n-1}(\ell)$ ([r3d0856b], [re71a735]; 첨자 하나 어긋남); $W_c(d)$ ([re71a735]) |
| $\mathfrak s_d(y)$ | 결손 좌표의 생존 확률 $s_{y+d-1}(y)$(같은 양의 좌표 변환 약기) | 6.3 | $s_d(y)$ ([re71a735]); $s_c(d)$ ([r98fb348]) |
| $\Upsilon_k, \hat\Upsilon_k$ | $\frac{k(k-1)b_{2k,k-1}}{(2k+1)p_{2k}}$와 그 상계 $(k-1)\mathsf u(k)/(2k+1)$ | 6.4 | — |
| $\varphi^\flat_k$ | 평평한 핵심 $k\sum_{t=k+1}^{2k+1}x_t(k)$ | 6.4 | flat-core(정의는 [r29b01e8] L146) |
| $\mathsf u(k)$ | $\Upsilon_k$ 상계의 함수 $\frac3{0.35}(1.35+\frac1k)(0.65-\frac1k)^{-3/2}k^{-1/2}$ | 6.4 | $g(k)$ ([r7e03176], [rb1d8cd5]); $\tilde g(k)$ ([rb6a2cd0]) |
| $D_k$ | 첫 층 기저 $\sum_{t=k}^{2k+1}x_t(k)=P_{2k+1}(k)$ | 6.5 | — |
| $\Pi_j(y)$ | 사슬 생존 곱의 $j$번째까지의 부분곱 $\prod_{i\le j}y/(y+q_i)$ | 6.5 | $\Pi_j(t)$ ([r845b205]); $\Pi_J(y)$ ([re71a735]) |
| $\psi(y)$ | 얼린 볼록성의 함수 $y\prod_iy/(y+q_i)$(사슬을 고정한 생존의 $y$-함수) | 6.5 | 같음 ([r845b205]) |
| $\mathcal U_k(m)$ | 볼츠만 꼬리합 $\sum_{m^\prime=m}^{2k}\mathfrak b_{m^\prime}$(판정 UL의 꼬리합; 핵심은 $\mathcal U_k(k)$) | 6.5 | $U_k(L)$ ([r7e03176]); [r29c10cd]의 $\mathcal U_k=\sum_{m\ge k}V_m$은 $2k$ 절단이 없는 다른 양 |
| $\mathcal V_k(m)$ | 확률 꼬리합 $\sum_{m^\prime=m}^{2k}\mathfrak p_{m^\prime}$(판정 V의 꼬리합; V-핵심은 $\mathcal V_k(k)$) | 6.5 | $\tilde U(L)$ ([r845b205], [r3d0856b], [r23f10e9]) |
| $\mathfrak b_m$ | 볼츠만 무게 $\delta_{m+1}e^{-m}/m!$(판정 UL의 항) | 6.5 | $V_m$ ([r29c10cd], [r9bf2dc6]) |
| $\mathfrak p_m$ | 확률 무게 $\delta_{m+1}/p_m$(판정 V의 항) | 6.5 | — |
| $\mathfrak X_d(y), \mathfrak X^0_d, \mathfrak X^1_d$ | $y\Pr_{y+d-1}(M\ge y)=y(1-\mathfrak s_d(y))$와 그 두 분해항(기울임 없는 보행 부분과 나머지) | 6.5 | $\Theta_d$, $\Theta^0_d$, $\Theta^1_d$ ([r845b205]) |
| $\mathsf{UL}, \mathsf V, \mathsf V^\ast$ | 첫 층 꼬리합 판정의 이름(볼츠만·확률·임계 기울임); 판정 V의 꼬리표는 (V) | 6.5 | — |
| $\mathsf v(k), \mathsf v^\prime_k$ | V-핵심 상수 $0.765\ldots$와 그 성분 $\max(k+1,4000)$ | 6.5 | — |
| $\mathsf x_k$ | 임계 기울임 $(k/(k+1))^{k-1}$(정리 `{{7:old-6-10}}`의 상수) | 6.5 | $x^*$ ([r051bfe1], [rcb2e2d4]); $c_k$ ([rad00a59]); $\rho_k$ ([rbeae3a3]) |
| $\mathrm{Bd}^{\mathrm V}_k$ | 망원 항등식의 경계항 가족 가운데 V-핵심 체류 꼴의 경계항 $2-2s_{2k+1}(k+1)-(k-1)\varsigma_{2k}(k)-(k-1)c_{2k}(k-1)$ | 6.5 | $B_k$ ([r845b205]); $Bd$, $Bd^\prime$ ([rae1f209])는 $\mathcal J_3$, $\mathcal J_4$ |
| $\mathrm{DD}(m,y)$ | 대각선 둘째 차분 $(y+2)s_{m+2}(y+2)-2(y+1)s_{m+1}(y+1)+ys_m(y)$; 10장의 약기 $\mathrm{DD}_m:=\mathrm{DD}(m-1,k-1)$ | 6.5 | $DD_m$ ([re71a735], [r3d0856b]); $D_d$ ([r98fb348]) |
| $\mathsf s_{\mathrm B}$ | Borel 질량의 Stirling 상수 $e/\sqrt{2\pi}$ | 6.6 | $B$ ([r7e03176], [r29c10cd]) |

### 7장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $\tilde n_k$ | 기록의 경계 $k(2\mathsf t_k+1)$ | 7.1 | $\tilde N_k$ ([r39ba7c1]) |
| $\bar A_n(y)$ | 실수 용량 보간 $\sum_\sigma\prod_i\min(h_i,y)$($\bar A_n(k)=A_{n,k-1}$; 각 구간 $[j,j+1]$에서 $\mathcal K_{n,j}(y)$) | 7.1 | — |
| $\mu_n(k)$ | 상대 둘째 차분 $d_{n,k}/A_{n,k-1}=\mathbb E^\sigma_{n,k}[\mathfrak v_k(Z_k,H_k)]$ | 7.1 | $\hat\delta_m$ ([r207f124]); $r_m$ ([r79ee9e0]); [r39ba7c1]의 $\mu_T$는 다른 양 |
| $\mathcal T_k(\sigma), \mathcal T_{n,k}$ | 모멘트 판정의 통계 $Z_k(Z_k-1)-kH_k$; 그 합 $\sum_{\sigma:M\le k-1}\mathcal T_k(\sigma)=A_{n,k-1}\mathbb E^\sigma_{n,k}[\mathcal T_k]$ | 7.1 | $\Sigma_{n,k}$ ([rad00a59]); $LM_{n,k}$ ([r475ada3]); $T_n=S_n-kh_n$ ([r10ff8c2]; 기댓값판) |
| $\mathsf{LM}$ | 왼쪽 모멘트 명제 | 7.1 | left-moment |
| $\mathsf t_k$ | 반감 경계 지표 $\min\{t\ge0:(k+1)^tk^{t+1}+(k-1)^{2t+1}\ge2k^{2t+1}\}$ | 7.1 | $t_k$ ([r39ba7c1], [rb6423c6]) |
| $\mathrm{Conv}_{n,k}, \mathrm{Kink}_{n,k}$ | 볼록–꺾임 분해의 볼록 항과 꺾임 항 | 7.1 | — |
| $\Pr^{\sigma}_{n,k}, \mathbb E^{\sigma}_{n,k}$ | 용량 가중 결과 순열 법칙 $\prod_i\min(h_i,k)/A_{n,k-1}$($\mathfrak S_n$ 위; 균등 주차함수를 $M\le k-1$로 조건화한 결과 순열의 법칙)과 그 기댓값 | 7.1 | — |
| $n^\natural_k$ | 자기일관 상계(정리 S)의 경계 | 7.2 | $N_k$ ([rad00a59], [r89eb039]) |
| $n^\sharp_k, n^\flat_k, n^\circ_k$ | 열 $k$의 증가 경계들(행 크기의 특정값): 반감 경계 $k+(k+1)\mathsf t_k$; 정리 `{{7:old-6-10}}`(임계 기울임 $\mathsf x_k$)의 경계; 극 영역의 정밀 시작 $\lceil2k^{3/2}\rceil$ | 7.2 | $N^\sharp_k$ ([rb6423c6]); $N^\flat_k$ ([r7c26b8b], [r89eb039]); $n_0=\lceil2k^{3/2}\rceil$ ([r89eb039]); [r39ba7c1]의 $N^\#_k$(생산자 경계)·[rc9aee43]의 $N_k=\lceil k^2/4\rceil$는 둘째 판이 쓰지 않는 다른 양 |
| $C_k(x), C_{n,k}$ | 용량 $k$ 아래 소인 주차함수의 지수 생성함수와 그 계수 $n!\,[x^n]C_k$ | 7.2 | $C_k$, $c_{n,k-1}$ ([rf451d83], [r7c079be]); $P_c$ ([r9e782f5]); $C_\ell(z)$, $c_{d,\ell}$ ([r60a6f55], [rf09e7ef]; 첨자 수준) |
| $\rho_k$ | 열 $k$의 극 | 7.2 | 같음 ([rb7effe0], [rf451d83]); $\rho_\ell$ ([rf09e7ef], 첨자는 수준); [r39ba7c1] peer 파일의 $\rho_k$(영점)와 [r051bfe1]의 $\rho^*=\rho_{k-1}$($=\mathfrak r_{k-1}$)은 다른 양 |
| $\mathfrak a^\circ_n$ | 용량 제한 없는 지수 생성함수 계수 $p_n/n!$ | 7.2 | $u_n$ ([r60a6f55]); $a^\circ_m$ ([rb7effe0]); $a_m$ ([r475ada3]); $a^\infty_m$ ([rad00a59]) |
| $\mathfrak P_k(n)$ | 문턱 자리 밀도 $\mathbb E^\sigma_{n,k}[kH_k]/n$ | 7.2 | 같음 ([rb7effe0]) |
| $\mathsf{LM}^{\flat\flat}$ | 왼쪽 모멘트 명제의 축소 | 7.2 | left-moment core |
| $\mathsf W_L, \mathsf W_L^\flat$ | 왼쪽 잔여 증가 명제와 그 축소 | 7.2 | — |
| $n_{\mathrm X}(k)$ | 유한 크기 전달 명제 $\mathsf X^\prime$의 시작 행 $\lceil k^{4/3}\rceil$(행 크기의 특정값) | 7.3 | $n_0$ ([rf451d83], [r207f124]) |
| $\mathfrak a^{\rho}_l$ | 극 정규화 갱신열 $\mathfrak a_l\rho_k^l$ | 7.3 | $f(l)$ ([rb7effe0], [r89eb039]); $u_l$ ([rf451d83]); $u^{(y)}_l$ ([r207f124]) |
| $\mathfrak P_k(\infty)$ | 문턱 자리 밀도의 $n\to\infty$ 극한 | 7.3 | 같음 ([rb7effe0]) |
| $\mathsf X^\prime$ | 유한 크기 전달 명제 | 7.3 | — |
| $\mathrm{pr}_{n,k}, \mathrm{pr}^\circ_n$ | 소인 질량 $C_{n,k}e^{-n}/n!$(볼츠만판 소인 수)과 용량 제한 없는 판 $(n-1)^{n-1}e^{-n}/n!$ | 7.3 | $d_{n,k}$ ([r7c079be], [rb7effe0] §6.4 L452); $d_n$ ([rf451d83]); $d_{N,k}$ ([r89eb039]); 무제한판 $d_n$ ([rb7effe0]), $d_m$ ([r89eb039]) |
| $J^{\mathrm G}_n(z)$ | Green 표현을 모든 $n$으로 연장한 경계 다항식의 상계(Green 원자; $z$는 무게 변수) | 7.4 | $J^G_n(c)$ ([r475ada3]) |
| $\mathcal P^{(k)}_m(j)$ | 용량 $k$ 아래의 뿌리 자리 법칙 $\min(j,k)\binom{m-1}{j-1}A_{j-1,k-1}A_{m-j,k-1}/A_{m,k-1}=\Pr_m(\mathrm{pos}_m=j\mid M\le k-1)$(마지막 차 자리 법칙을 $M\le k-1$로 조건화한 것) | 7.4 | $P_m(j)$, $P_N(J=j)$ ([r051bfe1] L68·163); $P_t(j)$, $\theta_N(j)$ ([r79ee9e0] L52·171; $N$은 행 크기); $\pi_n(s)$ ([r207f124]); $\pi_n(p)$ ([r10ff8c2] L72) |
| $\mathcal R_{\mathrm L}, \mathcal R^{(>40)}_{\mathrm L}$ | 왼쪽 잔여 위치 집합 $\{(k,n):k\ge2001,\max(2k+1,20001)\le n<\min(n^\flat_k,n^\natural_k)\}$와 그 $2k+41$판(실질 잔여 $\mathcal R_2$의 전신) | 7.4 | $\mathcal R_L$, $\mathcal R^{(>40)}_L$ ([r475ada3], [r89eb039]) |
| $\mathcal W_M$ | 모멘트 창(모멘트 인증의 위치 집합) | 7.4 | — |
| $\chi_m(j)$ | 원천 함수(뿌리 자리 $j$의 원천 몫) | 7.5 | $\varphi_t(j)$ ([r79ee9e0]) |
| $\mathcal W^{(>102)}, \mathcal W^{(>40)}$ | 왼쪽 창(한 걸음 판정을 묻는 위치 집합) $\{(k,n):k\ge2001,\max(2k+103,20001)\le n\le\lceil2k^{3/2}\rceil-1\}$; 기록의 넓은 판($2k+41$부터) | 7.5 | $\mathcal W^{(>102)}$ ([r6b37c7e]); $\mathcal W$ ([r89eb039]; $2k+41$판) |
| $\mathcal Z$ | $\mu_m(k)\ge0$이 알려진 크기 $m$의 집합(흡수 귀납의 입력 집합) | 7.5 | — |
| $\mathsf Q^\star, \mathsf Q^\star_2$ | 한 걸음 판정 명제와 그 둘째 층 판 | 7.5 | — |
| $\mathrm{cl}^+_m, \mathrm{cl}^-_m$ | 조건부 수준 질량 $c_m(k)/s_m(k)$, $c_m(k-1)/s_m(k)$(생존을 조건으로 한 수준 $k$·$k-1$의 질량) | 7.5 | $\beta^\pm_m$ ([r207f124]); $g^\pm(m)$ ([r79ee9e0], [r3d0856b]) |
| $\mathrm{inh}_k(n), \mathrm{inh}^{\mathrm{lin}}_k(n)$ | 첫 층 상속(첫 층 자식에서 상속되는 차분)과 그 선형 몫 | 7.5 | $\mathrm{FLlin}_k(t)$ ([r79ee9e0]) |
| $\mathrm{src}_k(m)$ | 토막 원천 $\sum_j\mathcal P^{(k)}_m(j)\,\chi_m(j)$(크기 $m$ 토막이 내는 원천) | 7.5 | $\hat\sigma_n$ ([r207f124]); [r10ff8c2]의 $\mathrm{src}_m$은 다른 양 |
| $(\star)(n)$ | 한 걸음 양 $\mathrm{src}_k(n)+\mathrm{inh}_k(n)$ | 7.5 | — |
| $n_{\mathrm{PD}}(k)$ | 전달 범위의 시작 $\lceil(k+1)^{4/3}\rceil+k+1$(행 크기의 특정값) | 7.6 | $t_{PD}(k)$ ([r79ee9e0] L269) |
| $\mathsf{SRC}^+$ | 원천 쪽 명제 | 7.6 | — |
| $w_m$ | 분할 무게 $\binom{n-1}mp_mA_{n-1-m,k-1}/A_{n,k-1}$($w_{k-1}:=0$) | 7.7 | 같음 ([r3d0856b], [re71a735]) |
| $\Pi^{\mathrm{up}}_h$ | 사슬 원소 수 $h$에서 사슬 생존 곱의 상계 계수 $\prod_{i=1}^h\frac{k+1}{k+i}$ | 7.7 | $\tau_h$ ([r3d0856b]) |
| $\mathfrak u_n$ | 문턱 단위 $w_{n-k}s_{n-k}(k+1)$ | 7.7 | $N_{thr}$ ([r3d0856b]) |
| $\mathsf{LRP}_2$ | 둘째 층 한 칸 비교 명제 | 7.7 | — |
| $\mathrm{Left}_n$ | 왼쪽 항 $\sum_{m=k}^{2k}w_m\mathfrak p_m$ | 7.7 | — |
| $\mathrm{Quad}_n, \mathrm{Stem}_n$ | 장부의 이차 몫; 깊은 자식 몫 | 7.7 | — |
| $\mathcal R_2$ | 실질 잔여 $\{(k,n):k\ge6668,\max(2k+103,20001)\le n\le3k-1\}$ | 7.8 | — |

### 8장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $s^{\mathrm{low}}_q$ | 원천의 생존 하계 수열(착지 창 크기 $k+q$의 생존 확률 $s_{k+q}(k+1)$을 아래에서 막는 임의의 수열; $s^{\mathrm{low}}_0=1$) | 8.1 | $Q^{\mathrm{low}}_c$ ([r030ffae] L94); [r030ffae]·[rfc69320]의 $Q_c$는 정확 생존 $s_{k+c}(k+1)$ |
| $\xi$ | 창 좌표 $q/k^{2/3}$(초과를 $k^{2/3}$ 눈금으로 잰 것; $\xi_c=c/k^{2/3}$); 10장에서 시작 초과 $\delta$의 것은 $\xi=\delta/y^{2/3}$ | 8.1 | $y$ ([r5909c9e]); $x_b$, $x$, $y$ ([r030ffae]); $y$ ([rfc69320]); $x$ ([re71a735] §4) |
| $\mathfrak D^{\mathrm{src}}_q$ | 부족량의 원천 항 $\frac q{k+q}\Psi(q)+\frac k{k+q}\sum_{m=1}^q\mathrm{Bor}(m)(1-s^{\mathrm{low}}_{q-m})$ | 8.1 | $\sigma_b$ ([r030ffae]) |
| $\mathfrak D_q$ | 부족량 $\Psi(q)-\mathfrak R_q$(창의 수준 질량이 극한값에서 모자라는 양; $\mathfrak D_0=0$) | 8.1 | $D_b$ ([r030ffae]) |
| $\mathfrak E_q$ | 부족량의 상위해(부족량 부등식을 만족하는 수열) | 8.1 | $E_b$ ([r030ffae]) |
| $\mathfrak R_q$ | 착지 창의 수준 질량 $k\,c_{k+q}(k)$ | 8.1 | $R_b=k\,r_{k+b}$ ([r030ffae]) |
| $\mathrm{Flow}_q$ | 부족량의 흐름 항 | 8.1 | $G_b$ ([r030ffae]) |
| $\tilde s^{\mathrm{env}}(\xi), \tilde s^{\mathrm{env}}_{\mathrm W}, \tilde s^{\mathrm{env}}_{\mathrm G}$ | 참 봉투(모든 $k\ge6600$에 걸친 하한으로 정의한 봉투 $\max(\tilde s^{\mathrm{env}}_{\mathrm W},\tilde s^{\mathrm{env}}_{\mathrm G})$; Jensen 쪽 $e^{-E^\ast}$, 탈출 쪽 $\max(0,\inf_{k}q_{k,k}(\xi))$ — $E^\ast$, $q_{k,k^\prime}$는 8.2 국소) | 8.2 | $\tilde Q$, $\tilde Q_W$, $\tilde Q_G$ ([rfc69320]) |
| $s^{\mathrm{cf}}(\xi)$ | 닫힌 꼴 봉투 $\max\{e^{-\mathsf j_\infty(\xi)}\ (\xi\le2.1),\ q_{6600,6600}(\xi)\ (\xi\ge2)\}$(저장된 봉투 표가 참 생존 확률의 하계임을 인증하는 장치; $q_{6600,6600}$은 8.2 국소의 탈출 하계 몫) | 8.2 | $Q^{\mathrm{cf}}$ ([rfc69320]) |
| $s^{\mathrm{env}}(\xi), s^{\mathrm{env}}_{\mathrm W}, s^{\mathrm{env}}_{\mathrm G}$ | 봉투($k$에 무관한 생존 하계 함수: $s_{k+c}(k+1)\ge s^{\mathrm{env}}(\xi_c)$); Jensen 봉투; 탈출 봉투 | 8.2 | $Q^{env}$, $Q^{env}_W$, $Q^{env}_G$ ([r030ffae]; [rfc69320]의 정정판) |
| $\Omega(\xi), \Omega_c$ | 윤곽 함수(상위해를 $\mathfrak E_q=\Psi(q)(1-\Omega(\xi_q))$ 꼴로 잡는 감소 함수)와 그 값 $\Omega(\xi_c)$ | 8.2 | $W$, $W_c$ ([r030ffae], [r5909c9e]) |
| $\Psi^{\mathrm{low}}_{(\varrho)}$ | 갱신함수 하계의 실수 인수 정밀판 $(2\pi)^{-1/2}(2\sqrt\varrho-\mathsf c_\Psi+\frac1{2\sqrt\varrho}-\frac1{24}\varrho^{-3/2})$ | 8.2 | $\Psi_{(r)}$ ([r030ffae]); $\Psi_\flat(r)$ ([rfc69320]) |
| $\mathfrak B_N, \mathfrak B^{\mathrm{low}}(k,\nu)$ | 명제 U의 사전 상계 $s_N(k)\le1/(1+\mathfrak B_N)$의 양과 그 명시 하계 | 8.2 | $B_N$ ([r8456f59]; 용량 $y$ 일반형, [r030ffae] 보고서); $B^{\mathrm{low}}(k,\nu)$ ([r030ffae] 보고서 L342) |
| $\mathsf c_\Psi$ | 갱신함수 하계의 상수 $1.6780525$(명명 상수; $\Psi^{\mathrm{low}}_{(\varrho)}$의 식에 든다; 8.2 `{{8:explicit-bounds}}`) | 8.2 | $C_\Psi$ ([rfc69320]) |
| $\mathsf j_\infty(\xi)$ | Jensen 봉투 지수의 $k\to\infty$ 극한 $\frac43(2\pi)^{-1/2}\xi^{3/2}$ | 8.2 | $B_\infty(y)$ ([rfc69320]) |
| $\mathrm{Bor}_{\le}(q)$ | $\sum_{m\le q}\mathrm{Bor}(m)$ | 8.2 | $S_0(b)$ ([r030ffae]); $S_0(\nu)$ ([r5909c9e]); $\beta(m)$ ([r29c10cd]) |
| $\mathrm{km}_N$ | 명제 U의 사슬 질량 $\sum_{m=k+1}^N\pi_N(m)\,k/m$ | 8.2 | $\kappa_N$ ([r8456f59], [r030ffae]; 6.2의 (Hz) 상수 $\kappa_N$과 다른 양) |
| $\mathrm{Lip}$ | Lipschitz 상수(봉투 표의 셀 검사) | 8.2 | — |
| $\mathfrak c_0$ | 용량 이동 비 $s_N(k-1)/s_N(k)$의 하계(보조정리 `{{8:old-6-30}}`) | 8.3 | $c_0$ ([r030ffae]; 보조정리 $C_0$의 최댓값) |
| $m_{\mathrm{fb}}$ | 되먹임 시작 $\lceil5k/4\rceil+q_{\max}$(크기 변수의 특정값) | 8.4 | $L_0$ ([r030ffae]) |
| $q_{\mathrm{fb}}, q^\circ_{\mathrm{fb}}$ | 되먹임 폭 $\lfloor(3(k-1)/4-q_{\max}-3)/8\rfloor$(정리 B″·B‴; 초과 변수의 특정값)와 정리 B′의 고정값 $300$ | 8.4 | $G$ ([r030ffae]; 두 정의 L241·L191) |
| $\mathfrak R^{\mathrm{low}}_k$ | 띠 정리 조립의 창 합(착지 창 수준 질량들의 합) 하계 | 8.4 | $\hat S_k$ ([r030ffae]) |
| $\mathrm{dup}_m$ | 한 블록 재귀의 중복 몫 | 8.4 | $\mathrm{rem}_L$ ([r030ffae]) |
| $\mathrm{fb}(\theta)$ | 되먹임 인자 $\sum_{i<8}(\theta\,\mathrm{Bor}_\le(q_{\mathrm{fb}}))^i$(되먹임 기하합) | 8.4 | $F(\theta)$ ([r030ffae]) |
| $\mathrm{LB}^{\mathrm{mono}}, \mathrm{LB}^{\mathrm{low}}, \mathrm{LOW}_k$ | 띠 정리 조립의 두 명시 하계와 생존 $1$ 착지 항 | 8.4 | $\rho_{\mathrm{mono}}$, $\rho_{\mathrm{low}}$, $\mathrm{LOW}_k$ ([r030ffae]) |

### 9장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $m_1(k)$ | 증가 시작점(열 $k$의 첫 층에서 행의 증가가 시작되어 끝까지 이어지는 가장 작은 행; 없으면 $2k+1$) | 9.1 | — |
| $P^+_t(k)$ | 빚 뺀 머리 합 $P_t(k)+1/k=\sum_{t^\prime=k+1}^{t}x_{t^\prime}(k)$ | 9.1 | — |
| $\pi_2(t)$ | 크기 $t$ 균등 라벨 나무의 무게중심이 둘일 확률 $[t\text{ 짝수}]\,2\binom{t}{t/2}/2^t$ | 9.1 | 같음 ([r2fe0259], [rae1f209]) |
| $\mathsf H^\ast, \mathsf H^\ast_+$ | 머리 합 조건과 그 정량판 | 9.1 | — |
| $A^{(t)}_N, A^\circ_N, A^\diamond_N$ | 최대 변위 $\le k-1$이고 모든 나무의 크기가 $t$ 이하인 크기 $N$ 숲의 수(생존 숲의 수; 윗첨자는 나무 크기의 문턱값); $A^\circ_N=A^{(k+1)}_N$(짝 없는 문턱 손실의 것), $A^\diamond_N=A^{(k+103)}_N$(덮인 문턱의 것) | 9.2 | — |
| $K_n(m)$ | 병합 핵 $\binom n{m+1}p_{n-1-m}$ | 9.2 | — |
| $\gamma_m$ | 병합 계수 $k(m+1)/(m+1-k)$ | 9.2 | $c_m$ ([rae1f209]) |
| $\pi_n(t_1,t_2)$ | 두 나무 순서쌍의 기대 수 $\mathrm{Bor}(t_1)\mathrm{Bor}(t_2)\mathrm{Bor}(n+1-t_1-t_2)/\mathrm{Bor}(n+1)$ | 9.2 | $\varpi_N(s_1,s_2)$ ([rae1f209]) |
| $\Theta^\circ_n$ | 짝 없는 문턱 손실 $\binom nkk^{k-2}A^\circ_{n-k}$ | 9.2 | — |
| $\mathcal C_n$ | $\mathrm{BV}_n-(\Theta_n-\Theta^\circ_n)$ | 9.2 | $X_n$ ([rae1f209]) |
| $\mathcal Q_m$ | 행별 비 $b^{(2)}_m/(\gamma_m\Theta_m)$ | 9.2 | — |
| $\mathsf B^+$ | 명제 「줄기 더하기 쌍, 벌크」 | 9.2 | — |
| $\mathcal J_1(k),\dots,\mathcal J_4(k)$ | 해석적 행 정리 하계의 네 성분 | 9.3 | $J,J^\prime,Bd,Bd^\prime$ ([rae1f209]) |
| $\mathfrak d_k, \bar{\mathfrak d}_k$ | 조건부 수준 질량의 최댓값 $\max_{k\le N\le2k-1}\mathrm{cl}^-_N$와 그 임의 상계 | 9.3 | $\delta_k$ ([rae1f209]) |
| $\mathfrak K_N, \mathfrak K^{\prime}_N$ | 생존 없는 핵 질량 상계의 양 $\sum_{t=k+2}^N\pi_N(t)k/t$와 그 잘린 판($t\ge k+104$) | 9.3 | $W_0^\prime$ ([rae1f209] L64, [r77e234e] L87); $W_0^{\prime\prime}$ ([rae1f209] L242); [r5909c9e]는 잘린 판을 $W_0^\prime$로 적음 |
| $\mathfrak l_m(t)$ | 착지 무게 $[\pi_m(t)/\pi_m(k)](k/t)$ | 9.3 | $w_m(s)$ ([rae1f209]) |
| $\mathfrak V_m$ | 쌍 보정 흡수의 양 $\sum_{t\ge k}\binom mtb^T_{t,k-1}A_{m-t,k-1}$ | 9.3 | $V_m$ ([rae1f209]) |
| $\mathsf L_\ast(k)$ | 해석적 행 정리의 하계 함수 $\mathcal J_1(k)+\dots+\mathcal J_4(k)$($k$에 비감소; 명명된 상수 함수. $\mathsf L_\ast(6668)=1.206$) | 9.3 | $L_*(k)$ ([rae1f209]) |
| $\mathrm{FL}^{(1)}_m$ | 첫 층 착지 항(행 $m$에서 첫 층 블록 하나가 수준 $k$ 또는 $k-1$에 서고 환경이 살아남는 배치 수) | 9.3 | — |
| $\mathrm{land}_m$ | 착지 비 $\mathrm{FL}^{(1)}_m/\Theta_m$ | 9.3 | $\Phi_m$ ([rae1f209]) |
| $\mathrm{need}_m, (\mathrm R_m)$ | 행 조건 $(\mathrm R_m)$과 그것이 요구하는 양 | 9.3 | — |
| $\mathrm{OB}_m$ | 한 블록 항등식의 몫 $A_{t-1,k}+A_{t-1,k-2}$ 항 | 9.3 | $E_m$ ([rae1f209]) |
| $\mathrm{Pcor}_m, \mathrm{Pcor}^{\pm}_m$ | 쌍 보정과 그 두 조각($\mathrm{Pcor}_m=\mathrm{Pcor}^+_m-\mathrm{Pcor}^-_m$) | 9.3 | $N^\prime_2$, $M_2$ ([rae1f209]) |
| $t^\dagger$ | 자르는 크기(나무 크기 변수의 특정값; 정리 11′) | 9.4 | $S$ ([rb6a2cd0]) |
| $P^{\theta\dagger}(t^\dagger)$ | 자르는 크기까지의 문턱 부분나무 머리 합들의 합 $\sum_{t=k+\nu+1}^{t^\dagger-1}P^\theta_t(k)$(정리 11′의 양) | 9.4 | $W_S$ ([rb6a2cd0]) |
| $P^{\theta}_t(k)$ | 문턱 부분나무 머리 합 $\sum_{t^\prime=k+1}^{t-1}\theta_{t^\prime}(k)$ | 9.4 | $U_k(s)$ ([rb6a2cd0]) |
| $\nu_0(k), \nu_1(k)$ | $\mathcal Y_k\ge0$이 되는 최소 $\nu$; 띠 전체 정리의 문턱(오프셋의 특정값) | 9.4 | — |
| $\varrho^\dagger(t^\dagger)$ | 자르는 크기에서의 무게 증분 로그꼴 하계 $g(t^\dagger-1)-g(n-t^\dagger+1)$(정리 11′의 양) | 9.4 | $r_S$ ([rb6a2cd0]) |
| $\mathcal F_k(\nu), \mathcal F^+_k, \mathcal F^{\mathrm{LP}}_k$ | 띠 안쪽·앞쪽·전체 정리의 판정 함수 | 9.4 | $F_k(\nu)$ ([rb6a2cd0]) |
| $\mathcal Y_k(n), \mathcal Y^{\mathrm{LP}}_k(n), \mathcal Y^\dagger_k(n)$ | 첫 층 선속 하계의 인자(정리 11·11′·11″의 양) | 9.4 | $X_k(n)$, $Y^{LP}_k(n)$, $Y_k$ ([rb6a2cd0]) |
| $\mathsf{FS}(n)$ | 위치 $n$에서 $\mathrm{regen}_n\ge0$이라는 명제 | 9.4 | — |
| $\mathsf h_N$ | 무거운 자리 하계 상수 $\frac32-\frac{47}{24k}+(1-\frac3{2k})\frac{0.307k}{N+1}$ | 9.4 | — |
| $\mathrm{flat}_k(t)$ | 평평한 꼬리 $\sum_{t^\prime=t}^{2k+1}x_{t^\prime}(k)$($k\le t\le2k+1$), $\mathrm{flat}_k(2k+2):=0$ | 9.4 | $T(s)$ ([rb6a2cd0]) |
| $\mathrm{LP}_k(n)$ | 선형 최소화의 값 | 9.4 | — |
| $\mathrm{regen}_n$ | 숲–나무 재생 원천 | 9.4 | $\tilde\sigma_n$ ([r05cf8c9], [rb6a2cd0]) |
| $A^{\diamond,\mathrm{up}}, A^\diamond_{\mathrm{dec}}$ | 덮인 문턱의 상계와 그 감소 부분 | 9.5 | $Q^{up}$, $Q_{dec}$ ([r5909c9e]) |
| $\Psi^{\mathrm{low}}(d)$ | 갱신함수의 칸 하계 $0.3989(2\sqrt d-1.678)$(정수 인수) | 9.5 | — |
| $\mathrm{merge}, \mathrm{merge}^{\mathrm{up}}$ | 덮개 몫(참값)과 그 상계 | 9.5 | — |

### 10장에서 정의하는 기호

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $\varkappa_m$ | 장부 계수 $2$($m\le N$) 또는 $1+(n-m)/k$($m>N$) | 10.1 | $c_m$ ([r3d0856b]) |
| $\mathfrak f_m$ | $1/p$ 장부의 항 $\varkappa_mk\,d_{m,k}/p_m+(2-\mathbf 1\{m>N\})c^{(2)}_m$ | 10.1 | $f_m$ ([r3d0856b], [re71a735]) |
| $\mathfrak L_\nu$ | 문턱 예산 $\sum_{m=N+1}^{2k}[(m-N)d_{m,k}/p_m+c^{(2)}_m]$ | 10.1 | — |
| $\mathfrak T_m$ | 장부 항의 꼬리합 $\sum_{i=m}^{2k}\mathfrak f_i$, $\mathfrak T_{2k+1}:=0$ | 10.1 | $T_m$ ([r3d0856b], [re71a735]) |
| $\mathrm{Bd}^{\Lambda}_\nu$ | 문턱 예산의 중앙 경계항(경계항 가족) | 10.1 | — |
| $m_0$ | 장부 꼬리합 $\mathfrak T_{m_0}$의 시작 크기; 창 안의 $m_0$에 대해 시작 초과는 $q_0=m_0-k$ | 10.2 | — |
| $\omega_m, \omega_y(d), \omega^\sharp_y(d), \tilde\omega(d)$ | 꺾인 무게 $2$($k<m\le N+1$), $2-(m-N)/k$($N+2\le m\le2k$); 결손 좌표의 같은 무게; 가중 무게; 그 변형 | 10.2 | — |
| $\mathrm{Bd}^{\mathrm S}$ | 체류 꼴(명제 S)의 중앙 경계항(경계항 가족) | 10.2 | — |
| $\mathrm{Stays}, \mathrm{Stays}^{\mathrm{vis}}, \mathrm{Stays}_{\mathrm{PM}}, \mathrm{Stays}_X$ | 문턱 뒤 머묾 질량 $2\varsigma_{N+1}(k)+\sum_{m=N+2}^{2k}\omega_m[\varsigma_m(k)+\varsigma_{m-1}(k-1)]$; 그 방문 질량 읽기; 정리 `{{7:old-6-4}}`(벌크 점질량 상계)를 넣은 것; 명제 X의 명시 상계 | 10.2 | `Stays` ([r3d0856b]); `Stays_θ` ([r3d0856b])는 $\mathrm{Stays}^{\mathrm{vis}}$ |
| $\nu_{\min}(k), \bar\nu$ | FLQ 범위의 실제 하한 $\max(103,20001-2k)$; $\nu$의 상한(오프셋의 특정값) | 10.3 | — |
| $\vartheta, \vartheta_0$ | 띠 인자 $2(1+\frac1k)A_{N,k-1}/A_{N,k}-1$(띠), $-1$(벌크); 상수 $(2e^{-0.48}-1)e^{-0.48}$ | 10.3 | $\theta$ ([r3d0856b]); $\theta_0$ ([re71a735] L317) |
| $\mathsf{FLQ}$ | 첫 층 열 값만의 두 부등식 명제(정의 `{{10:old-8-9}}`) | 10.3 | — |
| $s^{\mathrm W}_q(m,y)$ | 착지 창의 생존 상계(명제 W) | 10.4 | $W_b$ ([r3d0856b]) |
| $\pi^{\mathrm{two}}_N$ | 크기 $N-1$ 숲이 크기 $k$, $\nu-1$의 두 나무뿐일 확률 $\binom{N-1}kk^{k-1}(\nu-1)^{\nu-2}/N^{N-2}=\mathrm{Bor}(k)\mathrm{Bor}(\nu-1)/(e\,\mathrm{Bor}(k+\nu))$ | 10.4 | $\lambda$ ([r3d0856b] L343, [re71a735] L318) |
| $\vartheta_{\mathrm{lb}}$ | 띠 인자의 하계 $2(1+\frac1k)^{1-\nu}-1$ | 10.4 | $\theta_{lb}$ ([r3d0856b]) |
| $\mathsf r_\ast$ | 벌크 상수(명제 T 증명) | 10.4 | $\rho^*$ ([r3d0856b]) |
| $\mathrm{Bd}^{\mathrm T}(k,\nu)$ | 명제 T의 경계항 상계(경계항 가족) | 10.4 | $BD(k,\nu)$ ([r3d0856b], [re71a735]) |
| $\mathrm{DDL}(k)$ | 대각선 손실의 상계 $2\cdot50.62/\sqrt{k-1}$(명제 T의 것) | 10.4 | — |
| $\mathrm{Stays}^{\mathrm{up}}(k,\nu), \mathrm{Stays}^{\mathrm{up}}_{\mathrm{new}}, \mathrm{Stays}^{\mathrm{up}}_{\mathrm W}, \mathrm{Stays}^{\mathrm{up}}(k;\bar\nu), \mathrm{Stays}^{\mathrm{up}}_F$ | 머묾 질량의 상계들: 명제 T의 상계(띠 식 $4-3s^{\mathrm F}-\mathrm{Bd}^{\mathrm T}-\mathrm{DDL}+\vartheta_{\mathrm{lb}}(1+\frac1{k-1})^{-(\nu-1)}$, 벌크 식 $4-3s^{\mathrm F}-\mathrm{Bd}^{\mathrm T}-\mathrm{DDL}-e^{3/(2k)}\mathsf r_\ast$); 균일 증명의 새 상계; $3s^{\mathrm F}$를 $3\min(s^{\mathrm F},s^{\mathrm W}_q)$로 바꾼 값; $\nu$에 무관한 상계; 가족별 상계 | 10.4 | $S^*(k,\nu)$, $S^*_W$ ([r3d0856b]); $S^*_{new}$, $U(k; \bar\nu)$, $U_F(k)$ ([re71a735]) |
| $d^\star$ | 나눔점 $\lfloor0.6Y\rfloor$($Y\in\{k-1,k\}$는 열의 수준; 결손의 특정값; 명제 U·X) | 10.5 | $D_1=\lfloor0.6c\rfloor$ ([re71a735] L274; $c\to Y$); [r030ffae]의 $D_1$은 다른 양 |
| $k_0, k^\ast$ | 가족이 비지 않는 가장 작은 $k$(가족 시작점); 단계 (b)의 최소 열(용량의 특정값) | 10.5 | — |
| $y_0$ | 기준 용량 $k$(용량 변수의 특정값; 얼린 법칙의 용량) | 10.5 | — |
| $\mathcal G_y(q), \mathcal G^y(q)$ | 얼린 법칙 아래 수준 $q$의 생존 가중 방문 측도 $\mathbb E^{y_0}[\Pi_j(y); \,q_j=q]$; $\Pr^y$ 자신의 판 | 10.5 | $G_y(b)$ ([re71a735]) |
| $\mathfrak A_j, \mathfrak A^{\mathrm{crit}}_d(q)$ | 경로의 면적 $\sum_{i\le j}q_i/(y_0+1+q_i)$; 임계 면적 | 10.5 | — |
| $\mathfrak H_d$ | 정리 `{{10:old-8-22}}`의 수준별 손실 합(결손 $d$의 몫) | 10.5 | — |
| $\mathfrak h_y(q)$ | h-변환 함수 $\mathrm{Bor}(y+q)/\mathrm{Bor}(y_0+q)$ | 10.5 | $h_y$ ([re71a735]) |
| $\mathfrak k_d(q)$ | 젊은 사슬 정리의 계수 $e^{\mathrm{inc}^-_q}+e^{-\mathrm{inc}^+_q}-2$ | 10.5 | — |
| $\mathfrak s^{\mathrm{fr}}_d(y)$ | 얼린 생존 $\mathbb E^{y_0}[\Pi_J(y)]$ | 10.5 | — |
| $\mathfrak s^{\mathrm{up}}_d(y)$ | 첫 층 생존의 상계(자유 Borel 재귀의 상해; 정리 S′) | 10.5 | 없음([r6b37c7e]의 $\Phi_C(a)$는 다른 양) |
| $\mathsf m_{\mathrm S}$ | 상해 상수 $1.15$ 또는 $1.2$(정리 S′) | 10.5 | — |
| $\mathrm{DDL}_2(k), \mathrm{DDL}^\natural(k)$ | 대각선 손실의 명시 상계 $2\sum_d\mathfrak H_d$와 그 닫힌 꼴(감소함) | 10.5 | $DDL_2$, $CF^\natural$ ([re71a735]) |
| $\mathrm{inc}^{\pm}_q$ | 기울임 증분 $g(y_0+d)-g(y_0+q)$, $g(y_0-1+d)-g(y_0-1+q)$ | 10.5 | $u_b$, $v_b$ ([re71a735]) |
| $\mathrm{PM}_y(d)$ | 점질량 읽기 상계 $16.54(y+1+\frac{d-1}3)(d-1)^{-5/2}$ | 10.5 | $PM_c(d)$ ([re71a735]); $16.54(k+a/3)a^{-5/2}$ ([r7e03176]; $k=y+1$, $a=d-1$) |
| $\mathrm{Res}_d$ | 기울임 나머지(얼린 볼록 몫을 뺀 나머지) | 10.5 | — |
| $\mathrm{tr}_y(q)$ | 기울임 비 $\mathfrak h_y(q)/\mathfrak h_y(d)-1$ | 10.5 | — |
| $\mathfrak Q(y,\xi)$ | 두 조각 적분 꼴의 점질량 하계 | 10.6 | $Q_2(y,x)$ ([re71a735]) |
| $\mathfrak s^{\mathrm{low}}_d(y)$ | 착지 창의 생존 하계(보조정리 `{{10:old-8-30}}`) | 10.6 | — |
| $\mathsf f_1$ | 극한 결손 법칙의 첫 계수 $4/(3\sqrt{2\pi})=0.53192\ldots$ | 10.6 | $I_1$ ([re71a735]) |

