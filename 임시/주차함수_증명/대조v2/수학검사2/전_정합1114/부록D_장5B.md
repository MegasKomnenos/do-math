### D.{{D:window-mass-constant}} 가중 창 질량의 균일 상수 $\mathsf w_0$의 구간 산술 인증 (정리 {{5:old-5-32}})

**확인하는 진술.** 정리의 증명에서 가중 창 질량의 하계는 두 함수의 적분으로 적혔고 D.{{D:window-mass-constant}}에서는 그 두 함수를 단봉 계단 함수로 바꾸어 그 하계를 수치로 확인한다. 그러기 위해 $\mathfrak h_0=0.0342$, $\upsilon_{\max}=\sqrt{6\mathfrak h_0}$, $\mathfrak c_1=1/(2(1-\upsilon_{\max}))$로 둔다. $\theta\in[0,4.1]$의 $1600$개 셀에서 잰 $\mathfrak g$의 하계로 단봉 계단 함수 $\tilde\psi$를, $\theta\in[0,12]$의 $6400$개 셀에서 잰 $\bar\varrho$의 상계로 단봉 계단 함수 $\tilde\varphi$를 만든다. 확인하는 부등식은
$$
\Bigl(\int_0^{4.1}\tilde\psi-\mathfrak h_0\max\tilde\psi\Bigr)-\mathfrak h_0\Bigl(\int_0^{12}\tilde\varphi+\mathfrak h_0\max\tilde\varphi+e^{-12+\mathfrak h_0}\Bigr)-\mathfrak O(25000)\ \ge\ 0.71216 .
$$

**식.** 두 계단 함수로 바꾸기 전의 두 피적분함수, 곧 하계를 잴 함수와 상계를 잴 함수는 아래 성분들로 이루어진다.
$$
\begin{aligned}
P_{\min}(\kappa)&=\Bigl(\sqrt{2/\pi}\,(\kappa+\mathfrak h_0^2)^{-1/2}e^{-\mathfrak h_0^2/(12(\kappa+\mathfrak h_0^2))}-1.6\,\mathfrak h_0\sqrt\kappa\Bigr)_+,\qquad
\mathfrak b_{\min}(\theta)=\exp\bigl(-\theta^{3/2}-\mathfrak c_1\theta^2\mathfrak h_0\bigr),\qquad \mu(\theta,\kappa)=6-\kappa-\theta\mathfrak h_0,\\
\mathcal K(\sigma,\mathfrak b;\mu)&=\frac12\sqrt{\frac\pi{\mathfrak b}}\Bigl[e^{-2\sqrt{\sigma\mathfrak b}}\operatorname{erfc}\bigl(\sqrt{\sigma\mu}-\sqrt{\mathfrak b/\mu}\bigr)-e^{2\sqrt{\sigma\mathfrak b}}\operatorname{erfc}\bigl(\sqrt{\sigma\mu}+\sqrt{\mathfrak b/\mu}\bigr)\Bigr],\\
\mathcal T_{\max}(\theta,\mu)&=\frac{\theta}{\sqrt{2\pi}}\,e^{\theta^3\mathfrak h_0/(3\mu^2)}\Bigl[\mathfrak h_0^2\,\mu^{-3/2}e^{-(\theta-\mathfrak h_0)_+\mu/2-\theta^2/(2\mu)}+\mathcal K\Bigl(\frac{(\theta-\mathfrak h_0)_+}2,\frac{\theta^2}2;\mu\Bigr)\Bigr]\qquad(\mu\ge\theta^2/3),\\
\mathfrak Q(\theta,\kappa)&=P_{\min}(\kappa)\,e^{-\theta\kappa-\theta\mathfrak h_0^2}\,(1-\kappa\mathfrak h_0-\mathfrak h_0^3)\,\bigl(\mathfrak b_{\min}(\theta)-\mathcal T_{\max}(\theta,\mu(\theta,\kappa))\bigr)_+,\qquad
\mathfrak g(\theta)=\theta\int_0^{6-\theta\mathfrak h_0}\mathfrak Q(\theta,\kappa)\,d\kappa,\\
\mathfrak y(\theta)&=\max(\theta/2,\theta-\mathfrak h_0),\qquad
\bar\varrho(\theta)=\sqrt2\,\theta^{3/2}\exp\Bigl(-\theta\sqrt{\mathfrak y(\theta)}+\tfrac13\min\bigl(\theta^2\mathfrak h_0,\,\upsilon_{\max}\theta^{3/2}\bigr)\Bigr)\frac{1+\min(\theta\mathfrak h_0^2,\,6\mathfrak h_0)}{\sqrt{\mathfrak y(\theta)}-\tfrac13\min\bigl(\theta\mathfrak h_0,\,\upsilon_{\max}\sqrt\theta\bigr)},\\
\mathfrak O(Y)&=\frac1{Y^2}\sqrt{\frac{12}\pi}\,Y^{1/3}\sqrt{\frac2Y}\,(Y+1)\qquad(Y=25000\text{에서 평가}).
\end{aligned}
$$
$\mu(\theta,\kappa)<\theta^2/3$인 $(\theta,\kappa)$에서는 $\mathfrak Q$의 마지막 인자를 $0$으로 둔다. $\mathcal T_{\max}$의 대괄호 안 인자 $e^{-(\theta-\mathfrak h_0)_+\mu/2}$는 보조정리 {{5:bt-tail}}(나)의 $e^{-\sigma\mathfrak W_0}$($\sigma=(\theta-\mathfrak h)/2$, $\mathfrak W_0\mathfrak h^2\ge\mu$)에서 온 $\mu$의 함수다. 아래 알고리즘에서 $1$로 대신하는 인자는 이 인자가 아니라 꼬리 인자 $e^{-(\theta-\mathfrak h_0)_+\theta/2}$(보조정리 {{5:scaled-integrand}}(라) 증명의 $e^{-\varsigma_zz}\le1$)이며 위의 식에는 그 꼬리 인자가 이미 빠져 있다.

