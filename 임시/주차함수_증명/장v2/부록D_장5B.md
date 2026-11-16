### D.{{D:window-mass-constant}} 가중 창 질량의 균일 상수 $\mathsf w_0$의 구간 산술 인증 (정리 {{5:old-5-32}})

**확인하는 진술.** 정리의 증명에서 가중 창 질량의 하계는 두 함수의 적분으로 적혔고 이 항목에서는 그 두 함수를 단봉 계단 함수로 바꾸어 그 하계를 수치로 확인한다. 그러기 위해 $\mathfrak h_0=0.0342$, $\upsilon_{\max}=\sqrt{6\mathfrak h_0}$, $\mathfrak c_2=1/(2(1-\upsilon_{\max}))$로 둔다. $\theta\in[0,4.1]$의 $1600$개 셀에서 잰 $\mathfrak g$의 하계로 단봉 계단 함수 $\tilde\psi$를, $\theta\in[0,12]$의 $6400$개 셀에서 잰 $\bar\varrho$의 상계로 단봉 계단 함수 $\tilde\varphi$를 만든다. 확인하는 부등식은
$$
\Bigl(\int_0^{4.1}\tilde\psi-\mathfrak h_0\max\tilde\psi\Bigr)-\mathfrak h_0\Bigl(\int_0^{12}\tilde\varphi+\mathfrak h_0\max\tilde\varphi+e^{-12+\mathfrak h_0}\Bigr)-\mathfrak O(25000)\ \ge\ 0.71216 .
$$

**식.** 두 계단 함수로 바꾸기 전의 두 피적분함수, 곧 하계를 잴 함수와 상계를 잴 함수는 아래 성분들로 이루어진다.
$$
\begin{aligned}
P_{\min}(\kappa)&=\Bigl(\sqrt{2/\pi}\,(\kappa+\mathfrak h_0^2)^{-1/2}e^{-\mathfrak h_0^2/(12(\kappa+\mathfrak h_0^2))}-1.6\,\mathfrak h_0\sqrt\kappa\Bigr)_+,\qquad
\mathfrak b_{\min}(\theta)=\exp\bigl(-\theta^{3/2}-\mathfrak c_2\theta^2\mathfrak h_0\bigr),\qquad \mu(\theta,\kappa)=6-\kappa-\theta\mathfrak h_0,\\
\mathrm{ti}(\varsigma,\mathfrak b;\mu)&=\frac12\sqrt{\frac\pi{\mathfrak b}}\Bigl[e^{-2\sqrt{\varsigma\mathfrak b}}\operatorname{erfc}\bigl(\sqrt{\varsigma\mu}-\sqrt{\mathfrak b/\mu}\bigr)-e^{2\sqrt{\varsigma\mathfrak b}}\operatorname{erfc}\bigl(\sqrt{\varsigma\mu}+\sqrt{\mathfrak b/\mu}\bigr)\Bigr],\\
\mathcal T_{\max}(\theta,\mu)&=\frac{\theta}{\sqrt{2\pi}}\,e^{\theta^3\mathfrak h_0/(3\mu^2)}\Bigl[\mathfrak h_0^2\,\mu^{-3/2}e^{-(\theta-\mathfrak h_0)_+\mu/2-\theta^2/(2\mu)}+\mathrm{ti}\Bigl(\frac{(\theta-\mathfrak h_0)_+}2,\frac{\theta^2}2;\mu\Bigr)\Bigr]\qquad(\mu\ge\theta^2/3),\\
\mathfrak Q(\theta,\kappa)&=P_{\min}(\kappa)\,e^{-\theta\kappa-\theta\mathfrak h_0^2}\,(1-\kappa\mathfrak h_0-\mathfrak h_0^3)\,\bigl(\mathfrak b_{\min}(\theta)-\mathcal T_{\max}(\theta,\mu(\theta,\kappa))\bigr)_+,\qquad
\mathfrak g(\theta)=\theta\int_0^{6-\theta\mathfrak h_0}\mathfrak Q(\theta,\kappa)\,d\kappa,\\
\mathfrak y(\theta)&=\max(\theta/2,\theta-\mathfrak h_0),\qquad
\bar\varrho(\theta)=\sqrt2\,\theta^{3/2}\exp\Bigl(-\theta\sqrt{\mathfrak y(\theta)}+\tfrac13\min\bigl(\theta^2\mathfrak h_0,\,\upsilon_{\max}\theta^{3/2}\bigr)\Bigr)\frac{1+\min(\theta\mathfrak h_0^2,\,6\mathfrak h_0)}{\sqrt{\mathfrak y(\theta)}-\tfrac13\min\bigl(\theta\mathfrak h_0,\,\upsilon_{\max}\sqrt\theta\bigr)},\\
\mathfrak O(Y)&=\frac1{Y^2}\sqrt{\frac{12}\pi}\,Y^{1/3}\sqrt{\frac2Y}\,(Y+1)\qquad(Y=25000\text{에서 평가}).
\end{aligned}
$$
$\mu(\theta,\kappa)<\theta^2/3$인 $(\theta,\kappa)$에서는 $\mathfrak Q$의 마지막 인자를 $0$으로 둔다. $\mathcal T_{\max}$의 대괄호 안 인자 $e^{-(\theta-\mathfrak h_0)_+\mu/2}$는 보조정리 {{5:bt-tail}}(나)의 $e^{-\varsigma\mathfrak W_0}$에 $\varsigma=\varsigma_z=(\theta-\mathfrak h)\mathfrak h^2/2$를 넣고 $\mathfrak W_0\mathfrak h^2\ge\mu$를 쓴 것(보조정리 {{5:scaled-integrand}}(라)의 증명)에서 온 $\mu$의 함수다. 아래 알고리즘에서 $1$로 대신하는 인자는 이 인자가 아니라 꼬리 인자 $e^{-\varsigma_zz}=e^{-(\theta-\mathfrak h)\theta\mathfrak h/2}$(같은 증명의 $e^{-\varsigma_zz}\le1$)이며 위의 식에는 그 꼬리 인자가 이미 빠져 있다.

