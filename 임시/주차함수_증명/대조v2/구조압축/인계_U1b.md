# 인계 U1b — 2장 뒤 절반(2.7–2.12절) → 물결 2·3의 단위와 뒤 단계

작성 2026-11-17 05시대. `장v2/장2.md`(1234행)가 2장의 최종 꼴이다. 아래 표 다섯은 **2장 전체**의 것이다 — U1a의 표(`인계_U1a.md`)를 그대로 받아 U1b의 행을 더했고, 물결 2의 다섯 단위는 이 파일 하나만 읽으면 된다. 자리는 절·진술·문구로 적는다(행 번호는 조립이 바뀌면 밀린다). 보고는 `수리_U1b.md`.

## 표 1. 새 라벨(2장 17)

| 라벨 | 종류 | 자리 | 진술 한 줄 |
|---|---|---|---|
| `2:row-positive` | 보조정리(행의 양수성) | 2.1절, 따름정리 `2:old-2-4` 뒤 | 모든 $n\ge1$, $0\le\ell\le n-1$에서 $b_{n,\ell}\ge1$ |
| `2:capacity-ratio` | 보조정리 C(용량 곱의 한 걸음 비) | 2.1절, $Z_k$·$H_k$ 정의 문단 뒤 | $\mathrm{cp}(y):=\prod\min(\cdot,y)$: $\mathrm{cp}(y+1)/\mathrm{cp}(y)=(1+\frac1y)^{Z_y}$, $\mathrm{cp}(y-1)/\mathrm{cp}(y)=(1-\frac1y)^{Z_y+H_y}$; 첫 차분 두 꼴; 둘째 차분 $\mathrm{cp}(y)\mathfrak v_y(Z_y,H_y)$; 정규화 곱 $\prod\min(1,y/\cdot)$에도 그대로 |
| `2:root-removal` | 보조정리 R(뿌리 떼기와 조건부 균등성) | 2.2절 끝 | (가) 나무 ↔ (뿌리 라벨, 숲) 일대일·독립 균등; (나) 부분나무·나머지 숲·매다는 자리의 독립 균등, $t>n/2$인 꼭짓점은 하나 |
| `2:weighted-partition` | 정리 G(가중 분배함수) | 2.3절 첫 진술 | $A_n[\mathrm{wg}]$: (가) 숲 표현·나무 합 $\mathrm{wg}_tA_{t-1}[\mathrm{wg}]$ (나) 마지막 차 재귀·일대일 (다) 지수 공식·조각 (라) $t>t_\ast$에서 상수 $\mathrm{wg}_\infty$면 $A[\mathrm{wg}]=e^{\mathrm{adj}}/(1-\mathrm{wg}_\infty\int e^{\mathrm{adj}})$ (마) 단조성 |
| `2:chain-law` | 정리 B(지정 사슬 공식) | 2.5절, 지정 사슬·고리 정의 문단 뒤 | (가) 자식/자손 고리 지정 사슬의 기대 수 $\frac{\mathrm{Bor}(\mathfrak t_j)}{\mathrm{Bor}(n+1)}\prod_{\text{자식}}\mathrm{Bor}(\gamma_i)\prod_{\text{자손}}\mathrm{Ren}(\gamma_i)$ (나) 성분 $j$개 (다) 크기 $>n/2$면 기대 수=확률 (라) $\pi_n(m)$ Borel 꼴·$\Pr^T_t$·$\mathbb E^T_t$·$\theta_t(k)$ 두 꼴·$\mathbb E_n[H_t(F)]=\theta_{n+1}(t)$·$t\le2k\Rightarrow\theta_t(k)=\Pr^T_t(H_k=1)$·$\mathcal P_m(j)=\frac jm\pi_m(j)$·$\theta_{m+1}(t)\theta_t(t')$ |
| `2:union-bound` | 보조정리(합집합 상계) | 2.5절, B 뒤 | $\Pr_n(M\ge y)\le\sum_{t=y+1}^n\theta_{n+1}(t)\frac{t-y}t$($n,y\ge1$); 2.6절에 「좌변 $=1-s_n(y)$」 |
| `2:level-mass-jensen` | 보조정리 J | 2.6절, 2.25 뒤 | (가) $c_n(y)$의 두 기댓값 꼴, $n\le2y+1$이면 사슬 생존 곱 (나) 가중 Jensen($\mathrm{wgt}$·$\mathrm{exc}$·$\mathrm{surv}$) |
| `2:capacity-shift-ratio` | 보조정리(용량 이동 비) | 2.6절 끝 | $s_m(y)/s_m(y')\ge\prod_{i\le m}\min(i,y)/\min(i,y')$; $s_m(k-1)\ge(1-\frac1k)^{\max(m-k+1,0)}s_m(k)$ |
| `2:two-variable-frozen` | 따름정리 G2(두 변수 얼린 다항식의 닫힌 꼴) | 2.7절, 경계 다항식 $J_n(z)$ 정의 문단 뒤(옛 2.29 자리) | (ㄱ) $\mathcal K_k(\eta,y;x)=e^{\mathrm{adj}_k}/(1-y\int_0^xe^{\mathrm{adj}_k})$, $\mathrm{adj}_k(\eta,y;x)=\sum_{t<k}(t-y)p_{t-1}\frac{x^t}{t!}+(\eta-y)p_{k-1}\frac{x^k}{k!}$, $\partial_x\mathcal K_k=y\mathcal K_k^2+\partial_x\mathrm{adj}_k\cdot\mathcal K_k$ (ㄴ) $\mathcal K_{n,k}(k,k)=A_{n,k-1}$, $\mathcal K_{n,k}(k,k+1)=A_{n,k}$, $\mathcal K_{n,k}(k-1,k-1)=A_{n,k-2}$ (ㄷ) $J_n(z)=\partial_\eta\mathcal K_{n,k}(\eta,z)|_{\eta=k}$ (ㄹ) $\deg_\eta\le\lfloor n/k\rfloor$; $B_{n,k-1}=\mathcal K_{n,k}(k,k-1)-\mathcal K_{n,k}(k-1,k-1)=\sum_{r\ge1}\frac{(-1)^{r-1}}{r!}\partial^r_\eta\mathcal K_{n,k}(\eta,k-1)|_{\eta=k}$; $B\le J_n(k-1)$, 등호 $n\le2k-1$, $B_{2k,k-1}=J_{2k}(k-1)-\Xi_{2k,k}$ (ㅁ) $e_n=\partial_y^2\mathcal K_{n,k}(k,k)$, $\sum_\sigma A^\sigma_{k-1}Z_k=k\partial_y\mathcal K$, $\sum_\sigma A^\sigma_{k-1}Z_k(Z_k-1)=k^2\partial^2_y\mathcal K$, $\sum_\sigma A^\sigma_{k-1}H_k=k\,\partial_\eta\mathcal K(k,k)=k\,J_n(k)$ |
| `2:volterra-residual` | 따름정리 G4(선형화와 정확 잔차) | 2.7절, 보조 급수 묶음·Green 응답 정의 뒤, 2.30 앞 | $\mathcal K_k(y;x)=e^Te^{\mathrm{pd}}$, $\mathcal X=e^T(y\int_0^x\mathcal X+e^{\mathrm{pd}}-1-\mathrm{pd})$; (ㄱ) $\mathcal K_k\equiv\mathcal G_\ast\pmod{x^{2k+2}}$, $\mathcal E_{<k}+\mathrm{sm}_k\equiv e^{T^{\le k}}$ (ㄴ) $\mathcal X\equiv e^{T^{\le k}}[y\int\mathcal X+\frac12\mathrm{pd}^2]\pmod{x^{3k+3}}$ (ㄷ) $J(y;x)=\partial_\eta\mathcal K_k|_{\eta=k}$의 선형 방정식 $\partial_xJ=(2y\mathcal K_k+\partial_x\mathrm{adj}_k(k,y;x))J+p_{k-1}\frac{x^{k-1}}{(k-1)!}\mathcal K_k$, $J\equiv p_{k-1}e^Te^{y\mathrm{Gr}}\int_0^xe^{-y\mathrm{Gr}}\frac{\varsigma^{k-1}}{(k-1)!}\pmod{x^{2k+1}}$ (ㄹ) $0\le y\le k+1$: $\mathcal K_k\preceq e^T$, $J_n(y)\le p_{k-1}\mathcal G_{y,k-1,n}$ |
| `2:curvature-level-mass` | 보조정리 X(나무 곡률의 수준 질량 표현) | 2.9절 머리, 나무 곡률 정의 뒤·2.36 앞 | (가) $s^T_t(y)=\frac{\min(t,y)}ts_{t-1}(y)$ (나) $x_t(y)=\frac1t[(y+1)c_{t-1}(y)-(y-1)c_{t-1}(y-1)]$($t\ge y+1$), $x_y(y)=-\frac1y$, $0$($t\le y-1$) |
| `2:borel-arithmetic` | 보조정리 Bor-1(Borel 산술) [증명됨; 표준, r4868e30, r2ec875c] | 2.9절, 2.38 뒤·2.39 앞 | (ㄱ) Robbins 꼴·$\mathrm{rb}_m$ 엄격 감소·$\mathrm{Bor}(m)=(2\pi)^{-1/2}m^{-3/2}e^{-\mathrm{rb}_m}$·$\mathrm{Ren}(j)=(2\pi)^{-1/2}j^{-1/2}e^{-\mathrm{rb}_j}$·$1/\mathrm{Bor}(n+1)=n!e^{n+1}/p_n$·$e^{-1/(12m)}<e^{-\mathrm{rb}_m}<e^{-1/(12m+1)}<1$ (ㄴ) $1<\mathrm{Bor}(m)/\mathrm{Bor}(m')\le(m'/m)^{3/2}$($m<m'$) (ㄷ) $\Psi(q)\le(2\pi)^{-1/2}(2\sqrt q-1)\le0.7979\sqrt q$; $2(2\pi)^{-1/2}e^{-1/(12(q+1))}(q+1)^{-1/2}\le\sum_{m>q}\mathrm{Bor}(m)\le2(2\pi)^{-1/2}(q+\frac12)^{-1/2}\le\sqrt{2/\pi}q^{-1/2}$ (ㄹ) $\frac3{2i}-\frac5{6i^2}\le1-g(i)\le\frac3{2i}$; $\sum_{i=i_1}^{i_2}\frac1i\le\log\frac{i_2}{i_1-1}$ |
| `2:power-sum-renewal` | 보조정리 Bor-2(거듭제곱 합과 갱신함수의 하계) [증명됨, 보조정리 `2:zeta-constants`에 의존; 표준] | 2.9절, 2.39 뒤·2.40 앞 | (ㄱ) $\sum_{j\le q}j^{\mp1/2}$의 Euler–Maclaurin 상하계 넷, $\sum j^{-3/2}\le\mathsf z_{3/2}$ (ㄴ) $\mathsf c_\Psi=-\mathsf z_{1/2}+\mathsf z_{3/2}/12\in(\frac32,1.6781)$, $\Psi^{\mathrm{low}}_{(\varkappa)}=(2\pi)^{-1/2}(2\sqrt\varkappa-\mathsf c_\Psi+\frac1{2\sqrt\varkappa}-\frac1{24}\varkappa^{-3/2})$, $\Psi(q)\ge\Psi^{\mathrm{low}}_{(q)}$, 단조·도함수 범위·$(2\pi)^{-1/2}(2\sqrt\varkappa-\mathsf c_\Psi)\le\Psi^{\mathrm{low}}<2(2\pi)^{-1/2}\sqrt\varkappa$; $\Psi(q)\ge0.3989(2\sqrt q-1.678)\ge0.7978\sqrt q-0.8848$ |
| `2:tree-expansion` | 정리 A(표시 나무 전개) | 2.10절, 2.42 뒤·2.43 앞 | (가) $A_k-2A_{k-1}+A_{k-2}=A_{k-1}(\mathcal B_k-\mathcal B_{k-1})+A_{k-1}\sum_{j\ge2}\frac{\mathcal B_k^j}{j!}+A_{k-2}\sum_{j\ge2}\frac{(j-1)\mathcal B_{k-1}^j}{j!}$(교차항 계수 비음) (나) $A_k-A_{k-2}$ (다) $A_{k-1}-A_{k-2}$ 두 꼴 (라) 조합적 뜻; 절단 $n\le2k+1$·$2k-1$·$3k-1$ (마) $n=3k$ 보정 $-\frac{(3k)!}{6(k!)^3}k^{3(k-2)}$; 뒤 문단: (라) 첫 절단+2.42(가) ⇒ 2.6절 한 나무 재귀 |
| `2:supersolution` | 보조정리 S(첫 층 생존의 상위해 원리) [증명됨; re71a735, r3d0856b] | 2.11절, 2.47 뒤·기울임 인자 문단 앞 | (가) $\phi:\{1,\dots,y+2\}\to[0,1]$, $\phi(1)=1$, $\phi(q)\ge\sum_{j\ge q}\mathrm{Bor}(j)+\sum_{j<q}\mathrm{Bor}(j)\frac y{y+q-j}\phi(q-j)$ ⇒ $s_{y+q-1}(y)\le\phi(q)$ (나) $\phi_1(q)=1-\sum_{j<q}\mathrm{Bor}(j)\frac{q-j}{y+q-j}$는 상위해 ⇒ $s_{y+q-1}(y)\le\phi_1(q)$; 뒤 문단: 어느 초과까지만 확인해도 거기까지 결론 |
| `2:h-transform` | 보조정리 H($h$-변환과 얼린 볼록성) [증명됨; re71a735, r845b205] | 2.11절 끝(2.48 뒤) | (가) 엄격 하강 부분확률 핵 $\mathrm{ker}_0$, 양의 $\mathrm{hf}$($(\mathrm{ker}_0\mathrm{hf})\le\mathrm{hf}$), $\mathrm{ker}=\mathrm{ker}_0\,\mathrm{hf}(q')/\mathrm{hf}(q)$: $\mathrm{term}(d)-\mathrm{term}^0(d)=-\sum_{q<d}\frac qy\mathrm{vm}(q)(\frac{\mathrm{hf}(q)}{\mathrm{hf}(d)}-1)$; 경로의 $\mathrm{ker}$-확률 $=\mathrm{ker}_0$-확률$\times\mathrm{hf}(q_j)/\mathrm{hf}(d)$ (나) $\mathrm{fz}(y)=y\prod_i\frac y{y+q_i}$ 볼록, $\mathrm{fz}''/\mathrm{fz}=[(\sum\mathrm{ex}_i)^2+\sum\mathrm{ex}_i^2]/y^2$; 뒤 문단: $\mathrm{ker}_0=\mathrm{Bor}(q-q')$, $\mathrm{hf}=\mathrm{Bor}(y+\cdot)$ ⇒ 2.47의 무거운 사슬·기울임 인자 |
| `2:nf-log-coefficients` | 보조정리 N(정규화 인자의 로그 계수와 합성 법칙) [증명됨; r1aa0be6, r13b0b8f] | 2.12절 끝(2.52 뒤) | (가) $\log\mathrm{nf}(n,d)=\sum_i\mathrm{lc}_i(d)n^{-i}$, $\mathrm{lc}_i(d)=\frac1i[\frac{d^{i+1}}{i+1}+2d^i-\sum_{\rho<d}\rho^i]$, $\frac{2d^i}i\le\mathrm{lc}_i\le\frac{5d^i}{2i}$, $(1-\frac dn)^{-2}\le\mathrm{nf}\le(1-\frac dn)^{-5/2}$ (나) $\mathrm{nf}(n,d+d')=\mathrm{nf}(n,d)\mathrm{nf}(n-d,d')$ (다) $W_n(\gamma)=\mathrm{nf}(n,\gamma_1)\frac n{n-\gamma_1+1}(\frac n{n-\gamma_1})^{j-2}W_{n-\gamma_1}(\gamma')$($j\ge2$) |

## 표 2. 지운 라벨(2장 7)과 지운 항목

| 라벨 | 옛 번호 | 소비처가 받는 대체 |
|---|---|---|
| `2:old-2-16` | 2.17 | 없음(U1a) |
| `2:old-2-18` | 2.19 | B(가) 모두 자식 고리(U1a) |
| `2:old-2-19` | 2.20 | 없음(U1a) |
| `2:old-2-20` | 2.21 | 없음; 장1 107행 구 삭제(U15), 장11 22행(U16), 부록D_장2(U14)(U1a) |
| `2:old-2-30` | 2.29 | `2:two-variable-frozen`(ㄹ). 장4 2(U5), 장5A 4(U6), 장7B 1(U11), 장부 1(U17), 덧씌우기 6(지도) |
| `2:old-2-36` | 2.37 | `2:chain-law`(라)의 $\theta_t(k)$ 두 꼴. 장11 121행(U16), 장부(U17), 덧씌우기 1(지도) |
| `2:old-2-44` | 2.46 | 정의 `2:old-2-43` 뒤 문단($\Pr(j\in\mathcal H_{\mathrm B}(q))=\mathrm{Ren}(j)$, $\mathbb E|\mathcal H_{\mathrm B}(q)|=\Psi(q)$; 보조정리 `2:old-2-37`(나)). 장1 155행(U15), 장11 129행(U16), 장부(U17), 덧씌우기 1(지도) |
| (항목) `2:old-2-37`(라) | 2.38(라) | `2:borel-arithmetic`(ㄱ)(「$\mathrm{Ren}(j)<(2\pi j)^{-1/2}$」)·(ㄷ)(「$\Psi(q)\le0.7979\sqrt q$」). 장6 4, 장8 1, 장9 1, 장10 3, 덧씌우기 6 |
| (항목) `2:old-2-37`(마) | 2.38(마) | `2:chain-law`(라). 장5B 1, 장6 1, 장8 1, 장9 1, 덧씌우기 4 |
| (항목) `2:old-2-37`(가) 옛 내용 | 2.38(가) | 옛 (가) 「$\mathrm{Ren}(j)=j\mathrm{Bor}(j)$」는 2.5절의 정의가 되었고, (가)는 이제 갱신 방정식 $\mathrm{Ren}(j)=\mathrm{Bor}(j)+\sum_{m<j}\mathrm{Bor}(m)\mathrm{Ren}(j-m)$. 옛 (가)를 부르던 장6 2, 장8 1, 장10 1, 덧씌우기 3 → 2.5절 정의로(인용 삭제 또는 「$\mathrm{Ren}$의 정의」) |
| (항목) `2:chain-expansion`(가) | 2.49(가) | `2:chain-law`(라)의 $\mathbb E_n[H_t(F)]=\theta_{n+1}(t)$; 개수 꼴은 $p_n\theta_{n+1}(t)=\binom ntt^{t-1}(n+1-t)^{n-t}$(2.51(가) 증명이 유도). 장6 1, 장8 1, 장9 2, 부록A 1, 덧씌우기 3 |
| (항목) `2:chain-expansion`(나) | 2.49(나) | 2.12절 머리의 $\mathcal W_n(\gamma)=p_n\frac{\mathrm{Bor}(\mathfrak t_j)}{\mathrm{Bor}(n+1)}\prod\mathrm{Ren}(\gamma_i)$(정리 B(가), 모두 자손 고리) $j=2$. 장6 1, 덧씌우기 1 |
| (항목) `2:chain-expansion`(다) | 2.49(다) | 같은 식(2장 안에서만 쓰였음) |
| (항목) `2:J-egf`(가) | 2.30(가) | `2:two-variable-frozen`(ㄷ)과 `2:volterra-residual`(ㄷ)의 선형 방정식. 장4 1(U5), 부록D_장4 1(U14) |
| (부록 D) `D:fiber-enumeration`·`D:fiber-nonunimodal-bound` | — | 삭제(U14; U1a) |

## 표 3. 옮긴·합친·격하한 진술(2장 전체)

| 옛 라벨·자리 | 새 라벨 또는 처분 | 자리 |
|---|---|---|
| `2:old-2-5`(2.5) | 정리→명제, 셋째 문장·부록 D 문장 삭제, [증명됨; r81e7051, r15524fd] | 2.1절 끝(U1a) |
| `2:old-2-9`(정의 2.9) | 라벨 유지, 장 안 이동 | 2.2절 첫 진술(U1a) |
| $Z_k$·$H_k$·무거운/문턱 자리·「문턱」(2.5절 문단) | 정의 이동 | 2.1절(U1a); 숲의 $Z_k(F)$·$H_k(F)$·무거운 꼭짓점·문턱 부분나무는 2.2절 |
| $\mathfrak v_k(Z,H)$ | 보조정리 C의 진술에서 정의 | 2.1절(U1a) |
| $\mathrm{Ren}$·$\Psi$ 정의 문단(옛 2.9절) | 2.5절로; 2.9절의 옛 문단 삭제(U1b) | 2.5절 Lagrange 문단 뒤 |
| $\theta_t(k)$·$\Pr^T_t$·$\mathbb E^T_t$(옛 2.37·2.9절 문단) | 정리 B(라)에서 정의; 2.9절에는 $M^T_t$ 정의만 남음(U1b) | 2.5절 |
| 지정 사슬·크기·간격·고리(옛 2.12절 머리) | 2.5절 정리 B 앞 문단으로; 2.12절 머리는 2.5절을 가리키고 $\mathcal W_n(\gamma)$를 「모든 고리가 자손 고리인 (숲, 지정 사슬) 쌍의 수 $=p_n\frac{\mathrm{Bor}(\mathfrak t_j)}{\mathrm{Bor}(n+1)}\prod\mathrm{Ren}(\gamma_i)$」로 정의(U1b) | 2.5절·2.12절 |
| 2.5절 핵 문단 | 정리 B(라)와 두 문장으로 흡수(U1a) | 2.5절 |
| `2:old-2-13`(2.14) | (가)(나)(다) 항목화, (다) 자른 꼴 신설 | 2.5절(U1a) |
| `2:old-2-14`(2.15) | 증명 첫 단락 C 인용; † 문장 삭제; [증명됨; r88bed8a] | 2.5절(U1a) |
| `2:old-2-6`·`2:old-2-8`·`2:old-2-10`·`2:old-2-11`·`2:old-2-17` | 증명만 인용(G) | 2.3·2.4·2.5절(U1a) |
| 2.6절 정의 2.25 뒤 | 「한 나무 재귀」 문단 신설 | 2.6절(U1a) |
| 2.7절 얼린 다항식 정의 문단 | 두 변수 판 $\mathcal K_{n,k}(\eta,y)$·$\mathcal K_k(\eta,y;x)$ 정의 추가 | 2.7절(U1b) |
| 2.7절 Taylor 문단 | 축약(전개식·조합적 뜻·$e_n$ 정의만) | 2.7절(U1b) |
| `2:old-2-30`(2.29) | 삭제 → G2(ㄹ) | (U1b) |
| 2.7절 G3 문단 | 「$B_{n,k-1}$도 두 닫힌 꼴의 차로 적힌다(G2(ㄱ)(ㄴ)) … 부호가 섞인 차」로 교정 | 2.7절(U1b) |
| 2.7절 Gr 문단 | $\mathcal E_{<k}$·$T^{\le k}$·$T^{>k}$·$\mathrm{sm}_k$·$\mathcal K_k(y;x)$ 정의와 $\mathcal E_{<k}+\mathrm{sm}_k=e^T(1-T^{>k})$ 추가; Green 응답 뒤에 $\mathcal G_\ast$·$\mathcal X$·$\mathrm{pd}$ 정의(4.3절·7.4절에서 당김) | 2.7절(U1b) |
| `2:J-egf`(2.30) | (가) 삭제; 진술 하나(옛 (나))라 항목 표지 없음; 증명 G4(ㄷ) 인용; 지위 「증명됨」(작성자 판단 뗌) | 2.7절(U1b) |
| 2.7절 환원 문단 | 「2.28과 G2(ㄹ)을 합치면」 | 2.7절(U1b) |
| 2.8절 $\mathcal P_m(j)$ 정의 | 「$=\frac jm\pi_m(j)$(정리 B(라))」 추가 | 2.8절(U1b) |
| `2:old-2-34`(2.35) | (가) 등식·항별·망원 (나) 무게 부등식 (다) 가중 Abel 하계($\omega\ge0$; 비증가면 우변 항 비음)로 항목화; 지위 그대로(작성자 판단) | 2.8절(U1b) |
| 2.9절 준비 문단 | 보조정리 X로 승격; 나무 곡률 정의역 $t\ge1$ | 2.9절(U1b) |
| `2:old-2-35`(2.36) | 증명 첫 단락 C+2.11 인용 | 2.9절(U1b) |
| `2:old-2-36`(2.37) | 삭제 → B(라) | (U1b) |
| `2:old-2-37`(2.38) | (가) 갱신 방정식으로 교체, (라)(마) 삭제; 증명 순서 (나)→(가)→(다) | 2.9절(U1b) |
| 2.9절 설명·Robbins 준비 문단 | 한 문단으로 줄이고 Robbins 꼴은 Bor-1(ㄱ)의 진술로 | 2.9절(U1b) |
| `2:old-2-38`(2.40) | (ii) 증명 B(라); (iv) 증명 B(라)+Bor-1(ㄴ) | 2.9절(U1b) |
| `2:old-2-39`(2.41) | (c)(d) 증명 Bor-1(ㄱ)(ㄷ) | 2.9절(U1b) |
| 2.10절 준비 문단 | $b^T$·$\mathcal B$·$\delta_t$·$b^{(2)}$·$c^{(2)}$ 정의만 남기고 두 꼴·$\delta_t$ 꼴은 2.42로 | 2.10절(U1b) |
| `2:b-top`(2.42) | 「수준 개수의 두 꼴과 행의 마지막 항」 (가)(나)(다); 옛 진술은 (나); [증명됨; r33475a7, r05cf8c9] | 2.10절(U1b) |
| `2:old-2-40`(2.43) | 증명 A(가)(라)+2.42(다) 인용 | 2.10절(U1b) |
| 2.11절 머리 첫 문장 | 「2.5절에서 정의한 … 2.38(나)에 따라」 | 2.11절(U1b) |
| `2:old-2-44`(2.46) | 삭제 → 정의 2.45 뒤 문단 | (U1b) |
| `2:old-2-45`(2.47) | 증명: 첫 단락 B(라), 경로 확률 단락 B(가)(다) 모두 자식 고리 | 2.11절(U1b) |
| 10.20 `10:old-8-24` | → `2:supersolution`(가); 10.11 `10:old-8-15`의 내용 → S(나) | 2.11절(U1b) |
| `2:old-2-46`(2.48) | 증명의 「명제 2.46」 → 2.38(나); 곱셈성은 H 뒤 문단이 되가리킴 | 2.11절(U1b) |
| 10.12·10.14 `10:old-8-16`·`10:old-8-18`, 10.13 `10:old-8-17`(=6.37(나)) | → `2:h-transform`(가)/(나) | 2.11절(U1b) |
| 8.6 `8:explicit-bounds`(가)(다)(마) / (나)(라) | → `2:borel-arithmetic`(ㄱ)(ㄷ)(ㄴ)(ㄹ) / `2:power-sum-renewal`(ㄱ)(ㄴ) | 2.9절(U1b) |
| `2:chain-expansion`(2.49) | (가)(나)(다) 삭제; 이름 「지정 사슬의 포함배제 전개」; (라) → (ㄹ-1)(ㄹ-2)(ㄹ-3) | 2.12절(U1b) |
| `2:moving-tail`(2.51) | (다) 지수 $3\to5/2$(증명 사다리꼴); (라)·(마) 묶인 $\eta\to j$; (가)(라)(마)(사) 증명 인용 갱신 | 2.12절(U1b) |
| `2:chain-normalization`(2.52) | (나) 지수 $-j-2\to-j-3/2$; (가) 증명 B(가)+Bor-1(ㄱ); (다) 증명 (ㄹ-1)(ㄹ-2)(ㄹ-3) 인용 | 2.12절(U1b) |
| 2장 머리 둘째 문단 | 표준 결과 목록에 「Euler 합 공식」 추가 | (U1b) |

## 표 4. 새 글자와 바뀐 글자(2장 전체)

| 글자 | 뜻 | 전역/국소·정의 절 | 검색한 충돌 범위와 결과 |
|---|---|---|---|
| $A_n[\mathrm{wg}]$, $A[\mathrm{wg}](x)$ | 가중 분배함수·지수 생성함수 | 2.3 전역(2·4·5·7장) | `A_n[` 장v2 0(U1a) |
| $\mathrm{wg}_t$, $\mathrm{wg}(t,I)$ | 무게·국소 역전 수 세분 | 2.3 전역 | 7A 7.16의 $\mathrm{wg}^\sharp$ 같은 가족(U1a) |
| $I$, $t_\ast$, $\mathrm{wg}_\infty$, $\mathrm{adj}(x)$, $\sigma_{\mathrm L}$·$\sigma_{\mathrm R}$ | G 진술 국소 | 2.3 | (U1a) |
| $\mathrm{fs}_m$, $\mathrm{ts}_t$, $m_0<\dots<m_s$ | G 증명 국소 | 2.3 | (U1a) |
| $\mathrm{cp}(y)$, $Z_y$·$H_y$ | C의 용량 곱·다중집합의 초과/문턱 수 | 2.1 진술 국소(5·6·7·9·10장 인용) | (U1a) |
| $\mathcal S$ | R(나) 증명의 라벨 집합 | 2.2 증명 국소 | (U1a) |
| $v_i$, $\mathfrak t_i$, $\gamma_i$; 낱말 자식 고리·자손 고리 | 지정 사슬 | 2.5(옛 2.12) | (U1a) |
| $\rho_t$ | 2.18 증명 | 2.5 증명 국소 | (U1a) |
| $\mathrm{wgt}$, $\mathrm{exc}$, $\mathrm{surv}$, $\mathbb E'$ | J의 변수·밀도 바꾼 기댓값 | 2.6 | (U1a) |
| $y\le y'$, $m$ | 용량 이동 비 | 2.6 | (U1a) |
| $\eta$ | 문턱 자리 무게의 더미 인수(두 변수 판) | 2.7(1.1에 넣지 않음) | 2장: 옛 2.51(라)(마)의 $\eta$(진술·증명 열아홉 자리)를 $j$로 바꿔 충돌 해소; 4·5A·9장 $\eta$는 다른 장 국소 |
| $\mathcal K_{n,k}(\eta,y)$, $\mathcal K_k(\eta,y;x)$, $\mathcal K_k(y;x)=\mathcal K_k(k,y;x)$ | 두 변수 얼린 다항식·그 지수 생성함수·얼린 지수 생성함수 | 2.7 전역($\mathcal K_{n,k}(y)$ 행의 변형; 7B의 $\mathcal D(z;x)$·$\mathcal D(z,y;x)$ 대체 — 7B의 $\mathcal D(z,y;x)$는 $y$가 문턱·$z$가 무거운 무게라 $\mathcal K_k(\eta,z;x)$에 대응) | $\mathcal D$ 쓰지 않음(K0-7) |
| $\mathrm{adj}_k(\eta,y;x)$ | G2의 보정 급수(정리 G(라)의 $\mathrm{adj}$를 이 무게에 적은 것) | 2.7 진술 국소(G4가 씀) | `\mathrm{adj}_k` 장v2·장부 0 |
| $\mathcal E_{<k}(x)$ | 절단 급수 $\sum_{j<k}p_jx^j/j!$ | 2.7 전역(정의 절 4.3→2.7; 2·4·5·7장) | 7.2·7.3의 국소 $\mathcal E$는 다른 장 국소 |
| $T^{\le k}$, $T^{>k}$ | 나무 함수의 절단(7B의 $\mathfrak T_{\le k}$·$\mathfrak T_{>k}$) | 2.7 전역(7.4→2.7) | `T^{\le` 장v2·장부 0 |
| $\mathrm{sm}_k(x)$ | 작은 나무 급수 $(1-T)(e^T-\mathcal E_{<k})$(4.3·7.4의 $\mathcal Q_k$) | 2.7 전역(2·4·5·7장) | `\mathrm{sm}` 장v2·장부 0. $\mathcal Q_k$를 버린 까닭: 2.12 진술 $\mathcal Q_{n,r,j}$·9.2 전역 $\mathcal Q_m$(결정 47·53) |
| $\mathcal G_\ast(y;x)$ | 연쇄 해(4.3의 $F_\ast(y,x)$·7.4의 $\mathcal G_\ast(z;x)$) | 2.7 전역(Green 응답 $\mathcal G_{z,i,n}$ 가족의 변형) | — |
| $\mathcal X(y;x)$ | 잔차 $\mathcal K_k-\mathcal G_\ast$(7.4의 $\mathcal X$) | 2.7 전역(7.4→2.7) | 장2 0, 1.2 없음 |
| $\mathrm{pd}(y;x)$, $\mathrm{pd}_t(y)=y\mathcal K_{t-1,k}(y)-t^{t-1}$ | 조각 차이(7.4의 $\mathrm{bd}$) | 2.7 전역 | `\mathrm{pd}` 장v2·장부 0. $\mathrm{bd}$를 버린 까닭: 5.2 전역 $\mathrm{bd}_d$(생일 법칙); $\delta$를 버린 까닭: 2.10 전역 $\delta_t$ |
| $J(y;x)$ | 경계 다항식의 지수 생성함수 | 2.7 진술 국소(G4(ㄷ); $J_n(z)$의 변형) | — |
| $\mathcal Y$ | G4 증명의 Green 해(옛 2.30 증명 글자) | 2.7 증명 국소 | — |
| $\Phi$ | 2.5절 Lagrange 문단의 임의 멱급수(옛 $\phi$) | 2.5 본문 임시 | 2장 여유; 4장 전역 $\Phi$는 다른 장 |
| $\varkappa$ | $\Psi^{\mathrm{low}}_{(\varkappa)}$의 실수 인수 | 2.9 진술 국소(Bor-2) | 2장 여유 그리스(장부 5절); 8장의 $\varrho$를 쓰지 않은 까닭: 2.8 진술 국소 $\varrho$(2.32·2.33) |
| $\varepsilon$ | Bor-2 증명의 지수($\varsigma^{-\varepsilon}$; 8.6 증명의 $\beta$) | 2.9 증명 국소 | $\beta$는 2.11 전역 $\beta_i$ |
| $\mathsf c_\Psi$, $\Psi^{\mathrm{low}}_{(\cdot)}$ | 명명 상수·갱신함수 하계 | 정의 절 8.2→2.9(2·8·9장) | 같은 양의 이동 |
| $\mathrm{rb}_m$ | Robbins 나머지 | 2.9(진술로 승격) | 변화 없음 |
| $i_1\le i_2$ | Bor-1(ㄹ) 조화합 범위(8.6의 $\mathfrak i_1,\mathfrak i_2$) | 진술 국소(1.1 $i$의 첨자 변형) | — |
| $m<m'$ | Bor-1(ㄴ)의 두 크기(K3의 $a<b$ — 예약 글자) | 진술(1.1 변수) | — |
| $\phi$, $\phi_1$ | S의 상위해 함수·$\mathbf 1$의 상(10.5 묶음 $\phi$→2.11) | 2.11 진술 국소(6·10장 인용) | 2장: Lagrange 더미 $\phi\to\Phi$, 2.12 차분 더미 $\phi\to f$로 바꿔 유일하게 함 |
| $\mathrm{ker}_0$, $\mathrm{ker}$, $\mathrm{hf}$, $\mathrm{vm}$, $\mathrm{sp}_j$, $\mathrm{term}(d)$·$\mathrm{term}^0(d)$, $\mathrm{fz}$, $\mathrm{ex}_i$ | H: 기준 핵·변환 핵·$h$-함수·생존 가중 방문 측도·생존 곱·종료 가중값·얼린 함수·초과 비(10장 $\Pr^{y_0}$·$\mathfrak h_y$·$\mathfrak M_y$·$\Pi_j$·$\mathfrak s_d$·$\mathfrak s^{\mathrm{fr}}_d$·$\psi$·$\mathrm{ex}_i$) | 2.11 진술 국소(결정 53) | `\mathrm{ker}`·`\mathrm{vm}`·`\mathrm{sp}`·`\mathrm{term}`·`\mathrm{fz}` 장v2·장부 0; `\mathrm{hf}` 7A 184–188행 국소(다른 장 국소, 허용); $\mathrm{ex}_i$는 6.5·10.5의 같은 양(정의 절 →2.11) |
| $d$, $d'$ | N(나)의 두 결손 | 2.12(1.1 변형) | K3의 $a,b$는 예약 |
| $n'$, $\mathfrak t'_i$, $\gamma'$ | N(다)의 작은 숲·그 크기·남은 간격 수열 | 2.12 진술($\gamma'$)·증명 국소 | — |
| $f$ | 2.12절 차분 연산자 정의의 더미 함수(옛 $\phi$) | 2.12 본문 임시 | 장부 362행 「$f(\cdot)$」 |
| $f_1,f_2$ | 2.49 (ㄹ-2) 증명의 볼록함수(옛 $f,g$) | 2.12 증명 국소 | $g$는 2.6 전역 $g(x)$ |
| $j$ | 2.51(라)(마)의 두 간격의 합(옛 $\eta$) | 2.12 묶인 지표 | 1.1 변수 |
| $\mathrm{lc}_i(d)$ | 정규화 인자의 로그 계수 | 정의 절 5.4→2.12(2·5장) | 같은 양의 이동 |
| 낱말 | 두 변수 판; 작은 나무 급수; 연쇄 해(2.7, 4.3·7.4에서); 잔차; 조각 차이; 갱신 방정식(2.9); Borel 산술; 수준 성분, 표시 나무 전개, 교차항(2.10); 상위해, 상위해 조건(2.11, 10.5에서); $h$-변환, 기준 핵, 생존 가중 방문 측도, 생존 곱, 얼린 볼록성(2.11, 6.5·10.5에서); 포함배제 전개(2.12); 로그 계수, 합성 법칙, 첫 간격 떼기(2.12, 5.4에서) | | 장부 3절(U17) |

## 표 5. 바뀐 문턱·상수·범위(2장 전체)

| 자리 | 옛 값 | 새 값 | 흐르는 자리 |
|---|---|---|---|
| 용량 이동 비(옛 8.24(가)) | $k\ge2$, $k\le N\le2k-1$ | 모든 $1\le y\le y'$, $m\ge0$ | U9·U13·U11(U1a) |
| 합집합 상계 | (새) $n,y\ge1$ | | U10·U3/U11(U1a) |
| 2.14(다) | (새) $y\ge1$, $1\le n\le2y+1$, $y\le t_\ast\le n$ | | U12(U1a) |
| 2.15 지위 | 증명됨, 작성자 판단 | 증명됨 | 1.5절 표(U1a) |
| 2.5 종류·지위 | 정리; 계산 증거 섞임 | 명제; 증명됨 | U15·U16·U14·U17(U1a) |
| 2.14 식별자 | r39ea75d | r39ea75d, rae1f209 | 부록 B(U1a) |
| 2.30 지위 | 증명됨, 작성자 판단 | 증명됨(옛 † 단계는 (가)의 증명에만 있었음) | 1.5절 지위 표 |
| 2.30 항목 | (가)(나) | 진술 하나(옛 (나)), 항목 표지 없음 | 장4 1·장5A 3·장7B 1의 「(나)」 뗌; 장4 1·부록D_장4 1의 「(가)」 → G2(ㄷ)·G4(ㄷ) |
| 2.35 | 부등식 셋 | (가) 등식 꼴·(나) 무게·(다) 가중 Abel($\omega\ge0$; 비증가 조건은 우변 항의 부호에만) | 10.4(U13), 5.60(U7), 9.23(U12), 6.3절 한 문장(U8), 장1·장8·장9·부록D_장8·부록C·장11의 `2:old-2-34` 인용이 항목을 부르면 (가) |
| 2.38 | (가)–(마) | (가) 갱신 방정식(내용 교체), (나)(다) 그대로, (라)(마) 삭제 | 표 2 |
| 2.42 | 「행의 마지막 항」 한 주장 | (가) 두 꼴 (나) 마지막 항 (다) $\delta_t$ 네 경우·$\delta_t=t^{t-1}x_t(k)$ | 9.25(가)·9장 「2.10절」 인용 여덟 자리·8.1(U12·U9); 장1·장11의 이름 |
| 2.42(다)의 $k\,d_{t-1,k}+b^{(2)}_{t-1}$ 범위 | K3: $t\ge k+2$ | $t\ge k+1$(둘 다 참) | — |
| 나무 곡률 $x_t(y)$ 정의역 | $t\ge y$ | $t\ge1$($t\le y-1$에서 $0$) | — |
| G2(ㅁ) | K3 2-2: $k\,\partial_\eta\mathcal K_{n,k}(k,k)=J_n(k)$ | $=k\,J_n(k)$(교정) | 7.36(나)(U11) |
| Bor-1(ㄷ) 꼬리 상계 | 8.6(다): $\sqrt{2/\pi}q^{-1/2}$ | $2(2\pi)^{-1/2}(q+\frac12)^{-1/2}\le\sqrt{2/\pi}q^{-1/2}$(10.21 증명의 꼴을 포함) | `6:old-8-25` 증명(U8) |
| Bor-2(ㄴ) 따름 연쇄 | K3 2-12: $\Psi^{\mathrm{low}}\ge(2\pi)^{-1/2}(2\sqrt q-\mathsf c_\Psi)\ge0.3989(2\sqrt q-1.678)$ | 둘째 걸음이 $q=1$에서 거짓이라 $\Psi^{\mathrm{low}}_{(q)}\ge0.3989(2\sqrt q-1.678)$을 직접 증명; $\mathsf c_\Psi<1.6781$은 2.39에서(의존 표지) | 9.43·9.8 소비처(U12) |
| S의 범위 | 10.20: $D\le y+2$, $\phi:\{1,\dots,D\}$ | $\phi:\{1,\dots,y+2\}$; 뒤 문단에 축소 허용 | 6장 `6:old-8-25`(U8): $\phi(q)=\mathfrak s^{\mathrm{up}}_q(y)$를 $q\le y+2$ 전체에서 확인(10.21 증명이 그대로 함); 10.11 소비처(U13): $s^{\mathrm W}_{q-1}(y+q-1,y)=\phi_1(q)$ |
| 2.51(다) 지수 | $(\frac n{n-d})^3$ | $(\frac n{n-d})^{5/2}$ | 5.21(나)·5.27(U6) — 약한 쪽으로만 바뀜 |
| 2.52(나) 지수 | $(1-r/n)^{-j-2}$ | $(1-r/n)^{-j-3/2}$ | 5A의 `2:chain-normalization`(나) 인용 2(U6) |

상수 변화: 없음(새 수치 상수 없음; $0.7979$·$0.3989$·$1.678$·$0.7978$·$0.8848$은 옛 2.38(라)·9.43·9.8의 것).

## 받는 작업자별 자리

### U3(7A)
- 7A 2–8행이 이미 「따름정리 `2:two-variable-frozen`」·「따름정리 `2:volterra-residual`」·「보조정리 `2:borel-arithmetic`」으로 부른다 — 종류 낱말이 2장과 같다. 7.22(남으면)의 Riccati는 G(라)(U1a).
- 7A 184–188행의 국소 $\mathrm{hf}$는 2.11절 H의 $\mathrm{hf}$와 토큰이 같다(다른 장의 국소라 R1′ 허용; 바꿀 필요 없음 — 장부가 가른다).

### U5(4장)
1. 4.3절 머리(장4:83–85)의 $\mathcal E_{<k}$·$\mathrm{Gr}$ 정의 → 「2.7절의 절단 급수 $\mathcal E_{<k}$와 $\mathrm{Gr}$」 인용; 4.6 증명 둘째 단계의 $\mathcal Q_k$(5회) → $\mathrm{sm}_k$; 셋째 단계의 $F_\ast(y,x)$(6회) → $\mathcal G_\ast(y;x)$; 1–3단계 → 「따름정리 `2:volterra-residual`(ㄱ): $F_y\equiv\mathcal G_\ast(y;\cdot)\pmod{x^{2k+2}}$」(K3-3).
2. `{{2:old-2-30}}` 2자리 → `{{2:two-variable-frozen}}`(ㄹ); `{{2:J-egf}}(가)` 1자리 → G2(ㄷ)+G4(ㄷ)(옛 재귀는 없어졌다 — 4.6 첫째 단계가 그 재귀를 쓰면 G(나)·G2(ㄱ)로); `{{2:J-egf}}(나)` 1자리 → 「(나)」 뗌.
3. 4.5 개관(장4:73–77)의 $d\ge e_n-J_n(k-1)$ → 2.28+G2(ㄹ)(2.7절 끝 환원 문단).
4. 4장 Robbins 대입 세 자리 → `2:borel-arithmetic`(ㄱ)(U1a 표).

### U6(5A)
1. `{{2:old-2-30}}` 4자리 → G2(ㄹ); `{{2:J-egf}}(나)` 3자리 → 「(나)」 뗌.
2. 5.4(다)(장5A:100)의 $\mathcal K(k-1)-A_{k-2}=B$ → G2(ㄴ)(ㄹ); 5.5(가) 증명 → G(가)(다)+G4(ㄱ)($\mathcal Q_k\to\mathrm{sm}_k$, $\mathfrak T_{\le k}\to T^{\le k}$)+5.4(나).
3. 5.27(가)의 $\mathrm{lc}_i$ 유도 → `2:nf-log-coefficients`(가)($\mathrm{lc}_i$의 정의 절이 2.12); 5.17(나)·5.28(가)의 첫 간격 떼기 → N(다); `{{2:chain-normalization}}(나)` 2자리의 지수는 $-j-3/2$(옛 $-j-2$보다 강함 — 쓰는 부등식이 약한 쪽이면 그대로 섬); 2.51(다)의 지수 $5/2$(5.21(나)가 쓰면 확인).
4. 5.2 증명의 $c_n(y)$ 재귀 → 정리 A 뒤 문단(「(라)의 첫 절단에 2.42(가)」)·2.6절 한 나무 재귀.
5. $\mathrm{cb}_m$ Robbins 꼴 → Bor-1(ㄱ)(인증 상수 꼴 보존; K2).

### U7(5B)
1. `{{2:old-2-37}}(마)` 1자리 → `{{2:chain-law}}(라); 5.45 삭제 → B(라); 5.44 삭제 → 2.36(C+2.11).
2. 5.47 삭제 → Bor-1(ㄱ)(ㄷ)(11자리).
3. 5.5.1절 $x_t(y)$ 유도 → `2:curvature-level-mass`(가)(나).
4. 5.60의 착지 질량 → 2.35(다)($\omega$ 비증가 가정은 우변 항의 부호에만 필요); 5.50 경로 표현 → J(가)+2.47 두 줄(U1a).

### U8(6A)·U10(6B)
1. `{{2:old-2-37}}(가)` 2자리 → 2.5절 정의($\mathrm{Ren}(j)=j\mathrm{Bor}(j)$); `(라)` 4자리 → Bor-1(ㄱ)($\mathrm{Ren}$ 상계) 또는 (ㄷ)($\Psi$ 상계); `(마)` 1자리 → B(라).
2. `{{2:chain-expansion}}(가)` 1자리 → B(라) $\mathbb E_n[H_t(F)]=\theta_{n+1}(t)$; `(나)` 1자리(6.51) → 6.51은 삭제(B(라) $\theta_{m+1}(t)\theta_t(t')$); 남는 쌍 공식 인용은 2.12절 머리의 $\mathcal W_n(\gamma)$ $j=2$.
3. `6:old-8-25`(10.21 이동): 상위해 원리는 `2:supersolution`(가) — $\phi(q)=\mathfrak s^{\mathrm{up}}_q(y)$를 $1\le q\le y+2$ 전체에서 확인(10.21 증명 그대로); Stirling 하계와 꼬리 $\sum_{j\ge q}\mathrm{Bor}(j)\le2(2\pi)^{-1/2}(q-\frac12)^{-1/2}$는 Bor-1(ㄱ)·(ㄷ)(꼬리 상계 $2(2\pi)^{-1/2}(q'+\frac12)^{-1/2}$를 $q'=q-1$에).
4. 6.37 삭제·10.12–10.14 대체·6.5절로 옮기는 10.15–10.19의 준비 산문: $h$-변환은 `2:h-transform`(가)에 $\mathrm{ker}_0=\Pr^{y_0}$의 전이, $\mathrm{hf}=\mathfrak h_y$, $\mathrm{vm}=\mathfrak M_y$, $\mathrm{term}(d)=\mathfrak s_d(y)$, $\mathrm{term}^0(d)=\mathfrak s^{\mathrm{fr}}_d(y)$, $\mathrm{sp}_j=\Pi_j(y)$; 얼린 볼록성은 H(나)($\mathrm{fz}=\psi$, $\mathrm{ex}_i$ 같은 글자). 6.14(나) → 정리 A 뒤 문단(한 나무 재귀); 6.20·6.34·6.35 → X; 6.22 → C; 6.52 → J(나); 6.3절 머리 「둘째 괄호 = 2.35(가)의 둘째 괄호」.
5. 6.53 증명의 $\Psi(d)\ge(2\pi)^{-1/2}(2\sqrt{d+1}-2.218)$ → Bor-2(ㄴ) 또는 현행(K2).

### U9(8장)
1. `{{8:explicit-bounds}}` 17자리(장8) → 항목 대응: (가)→`2:borel-arithmetic`(ㄱ); (나)→`2:power-sum-renewal`(ㄱ); (다)→Bor-1(ㄷ)(「$\mathrm{Bor}_\le(q)\ge1-\sqrt{2/\pi}q^{-1/2}$」는 꼬리 상계의 여집합; 6.1절 글자 $\mathrm{Bor}_>$·$\mathrm{Bor}_\le$는 2장에 없음 — 2장은 $\sum_{m>q}\mathrm{Bor}(m)$로 적는다); (라)→Bor-2(ㄴ)(실수 인수의 글자는 2장에서 $\varkappa$; 8장이 $\Psi^{\mathrm{low}}_{(\varrho)}$로 자기 변수를 넣는 것은 인수 대입이라 그대로 된다); (마)→Bor-1(ㄹ)(첫 부등식·조화합)과 (ㄴ)(Bor 비 — 8.6(마)의 $((i'-1)/(i'-1-j))^{3/2}$보다 강한 $(i'/(i'-j))^{3/2}$). 8.6의 Apostol·Titchmarsh 인용은 Bor-2 증명으로 옮겨 갔다.
2. `{{2:old-2-37}}(가)` 1 → 2.5절 정의; `(라)` 1 → Bor-1; `(마)` 1 → B(라); `{{2:chain-expansion}}(가)` 1 → B(라).
3. 8.7 삭제 → J(나)에 $\mathrm{wgt}=1$, $\mathrm{surv}=\prod y/S_i$, $\mathrm{exc}=\sum(S_i-y)$ + B(라)(U1a); 8.1 증명 → 정리 A 뒤 문단(한 나무 재귀) + 2.42(가); 8.25(가) → B(라); 8.24(가) → `2:capacity-shift-ratio`; 8.11 첫 문장 → J.
4. 8장 552·733행 설명값은 K4-6.

### U11(7B)
1. 7.4절 머리(장7B:78–92)의 $\mathcal D(z;x)$·$\mathcal D_{\ge k}$·$\mathfrak T_{\le k}$·$\mathfrak T_{>k}$ 정의 → 2.7절 인용: $\mathcal D(z;x)=\mathcal K_k(z;x)$, $\mathcal D_{\ge k}=\mathcal K_k(z;x)-\mathcal E_{<k}$, $\mathfrak T_{\le k}=T^{\le k}$, $\mathfrak T_{>k}=T^{>k}$(각 6·6·8·5회); 7.40(나)의 $\mathcal Q_k$(3회) → $\mathrm{sm}_k$; $\mathcal G_\ast(z;x)$는 2.7의 $\mathcal G_\ast(y;x)$를 $y=z$에서; $F_\ast$ 1회 → $\mathcal G_\ast$; $\mathrm{bd}(z;x)$·$\mathrm{bd}_t(z)$(7.4의 조각 차이, 10회 가운데 이 뜻인 것) → $\mathrm{pd}(z;x)$·$\mathrm{pd}_t(z)$.
2. 7.40: (가) → G4(ㄱ)의 $\mathcal K_k=e^Te^{\mathrm{pd}}$(또는 G(다)); (나) → 2.7절 정의와 4.6의 (4.2); (다) → G4(ㄴ). 7.41: 두 꼴의 일치와 $n\le2k$ 등호 → G4(ㄷ)·2.30; 부등식 → G4(ㄹ)($J^{\mathrm G}_n(z)=p_{k-1}\mathcal G_{z,k-1,n}$은 7B에 남는 이름); 증명의 $\mathcal D(z,y;x)$ → $\mathcal K_k(\eta,z;x)$(문턱 $\eta$, 무거운 $z$).
3. 7.36(나)의 세 모멘트 재귀 → G2(ㅁ) — 주의: $\sum_\sigma A^\sigma_{k-1}H_k(\sigma)=k\,J_n(k)$($J_n(k)$가 아님).
4. `{{2:old-2-30}}` 1 → G2(ㄹ); `{{2:J-egf}}(나)` 1 → 「(나)」 뗌; 7.39 삭제 → G2(ㄹ)·2.30 직접 인용.
5. 7B:146의 환원 $d\ge e_n-J_n(k-1)$ → 2.7절 끝 환원 문단(2.28+G2(ㄹ)); 7B:592 Robbins → Bor-1(ㄱ); 7.74 → `2:capacity-shift-ratio`; 7.67(나)·7.69(나) → B(라).

### U12(9장)
1. `{{2:old-2-37}}(라)` 1 → Bor-1; `(마)` 1 → B(라); `{{2:chain-expansion}}(가)` 2 → B(라) $\theta_{n+1}(t)$(개수 꼴 $p_n\theta_{n+1}(t)=\binom ntt^{t-1}(n+1-t)^{n-t}$은 2.51(가) 증명에 있음).
2. 9.19 → A(나)의 $n\le3k-1$ 절단; 9.20 → A(라) 두 제곱항; 9.21 → A(다)의 절단; 9.25(가) → 2.42(다)(「(가)」가 아니라 (다)에 $\delta_t$ 꼴, (나)에 $b_{k,k-1}$); 9.25(나) 삭제 → A(가); 9.26의 $\mathcal O_n=\mathrm{PAIR}_n$ → A(라); 9.22 첫 층 항 → 정리 A 뒤 문단(한 나무 재귀); 9장 「2.10절」 여덟 자리 → 2.42(가)(다).
3. 9.8·9.43 삭제 → Bor-2(ㄴ)·Bor-1(ㄷ)($\Psi^{\mathrm{low}}$의 2장 인수 글자는 $\varkappa$; 9장이 $\Psi^{\mathrm{low}}_{(d)}$처럼 자기 변수를 넣는다); 9.7의 $e^{1/(12\cdot)}$ → Bor-1(ㄴ).
4. 9.4 → J(가); 9.6 하계 → J(나); 9.5 → B(라); 9.14·9.18 → 2.14(다); 9.40·9.2절 → B(나)(U1a).

### U13(10장)
1. `{{10:old-8-24}}` 2자리 → `{{2:supersolution}}`(가); 10.11(`10:old-8-15`) 삭제·소비처 → S(나)와 $s^{\mathrm W}_{q-1}(y+q-1,y)=\phi_1(q)$(10장 안에 $s^{\mathrm W}$ 정의 줄 하나를 두거나 $\phi_1$ 식을 적음 — K0-2). 10.20의 글자 $D\le y+2$는 2장에 없다(S는 $\{1,\dots,y+2\}$ 전체 + 축소 허용 문단).
2. 10.12·10.14 삭제 → H(가)에 $\mathrm{ker}_0=\Pr^{y_0}(q\to q')$, $\mathrm{hf}=\mathfrak h_y$, $\mathrm{vm}(q)=\mathfrak M_y(q)$, $\mathrm{term}(d)=\mathfrak s_d(y)$, $\mathrm{term}^0(d)=\mathfrak s^{\mathrm{fr}}_d(y)$, $\mathrm{sp}_j=\Pi_j(y)$, 비 $\mathrm{hf}(q)/\mathrm{hf}(d)-1=\mathrm{tr}_y(q)$; 10.13 삭제 → H(나)($\mathrm{fz}=\psi$). 이 글자 대응은 10.15–10.19를 6.5절로 옮기는 U10도 받는다.
3. `{{2:old-2-37}}(가)` 1 → 2.5절 정의; `(라)` 3 → Bor-1(ㄱ)(ㄷ); 10.3(d) → B(나) $j=1$; 10.22 첫 식 → J(가) 둘째 꼴 $y=k+1$; 10.26 → J(나)+Bor-1(ㄴ)(ㄷ); 10.27(i) → J(나); 10.28 → R(나); 10.30 → Bor-1(ㄷ); 10.23′(4)(5)·10.31 → `2:capacity-shift-ratio`; 10.4 → 2.35(가).
4. 10.5절 머리의 「2.11절의 자유 Borel 보행의 재귀」·「상위해」 문장은 2.11절 S를 가리킨다.

### U14(부록 D)
- 부록D_장4의 `{{2:J-egf}}(가)` 1 → G2(ㄷ)·G4(ㄷ)(또는 삭제); 부록D_장8의 `{{8:explicit-bounds}}` 1 → Bor-1/Bor-2 해당 항목, `{{2:old-2-34}}` 1 → 2.35의 항목(쓰는 부등식이 항별이면 (가), 가중이면 (다)); 부록D_장2 두 항목 삭제(U1a).

### U15(1장)
- 155행 「명제 `2:old-2-46`」(= 2.46) 삭제; 164행 등 2.42를 이름으로 부르면 「수준 개수의 두 꼴과 행의 마지막 항」; `2:old-2-34`를 부르는 자리는 항목 없이 그대로 되거나 (가); 107·113·127행은 U1a 인계.

### U16(11장)
- 11.3 「2장의 표현」 행: U1b의 새 라벨 아홉(`2:two-variable-frozen`·`2:volterra-residual`·`2:curvature-level-mass`·`2:borel-arithmetic`·`2:power-sum-renewal`·`2:tree-expansion`·`2:supersolution`·`2:h-transform`·`2:nf-log-coefficients`)이 U1a의 여덟과 함께 든다. 121행의 `2:old-2-36`(2.37) → B(라); 129행의 `2:old-2-44`(2.46) → 2.38(나)+정의 2.45 뒤 문단; `2:old-2-34`(2.35)는 공유 행으로(5.60·9.23·10.4 소비); 「2.10절 준비 문단」 괄호 → 2.42; `8:explicit-bounds` 3자리 → 2장 두 라벨; `10:old-8-16` 1자리 → H.
- 2장 머리 넷째 문단(「첫째 증명만 쓰는 것은 셋(2.40·2.41·2.44) / 둘째만 2.48」)은 11.3 총표가 선 뒤 S·H·Bor-1·Bor-2·2.35·2.42의 공유 여부와 대조해 U15와 함께 고친다(K3-21).
- 11.4 문헌: Robbins 행의 쓰인 자리에 2.9절 Bor-1(ㄱ)(8.6의 자리는 소멸); Apostol·Titchmarsh(Euler 합 공식) 행의 자리 8.2절 → 2.9절 Bor-2; 1.6절 여파 표.

### U17(장부·부록 A·B·C·구조표)
- 1.2 정의 절: $\mathcal E_{<k}$ 4.3→2.7(쓰이는 장 2·4·5·7), $T^{\le k}$·$T^{>k}$ 신설(7.4의 $\mathfrak T$ 행 대체), $\mathrm{sm}_k$ 신설(4.3·7.4의 $\mathcal Q_k$ 행 대체 — 1.3 4.3·7.4 묶음의 $\mathcal Q_k$ 삭제), $\mathcal G_\ast(y;x)$ 신설(1.3 4.3 묶음 $F_\ast$·7.4 묶음 $\mathcal G_\ast$ 삭제), $\mathcal X(y;x)$·$\mathrm{pd}(y;x)$ 신설(7.4 묶음의 $\mathcal X$·$\mathrm{bd}$ 삭제), $\mathcal K_{n,k}(\eta,y)$·$\mathcal K_k(\eta,y;x)$·$\mathcal K_k(y;x)$는 $\mathcal K_{n,k}(y)$ 행의 뜻 열에(7.4 묶음 $\mathcal D$ 삭제), $\mathsf c_\Psi$·$\Psi^{\mathrm{low}}$ 8.2→2.9(인수 글자 $\varkappa$), $\mathrm{lc}_i$ 5.4→2.12, $\mathrm{ex}_i$ 6.5→2.11(H 진술 국소지만 6·10장이 부름).
- 1.3 2장 묶음: 2.7 — $\eta$(더미; 1.1에 넣지 않음), $\mathrm{adj}_k$, $J(y;x)$, $\mathcal Y$(유지); 2.9 — $\varkappa$, $\varepsilon$(증명), $i_1,i_2$; 2.11 — $\phi,\phi_1$, $\mathrm{ker}_0,\mathrm{ker},\mathrm{hf},\mathrm{vm},\mathrm{sp}_j,\mathrm{term},\mathrm{term}^0,\mathrm{fz}$; 2.12 — $d'$, $n'$, $\mathfrak t'_i$, $\gamma'$, $f$(차분 더미), $f_1,f_2$, $j$(옛 $\eta$ 행 삭제), $D$(2.51(아), 유지); 2.5 — $\Phi$(Lagrange 더미; 옛 $\phi$). 옛 2.30(가) 증명의 $\Phi_\sigma$·$\phi_{i+1}$ 국소 소멸; 옛 2.29의 $\Xi_{n,k}$는 G2(ㄹ)로(유지). 2.32·2.41·2.51(바) 증명의 표준 전개 더미 $u$(1.1 꼭짓점 글자) 셋은 옛 본문 그대로다 — 장부가 가른다.
- 3절 낱말: 표 4 마지막 행. 「갱신 방문 핵」「Borel 갱신함수」 정의 절 2.9→2.5(U1a); 「상위해」 첫 정의 절 2.11; 「h-변환」 10.5→2.11; 「얼린 볼록성」 6.5→2.11; 「연쇄 해」 4.3→2.7; 「조각 차이」 7.4→2.7.
- 4절 이름 행: 2.29·2.37·2.46 뺌(결정 K3-2·K3-8); 2.38 이름 「갱신 방문 핵과 갱신 항등식」 유지(항목 변경); 2.42 이름 변경; 2.49 이름 변경; 새 라벨 아홉 행(기록 이름 없음; 식별자는 표 1의 머리). 8.6·10.20·10.12·10.13·10.14의 뺌 행에 「2장 흡수(라벨 …)」.
- 부록 B: 소멸하는 식별자 없음(2.29의 r5f5cf73은 G2가, 2.37의 r4868e30은 Bor-1·X가, 2.46의 r6a8c8b6은 2.38이 가진다).
- 부록 C: 새 라벨 아홉 행; 2.29·2.37·2.46 뺌; `10:old-8-24`·`10:old-8-16`·`10:old-8-17`·`10:old-8-18`·`8:explicit-bounds` 행의 대응을 2장 라벨로.
- 구조표: 2.7절 제목 유지; 2.9·2.10·2.11절 진술 수 변화.

### 지도 갱신 작업자
- 삭제 라벨 `2:old-2-30`·`2:old-2-36`·`2:old-2-44`(덧씌우기 6·1·1 출현); 새 노드 후보 `2:two-variable-frozen`·`2:volterra-residual`·`2:tree-expansion`·`2:borel-arithmetic`·`2:power-sum-renewal`·`2:supersolution`·`2:h-transform`(설계서 7.7); `2:curvature-level-mass`·`2:nf-log-coefficients`는 5·6장이 부르므로 표지로 가른다.
- 덧씌우기의 `2:old-2-37}}(가)` 3·`(라)` 6·`(마)` 4, `2:chain-expansion}}(가)` 3·`(나)` 1 → 표 2의 대체 라벨·항목으로.

### 번역 알림
- 2.7–2.12절 전부(여섯 절 재편; 2.7·2.9·2.10·2.11절은 새 진술 포함). U1a의 2장 머리·2.1–2.6절과 합쳐 2장 전부.