**알고리즘.** 셀마다 피적분함수의 하계를 잡기 위해 세 변수를 격자로 나눈다. $\theta$-격자는 $1600$개 셀($[0,4.1]$), $\sigma$-격자는 $1200$개 셀($\kappa=\sigma^2$, $\sigma\in[0,\sqrt6]$), $\mu$-격자는 간격 $0.1$이며 셀의 $\mu$ 하계는 격자 아래 끝으로 내린다. 셀 $[\theta_a,\theta_b]\times[\sigma_j,\sigma_{j+1}]$에서 $2\sigma P_{\min}(\sigma^2)$의 첫 항은 $\sigma_j$에서, 뺄 항은 $\sigma_{j+1}$에서, $e^{-\theta\kappa-\theta\mathfrak h_0^2}$와 $1-\kappa\mathfrak h_0-\mathfrak h_0^3$은 $(\theta_b,\kappa_{j+1})$에서, $\mathfrak b_{\min}$은 $\theta_b$에서, $\mathcal T_{\max}$는 인자별로 불리한 끝에서 평가한다(보조정리 {{5:scaled-integrand}}의 단조 방향). $\theta$ 자리에는 앞 인자 $\mathfrak h_0^2\theta$, $\theta^3$, $\theta$와 지수 $e^{\theta^3\mathfrak h_0/(3\mu^2)}$에서는 $\theta_b$를 넣고, 지수 $e^{-(\theta-\mathfrak h_0)\mu/2-\theta^2/(2\mu)}$와 $\mathcal K$의 두 인수에서는 $\theta_a$를 넣는다. $\mu$ 자리에는 $e^{-\theta^2/(2\mu)}$에서는 격자 위 끝을 넣고 $\mu^{-3/2}$, $e^{-(\theta-\mathfrak h_0)\mu/2}$, $e^{\theta^3\mathfrak h_0/(3\mu^2)}$, $\mathcal K$에서는 격자 아래 끝을 넣는다. $\mu$의 하계가 $\theta_b^2/3$보다 작은 셀은 버리고 $\theta>4.1$인 범위는 쓰지 않는다. 셀 하계로 $\tilde\psi$를, $\bar\varrho$의 셀 상계($6400$개 셀로 나누어 $\mathfrak y(\theta)$는 왼쪽 끝에서, 나머지 인자는 각각 불리한 끝에서 잰 것)으로 $\tilde\varphi$를 만든다. 하계 쪽은 하계가 가장 큰 셀을 봉우리로 삼아 봉우리 왼쪽에서는 오른쪽으로부터의 누적 최소로 바꾸고 오른쪽에서는 왼쪽으로부터의 누적 최소로 바꾸며, 상계 쪽은 상계가 가장 큰 셀을 봉우리로 삼아 그 왼쪽은 왼쪽 끝에서부터 누적 최대로 바꾸고 오른쪽은 오른쪽 끝에서부터 누적 최대로 바꾸어 둘 다 단봉이 되게 한 뒤 보조정리 {{5:riemann-unimodal}}을 쓴다. $\operatorname{erf}$는 교대 Taylor 급수를 항이 감소하기 시작한 뒤 첫 생략항이 $10^{-42}$ 아래가 될 때 끊고 그 항을 나머지로 더하며, 증가함수이므로 구간 입력에는 끝점 값을 쓴다. 이 글을 쓰며 만든 코드 `ul_iv_fixed.py`에서도 $\mathcal T_{\max}$의 꼬리 인자 $e^{-(\theta-\mathfrak h_0)_+\theta/2}$는 $1$로 두고 앞 상수 $1/\sqrt{2\pi}$는 남긴다.

**범위.** $Y\ge25000$($\mathfrak h\le\mathfrak h_0=0.0342$).

**산술 등급.** 방향 반올림 구간(mpmath 구간 산술 `iv`, 소수 $25$에서 $40$자리).

**결과.** $\mathsf w_0\ge0.71216801$($1600\times1200$ 격자).

**독립 재계산.** 〔구현 같은 코드 재실행; 범위 전체; 산술 방향 반올림 구간; 자료 기록·이 글〕 같은 격자로 다시 실행해 같은 값을 얻었다. 더 성긴 격자 $800\times600$($\tilde\varphi$는 $3200$개 셀)의 실행은 더 작은 하계를 내며 모순이 없다. 이 글을 쓰며 2026-11-13에 `ul_iv_fixed.py`를 $1600\times1200$·$800\times600$으로 실행해 $0.71216801$·$0.70623905$를 얻었다(`원고_자료/세션_재계산/r8a9b11e/outputs_fixed/`).

**자료.** `원고_자료/세션_재계산/r8a9b11e/ul_iv_fixed.py`(이 글의 코드; 인자 `25000 1600 1200 0.1 6400 4`), `원고_자료/세션_재계산/r8a9b11e/outputs_fixed/`; `records/r8a9b11e…/evidence/peer/ul_iv.py`, `outputs/ul_iv_1600x1200.txt`, `outputs/ul_iv_800x600.txt`.

**출처.** [r8a9b11e] §2.6, §6; `review/feedback.md` §3.3.

### D.{{D:zeta-constants}} 세 제타 상수 $\mathsf z_{1/2}$·$\mathsf z_{-1/2}$·$\mathsf z_{3/2}$의 인증 구간 (보조정리 {{5:zeta-constants}})

**확인하는 진술.** 보조정리 {{5:zeta-constants}}가 진술하는 세 구간 $\mathsf z_{1/2}\in[-1.46036,-1.46035]$, $\mathsf z_{-1/2}\in[-0.20789,-0.20788]$, $\mathsf z_{3/2}\in[2.61237,2.61238]$을 확인한다.

