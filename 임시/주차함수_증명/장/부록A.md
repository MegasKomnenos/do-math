## 부록 A. 기호표

1장부터 8장까지 본문에 실제로 나오는 기호를 처음 정의된 절의 순서로 적는다. 열은 기호, 뜻, 처음 정의된 절, 그리고 기록이 다른 글자를 쓰는 경우 그 글자다. 같은 글자가 다른 뜻으로 쓰이는 자리는 한 행에 함께 적고, 그 구별을 본문의 어느 절이 밝히는지도 적는다. 한 증명 안에서만 쓰이고 그 증명 밖으로 나오지 않는 기호는 진술 단위로 묶어 적는다. 9장은 새 기호를 두지 않되, 9.6절이 형식 결과의 진술을 위해 한 줄로 정의한 $\mathcal J_y$만 끝에 적는다.

### 1장과 2장

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $n$ | 차와 자리의 수, 곧 행의 크기. 7장과 8장에서는 둘째 층 행 $n=2k+\nu$의 지표 | 1.1 | 기록 [r3d0856b]·[re71a735]는 행을 $t$로 적는다(8.1절에 언급) |
| $a_i$, $s_i$, $d_i$ | 차 $i$의 선호 자리, 실제 자리, 변위 $s_i-a_i$. 2.1절부터 $d_i$는 자리 $i$에 선 차의 변위. 2.11절과 8장의 $a_i$는 무거운 사슬의 초과 $S_i-y$이며 2.11절에 구별 문장이 있다 | 1.1, 1.2, 2.1, 2.11 | |
| $\mathrm{PF}_n$, $p_n$ | 길이 $n$ 주차함수의 집합, 그 개수 $(n+1)^{n-1}$ | 1.1 | |
| $M(\alpha)$, $M_n$ | 주차함수 $\alpha$의 최대 변위; 균등 주차함수의 최대 변위 | 1.2, 2.3 | |
| $b_{n,\ell}$, $A_{n,\ell}$ | 최대 변위가 $\ell$인 개수, $\ell$ 이하인 개수($A_{0,\ell}=1$, $A_{n,-1}=0$) | 1.3 | |
| 행, 열, 수준 | $n$을 고정한 수열 $b_{n,0},\dots,b_{n,n-1}$; $\ell$을 고정한 수열; 최대 변위의 값 $\ell$. 3.4절부터 「열 $k$」는 용량 $k$의 비교 $b_{n,k-1}$ 대 $b_{n,k}$가 놓인 열 | 1.3, 3.4 | |
| $P$, $P(n)$ | 문제 P(모든 행이 단봉이라는 명제), 그 행별 명제 | 1.3, 4.1 | |
| $m$ | 행의 한가운데 첨자 $\lceil n/2\rceil$(1.4절, 4장); 5.2절에서는 꼬리 지표 $n-k$; 5.5절과 6·7·8장에서는 숲(행)이나 블록의 크기. 각 자리에 구별 문장이 있다 | 1.4 | |
| $k$ | 열의 용량 $\ell+1$, 곧 비교 $b_{n,k-1}$ 대 $b_{n,k}$의 좌표 | 1.4(앞당겨 씀), 2.6 | |
| $\sigma$, $t_i$, $h_i$ | 결과 순열, 자리 $i$의 왼쪽에서 가장 가까운 큰 차의 자리, 선호 용량 $i-t_i$. 6.7절의 머묾 질량 $\sigma_m(\ell)$, 7.3절의 재생 원천 $\tilde\sigma_n$과 구별 | 2.1 | |
| $C_\sigma(\ell)$ | 섬유의 누적 개수 $\prod_i\min(h_i,\ell+1)$ | 2.1 | |
| $J$, $U_J$ | 마지막 차가 선 자리 $J+1$, 그 변위. 2.5절의 $J$는 최대 나무 사슬에서 문턱을 넘는 항의 수(2.5절에 구별 문장) | 2.3, 2.5 | |
| $F_\ell(x)$, $H_\ell$, $Q_\ell$ | 누적 개수의 지수 생성함수, 그 역수가 만족하는 미분방정식의 다항식, 그 적분. 3.1절의 극한 분포 $F$, 2.5절의 문턱 자리 수 $H_k$, 4.2절의 명제 $Q$와 구별. 2.8절의 분포함수 $F_m(x)$와 7.3절의 판정 함수 $\mathcal F_k(\nu)$에는 구별 문장이 있다 | 2.3 | 6.3절의 $Q_{k-1}$을 기록은 $\Pi_k$로 적는다 |
| $I_v$, $s_v$, $H(F)$ | 꼭짓점 $v$의 국소 역전 수, 부분나무 크기, 숲 $F$의 최대 국소 역전 수 | 2.4 | |
| $T_\ell(z)$, $\mathcal N_\ell(s)$ | 허용 나무 생성함수 $\sum_s\mathcal N_\ell(s)z^s/s!$($F_\ell=\exp T_\ell$); 크기 $s$의 허용 나무 수 $\min(s,\ell+1)A_{s-1,\ell}$ | 2.4 | $c_N(\kappa)=\mathcal N_{\kappa-1}(N)$ ([r4868e30]), $T_\ell(s)$ ([r5909c9e]) |
| $\pi_N(m)$, $G$ | 자유 균등 숲에서 크기 $m$인 나무 수의 기댓값 $\mathrm{Bor}(m)\mathrm{Bor}(N+1-m)/\mathrm{Bor}(N+1)$($m>N/2$에서 가장 큰 나무 핵 $\Pr_N(G=m)$); 가장 큰 나무의 크기. 7.1절의 $\pi_N(s_1,s_2)$는 크기 $(s_1,s_2)$인 두 나무 순서쌍의 기대 수 | 2.5, 7.1 | $\varpi_N(s)$, $\varpi_N(s_1,s_2)$ ([rae1f209], [r5909c9e], [r030ffae]) |
| $\pi^0_N(y)$ | 조각남 확률 $\Pr_N(G\le y)$. 7장은 $\pi^0_N(k)$를 환경이 조각나 있을 확률이라 부른다 | 2.5 | $P_0(N)$ ([rae1f209], [r5909c9e]) |
| $f_N(y)$ | 모든 나무의 크기가 $y$ 이하인 $[N]$ 위 뿌리 숲의 수. 3.1절의 극한 밀도 $f$와 구별 | 2.5 | |
| $S_i$, $J$ | 최대 나무 사슬 $S_1>S_2>\cdots$, 문턱을 넘는 항의 수. 2.5절의 명제 {{old:명제 8.1}} 블록은 기록 [r88bed8a]를 따라 첫 항을 $S_0$으로 적는다(구별 문장). 2.11절의 보행 부분합은 $R_j$로 적어 구별 | 2.5 | |
| $Z_k$, $H_k$, $\mathfrak v_k(Z,H)$ | 결과 순열에서 용량이 $k$를 넘는 자리 수, 용량이 $k$인 자리 수, 섬유 부호식 $(1+1/k)^Z+(1-1/k)^{Z+H}-2$. 2.7절과 6.1절이 되가리킨다. 4.3절의 Borel 꼬리 $H_k(s)$와 구별 | 2.5 | |
| $\mathrm{Bor}(k)$, $\tau_k$, $BT(z,D)$ | Borel 질량 $e^{-k}k^{k-1}/k!$($\tau_k=\mathrm{Bor}(k)$); Borel–Tanner 질량. 7·8장은 $\mathrm{Bor}$만 쓴다 | 2.6, 5.5.6 | $\beta_j$ ([r4868e30]) |
| $\Pr_B$, $g_N(c)$ | 임계 볼츠만 법칙; 크기 $N$의 균등 나무가 용량 $c$ 아래 살아남을 확률(5.5.1절의 $g_t(Y)$와 같은 양) | 2.6 | $\chi(g)$, $\chi^+(g)$ ([r030ffae]; 6.9절에 언급) |
| $s_m(y)$ | 생존 확률 $A_{m,y-1}/p_m=\Pr_m(M\le y-1)$. 5.5절은 같은 양을 $u_m(Y)$로도 적으며 5.5.1절이 $u_m=s_m$을 밝힌다 | 2.6 | $F_m(y)$ ([r317d678], [r845b205]); $F_m(\ell)=\Pr_m(M\le\ell)=s_m(\ell+1)$ ([r3d0856b], [re71a735]; 첨자가 하나 어긋남); $s_N$, $q_N$, $t_N$은 $s_N(k)$, $s_N(k+1)$, $s_N(k-1)$ ([rae1f209], [r030ffae], [r5909c9e]); $\mathfrak s_N$ ([rb6a2cd0]) |
| $c_m(Y)$ | 수준 질량 $b_{m,Y}/p_m=\Pr_m(M=Y)$(수준 확률·점질량이라고도 부른다). 6.2절의 상수 $c_k$, 6.7절의 V-core 상수 $c(k)$와 구별 | 2.6 | $\pi_m(\ell)$ ([r3d0856b], [re71a735]); $r_N$, $r'_N$은 $c_N(k)$, $c_N(k-1)$ ([rae1f209], [r030ffae]); $c^+_m$, $c^-_m$ ([r5909c9e]); $V_c(d)=c_{c+d}(c)$ ([re71a735]) |
| $g(x)$ | $(x-1)\log(1+1/x)$, $x\ge1$에서 엄격 증가; $\mathrm{Bor}(s+1)/\mathrm{Bor}(s)=e^{g(s)-1}$. 2.9절의 $g_k(a)$, 5.5.6절의 $\mathfrak g(\zeta)$, 6.5절의 $g^\pm(s)$와 구별 | 2.6 | $g(j)$ ([rb6a2cd0]) |
| $\mathscr K_{n,k}(y)$ | 얼린 용량 다항식 | 2.7 | |
| $K_M$, $E_{n,k}$, $E2_{n,k}$, $B_{n,m}$ | 최대값 동률 수, 짝수 동률 수, 두 차 동률 수, 막힌 목록 수. 7.1절의 병합 핵 $K_n(m)$, 8.6절의 $\mathcal K(\tau)$에는 구별 문장이 있다 | 2.7 | |
| $e_n$, $J_n(c)$ | $\mathscr K''_{n,k}(k)=2E2_{n,k}$; 경계 다항식. 6.4절은 $J_n(k-1)$을 참 경계 다항식이라 부른다 | 2.7 | 기록 [r475ada3]은 $J_n(k-1)$을 「표지」라 부른다(6.4절) |
| $d_{n,k}$ | 한 칸 차분 $b_{n,k}-b_{n,k-1}$ | 2.7 | |
| (SM), (DM0), (SC) | 크기 결합의 세 부등식 $s_{N+1}(y)\le s_N(y)$, $s_{m-1}(k)\le s_m(k+1)$, $A_{N,\ell}/p_N\le A_{N+1,\ell+1}/p_{N+1}$. 8.5절의 상해 조건 꼬리표 (SS)와 구별 문장 | 2.8 | 기록 [re71a735]는 (SS)를 (SC)로 적는다 |
| $\Pi_m(j)$ | 마지막 차 자리 법칙 $j\binom{m-1}{j-1}p_{j-1}p_{m-j}/p_m$. 6.6절은 같은 법칙을 $\Pi_t(j)$로 적는다. 2.9절의 $\Pi_T$, 6.7절의 $\Pi_j(y)$와 구별 문장 | 2.8 | |
| $x_N(k)$, $M^T_N$ | 나무 곡률 $\Pr(M^T_N=k)-\Pr(M^T_N=k-1)$; 크기 $N$ 균등 뿌리 나무의 최대 변위. 5.5.1절의 나무 차분 $x_t(y)$, 6.7절의 $\delta_N/N^{N-1}$과 같은 양 | 2.9 | |
| $\theta_N(k)$ | 문턱 부분나무 기대 수 $\binom Nk k^{k-1}(N-k)^{N-k}/N^{N-1}$. 7장의 $\theta'$, 8장의 띠 인자 $\vartheta$와 구별 | 2.9 | |
| $N_T$, $H_T$, $\Pi_T$, $G_k(a,h)$, $g_k(a)$ | 나무 $T$를 고정한 양들(무거운 꼭짓점 수, 문턱 자리 수, 생존 곱)과 보조정리 {{new:2:tree-conditional}}의 함수 | 2.9 | |
| $\mathrm{Ren}(j)$, $\Psi(b)$, $B(x)$ | 갱신 방문 핵 $j^je^{-j}/j!$($\mathrm{Ren}(0)=1$), Borel 갱신함수 $\sum_{r=1}^b\mathrm{Ren}(r)$, Borel 생성함수. 5.5.9절의 $\Psi$는 다른 양(구별 문장) | 2.9 | $c_j$ ([r4868e30]), $u(j)$ ([r030ffae], [re71a735]); $U(D)=1+\Psi(D)$ ([r4868e30]) |
| $P_s(k)$ | 머리 합 $\sum_{t=k}^sx_t(k)$(6.8절이 되가리킨다). 6.5절의 뿌리 자리 법칙 $P_m(j)$와 구별 문장 | 2.9 | |
| $\Theta_n$, $FL^{(5)}_n$, $BV_n$, $KD_n$, $PAIR_n$ | 다섯 조각: 문턱 나무 손실, 첫 층 선속, 줄기 이득, 둘째 층 상속, 두 수준 블록 쌍 | 2.10 | 기록은 $FL^{(5)}_n$을 $FL_n$으로 적는다 |
| $U$, $V$, $u_s$, $v_s$ | 급수 $T_k-T_{k-1}$, $T_{k-1}-T_{k-2}$와 그 계수. 4.3절의 함수 $V(t)$, 2.7절의 $U$와 구별 문장 | 2.10 | |
| $\delta_s$ | 다섯 조각의 계수 $\min(s,k+1)A_{s-1,k}-2\min(s,k)A_{s-1,k-1}+\min(s,k-1)A_{s-1,k-2}$; $s\ge k+1$에서 6.7절의 나무 행 차분 $\delta_{m+1}$과 같다 | 2.10 | |
| $b^{(2)}_m$, $c^{(2)}_m$ | 두 수준 개수 $b_{m,k}+b_{m,k-1}$, 두 수준 질량 $c_m(k)+c_m(k-1)$ | 2.10 | $L_m$, $\ell_N$ ([rae1f209]); $s_m$ ([r3d0856b]) |
| $Y_i$, $R_j$, $H_B(r)$ | 독립 Borel 변수, 자유 Borel 보행의 부분합, Borel 갱신 집합 $\{R_j\le r\}$ | 2.11 | |
| $\delta$, $p^y(a\to c)$, $P^y$, $\tau_\delta(c)$ | 무거운 사슬의 시작 초과 $N+1-y$, 초과 $a$에서 $c$로 내려갈 확률, 용량 $y$의 사슬 법칙, 기울임 인자 $\mathrm{Bor}(y+c)/\mathrm{Bor}(y+\delta)$. 2.10절의 $\delta_s$, 2.6절의 $\tau_k$와 구별 | 2.11 | |