**알고리즘.** 셀마다 피적분함수의 하계를 잡기 위해 세 변수를 격자로 나눈다. $\theta$-격자는 $1600$개 셀($[0,4.1]$), $\omega$-격자는 $1200$개 셀($\kappa=\omega^2$, $\omega\in[0,\sqrt6]$), $\mu$-격자는 간격 $0.1$이며 셀의 $\mu$ 하계는 격자 아래 끝으로 내린다. 셀 $[\theta_a,\theta_b]\times[\omega_j,\omega_{j+1}]$에서 $2\omega P_{\min}(\omega^2)$의 첫 항은 $\omega_j$에서, 뺄 항은 $\omega_{j+1}$에서, $e^{-\theta\kappa-\theta\mathfrak h_0^2}$와 $1-\kappa\mathfrak h_0-\mathfrak h_0^3$은 $(\theta_b,\kappa_{j+1})$에서, $\mathfrak b_{\min}$은 $\theta_b$에서, $\mathcal T_{\max}$는 인자별로 불리한 끝에서 평가한다(보조정리 {{5:scaled-integrand}}의 단조 방향). $\theta$ 자리에는 앞 인자 $\theta$와 지수 $e^{\theta^3\mathfrak h_0/(3\mu^2)}$에서는 $\theta_b$를 넣고, 지수 $e^{-(\theta-\mathfrak h_0)_+\mu/2-\theta^2/(2\mu)}$와 $\mathrm{ti}$의 두 인수에서는 $\theta_a$를 넣는다. $\mu$ 자리에는 $e^{-\theta^2/(2\mu)}$에서는 격자 위 끝을 넣고 $\mu^{-3/2}$, $e^{-(\theta-\mathfrak h_0)_+\mu/2}$, $e^{\theta^3\mathfrak h_0/(3\mu^2)}$, $\mathrm{ti}$에서는 격자 아래 끝을 넣는다. $\mu$의 하계가 $\theta_b^2/3$보다 작은 셀은 버리고 $\theta>4.1$인 범위는 쓰지 않는다. 셀 하계로 $\tilde\psi$를, $\bar\varrho$의 셀 상계($6400$개 셀로 나누어 $\mathfrak y(\theta)$는 왼쪽 끝에서, 나머지 인자는 각각 불리한 끝에서 잰 것)으로 $\tilde\varphi$를 만든다. 하계 쪽은 하계가 가장 큰 셀을 봉우리로 삼아 봉우리 왼쪽에서는 오른쪽으로부터의 누적 최소로 바꾸고 오른쪽에서는 왼쪽으로부터의 누적 최소로 바꾸며, 상계 쪽은 상계가 가장 큰 셀을 봉우리로 삼아 그 왼쪽은 왼쪽 끝에서부터 누적 최대로 바꾸고 오른쪽은 오른쪽 끝에서부터 누적 최대로 바꾸어 둘 다 단봉이 되게 한 뒤 보조정리 {{5:riemann-unimodal}}을 쓴다. $\operatorname{erf}$는 교대 Taylor 급수를 항이 감소하기 시작한 뒤 첫 생략항이 $10^{-42}$ 아래가 될 때 끊고 그 항을 나머지로 더하며, 증가함수이므로 구간 입력에는 끝점 값을 쓴다. 이 글의 코드 `ul_iv_fixed.py`는 $\mathcal T_{\max}$의 꼬리 인자 $e^{-\varsigma_zz}=e^{-(\theta-\mathfrak h)\theta\mathfrak h/2}$를 $1$로 두고 앞 상수 $1/\sqrt{2\pi}$는 남긴다. 기록의 `ul_iv.py`와는 이 인자를 두는 한 줄만 다르다.