**식.** $\mathsf z_{3/2}$의 경우 정수 $N\ge2$와 $S:=\sum_{j<N}j^{-3/2}$에 대해 볼록 감소 함수 $f(x)=x^{-3/2}$의 적분 비교로
$$
S+2N^{-1/2}+\tfrac12N^{-3/2}\ \le\ \mathsf z_{3/2}\ \le\ S+2\bigl(N-\tfrac12\bigr)^{-1/2}
$$
이다. 하계는 사다리꼴 비교 $\int_N^\infty f\le\sum_{j\ge N}f(j)-\tfrac12f(N)$에서 나오고 상계는 중점 비교 $\sum_{j\ge N}f(j)\le\int_{N-1/2}^\infty f$에서 나온다. $\mathsf z_{-1/2}$와 $\mathsf z_{1/2}$의 경우에는 Euler–Maclaurin 공식(Graham–Knuth–Patashnik, *Concrete Mathematics*, 2nd ed., §9.5)에 따라
$$
\sum_{j\le N}\sqrt j=\tfrac23N^{3/2}+\mathsf z_{-1/2}+\tfrac12N^{1/2}+\tfrac1{24}N^{-1/2}+R'_N,\quad |R'_N|\le\tfrac1{1920}N^{-5/2};\qquad
\sum_{j\le N}j^{-1/2}=2\sqrt N+\mathsf z_{1/2}+\tfrac12N^{-1/2}-\tfrac1{24}N^{-3/2}+R_N,\quad |R_N|\le\tfrac1{384}N^{-7/2}
$$
이다($\sqrt x$, $x^{-1/2}$의 도함수들이 부호를 번갈므로 나머지는 첫 생략항의 절댓값 이하다).

**알고리즘.** 기록의 `cemaj_iv.py`는 함수 `zeta32`에서 $N=2000$의 부분합 $S$(지표 $1\le j\le1999$)를 구간 산술로 더하고 위의 두 상하계를 더해 $\mathsf z_{3/2}$의 구간을 만들며 $-\mathsf z_{-1/2}$는 상수 $0.2078862250607$로 둔다(참값 $0.20788622497735\ldots$보다 $8\times10^{-11}$ 큰 상계이고 그 코드에서 쓰이는 방향은 $\mathsf z_{-1/2}\ge-0.2079$뿐이다). 이 글의 재계산 `zeta_iv.py`는 세 상수를 모두 위의 식으로 $N=4000$에서 구간 산술로 평가하고 확인하는 진술의 세 구간에 들어 있는지 판정한다.

**범위.** 상수 셋이라 범위가 따로 없다.

**산술 등급.** 방향 반올림 구간(mpmath `iv`, 소수 $30$자리).

**결과.** `zeta32`($N=2000$)에서는 $\mathsf z_{3/2}\in[2.6123753479,2.6123753491]$이다. 이 글의 재계산($N=4000$)에서는 $\mathsf z_{3/2}\in[2.6123753485,2.6123753488]$, $\mathsf z_{-1/2}\in[-0.2078862249784,-0.2078862249773]$, $\mathsf z_{1/2}\in[-1.4603545088096,-1.4603545088095]$이고 셋 다 확인하는 진술의 구간 안에 있다. 이 구간이 쓰이는 곳은 8장의 정리 {{8:pieces-k-monotone}}·{{8:jensen-H-ii}}와 9장의 보조정리 {{9:psi-two-sided}}·{{9:psi-low}}이고 그 증명들에서는 진술의 끝값 $\mathsf z_{-1/2}\ge-0.20789$, $\mathsf z_{1/2}\ge-1.46036$, $\mathsf z_{3/2}\le2.61238$만 쓴다.

**독립 재계산.** 〔구현 같은 식의 새 구현; 범위 전체; 산술 방향 반올림 구간; 자료 이 글〕 이 글을 쓰며 2026-11-13에 `원고_자료/세션_재계산/zeta_constants/zeta_iv.py`(mpmath 구간 산술, 소수 $30$자리, $N=4000$)를 실행해 세 구간을 확인했다(출력 `zeta_iv_out.txt`). 사다리꼴 보정 없이 부분합 $\sum_{j\le N}j^{-3/2}$에 두 적분 상하계 $2(N+1)^{-1/2}$·$2(N+\tfrac12)^{-1/2}$만 더하는 더 성긴 방법으로는 $N=2000$에서 하단이 $2.6123698$이 되어 구간 $[2.61237,2.61238]$을 확인하지 못하므로 기록의 코드와 이 글의 재계산은 모두 위 식 항목의 사다리꼴 하계를 쓴다.

**자료.** `records/r8a9b11e…/evidence/peer/cemaj_iv.py`(함수 `zeta32`, 상수 `ZM12_ABS`), `emaj_upper_fixed.py`(상수 `ZETA32`, `ZETA12`, `ZETAm12`); `원고_자료/세션_재계산/zeta_constants/zeta_iv.py`, `zeta_iv_out.txt`.

**출처.** [r8a9b11e] §4.5.

### D.{{D:band-check}} 조립 범위의 포락선 검사 (명제 {{5:band-inequality}})

**확인하는 진술.** 조립 범위의 판정식은 그 범위의 모든 위치에서 성립해야 하고 D.{{D:band-check}}에서는 그 범위를 소구간으로 잘라 소구간마다 좌변의 하계를 잰다. 곧 $\lambda\in[1/2,2/3]$의 $4000$개 소구간(두 끝점을 $[\theta_a,\theta_b]$로 적는다) 각각에서 아래 다섯 포락선을 $n=50001$, $\mathsf w_0=0.71216$으로 평가한 $(5.53)$의 좌변 하계와 우변 $1$의 비가 $1.3558$ 이상이다.