### 3장과 4장

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $X_n$, $X$, $f$, $F$, $S$, $m_0$ | 정규화 결손 $(n+1-M_n)/(n+1)^{2/3}$, 그 극한, 극한 밀도·분포·생존함수, 최빈점 $0.5996$. 7.3절의 $\mathcal X_n$, 8.5절의 $\mathsf X$와 구별 문장 | 3.1($m_0$는 3.2) | |
| $\mathcal B$ | 브라운 누적 최댓값의 넓이 | 3.1 | |
| $\lambda$ | $k/n$. 5.5절에서는 $y/n$(같은 뜻); 7.6절의 $\lambda=k/N$에는 구별 문장이 있다 | 3.4 | $\lambda_1(m)=k/(m+1-k)$ ([rae1f209]; 7.1절) |
| 층, $r$번째 층 | $1/(r+1)\le\lambda<1/r$. 5.2절의 꼬리 좌표 $r$과 구별 문장 | 3.4 | |
| $t$ | 중앙 창 좌표 $(n-2k)/k^{2/3}$. 2.1절의 $t_i$, 6.5·6.8절의 행 지표 $t$와 구별 문장 | 3.4 | |
| $x$, $\hat x$ | 임계 창 좌표 $(n-k)/n^{2/3}$, $(n-\ell)(\ell+1)^{-2/3}$. 7.4절의 $\xi$, 8.1절의 $\zeta$, 8.6절의 $\chi$와 구별 | 3.4 | |
| $G_n$ | 크기 $n$ 균등 뿌리 숲의 가장 큰 나무 크기(6.9절의 $G_N$) | 3.4 | |
| $L,T,C,R$; $P_L,P_X,P_C,P_R$ | 네 위치쌍 명제(행별)와 그 이름 붙은 명제: 왼쪽 내부, 횡단, 중앙 틈, 오른쪽 내부 | 4.1 | |
| $\delta_n$ | 중앙 차분 $b_{n,m}-b_{n,m-1}$ | 4.3 | |
| $LH$, $LH^+$ | 왼쪽 절반의 증가, 각각 $b_{n,m-1}$까지와 $b_{n,m}$까지 | 4.1 | |
| $Q$, $Q_L$, $Q_R$ | 조건부 로그오목성(절 제목은 감소 뒤의 로그오목성)과 그 두 반쪽. 6.9절의 $Q^{\mathrm{low}}_c$, $Q^{\mathrm{env}}$와 구별 문장 | 4.2 | |
| $S_{n,k}$, $S_R$, $B_\pm$, $\Gamma_d$, $(G)_d$ | 경계 응답 부등식과 그 명제, 두 경계항(경계 응답), 경계 응답 다항식, 합 지표 $d$에 따른 조각(원천별 비교) | 4.2 | |
| $H_k(s)$ | Borel 꼬리: 모수 $s$의 Borel 분포에서 질량이 $k$를 넘는 부분 | 4.3 | |
| $\mathcal A_{k,n}$, $\mathcal M_r$, $\mathcal I_k$, $I$, $V(t)$, $W_j$, $\mathcal H_j$, $\mathcal D(\beta)$, $\Phi$ | 중앙 틈 증명의 국소 기호. 7.4절의 $\mathcal I_i(k)$, 7.2절의 $\Phi_m$, 7.3절의 $\mathcal H^\theta_k(s)$는 다른 양 | 4.3 | |
| $N_k$, $N_\infty$ | 4.3절 중앙 틈 증명의 정규화 상수 $N_k=\frac{n!}{p_n}\cdot(\dots)$와 그 극한 $N_\infty=2/\sqrt\pi$. 6.2절의 열별 증가 문턱 $N_k$, 정리 {{old:정리 3.4}}의 비명시 문턱 $N_0$과 다른 양(구별 문장은 4.3절) | 4.3 | 기록 [rce3dc75]는 극한을 $N_0$으로 적음 |