**범위.** $Y\ge25000$($\mathfrak h\le\mathfrak h_0=0.0342$).

**산술 등급.** 방향 반올림 구간(mpmath 구간 산술 `iv`, 소수 $40$자리).

**결과.** $\mathsf w_0\ge0.71216801$($1600\times1200$ 격자).

**독립 재계산.** 〔구현 같은 코드 재실행; 범위 전체; 산술 방향 반올림 구간; 자료 이 글〕 기록의 검토가 기록의 `ul_iv.py`에서 위의 한 줄을 고친 코드로 $1600\times1200$·$800\times600$ 격자에서 $0.71216801$·$0.70624$를 얻었다. 그 코드와 출력은 기록에 보존되어 있지 않고 결과만 기록의 `review/feedback.md` §3.3에 적혀 있다. 이 글을 쓰며 2026-11-13에 같은 수정을 한 `ul_iv_fixed.py`를 같은 두 격자로 실행해 $0.71216801$·$0.70623905$를 얻었다(`원고_자료/세션_재계산/r8a9b11e/outputs_fixed/`). 더 성긴 격자 $800\times600$($\tilde\varphi$는 $3200$개 셀)의 실행은 더 작은 하계를 내며 모순이 없다.

**자료.** `원고_자료/세션_재계산/r8a9b11e/ul_iv_fixed.py`(이 글의 코드; 기록의 `ul_iv.py`와 115행 한 줄만 다르다; 인자 `25000 1600 1200 0.1 6400 4`), `원고_자료/세션_재계산/r8a9b11e/outputs_fixed/`; `records/r8a9b11e…/evidence/peer/ul_iv.py`.

**출처.** [r8a9b11e] §2.6, §6; `review/feedback.md` §3.3.

### D.{{D:band-check}} 조립 범위의 포락선 검사 (명제 {{5:band-inequality}})

**확인하는 진술.** 조립 범위의 판정식은 그 범위의 모든 위치에서 성립해야 하고 이 항목에서는 그 범위를 셀로 잘라 셀마다 좌변의 하계를 잰다. 곧 $\lambda\in[1/2,2/3]$의 $4000$개 셀(두 끝점을 $[\lambda_a,\lambda_b]$로 적는다) 각각에서 아래 다섯 포락선을 $n=50001$, $\mathsf w_0=0.71216$으로 평가한 $(5.4)$의 좌변 하계와 우변 $1$의 비가 $1.3558$ 이상이다.

**식.** $\overline{\mathrm{wid}}=0.75(1.1\lambda_bn)^{2/3}+1$, $\bar{\mathfrak c}_1=\dfrac{1.5\bigl((2\lambda_b-1)n+2\,\overline{\mathrm{wid}}\bigr)}{\lambda_an\,((1-\lambda_b)n-\overline{\mathrm{wid}})}$, $\bar\epsilon_0=\dfrac{1.5\,\overline{\mathrm{wid}}\bigl((2\lambda_b-1)n+2\,\overline{\mathrm{wid}}\bigr)}{(\lambda_an-1)((1-\lambda_b)n-\overline{\mathrm{wid}})}$에 대해
$$
\begin{aligned}
&\mathrm{hov}(\rho_0,\chi_{\mathrm w})\ \ge\ \sum_{z\ge0}\Bigl(\lambda_a-\frac1n\Bigr)^z\Bigl(1-\frac2{\sqrt\pi}z^{3/2}\bigl(\lfloor0.3(1-\lambda_b)n-1\rfloor-1\bigr)^{-1/2}\Bigr)_+\quad(\text{양의 항이 끝날 때까지 더한다}),\\
&\sum_{i\le\chi_2}\mathrm{Bor}(i)-\chi_2\pi_n(t_0-1)\ \ge\ 1-\sqrt{2/\pi}\,\bigl(0.3(1-\lambda_b)n-1\bigr)^{-1/2}-0.3(1-\lambda_a)n\cdot(2\pi)^{-1/2}\Bigl[\frac{n+1}{\lambda_an\,((1-\lambda_b)n-\overline{\mathrm{wid}})}\Bigr]^{3/2}e^{1/(12(n+1))},\\
&\mathrm{top}_\pi\ \le\ (2\pi)^{-1/2}(1+\tfrac1n)^{3/2}\lambda_a^{-1/2}(1-\lambda_b)^{-3/2}n^{-1/2}e^{1/(12n)},\\
&\tilde K\ \ge\ \lambda_a\exp\Bigl(-\frac1{12(0.4(1-\lambda_b)n-6(\lambda_bn)^{2/3}+1)}-\frac1{12\lambda_an}-\frac1{12(n+1)}\Bigr),\\
&\mathcal W\ \le\ (2\pi)^{-1/2}\tfrac23(\overline{\mathrm{wid}}+1)^{3/2}\,\bar{\mathfrak c}_1\,\Bigl(1+\frac{\overline{\mathrm{wid}}}{\lambda_an}\Bigr)^{3/2}e^{\bar\epsilon_0+1/(12\lambda_an)},
\end{aligned}
$$
그리고 다섯 포락선을 각자의 자리에 넣으면 $\mathrm{hov}^{\mathrm{lo}}\cdot\mathsf w_0\cdot\tilde K^{\mathrm{lo}}\cdot[2(\text{둘째 하계})-\mathrm{top}_\pi^{\mathrm{hi}}]-\mathcal W^{\mathrm{hi}}$가 된다. 첫 인자는 첫째 포락선의 값이고 위 첨자는 그 포락선이 하계인지 상계인지를 적은 것이다. 우변이 $1$이므로 이 좌변의 하계가 곧 비다.