**식.** $\bar\varrho=0.75(1.1\theta_bn)^{2/3}+1$, $\bar{\mathfrak c}_0=\dfrac{1.5\bigl((2\theta_b-1)n+2\bar\varrho\bigr)}{\theta_an\,((1-\theta_b)n-\bar\varrho)}$, $\bar\epsilon_0=\dfrac{1.5\bar\varrho\bigl((2\theta_b-1)n+2\bar\varrho\bigr)}{(\theta_an-1)((1-\theta_b)n-\bar\varrho)}$에 대해
$$
\begin{aligned}
&\mathrm{hov}(\rho_0,Q_{\mathrm w})\ \ge\ \sum_{z\ge0}\Bigl(\theta_a-\frac1n\Bigr)^z\Bigl(1-\frac2{\sqrt\pi}z^{3/2}\bigl(\lfloor0.3(1-\theta_b)n-1\rfloor-1\bigr)^{-1/2}\Bigr)_+\quad(\text{양의 항이 끝날 때까지 더한다}),\\
&\sum_{i\le Q_2}\mathrm{Bor}(i)-Q_2\pi_n(t_0-1)\ \ge\ 1-\sqrt{2/\pi}\,\bigl(0.3(1-\theta_b)n-1\bigr)^{-1/2}-0.3(1-\theta_a)n\cdot(2\pi)^{-1/2}\Bigl[\frac{n+1}{\theta_an\,((1-\theta_b)n-\bar\varrho)}\Bigr]^{3/2}e^{1/(12(n+1))},\\
&\mathrm{top}_\pi\ \le\ (2\pi)^{-1/2}(1+\tfrac1n)^{3/2}\theta_a^{-1/2}(1-\theta_b)^{-3/2}n^{-1/2}e^{1/(12n)},\\
&\tilde K\ \ge\ \theta_a\exp\Bigl(-\frac1{12(0.4(1-\theta_b)n-6(\theta_bn)^{2/3}+1)}-\frac1{12\theta_an}-\frac1{12(n+1)}\Bigr),\\
&\mathcal W\ \le\ (2\pi)^{-1/2}\tfrac23(\bar\varrho+1)^{3/2}\,\bar{\mathfrak c}_0\,\Bigl(1+\frac{\bar\varrho}{\theta_an}\Bigr)^{3/2}e^{\bar\epsilon_0+1/(12\theta_an)},
\end{aligned}
$$
그리고 다섯 포락선을 각자의 자리에 넣으면 $H^{\mathrm{lo}}\cdot\mathsf w_0\cdot\tilde K^{\mathrm{lo}}\cdot[2(\text{둘째 하계})-\mathrm{top}_\pi^{\mathrm{hi}}]-\mathcal W^{\mathrm{hi}}$가 된다. 첫 인자는 첫째 포락선의 값이고 위 첨자는 그 포락선이 하계인지 상계인지를 적은 것이다. 우변이 $1$이므로 이 좌변의 하계가 곧 비다.

**알고리즘.** 소구간 끝점을 정확한 다정밀도 수로 두고 각 소구간에서 따름정리 {{5:old-5-34}}의 조건 $0.4(1-\theta_b)n\ge6(\theta_bn)^{2/3}+1$을 확인한 뒤 하계 인자는 그 값을 감싼 구간의 아래 끝을, 상계 인자는 위 끝을 곱해 비의 하계를 구하고 소구간 전체의 최솟값을 낸다.

**범위.** $n=50001$(포락선의 $n$-단조성, 곧 하계 포락선은 증가하고 상계 포락선은 감소한다는 사실로 모든 $n\ge50001$을 덮으며 단조성은 명제의 증명에서 확인한다), $\lambda\in[1/2,2/3]$.

**산술 등급.** 방향 반올림 구간(mpmath `iv`, 소수 $30$자리).

**결과.** 최소 비 $1.355874$($\lambda\in[\frac12,\frac12+\frac1{24000}]$, 첫 소구간). 그 소구간의 값은 $\mathrm{hov}\ge1.957$, 둘째 포락선이 주는 꼭대기 행들의 무게 합의 하계 $\ge0.9885$, $\mathrm{top}_\pi\le0.00714$, $\tilde K\ge0.49998$, $\mathcal W\le0.0169$다(계산값 $1.9570106\ldots$, $0.9885536\ldots$, $0.0071375\ldots$, $0.4999889\ldots$, $0.0168737\ldots$). $(5.53)$에 필요한 것은 비 $\ge1$이므로 보증의 여유는 $0.3558$이고 $1.3558$은 계산값을 다섯째 자리에서 내린 표시값이다.

**독립 재계산.** 〔구현 같은 코드 재실행·같은 식의 새 구현; 범위 전체; 산술 방향 반올림 구간; 자료 기록·이 글〕 이 글을 쓰며 기록의 `band_iv.py`를 인자 `0.71216 0 4000`(둘째 인자는 우변에 더하는 항의 계수이고 $0$이면 우변이 $1$이다)으로 실행해 최소 비 $1.355874$와 위의 최악 소구간·다섯 계산값을 얻었다. 또 위 식에서 새로 쓴 구간 산술 코드(mpmath `iv`, 소수 $30$자리)로 $4000$개 소구간의 비를 모두 적고 그 표를 따로 읽어 소구간이 $[\frac12,\frac23]$을 빈틈없이 덮고 하계 $1.3558$ 미만인 소구간이 없으며 최솟값이 첫 소구간의 $1.3558740$(여유 $7.4\times10^{-5}$)임을 확인했다. 기록 [r8a9b11e]에서는 같은 코드를 우변에 $7.72(\theta_an-1)^{-1/3}$을 더한 더 강한 판정식으로 돌렸고 그때의 값 $1.072666$은 참고로 적어 두는 기록의 값이다. 조립 범위 밖인 오른쪽 부분(보조정리 {{5:right-part}})은 이 소구간 검사의 대상이 아니다. 거기서는 포락선 대신 손으로 계산한 네 상수로 판정식을 확인하며, 그 상수를 넣은 격자 대조가 `rplus.py`에 있어 함께 적어 둔다.