### 5장

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $a_n(c)$, $\beta_n(c)$ | C50 열 재귀의 생존 확률과 열 값 | 5.1 | |
| $r$, $\mathfrak m(n)$ | 꼬리 좌표 $n-\ell-1$; 명시적 꼬리 덮개의 길이 | 5.2 | 기록 [ra4c01fc]는 $r=n-c$를 $Y$로 적는다(5.4절) |
| $K_r(n)$, $\kappa_{r,a}$, $\Pi_{m,d}(u)$, $\mathscr D_n(r)$ | 5.2절의 국소 기호 | 5.2 | |
| $\xi$ (5.2절) | Bernstein 전개의 변수 $r^{3/2}/n=\tfrac{16}{25}+\tfrac{\xi}{100}$(국소). 6.9절부터의 창 좌표 $\xi$와 다른 뜻 | 5.2 | |
| $r_0(n)$ | 진입 지표 | 5.3 | |
| $W$, $W^\sharp$, $X$ | 오른쪽 벌크 증가, 임계 창 잔여, 두 항 부등식. 6.9절의 시험 함수 $W(\xi)$, 6.2절의 $W_L$과 구별 문장 | 5.3, 5.4 | |
| $y$, $Y$ | 문턱 좌표 $\ell+1$ | 5.5.1 | |
| $u_m(Y)$, $c_m(Y)$, $x_t(y)$, $g_t(Y)$ | 생존 확률($=s_m(Y)$), 수준 질량(2.6절), 나무 차분(2.9절의 나무 곡률), 크기 $t$ 나무의 생존(2.6절의 $g_N(c)$) | 5.5.1 | |
| $t_0(y)$, $\mathrm{IH}(n,y)$, $\mathrm{src}_m$ | 이음 행, 귀납 가정, 원천 항. 6.5절의 블록 원천 $\mathrm{src}_k(m)$, 6.9절의 $\mathrm{Src}_b$와 구별 | 5.5.2 | |
| $\mathcal T_s(y)$, $D2S_n(y)$ | 꼬리합, 기저량. 6.8절의 표시 나무 무게 $\mathcal T_n(t)$와 구별 문장(6.8절, 7.3절) | 5.5.2 | |
| $POS_0$, $WIN_0$, $\mathcal E$, $top$ | (R₀)의 항들과 보정 | 5.5.2, 5.5.4 | |
| $\Lambda_w$, $s_0$, $C_E$ | 창 질량과 그 균일 하계 $0.71216$; 열 1차 모멘트의 균일 상수 $7.7148$. 8.1절의 문턱 예산 $\Lambda_\nu$와 구별 문장 | 5.5.6, 5.5.8 | |
| $Lc(\ell,r)$, $\mathfrak g(\zeta)$ | 창 열 값의 닫힌 꼴 하계; 정리 {{old:정리 5.32}}의 피적분함수(문단 안 기호) | 5.5.6 | $g$ ([r8a9b11e]) |
| $\zeta$, $\kappa$, $h$ (5.5.6절) | 해석적 사슬의 척도 변수 $z/\ell^{1/3}$, $t/\ell^{2/3}$, $\ell^{-1/3}$. 5.5.8절·7.4절·8.8절의 $\zeta(\cdot)$는 Riemann 제타 함수(각 자리에 구별 문장) | 5.5.6 | |
| $\varphi_1(\lambda)$ | $(2\pi)^{-1/2}(\lambda(1-\lambda))^{-3/2}$ | 5.5.10 | |
| $\mathrm{Main}_D$, $\mathrm{First}_D$, $\mathrm{Second}_D$, $\mathrm{Dg}_D$, $\mathrm{Rem}_D$, $\mathrm{arc}_r$, $N_k$, $B_k$, $N_n$, $\eta$, $Q_c$, $\mathcal E$ | 정리 {{old:정리 5.39}} 증명의 국소 기호: $k^{5/2}c_D$의 네 주항과 나머지, 호 적분의 오차, $N_k=N_nk^{-3/2}$(6장의 증가 문턱 $N_k$와 무관함을 그 자리에 적음), $B_k=\tau_kN_n$, 셋째 차수 이상의 나머지(5.5절의 $\mathcal E$와 다른 양) | 5.6 | |