**알고리즘.** 셀 끝점을 정확한 유리수로 두고(구간 산술에는 그 유리수를 담는 구간으로 넣는다) 각 셀에서 따름정리 {{5:old-5-34}}의 조건 $0.4(1-\lambda_b)n\ge6(\lambda_bn)^{2/3}+1$을 확인한 뒤 하계 인자는 그 값을 감싼 구간의 아래 끝을, 상계 인자는 위 끝을 곱해 비의 하계를 구하고 셀 전체의 최솟값을 낸다.

**범위.** $n=50001$(포락선의 $n$-단조성, 곧 하계 포락선은 증가하고 상계 포락선은 감소한다는 사실로 모든 $n\ge50001$을 덮으며 단조성은 명제의 증명에서 확인한다), $\lambda\in[1/2,2/3]$.

**산술 등급.** 방향 반올림 구간(mpmath `iv`, 소수 $30$자리).

**결과.** 최소 비 $1.355874$($\lambda\in[\frac12,\frac12+\frac1{24000}]$, 첫 셀). 그 셀의 값은 $\mathrm{hov}\ge1.957$, 둘째 포락선이 주는 꼭대기 행들의 무게 합의 하계 $\ge0.9885$, $\mathrm{top}_\pi\le0.00714$, $\tilde K\ge0.49998$, $\mathcal W\le0.0169$다(계산값 $1.9570106\ldots$, $0.9885536\ldots$, $0.0071375\ldots$, $0.4999889\ldots$, $0.0168736\ldots$). $(5.4)$에 필요한 것은 비 $\ge1$이므로 보증의 여유는 $0.3558$이고 $1.3558$은 계산값을 다섯째 자리에서 내린 표시값이다.

**독립 재계산.** 〔구현 같은 식의 새 구현·같은 코드 재실행; 범위 전체; 산술 방향 반올림 구간; 자료 기록·이 글〕 위의 「결과」는 이 글을 쓰며 위 식에서 새로 쓴 구간 산술 코드(셀 끝점은 정확한 유리수, mpmath `iv` 소수 $30$자리)로 $4000$개 셀의 비의 하계를 모두 적고 그 표를 따로 읽어 얻은 것이다. 그 판독은 셀이 $[\frac12,\frac23]$을 빈틈없이 덮고 하계 $1.3558$ 미만인 셀이 없으며 최솟값이 첫 셀의 $1.3558739652$(여유 $7.4\times10^{-5}$)임을 확인한다. 기록의 `band_iv.py`를 같은 인자 `0.71216 0 4000`(둘째 인자는 우변에 더하는 항의 계수이고 $0$이면 우변이 $1$이다)으로 다시 실행한 출력도 같은 첫 셀에서 최소 비 $1.355874$와 위의 다섯 계산값을 주어 표시 자리에서 일치한다.

**자료.** `records/r8a9b11e…/evidence/peer/band_iv.py`; `원고_자료/세션_재계산/band_check/band_cells.py`(이 글의 코드), `band_cells_CE0.tsv`(셀별 비의 하계), `band_read.py`, `band_read_out_CE0.txt`(판독); `band_iv.py`(기록 코드의 사본), `band_iv_out_CE0.txt`(인자 `0.71216 0 4000`의 실행).

**출처.** [r8a9b11e] §5.1; `review/feedback.md` §0, §5.1.