**자료.** `records/r8a9b11e…/evidence/peer/band_iv.py`, `rplus.py`, `outputs/rplus_out.txt`; `원고_자료/세션_재계산/band_check/band_iv.py`(기록 코드의 사본), `band_iv_out_CE0.txt`(인자 `0.71216 0 4000`의 실행), `band_cells.py`, `band_cells_CE0.tsv`(소구간별 비), `band_read.py`, `band_read_out_CE0.txt`.

**출처.** [r8a9b11e] §5.1, §5.2; `review/feedback.md` §0, §5.

### D.{{D:induction-rows}} 인증 행 자료의 첫 감소 수준 검사 (보조정리 {{5:old-5-38}})

**확인하는 진술.** 모든 $10001\le m\le20000$에서 행 $m$의 오른쪽 절반의 첫 감소 수준 $Y_0(m)$이 $m-\lfloor\frac34m^{2/3}\rfloor$ 이상이다.

**식.** 바닥 함수는 정수 산술로 계산한다. 곧 $\lfloor\frac34m^{2/3}\rfloor=\max\{f:64f^3\le27m^2\}$에서 최댓값을 정수 범위에서 잡는다.

**알고리즘.** 정리 {{5:old-5-1}}의 계산이 행마다 남긴 인증 자료에서 첫 감소 수준을 읽어 하계와 비교한다.

**범위.** $10001\le m\le20000$($10000$행).

**산술 등급.** 정확 정수·유리수.

**결과.** 위반 $0$, 최소 여유 $42$($m=10001$에서 $Y_0=9695$, 하계 $9653$).

**독립 재계산.** 〔구현 인증서 판독; 범위 전체; 산술 정확 정수·유리수; 자료 이 글〕 기록 [r58b4caa]에서는 같은 자료를 다시 읽어 확인했다. 이 글을 쓰며 같은 행 자료(SHA-256 `d35451d1…`)를 새로 쓴 판독기로 읽었다. $10000$행 모두에서 미결 위치가 없고 $\lceil(m-1)/2\rceil$부터 $Y_0(m)-1$까지가 모두 증가 인증 위치이며 $Y_0(m)$에서 감소가 인증됨을 확인했고 정수 바닥 함수로 구한 하계와 비교해 위반 $0$, 최소 여유 $42$($m=10001$에서 처음)를 다시 얻었다.

**자료.** 정리 {{5:old-5-1}}의 행 자료 `records/r19de912…/evidence/peer/cert/v2run20000-rows.tsv`(열 firstQ_ell, lastI_ell, I, Q, Qdec_cert, unimodal_right_cert; 사본 `원고_자료/r19de912/v2run20000-rows.tsv`); 검사는 [r58b4caa] §6·§9.5; `원고_자료/세션_재계산/induction_rows/induction_rows.py`, `induction_rows_out.txt`.

**출처.** [r58b4caa] §6, §9.5.

### D.{{D:lemma-H-interval}} 두 항 부등식의 전 영역 구간 산술 덮개 (정리 {{5:old-5-39}}, 보조정리 {{5:old-5-40}})

**확인하는 진술.** 두 항 부등식의 증명은 아래 적는 함수가 매개변수 영역 전체에서 양이라는 사실과 그 함수에 드는 상하계들의 부호 조건으로 귀결되었다. D.{{D:lemma-H-interval}}에서는 그 영역을 상자로 덮어 둘을 확인한다. 곧 영역 $\{0<\varsigma\le1,\ 0<\mathfrak K\le\min(1,\gamma^\ast/\varsigma)\}$, $\gamma^\ast=(1000/25001)^{1/6}$의 모든 점에서 $F\cdot\varsigma^7>0$이고 부호 조건 $\tilde I^{\mathrm{lo}}_0>\widetilde{\mathrm{arc}}_0$, $\tilde I^{\mathrm{lo}}_2>\widetilde{\mathrm{arc}}_2$(그리고 $y=k-1$에서의 같은 조건), $\tilde I^{\mathrm{lo}}_4>\widetilde{\mathrm{arc}}_4$, $\mathrm{lb}(\mathsf g^{\mathrm{lo}},k)>0$이 성립한다. 같은 사실이 $\gamma^\ast=(1000/10001)^{1/6}$의 영역에서도 성립한다.