### 6장

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $\nu_{n,k}$, $T_k$ | 용량 가중 결과 순열 법칙, $Z_k(Z_k-1)-kH_k$. 8.1절의 $\mathfrak T_m$과 글자체로 구별 | 6.1 | |
| $\mu_n(k)$ | 상대 둘째 차분 | 6.1 | |
| $\mathcal A_n(y)$, Conv, Kink | 실수 용량 보간과 볼록–꺾임 분해 | 6.1 | |
| $LM$, $LM^{\flat\flat}$ | 왼쪽 모멘트 명제와 그 축소(왼쪽 모멘트 핵) | 6.1, 6.4 | |
| $W_L$, $W_L^\flat$ | 왼쪽 잔여 증가와 그 축소 | 6.2 | |
| $N^\sharp_k$, $N^\flat_k$, $\tilde N_k$, $N_k$, $N^\circ_k$ | 열별 증가 문턱들. 7·8장의 $N=n-k$와 구별 | 6.1–6.3 | |
| $\mathfrak P_k(n)$, $c_k$ | 문턱 자리 밀도 $\mathbb E[kH_k]/n$; 상수 $(k/(k+1))^{k-1}$ | 6.2 | |
| $\mathrm{Hyp}(n,a,r)$, $Y_r$ | 정리 {{old:정리 6.6}} 증명의 국소 기호: 초기하 분포와 상위 $r$개 순위 가운데 아래 닫힌 집합에 속한 수 | 6.2 | |
| $\rho_k$, $u_l$, $X'$ | 열 $k$의 극, 극 정규화 갱신열, 유한 크기 전달 명제. 6.7절의 $\rho(s)$, 7.3절의 $\varrho_s$, 8.4절의 $\varrho^*$와 구별 문장 | 6.3 | |
| $\nu=n-2k$, $\mathcal W_M$, $\mathcal W^{(>102)}$ | 중앙 왼쪽 오프셋, 모멘트 창, 왼쪽 창 | 6.4, 6.5 | |
| $P_m(j)$, $\varphi_m(j)$, $\mathrm{src}_k(m)$, $(\star)(t)$, $g^\pm(s)$, $r_s$, $\varepsilon_j$, $L$, $R$ | 뿌리 자리 법칙, 원천 함수, 블록 원천, 한 걸음 양, 첫째 차분 비, $d_{s,k}/A_s$, 무거운 뿌리 지시, 좌우 자식 블록의 크기. 8장은 한 걸음 양을 $(\star)(n)$으로 적는다 | 6.5 | 기록 [r3d0856b]은 제한 성장비를 $r_N$으로 적는데 이 글의 $r_s$와 겹쳐 $\mathfrak r_N$으로 바꾸었다(8.1절) |
| $Q^\star$, $Q^\star_2$, $\mathrm{FL}_k$, $\mathrm{FLlin}_k$ | 한 걸음 판정 명제와 그 둘째 층 판, 첫 층 상속과 그 선형 몫 | 6.5, 6.6, 6.8 | |
| $h_m$ (6.6절) | 크기 방향 생존 위험률 $1-s_{m+1}/s_m$(이 절 안의 기호; 6.9절의 $\mathrm{hz}_k(m)$과 같은 양). 2.1절의 $h_i$와 무관 | 6.6 | |
| $\delta_{m+1}$, $v_m$, $V_m$, $\tilde U(k)$, $U_k(L)$ | 나무 행 차분과 그 꼬리합들. 7.2절의 $\mathcal V_m$과 글자체로 구별 | 6.7 | |
| UL, V, V*, UL♭, FC, $\varphi^\flat_k$, $D_k$ | 첫 층 꼬리합 판정들(볼츠만, 확률, 임계 기울임, 평평), 평평한 핵 명제, 평평한 핵 $1+kD_k$, 첫 층 기저 | 6.7 | |
| $c(k)$, $\tilde g(k)$, $c'_k$, $\alpha_k$ | V-core 상수와 그 성분; $\Upsilon_k$의 상계 함수 $\tilde g(k)$ | 6.7 | $g(k)$ ([r7e03176]) |
| $\sigma_m(\ell)$ | 머묾 질량 $s_{m+1}(\ell+1)-s_m(\ell)$: 크기 $m\to m+1$에서 최대 변위가 수준 $\ell$에 머무는 몫 | 6.7 | $\sigma_n(\ell)$ ([r3d0856b]; 이 글의 $\sigma_n(\ell+1)$, 첨자가 하나 어긋남); $W^{(\ell)}_n=\sigma_{n-1}(\ell)$ ([r3d0856b]); $W_c(d)=\sigma_{c+d-1}(c)$ ([re71a735]) |
| $DD(m,y)$ | 대각선 둘째 차분 $(y+2)s_{m+2}(y+2)-2(y+1)s_{m+1}(y+1)+ys_m(y)$ | 6.7 | $DD_m=DD(m-1,k-1)$ ([re71a735], [r3d0856b]; 8.2절) |
| $\mathrm{Bd}_k$ | 정리 {{old:정리 6.18}} 증명의 경계항. 8.2절의 $\mathrm{Bd}^S$, 8.1절의 $\mathrm{Bd}_\nu$와 구별 문장 | 6.7 | |
| $\mathfrak X_d(y)$, $\mathfrak X^0_d$, $\mathfrak X^1_d$ | $y\Pr_{y+d-1}(M\ge y)$와 그 두 분해항 | 6.7 | |
| $a_j$, $\Pi_j(y)$, $r_j(y)$, $K^0(d)$, $K^{tilt}(d)$, $\rho(s)$ | 정리 {{old:정리 6.18}} 증명의 양: 사슬 초과, 생존 곱, 기울임 인자, 두 상수, 한 칸 비 $\mathrm{Bor}(s)/\mathrm{Bor}(s+1)$ | 6.7 | |
| $\mathrm{Left}_t$, $w_m$, $N_{thr}$, $\mathrm{Quad}$, $\mathrm{Stem}$, $KD'_t$, $h(m)$ | 둘째 층 한 걸음 항등식의 항들: 왼쪽 항, 분할 무게 $\binom{t-1}mp_mA_{t-1-m,k-1}/A_{t,k-1}$, 문턱 단위, 이차 몫, 줄기, 상속 몫, 성장률 $(1+\tfrac1{m+1})^m$ | 6.8 | |
| $LRP_2$, $\mathcal R_2$ | 둘째 층 한 칸 비교, 실질 잔여 | 6.8 | |
| $Q_s(k)$, $m_1(k)$, $\Upsilon_k$, $\hat\Upsilon_k$ | 빚 뺀 머리 합, 증가 시작점, 상수 $k(k-1)b_{2k,k-1}/((2k+1)p_{2k})$와 그 상계 $(k-1)\tilde g(k)/(2k+1)$ | 6.8 | |
| $\mathcal T_n(t)$, $\tilde\pi_n(t)$ | 표시 나무 무게 $\binom ntt^{t-1}A_{n-t,k-1}$(기록은 환경 무게라고도 부른다), 그 정규화 | 6.8 | $\varpi_n(s)$ ([rb6a2cd0], [r4868e30]) |
| $H^*$, $H^*_+$ | 머리 합 조건과 그 정량판 | 6.8 | |
| $\rho^{\mathrm{thr}}_k$, $H$, $\Pi$, $\tau_h$, $h_0$ | 정리 {{old:정리 6.20}} 증명의 국소 기호(생존비, 사슬 원소 수, 생존 곱). 8.4절이 같은 $H$, $\Pi$를 다시 쓴다 | 6.8 | $\rho_k$ ([r317d678]) |
| $W(\xi)$, $\xi$, $\xi_c$ | 정리 {{new:6:theorem-W}}의 시험 함수(감소하는 $C^1$ 함수), 창 좌표 $b/k^{2/3}$, $c/k^{2/3}$. 7.4절이 $\xi:=b/k^{2/3}$를 다시 적는다 | 6.9 | $y$ ([r5909c9e]), $x_b$ ([r030ffae]) |
| $\mathcal R_b$, $\mathfrak D_b$, $\mathfrak E_b$, $\mathrm{Src}_b$, $\mathrm{Flow}_b$ | 창의 수준 질량 $k\,c_{k+b}(k)$, 결손 $\Psi(b)-\mathcal R_b$, 결손의 상위해, 결손의 원천 항, 결손의 흐름 항 | 6.9 | $R_b$, $D_b$, $E_b$, $\sigma_b$, $G_b$ ([r030ffae]) |
| $Q^{\mathrm{low}}_c$, $Q^{\mathrm{env}}(y)$, (SUP), $(C_b)(\xi)$ | 원천의 생존 하계 수열, 봉투, 정리 W 증명의 두 조건 | 6.9 | |
| $\mathrm{Bor}_\le(b)$ | $\sum_{m\le b}\mathrm{Bor}(m)$ | 6.9 | $S_0(b)$ ([r030ffae]) |
| $\mathrm{Lip}$, $\mathrm{rem}_L$ | 정리 {{new:6:theorem-W}} 증명의 Lipschitz 경계 상수; 보조정리 {{new:6:E1}}의 한 블록 재귀에서 최대 변위 $k$를 내는 뿌리 블록이 둘 이상인 몫(음이 아님) | 6.9 | |
| $b_{\max}$, $\ell_{\mathrm{fb}}$, $L_0$, $\Phi_{\mathrm{fb}}(\theta)$, $\hat\Sigma_k$, $\mathfrak c_0$, $\mathrm{LB}^{\mathrm{mono}}$, $\mathrm{LB}^{\mathrm{low}}$, $\mathrm{LOW}_k$ | 창 끝 $\lfloor6k^{2/3}\rfloor$, 되먹임 폭, 되먹임 시작, 되먹임 인자, 창 합의 하계, 용량 이동 비의 하계, 조립의 두 명시 하계, 생존 1 착지 항 | 6.9 | $B$, $G$, $F$, $\hat S_k$, $c_0$, $\rho_{mono}$, $\rho_{low}$ ([r030ffae]) |
| $\mathrm{hz}_k(N)$, $\Sigma_{\mathrm{hz}}$ | 크기 방향 생존 위험률 $1-s_{N+1}(k)/s_N(k)$(6.6절의 $h_N$과 같은 양), 위험률 합 | 6.9 | $h_k(N)$ ([r030ffae], [rb6a2cd0]) |
| $\Delta_{\mathrm{cap}}(g)$, $\Delta_{\mathrm{size}}(g)$, $G_N$, $\Delta^G_N(j)$, $\beta(m)$ | 용량 증분, 크기 증분, 크기 $N$ 숲의 가장 큰 나무 크기, $\Pr(G_N\le j)-\Pr(G_{N+1}\le j)$, Borel 이웃비 $\mathrm{Bor}(m+1)/\mathrm{Bor}(m)$ | 6.9 | $D_N(j)$ ([r030ffae]) |