**식.** $(5.55)$의 $F$. 아래 식의 보조 변수들은 상자의 기본 변수 둘의 거듭제곱으로 정해지며 그 관계식은 D.{{D:lemma-V-coefficients}}의 식 항목에 적는다. 보조정리 {{5:old-5-40}}의 정규화 구간은 차례로 $\tilde I^{\mathrm{lo}}_{2j}=1-\frac35(2j+5)\frac{\varepsilon^2}\eta-\frac{(1+\eta)^2\varepsilon^2}{54\eta^3}(2j+5)(2j+7)(2j+9)-\tilde{\mathcal T}_{2j}-\tilde{\mathcal O}_{2j}$, $\tilde I^{\mathrm{hi}}_{2j}=1+e^{\mathfrak c_{\mathrm H}}\frac{(1+\eta)\varepsilon^2}{4\eta^2}(2j+5)(2j+7)+\tilde{\mathcal O}_{2j}$이다. 여기에 드는 재료를 차례로 적는다. 상수는 $\mathfrak c_{\mathrm H}=\frac{6^{4/3}}4(\varepsilon^2/(1+\eta))^{1/3}$이다. 꼬리는 $\tilde{\mathcal T}_{2j}=4(2\mathrm{ex}_{\mathrm H})^{(2j+3)/2}e^{-\mathrm{ex}_{\mathrm H}}/((2j+3)!!\sqrt{2\pi})$, $\mathrm{ex}_{\mathrm H}=Q_k\upsilon^{\ast2}/2=5\cdot6^{2/3}(1+\eta)^{-2/3}/\mathfrak K^2$이다. 외부 꼬리 $\tilde{\mathcal O}_{2j}$는 세 조각(지수 $-(Q_k/2-(n+1)\upsilon^{\ast2})\upsilon^2$, $-3Q_k\upsilon^2/8$, $-Q_k\upsilon^2/4$의 홀수 거듭제곱 닫힌 꼴을 $Q_k^{3/2}/(n+1)=10\sqrt{10}/((1+\eta)\mathfrak K^3)$으로 정규화한 것)이다. 호는 $\widetilde{\mathrm{arc}}_{2j}=2\pi\,\mathrm{rad}(1+\mathrm{rad})^{2j+1}\cdot3/((2j+3)!!\sqrt{2\pi})\cdot\frac{Q_k^{3/2}}{n+1}Q_k^{(2j+2)/2}e^{-\mathrm{ex}_3}$, $\mathrm{ex}_3=Q_k^2/(4(n+1))=250/((1+\eta)\varsigma^2\mathfrak K^6)$, $\mathrm{rad}^2=1+\eta/(1+\eta)$이다. $\mathcal M^{\mathrm{lo}}_0\varsigma^5=\mathsf n^{\mathrm{lo}}_k\sqrt{2\pi}(1+\eta)(\tilde I^{\mathrm{lo}}_0-\widetilde{\mathrm{arc}}_0)$, $\mathsf g^{\mathrm{lo}}\varsigma^2=2\eta+5(\tilde I^{\mathrm{lo}}_2-\widetilde{\mathrm{arc}}_2)/(\tilde I^{\mathrm{hi}}_0+\widetilde{\mathrm{arc}}_0)$, Stirling 인자 $\mathsf n_k\in[(2\pi)^{-1/2}(1+\eta)^{3/2}(1-\frac32\varepsilon^2/(1+\eta)),\ (2\pi)^{-1/2}(1+\eta)^{3/2}e^{19\varepsilon^2/12}]$, $\mathrm{Bor}(k)k^{3/2}\ge(2\pi)^{-1/2}(1-\varepsilon^2/12)$, $\mathsf a_0\le12879/10000$, $\mathsf a_1\le939/1000$. 보조정리 {{5:old-5-41}}의 항들은 D.{{D:lemma-V-coefficients}}에 적은 식으로 계산한다. $y=k-1$의 부호 조건은 $\eta$를 $\eta+\varepsilon^2$로 바꾼 다항 부분과 $y=k$의 꼬리·호(둘 다 $Q_y$에 감소하므로 보수적)로 확인한다.

**알고리즘.** $\varsigma$-격자의 구간은 $[0,10^{-3}]$ 하나와 $10^{-3}$부터 $1$까지를 기하 $40$등분한 구간들이고 여기에 분할점 $\sqrt{1/2}$를 더한다. $\mathfrak K$-격자는 각 $\varsigma$-띠에서 $[0,\min(1,0.58480/\varsigma_{\mathrm{lo}})]$(위 끝의 상수는 확인하는 진술에 적힌 영역 경계 상수를 위로 반올림한 값)의 $4$등분으로 시작해 그렇게 생긴 직사각형 상자의 하계가 양이 아니거나 부호 조건이 확인되지 않으면 긴 변을 이분한다(깊이 $\le14$). 호 매개변수의 분지는 상자의 $\eta$ 범위로 정한다($\eta\le1/2$이면 $\eta/8$, $\eta\ge1/3$이면 $1/16$이고, 두 범위에 걸친 상자는 가른다). 다항 조각은 정확한 기호식을 구간으로 평가하고 지수적으로 작은 조각은 $u^me^{-u}$($u\ge m$)를 상자의 $u$ 하계에서 평가한다. $k\ge10001$ 판은 $\varsigma$ 기하 $60$등분, $\mathfrak K$ $6$등분, 깊이 $\le18$로 시작하고 $\varsigma_{\mathrm{lo}}\mathfrak K_{\mathrm{lo}}>(1000/10001)^{1/6}$인 상자를 정확 유리수 판정으로 버린다.

**범위.** $k\ge25001$, $\hat x\ge10$, $\eta\le1$(그리고 $k\ge10001$ 판).

**산술 등급.** 방향 반올림 구간(mpmath `iv`, $53$비트와 $113$비트 재평가).

**결과.** $k\ge25001$에서는 $218$회 평가, 이분을 멈춘 상자 $193$개 모두 통과, 실패 $0$, 상자마다 구한 확인 대상 곱의 하계 가운데 최솟값 $0.0466028$(중앙 근처의 큰 상자). $k\ge10001$에서는 $437$회 평가, 이분을 멈춘 상자 $402$개 통과, 영역 밖으로 버린 상자 $5$개, 실패 $0$, 최솟값 $0.00282$. 이분을 멈춘 상자들의 감사에서는 그 상자들이 영역을 정확 유리수로 빈틈없이 덮고($51$개와 $72$개 $\varsigma$-구간, 문제 $0$) 분지 조건이 정확 유리수 산술로 확인되며(첫째 판에서 $\theta_{\mathrm{arc}}=\eta/8$인 상자 $153$개는 $\varsigma_{\mathrm{hi}}^2\le1/2$, $1/16$인 상자 $40$개는 $\varsigma_{\mathrm{lo}}^2\ge1/3$) $113$비트 재평가에서도 모든 상자가 같은 결과로 통과한다. 코드의 두 `assert`(꼬리 부등식의 조건)는 필요한 조건보다 약하지만 전 영역에서 $\mathrm{ex}_{\mathrm H}\ge10.40>7$, $\sigma\upsilon_{\mathrm L}^2\ge31.25>13$으로 필요한 조건이 성립한다.

**독립 재계산.** 〔구현 같은 코드 재실행·다른 방법; 범위 전체; 산술 방향 반올림 구간·정확 정수·유리수·배정밀도 평가; 자료 기록〕 덮개와 감사를 재실행해 같은 값을 얻었고 인증 성분 $\mathcal M^{\mathrm{lo}}_0\le\mathcal M_0$, $\mathsf g^{\mathrm{lo}}\le\mathsf g_k(n)$, $[k^{5/2}\mathsf b_D]^{\mathrm{lo}}\le k^{5/2}\mathsf b_D$, $[k^{5/2}\mathsf b_J]^{\mathrm{hi}}\ge k^{5/2}\mathsf b_J$를 $k=25001$, $10^5$, $10^6$의 표본점에서 상하계로 바꾸기 전의 수직선 적분 값과 대조했으며 $k=10001$, $25001$의 $\hat x\ge10$ 전 범위에서 $F$가 독립 재귀로 구한 참값 $k^{5/2}(e_n-B_{n,k-1})/p_n$보다 작음(비 $0.55$ 이하)을 확인했다.

**자료.** `records/r5f5cf73…/evidence/producer/code/certify2.py`(SHA-256 `758c357c…`), `lemmaH_bounds.py`, `records/r5f5cf73…/evidence/producer/logs/certify_cover_full2.log`; `records/r5f5cf73…/evidence/peer/code/leaf_audit.py`, `cover_pruned.py`, `audit_pruned.py`, `compare_components.py`, `compare_F_truth.py`, `vertical_indep.py`, `records/r5f5cf73…/evidence/peer/logs/leaf_audit.log`, `cover_pruned_k10001.log`, `audit_pruned_k10001.log`, `leaves.json`, `leaves_k10001.json`. 재현: `cd evidence/producer/code; python -I certify2.py cover 40 4 1e-3 14`.

**출처.** [r5f5cf73] §5, §7, §7.1, §8; `review/feedback.md` §2.4, §2.8.

### D.{{D:lemma-V-coefficients}} 두 보정 상하계의 계수 생성 알고리즘 (보조정리 {{5:old-5-41}})

**확인하는 진술.** D.{{D:lemma-H-interval}}의 상자 평가에 드는 두 보정의 상하계는 보조정리 {{5:old-5-41}}의 항들로 이루어진다. D.{{D:lemma-V-coefficients}}에서는 그 항 $\mathrm{Main}_D$, $\mathrm{First}_D$, $\mathrm{Second}_D$, $\mathrm{Dg}_D$, $\mathrm{Rem}_D$, $\mathrm{Tail}_D$, $\mathrm{Arc}_D$, $\mathrm{Main}_J$, $\mathrm{Err}_J$, $\mathrm{Tail}_J$, $\mathrm{Arc}_J$의 닫힌 꼴을 만드는 방법을 적는다. 단항식 계수표는 어느 파일에도 저장되어 있지 않고 실행 때 정확 유리수로 생성된다.

**식.** 상자의 기본 변수는 $\varsigma$, $\mathfrak K$이고 D.{{D:lemma-H-interval}}의 식에 나온 보조 변수들은 $\eta=\varsigma^2$, $\varepsilon=\varsigma^3\mathfrak K^3/(10\sqrt{10})$, $k^{-1/3}=\varsigma^2\mathfrak K^2/10$으로 이 둘에서 정해진다. 적분 변수 $\upsilon$, $\rho$의 다항식 $p(\upsilon,\rho)=\sum c_{m,p}\upsilon^m\rho^p$와 Gauss 무게 $e^{-\sigma\upsilon^2}$에 대해 $\int_0^\infty\!\!\int_0^1p\,e^{-\sigma\upsilon^2}d\rho\,d\upsilon=\sum c_{m,p}\frac{\Gamma((m+1)/2)}{2\sigma^{(m+1)/2}}\cdot\frac1{p+1}$(기법 (ㄱ), 반모멘트). $e^{-\varrho^2/2}=e^{-\rho^2\upsilon^2/2}$가 붙은 항은 $\rho$를 먼저 적분한다(기법 (ㄴ)). 그 적분은 $\int_0^1\rho^{2i+1}e^{-\rho^2\upsilon^2/2}d\rho=\frac{i!}{2(\upsilon^2/2)^{i+1}}\bigl(1-e^{-\upsilon^2/2}\sum_{l\le i}\frac{(\upsilon^2/2)^l}{l!}\bigr)$이고 결과의 다항 부분은 무게 $e^{-\sigma\upsilon^2}$로, $e^{-\upsilon^2/2}$ 부분은 무게 $e^{-(\sigma+1/2)\upsilon^2}$으로 (ㄱ)을 쓴다. 그 밖에 같은 Gauss 인자가 붙은 항에는 $\varrho^2e^{-\varrho^2/2}\le2/e$를 쓴다(기법 (ㄷ)).

Dawson 가중 모멘트 $\mathfrak j_m(\eta)=(-2)^m\mathfrak F^{(m)}(\eta)$, $\mathfrak F(\sigma)=\sqrt{\pi/2}\sqrt\sigma/(\sigma+1)$는 기호 미분으로 얻고 $\mathcal Y_j(\eta)=4\sum_m\gamma_m(\eta)\mathfrak j_{m+1}(\eta)$의 $\gamma_m$은 $(s+\varrho^2)^{j/2}(s+s^2/4)/2$를 $s$의 다항식으로 펼쳐 $\int_0^\infty s^pe^{-\eta s/2}ds=p!(2/\eta)^{p+1}$로 적분해 얻는다. $\mathfrak C_{\mathrm I}(\eta)=8\sqrt{2\pi}\,\eta^{-3}(1+\eta)^{-3/2}-\frac{2(1+\eta)}3\int_0^\infty\tfrac12\bigl(\upsilon^{10}\,\mathfrak I_1(\upsilon)+\tfrac{\upsilon^{12}}4\mathfrak I_2(\upsilon)\bigr)e^{-\eta\upsilon^2/2}d\upsilon$, $\mathfrak I_i(\upsilon)=\int_0^1u(1-u)^ie^{-\upsilon^2u/2}du$($u=\rho^2$; 둘째 항은 (ㄴ)으로 적분한다).