### 7장

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $N$, $\theta'$ | 환경의 크기 $n-k=k+\nu$; 비 $\nu/k$(6.9절 끝에 한 번 괄호로 정의됨) | 7.1 | $a$ ([r3d0856b], [re71a735]; 8.1절에 언급) |
| $A^\circ_N$, $\Theta^\circ_n$ | 최대 변위 $\le k-1$이고 모든 뿌리 블록이 $k+1$ 이하인 배치의 수; 짝 없는 문턱 손실 $\binom nkk^{k-2}A^\circ_{n-k}$ | 7.1 | |
| $K_n(m)$, $\gamma_m$, $\lambda_1(m)$ | 병합 핵 $\binom n{m+1}p_{n-1-m}$, 병합 계수 $k(m+1)/(m+1-k)=k(1+\lambda_1(m))$ | 7.1 | $c_m$ ([rae1f209]) |
| $\mathcal Q_m$ | 행별 비 $b^{(2)}_m/(\gamma_m\Theta_m)$ | 7.1 | |
| $A^{(G)}_N$, $A^\diamond_N$ | 모든 나무가 $G$ 이하인 생존 배치의 수; $G=k+103$인 경우(덮인 문턱) | 7.1 | |
| $\mathcal C_n$ | $BV_n-(\Theta_n-\Theta^\circ_n)$ | 7.1 | $X_n$ ([rae1f209]) |
| $\pi_2(M)$ | 크기 $M$의 균등 라벨 나무가 무게중심을 둘 가질 확률 | 7.1 | |
| $\Omega_m$, $\mathrm{FL1}_m$, $\mathrm{Pair}^+_m$, $\mathcal P^\pm_m$ | 한 블록 항등식의 항들; $\mathrm{Pair}^+_m=\mathcal P^+_m-\mathcal P^-_m$ | 7.2 | $E_m$, $N'_2$, $M_2$ ([rae1f209]) |
| $\mathcal V_m$, $\mathfrak d_k$ | $\sum_{s\ge k}\binom msv_sA_{m-s,k-1}$; $\max_{k\le N\le2k-1}c_N(k-1)/s_N(k)$ | 7.2 | $V_m$, $\delta_k$ ([rae1f209]) |
| $\mathrm{need}_m$, $(\mathrm R_m)$ | 행 조건 $(\mathrm R_m)$: $\Phi_m+\Omega_m/(k\Theta_m)$이 넘어야 하는 양 $\mathrm{need}_m:=\frac{1+\lambda_1(m)}{1-\bar{\mathfrak d}_k/2}-W_0'(m-k)-\frac1k$ | 7.2 | |
| $\varsigma_m(s)$, $\Phi_m$ | 착지 무게 $[\pi_m(s)/\pi_m(k)](k/s)$; 착지 비 $\mathrm{FL1}_m/\Theta_m$ | 7.2 | $w_m(s)$ ([rae1f209]) |
| $W_0'(N)$, $W_0''(N)$ | 생존 없는 핵 질량 상계의 양 $\sum_{g=k+2}^N\pi_N(g)k/g$와 그 잘린 판 $\sum_{g=k+104}^N\pi_N(g)k/g$(7.4절) | 7.2 | 기록 [r5909c9e]는 잘린 판을 $W_0'$로 적는다 |
| $L_*(k)$, $\mathcal J_1(k),\dots,\mathcal J_4(k)$ | 정리 {{new:7:theorem-AR}}의 하계 $1.206$과 네 성분. 8.5절의 $\mathcal J'_1,\mathcal J'_2$와 구별 문장 | 7.2 | $J(k)$, $J'(k)$, $Bd(k)$, $Bd'(k)$ ([rae1f209]) |
| $\mathrm{rb}_m$, $\omega(s)$, $\Lambda_k$, $\Lambda'_k$, $\mathsf G(N)$, $\mathsf G'(N)$, $a_\ast$, $D$ | 정리 {{new:7:theorem-AR}} 증명의 국소 양: Robbins 나머지, $(k/s)^{5/2}$, 두 하계 합, 첫 층 생존 하계 함수, $\lceil(3k)^{2/3}\rceil$, $6.62/\sqrt k$ | 7.2 | $\rho_m$, $G(N)$, $a_1$ ([rae1f209], [r5909c9e]) |
| $\tilde\sigma_n$, $\mathrm{FS}(n)$, $\mathcal X_n$, $\hat\lambda_k(n)$, $\lambda_k(n)$, $B_k(n)$ | 숲–나무 재생 원천, 그 양성의 진술, 분해의 음 아닌 나머지, 잘리지 않은 한 걸음 합과 그 두 조각 | 7.3 | |
| $\mathfrak t_k(s)$ | 평평한 꼬리 $\sum_{s'=s}^{2k+1}x_{s'}(k)$ | 7.3 | $T(s)$ ([rb6a2cd0]) |
| $\mathfrak r_N$, $\eta(N)$, $\kappa_N$ | 제한 성장비 $A_{N+1,k-1}/((N+1)A_{N,k-1})$, 감소율 $k(1-\log\mathfrak r_N)$, (Hz)의 상수. 8.6절의 $\eta_k$와 구별 문장 | 7.3 | $r_N$ ([rb6a2cd0], [r3d0856b]) |
| $\varrho_s$, $\varrho^H$, $\varrho^L$, $\varrho_{\min}$ | 무게 증분 $\mathcal T_n(s)/\mathcal T_n(s-1)-1$과 그 하계들 | 7.3 | $\rho_s$, $\rho^H$, $\rho^L$, $\rho_{\min}$ ([rb6a2cd0]) |
| $\mathcal Y_k(n)$, $\nu_0(k)$, $\mathcal F_k(\nu)$, $\mathcal F^+_k$, $\mathcal F^{LP}_k$, $\nu_1(k)$ | 정리 {{new:7:theorem-11}}의 인자, 그 영점, 정리 P·P⁺·P⁺⁺의 판정 함수, 문턱 | 7.3 | $X_k(n)$, $F_k(\nu)$ ([rb6a2cd0]) |
| $\mathcal H^\theta_k(s)$ | 문턱 부분나무 머리 합 $\sum_{N=k+1}^{s-1}\theta_N(k)$ | 7.3 | $U_k(s)$ ([rb6a2cd0]) |
| $s^\dagger$, $\varrho^\dagger(s^\dagger)$, $\mathfrak h(s^\dagger)$, $\mathcal Y^\dagger_k(n)$, $L_N$, $LP_k(n)$, $\mathcal Y^{LP}_k(n)$ | 자르는 자리와 정리 11′의 양, 선형 최소화의 하계 | 7.3 | $S$, $r_S$, $W_S$, $Y_k$, $Y^{LP}$ ([rb6a2cd0]) |
| $\Psi^{low}(d)$, $F^{low}(k,\theta')$, $G^{low}(k,\theta')$ | 칸 하계 $0.3989(2\sqrt d-1.678)$(정수 $d$의 함수), 한 변수 함수, 거대 블록 몫 하계 | 7.4 | $L_2$ ([r5909c9e]) |
| $\pi^{0,up}$, $\mathrm{merge}^{up}$, $A^{\diamond,up}$, $A^\diamond_{dec}$ | 조각남 확률 상계, 덮개 몫 상계, 덮인 문턱의 상계와 그 감소 부분 | 7.4 | $P^{up}_0$, $Q^{up}$, $Q_{dec}$ ([r5909c9e]) |
| $\mathfrak B$, $\mathfrak a$, $\mathfrak w_b$, $\mathfrak w'_b$, $\Sigma_v$, $\Sigma_u$, $\mathfrak e$, $\mathfrak m_i$, $z_j$, $\xi_i$, $\underline\xi_i$, $\overline\xi_i$, $\mathcal I_i(k)$ | 정리 {{new:7:P-diamond}} 증명의 양: $\lfloor4k^{2/3}\rfloor$, $\nu+1-m$, 창 무게 인자, 창 합, 보조정리의 국소 양, 칸 끝점, 칸 적분 | 7.4 | $B$, $a$, $\rho_b$, $\rho'_b$, $\delta$, $M_i$, $y_i$, $I_i$ ([r5909c9e]) |
| $\mathcal C^\pm_s$, $\lambda$ ($=k/N$), $H_\infty$, $w_\infty$, $\mathcal L_P$, $\psi(\lambda)$, $g_\infty$, $m_v$, $m_v^{+}$, $m_u$ | 블록 반응 정규화 $v_s/p_{s-1}$, $u_s/p_{s-1}$; 명제 C의 매개변수; 극한 양들; 창 질량과 블록 내부의 생존 몫을 더한 창 질량 $m_v^{+}=m_v+\frac1k\sum_bs_{k-1+b}(k)$ | 7.6 | $C^\pm_s$, $H$, $w$, $L_P$, $\psi$, $g$ ([r5909c9e]) |