$\mathrm{Rem}_D$의 세 부분은 $|\mathcal Q_3|(1+\epsilon_{\mathfrak f})$, $\epsilon_{\mathfrak f}(|\mathcal Q_1|+|\mathcal Q_2|)$, $2(2\pi)^{-1/2}|\epsilon_{\mathfrak f}-\frac{(n+1)\upsilon^4}{4k^2}|$에 무게 $\upsilon^4\rho^2Q_0e^{-\eta\upsilon^2/2}$를 곱한 것이다. $\epsilon_{\mathfrak f}$가 붙은 항에서는 무게가 $e^{\gamma_7\upsilon^2}$만큼 약해진 $e^{-7\eta\upsilon^2/16}$이 된다. 여기에 쓰는 상수는 $P_6$의 계수 $\frac59,\frac7{18},\frac{13}{12}\cdot\frac{49}{144}$, $\mathfrak c_{\mathrm T}=\frac19+\frac1{256}$, $\mathsf d_{\mathrm I}=\frac{204}{100}$, Dawson 상계 $8/\varrho^2$다.

꼬리의 단항식 $\upsilon^m\rho^p$ 계수 $c_{m,p}$는 보조정리의 증명에서 정확히 적분한 네 조각의 피적분함수 $\upsilon^4\rho^2Q_0(2(2\pi)^{-1/2}+\frac43\varepsilon\varrho^2+\varrho\psi_1+(2\pi)^{-1/2}\psi_1^2+2(2\pi)^{-1/2}\frac{(1+\eta)\varepsilon^2\upsilon^4}4)$에서 나온다. 꼬리 부등식의 매개변수는 분지 $\eta/8$에서 $\mathrm{ex}_4=\sigma\upsilon_{\mathrm L}^2=62.5/(\varsigma^2\mathfrak K^6)$, 분지 $1/16$에서 $\mathrm{ex}_4=31.25/(\varsigma^4\mathfrak K^6)$이고, 호의 $\mathrm{ex}_5=Q_k\theta_{\mathrm{arc}}/4$는 각각 $31.25/(\varsigma^2\mathfrak K^6)$, $15.625/(\varsigma^4\mathfrak K^6)$다.

$\mathrm{Err}_J$의 세 조각은 $\rho^5\upsilon^4|\mathrm{ph}_\rho|\varepsilon^2/4$, $\rho(1+\eta)\varepsilon^2\upsilon^5/5$, $\rho\varepsilon^2(|\mathrm{ph}_\rho|+(1+\eta)\varepsilon^2\upsilon^5/5)^3/6$에 $\upsilon^3$을 곱한 것이고 $\gamma_6$의 상계 $(1+\eta)/6-1/15+\varepsilon^2/15$를 쓴다.

**알고리즘.** sympy로 $(\varsigma,\mathfrak K)$의 정확한 기호식을 만들고(`Float` 상수 금지), 항별로 약분해 $\varsigma=0$에서 정칙한 꼴로 바꾼 뒤 상자마다 mpmath 구간 산술로 평가한다. 부호가 정해지지 않은 조각($\mathrm{First}_D$, $\mathrm{Second}_D$, $\mathrm{Dg}_D$)은 $\mathsf n_k$의 두 끝 값을 곱한 구간의 합집합을 쓰고 $\mathrm{Main}_D$와 주항은 $\mathsf n_k$, $\mathrm{Bor}(k)k^{3/2}$의 하계를, 빼는 조각은 상계를 쓴다.

**범위.** D.{{D:lemma-H-interval}}과 같다.

**산술 등급.** 정확 정수·유리수(계수 생성). 상자 평가의 방향 반올림 구간은 D.{{D:lemma-H-interval}}의 것이다.

**결과.** 닫힌 꼴 조각 $\mathrm{Main}_D$, $\mathrm{First}_D$, $\mathrm{Second}_D$, $\mathrm{Dg}_D$, $\mathrm{Rem}_D$, $\mathrm{Main}_J$, $\mathrm{Err}_J$와 $\epsilon_{\mathfrak f}$ 교차항의 값이 $(\varsigma,\mathfrak K)$의 여섯 표본점($\eta\in[0.01,1]$, $\hat x\in[10,62.5]$)에서 직접 구적한 값과 상대 오차 $2\times10^{-13}$ 안에서 같다. $k=25001$, $\hat x=10$에서 $k^{5/2}\mathsf b_D\in[51.7,88.1]$(독립 수치 적분값은 $70.6$), $k^{5/2}\mathsf b_J\le57.0$(독립 수치 적분값은 $52.8$)이다.

**독립 재계산.** 〔구현 다른 방법; 범위 표본; 산술 배정밀도 평가; 자료 기록〕 $\mathrm{Main}$, $\mathrm{First}$, $\mathrm{Second}$, $\mathrm{Dg}$, $\mathrm{Rem}$의 기호식의 값을 독립 구적으로 $10^{-14}$ 안에서 재현했고 본문이 쓰는 상수 $\mathsf d_{\mathrm I}=2.04$와 호의 앞인자 $3$이 코드의 값과 같음을 확인했다.

**자료.** `records/r5f5cf73…/evidence/producer/code/certify2.py`(함수 `int_poly`, `int_poly_rhoexp`, `J_m`, `D_j`, `C1_closed`, `regularise`, `IVEval`, `Xm_exp_dec`, `evaluate_box`), `closed_forms4.py`, `lemmaV2.py`, `vertical_exact2.py`; `records/r5f5cf73…/evidence/peer/code/check_pieces.py`, `records/r5f5cf73…/evidence/peer/logs/check_pieces.log`.

**출처.** [r5f5cf73] §6.1에서 §6.7까지, §7, §9; `review/feedback.md` §2.5에서 §2.8까지.