### 8장

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $\zeta$ | 띠 안의 위치를 창의 척도로 잰 좌표 $\nu/k^{2/3}$ | 8.1 | $x$ ([r3d0856b]) |
| $\varkappa_m$, $\mathfrak f_m$, $\mathfrak T_m$ | 장부 계수($2$ 또는 $1+(n-m)/k$), 1/p 장부의 항, 꼬리합 | 8.1 | $c_m$, $f_m$, $T_m$ ([r3d0856b], [re71a735]) |
| $\Delta c_m$ | 한 칸 차분의 확률판 $c_m(k)-c_m(k-1)=d_{m,k}/p_m$ | 8.1 | $\Delta\pi_m$ ([r3d0856b]) |
| $\Lambda_\nu$, $\mathrm{Bd}_\nu$ | 문턱 예산과 그 경계항 | 8.1 | |
| $\mathcal L_X$, $\mathcal L_Y$ | 예산 분해의 손실항 | 8.1 | $L_X$, $L_Y$ ([r3d0856b]) |
| $\mathfrak s_d(y)$ | $d$-좌표 생존 $s_{y+d-1}(y)$ | 8.2 | $s_d(y)$ ([re71a735]) |
| $\omega_m$, $\mathrm{Stays}$, $\mathrm{Bd}^S$, $\mathsf a_m$, $\mathsf b_m$, $\varkappa_0$, $\mathsf H$ | 명제 {{new:8:prop-S}}의 꺾인 무게($1<\omega_m\le2$), 문턱 뒤 머묾 질량, 중앙 경계항, 증명의 계수, $3k+\nu-m_0$, 수준 $k$에 처음 닿는 크기. 8.6절의 $\mathsf H$는 $\lceil\sqrt{5k\log k}\rceil$ | 8.2 | $\alpha_m$, $\beta_m$, $c_0$ ([r3d0856b]) |
| $DD_m$ | $DD(m-1,k-1)$ | 8.2 | |
| $\vartheta$, $\vartheta_{lb}$ | 띠 인자 $2(1+1/k)A_{N,k-1}/A_{N,k}-1$(띠), $-1$(벌크); 그 하계 | 8.3, 8.4 | $\theta$, $\theta_{lb}$ ([r3d0856b]) |
| $\mathcal S^*(k,\nu)$, $\mathrm F'(k,\nu)$, $\mathrm{BD}(k,\nu)$, $\mathrm{DDL}(k)$, $\mathsf q_h$, $\mathsf p_{\mathrm{two}}$, $\varrho^*$ | 명제 {{new:8:prop-T}}의 머묾 상계와 그 성분, 두 계수, 벌크 상수 | 8.4 | $S^*(k,\nu)$, $\tau_h$, $\lambda$, $\rho^*$ ([r3d0856b]) |
| $\mathrm{Stays}^{\mathrm{vis}}$, $\mathrm{Stays}_{\mathrm{PM}}$, $\mathrm{Stays}_X$ | 머묾 질량의 세 읽기 | 8.4, 8.5 | $\mathrm{Stays}_\theta$ 등 ([r3d0856b]) |
| $\mathcal W_b(M',y)$ | 창의 생존 상계 | 8.4 | $W_b$ ([r3d0856b]) |
| $P^y$, $\mathbb E^y$, $P_0$, $\mathbb E_0$, $\mathcal E^y(a)$, $\mathsf h_y(a)$ | 용량 $y$의 사슬 법칙과 기댓값(2.11절), 얼린 법칙 $P^{y_0}$과 기댓값, 멈춤 확률, h-변환의 함수 | 8.5 | |
| $\psi(y)$, $\mathsf V_y(d)$, $\mathrm{Res}_d$ | 얼린 볼록성의 함수 $y\prod_iy/(y+a_i)$(7.6절의 $\psi$와 다른 함수), 얼린 생존, 기울임 나머지 | 8.5 | |
| $\mathsf u_b$, $\mathsf v_b$, $\mathsf D_y(b)$, $\mathcal G_y(b)$, $\tilde X_j$, $\mathsf S_d(b)$, $X^{\mathrm{crit}}_d(b)$, $\mathsf r_b$, $\mathsf N_b$, $\mathsf H_2(d)$ | 정리 {{new:8:theorem-A}}·{{new:8:theorem-B}}·{{new:8:theorem-C}}의 양: 수준별 지수, 수준별 공식, 젊은 사슬의 면적, 임계 면적, 방문 상계의 양 | 8.5 | $u_b$, $v_b$, $G_y(b)$ ([re71a735]) |
| $\mathrm{DDL}_2(k)$, $\mathrm{CF}^\natural(k)$, $\tilde{\mathsf D}$, $\mathfrak q(t)$, $\mathcal J'_1$, $\mathcal J'_2$, $\mathsf A$, $\mathsf E$, $\beta$ | 대각선 손실의 상계와 닫힌 꼴, 명제 {{new:8:prop-M-natural}}의 양($\mathsf A=k-1+b$, $\mathsf E=k-1+d$는 그 증명 안의 기호); $\beta=(2\pi)^{-1/2}$ | 8.5 | $DDL_2$, $CF^\natural$ ([re71a735]) |
| $\phi_C(m)$, $\phi_C(d;c)$, $\mathsf g(x)$, $\mathcal I(w)$, $\mathcal F(w)$ | 정리 {{new:8:theorem-S-prime}}의 첫 층 생존 상계와 보조 함수 | 8.5 | |
| $\mathrm{PM}_c(d)$, $\omega_c(d)$, $\omega^\sharp_c(d)$, $\mathsf D_1$, $I_c$ | 명제 {{new:8:prop-X}}의 점질량 읽기와 무게 | 8.5 | |
| $\mathcal L_\delta(k)$, $\hat{\mathsf E}(\delta)$ | 선도 몫, 보조정리 {{new:8:lemma-F}}의 양 | 8.5 | $L_\delta(k)$ ([re71a735]) |
| (SS) | 보조정리 {{new:8:lemma-SS}}의 상해 조건의 꼬리표(2.8절의 (SC)와 다른 꼬리표; 구별 문장) | 8.5 | (SC) ([re71a735]) |
| $\mathsf c_1$ | $4/(3\sqrt{2\pi})=0.53192\ldots$ | 8.6 | $I_1$ ([re71a735]) |
| $\chi$ | 창 안 결손의 척도 좌표 $\delta/y^{2/3}$ | 8.6 | $x$ ([re71a735]) |
| $\mathfrak s_*(u,y)$, $\mathsf S_{\mathrm R}$, $\mathrm{Ren}_*(j)$, $\mathsf B_\delta(b)$, $\mathcal G^y(b)$, $\kappa_{\mathrm R}$, $\gamma(a)$, $\mathfrak Q(y,\chi)$ | 보조정리 J·R·R′의 양: 창의 생존 하계, 점질량 하계의 성분들 | 8.6 | $Q_2(y,x)$ ([re71a735]) |
| $\mathcal U(k;\bar\nu)$, $\mathrm{Flat}$, $\mathrm{Ab}$, $\mathrm{Top}$, $\mathrm{Sub}$, $\mathcal K(\tau)$, $\eta_k$, $\mathsf s_c$, $\mathsf a_c$, $\tilde\omega$, $\mathsf w$, $\mathsf r(x)$, $\mathsf f(x)$, $\mathsf W(x)$, $\mathsf h^{\mathrm{up}}$, $\mathsf B(c,k)$ | 명제 {{new:8:prop-U}}의 $\nu$에 무관한 머묾 상계와 그 네 몫(평탄, Abel 꼬리, 위쪽, 뺄 몫), 보조 양 | 8.6 | $U(k;\bar\nu)$ ([re71a735]) |
| $\mathcal S^*_{\mathrm{new}}$, $\mathsf T_\vartheta(k,\nu)$, $\mathcal L_F$, $\mathcal U_F$, $\mathcal R_F$, $\mathcal R'_F$, $k_0$, $\mathsf e_1$, $\mathsf s_2$, $\vartheta_0$, $\bar{\mathsf E}(k)$, $\eta'_k$, $\Delta_0$, $\chi_{\mathrm{cap}}$, $\chi^*$, $k^*$, $\mathcal L_{\mathrm{low}}$ | 균일 증명의 새 하계, $\vartheta$ 몫, 가족별 함수 셋과 시작점, 보조 양 | 8.6 | $S^*_{new}$, $\Theta(k,\nu)$, $\Lambda_F$ ([r3d0856b], [re71a735]) |
| $\mathsf X$, $\bar{\mathsf t}$, $\mathcal H_y(u)$, $\mathcal H_0(u)$, $\mathsf X_J$ | 정리 {{new:8:theorem-FO}}의 양 | 8.8 | |

### 9장

| 기호 | 뜻 | 처음 정의된 절 | 기록의 글자 |
|---|---|---|---|
| $\mathcal J_y$ | 임계 생성함수 증분 $F_y(1/e)-F_{y-1}(1/e)=e\cdot\Pr_B(M=y)$: 2.6절의 임계 볼츠만 법칙 아래에서 최대 변위가 정확히 $y$일 확률의 $e$배. 필요조건 D는 $y^{3/2}\mathcal J_y\to e/\sqrt{2\pi}$ | 9.6 | 기록 [r0af7f41]의 정리 `Parking.critical_increment_unconditional`의 양 |
