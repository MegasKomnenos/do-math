### D.{{D:window-mass-constant}} 가중 창 질량의 균일 상수 $\mathsf w_0$의 구간 산술 인증 (정리 {{5:old-5-32}})

**확인하는 진술.** $\mathfrak h_0=0.0342$, $\upsilon_{\max}=\sqrt{6\mathfrak h_0}$, $\mathfrak c_1=1/(2(1-\upsilon_{\max}))$에 대해, $\theta\in[0,4.1]$의 $1600$개 셀에서 잰 $\mathfrak g$의 하한으로 만든 단봉 계단 함수 $\tilde\psi$와 $\theta\in[0,12]$의 $6400$개 셀에서 잰 $\bar\varrho$의 상한으로 만든 단봉 계단 함수 $\tilde\varphi$에 대해
$$
\Bigl(\int_0^{4.1}\tilde\psi-\mathfrak h_0\max\tilde\psi\Bigr)-\mathfrak h_0\Bigl(\int_0^{12}\tilde\varphi+\mathfrak h_0\max\tilde\varphi+e^{-12+\mathfrak h_0}\Bigr)-\mathfrak O(25000)\ \ge\ 0.71216 .
$$

**식.** 피적분함수의 모든 성분은 다음과 같다.
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
$\mu(\theta,\kappa)<\theta^2/3$인 $(\theta,\kappa)$에서는 $\mathfrak Q$의 마지막 인자를 $0$으로 둔다. $\mathcal T_{\max}$의 대괄호 안 인자 $e^{-(\theta-\mathfrak h_0)_+\mu/2}$는 보조정리 {{5:bt-tail}}(나)의 $e^{-\sigma\mathfrak W_0}$($\sigma=(\theta-\mathfrak h)/2$, $\mathfrak W_0\mathfrak h^2\ge\mu$)에서 온 것으로 $\mu$의 함수이고, 아래 알고리즘이 $1$로 대신하는 꼬리 인자 $e^{-(\theta-\mathfrak h_0)_+\theta/2}$(보조정리 {{5:scaled-integrand}}(라) 증명의 $e^{-\varsigma_zz}\le1$)와는 다른 인자다.

**알고리즘.** $\theta$-격자 $1600$칸($[0,4.1]$), $\sigma$-격자 $1200$칸($\kappa=\sigma^2$, $\sigma\in[0,\sqrt6]$), $\mu$-격자 간격 $0.1$(셀의 $\mu$ 하계를 격자 아래 끝으로 내림). 셀 $[\theta_a,\theta_b]\times[\sigma_j,\sigma_{j+1}]$에서 $2\sigma P_{\min}(\sigma^2)$의 첫 항은 $\sigma_j$에서, 뺄 항은 $\sigma_{j+1}$에서, $e^{-\theta\kappa-\theta\mathfrak h_0^2}$와 $1-\kappa\mathfrak h_0-\mathfrak h_0^3$은 $(\theta_b,\kappa_{j+1})$에서, $\mathfrak b_{\min}$은 $\theta_b$에서, $\mathcal T_{\max}$는 $\theta_b$와 $\mu$의 격자 아래 끝에서 인자별로 평가한다(보조정리 {{5:scaled-integrand}}의 단조 방향). $\mu$의 하계가 $\theta_b^2/3$보다 작은 셀과 $\theta>4.1$은 버린다. 셀 하한으로 $\tilde\psi$를, $\bar\varrho$의 셀 상한($6400$칸; $\mathfrak y(\theta)$는 왼쪽 끝, 나머지 인자는 각각 불리한 끝)으로 $\tilde\varphi$를 만들고 보조정리 {{5:riemann-unimodal}}을 쓴다. $\operatorname{erf}$는 교대 Taylor 급수를 항이 감소하기 시작한 뒤 첫 생략항이 $10^{-42}$ 아래가 될 때 끊고 그 항을 나머지로 더하며, 증가함수이므로 구간 입력에는 끝점 값을 쓴다. 실행 코드에서 $\mathcal T_{\max}$의 꼬리 인자 $e^{-(\theta-\mathfrak h_0)_+\theta/2}$는 자명한 상계 $1$로 대신한다(`ul_iv.py` 115행 `pref = SQ2PI_INV * iv.exp(-iv.mpf(dlo) * Za / 2)`를 `pref = SQ2PI_INV`로 바꾼 판; 앞 상수 $1/\sqrt{2\pi}$는 남긴다).

**범위.** $Y\ge25000$($\mathfrak h\le\mathfrak h_0=0.0342$).

**산술 등급.** 방향 반올림 구간(mpmath 구간 산술 `iv`, 소수 $25$–$40$자리).

**결과.** $\mathsf w_0\ge0.71216801$($1600\times1200$ 격자).

**독립 재계산.** 같은 격자로 다시 실행해 같은 값을 얻었다. 더 성긴 격자 $800\times600$($\tilde\varphi$는 $3200$칸)의 실행은 더 작은 하계를 내며 모순이 없다. 세션이 2026-11-13에 같은 수정판을 $1600\times1200$·$800\times600$으로 다시 실행해 $0.71216801$·$0.70623905$를 얻었다(`원고_자료/세션_재계산/r8a9b11e/outputs_fixed/`).

**자료.** `records/r8a9b11e…/evidence/peer/ul_iv.py`(115행을 `pref = SQ2PI_INV`로 바꾼 판 `원고_자료/세션_재계산/r8a9b11e/ul_iv_fixed.py`을 인자 `25000 1600 1200 0.1 6400 4`로 실행), `outputs/ul_iv_1600x1200.txt`, `outputs/ul_iv_800x600.txt`, `원고_자료/세션_재계산/r8a9b11e/outputs_fixed/`.

**출처.** [r8a9b11e] §2.6, §6; `review/feedback.md` §3.3.

### D.{{D:column-moment-constant}} 열 1차 모멘트 상수 $\mathsf C_E$의 세 영역 구간 산술 인증 (정리 {{5:old-5-37}})

**확인하는 진술.** $C_{\mathrm I}\le6.0961$, $\mathfrak h_0C_{\mathrm{II}}\le0.1153$, $C_{\mathrm{III}}\le1.5034$, 따라서 $C_{\mathrm I}+\mathfrak h_0C_{\mathrm{II}}+C_{\mathrm{III}}+2\times10^{-10}\le7.7148$.

**식.** 영역 I. 조각 경계 $\mathfrak k_0,\dots,\mathfrak k_{13}=0,\frac1{16},\frac18,\frac14,\frac38,\frac12,\frac34,1,\frac32,2,3,4,5,6$; 조각 $i$에서 $\mathfrak p_i=\log2/(1+\min(\mathfrak k_{i+1}\mathfrak h_0+\mathfrak h_0^3,1))$, $u_i=\min(\mathfrak k_{i+1}\mathfrak h_0,1)$, $\varrho_i=\log(1+u_i)/u_i$, $\Upsilon^{(i)}_1=2(2\mathfrak p_i)^{-1/2}$, $\Upsilon_{\mathrm{lin}}=1/(3(1-\mathfrak c_3))$, $\mathfrak c_3=0.05$, $\Upsilon^{(i)}_2=\mathsf z_{3/2}(2\mathfrak p_i)^{-3/2}$, $\Upsilon^{(i)}_{\log}=1.2(2\mathfrak p_i)^{-1}$, $\mathfrak s_1=\sqrt{2/\pi}$, $\mathfrak s_2=(2\pi)^{-1/2}\frac23(1+\mathfrak h_0^3)^{3/2}$, $\mathfrak A_{00}=1.5\mathfrak s_1+1.3\mathfrak s_2+1.3\Upsilon^{(i)}_2-1.5/(\sqrt{2\log2}(1+\mathfrak h_0^3))$;
$$
\bar{\mathcal P}_i(\theta)=\exp\Bigl(-\sqrt{2\mathfrak p_i}\Bigl[\tfrac23(\theta-\mathfrak h_0)_+^{3/2}+\tfrac12(\theta-\mathfrak h_0)_+^{1/2}\mathfrak h_0\Bigr]-\mathsf z_{-1/2}\sqrt{2\log2}\,\mathfrak h_0^{3/2}+\tfrac{\log2}3\mathfrak h_0\theta^2\Bigr),\qquad
\Xi_i(\theta,\varkappa)=\exp\Bigl(-\varrho_i\frac{\varkappa(\theta-\mathfrak h_0)_+}{1+\mathfrak h_0^3}\Bigr),
$$
열다섯 단항식 $\mathfrak L_i(\theta,\varkappa)=\sum\mathfrak A\,\varkappa^\alpha\theta^p$:

| 번호 | 계수 $\mathfrak A$ | $\varkappa^\alpha\theta^p$ |
|---|---|---|
| 1 | $1.5$ | $\varkappa$ |
| 2 | $\mathfrak h_0^{1/2}\mathfrak A_{00}$ | $1$ |
| 3 | $1.3\mathfrak h_0$ | $\varkappa^2$ |
| 4 | $2.6\mathfrak s_1\mathfrak h_0^{3/2}$ | $\varkappa$ |
| 5 | $1.5\Upsilon^{(i)}_1$ | $\theta^{1/2}$ |
| 6 | $1.5\Upsilon_{\mathrm{lin}}\mathfrak h_0$ | $\theta$ |
| 7 | $2.6\mathfrak h_0\Upsilon^{(i)}_1$ | $\varkappa\theta^{1/2}$ |
| 8 | $2.6\mathfrak h_0^2\Upsilon_{\mathrm{lin}}$ | $\varkappa\theta$ |
| 9 | $2.6\mathfrak s_1\mathfrak h_0^{3/2}\Upsilon^{(i)}_1$ | $\theta^{1/2}$ |
| 10 | $2.6\mathfrak s_1\mathfrak h_0^{5/2}\Upsilon_{\mathrm{lin}}$ | $\theta$ |
| 11 | $1.3\mathfrak h_0(\Upsilon^{(i)}_1)^2$ | $\theta$ |
| 12 | $2.6\mathfrak h_0^2\Upsilon^{(i)}_1\Upsilon_{\mathrm{lin}}$ | $\theta^{3/2}$ |
| 13 | $1.3\mathfrak h_0^3\Upsilon_{\mathrm{lin}}^2$ | $\theta^2$ |
| 14 | $1.3\Upsilon^{(i)}_{\log}\mathfrak h_0^2(1+\log(1/\mathfrak h_0))$ | $1$ |
| 15 | $1.3\Upsilon^{(i)}_{\log}\mathfrak h_0^2$ | $\log_+\theta$ |

$$
C_{\mathrm I}=\sqrt{2/\pi}\,e^{\mathfrak h_0^3/12}\sum_{i=0}^{12}\sum_{\text{단항식}}\mathfrak A\int_0^{\infty}\!\!\int_{(\mathfrak k_i-\mathfrak h_0^2)_+}^{\mathfrak k_{i+1}}\mathfrak R_\alpha(\varkappa)\,(\theta+\mathfrak h_0)^{1+p}\sup_{[\theta,\theta+\mathfrak h_0]}\bar{\mathcal P}_i\cdot\Xi_i(\theta,\varkappa)\,d\varkappa\,d\theta,
$$
$\mathfrak R_\alpha(\varkappa)=\varkappa^{-1/2}$($\alpha=0$), $(\varkappa+\mathfrak h_0^2)^{\alpha-1/2}$($\alpha\ge1$); $\log_+\theta$ 단항식은 $(\theta+\mathfrak h_0)\log_+(\theta+\mathfrak h_0)$로 읽는다. 영역 II. $\mathfrak p_{\mathrm{II}}=\log2/(1+\mathfrak h_0^3)$, $\bar{\mathcal P}_{\mathrm{II}}$는 $\bar{\mathcal P}_i$에서 $\mathfrak p_i$를 $\mathfrak p_{\mathrm{II}}$로 바꾼 것, $\mathfrak L_{\mathrm{II}}$는 $\mathfrak L_i$에서 $\varkappa$가 든 단항식을 뺀 것이고 $C_{\mathrm{II}}=e^{\mathfrak h_0^3/12}\int_0^\infty(\theta+\mathfrak h_0)\sup_{[\theta,\theta+\mathfrak h_0]}\bar{\mathcal P}_{\mathrm{II}}\cdot\mathfrak L_{\mathrm{II}}(\theta+\mathfrak h_0)\,d\theta$. 영역 III. $\mathfrak i_0\ge6\mathfrak h^{-2}-1$, $w=\mathfrak h^{-3}$, $y=w+1$, $\Upsilon_{\mathrm{III},1}=2/((1-\mathfrak c_3)\sqrt{\log2})$, $\Upsilon_{\mathrm{III},2}=\mathsf z_{3/2}(1-\mathfrak c_3)^{-3}(\log2)^{-3/2}$, $\mathfrak I_{3/2}=2(\mathfrak i_0^{-1/2}-w^{-1/2})$, $\mathfrak I_{5/2}=\frac23(\mathfrak i_0^{-3/2}-w^{-3/2})$, $\mathfrak I_{1/2}=2(w^{1/2}-\mathfrak i_0^{1/2})$, $\mathfrak I^{\mathrm{up}}_{1/2}=\frac23((w+1)^{3/2}-\mathfrak i_0^{3/2})$, $\mathfrak I_3=\frac12\mathfrak i_0^{-2}$, $\mathfrak I_2=\mathfrak i_0^{-1}$, $\mathfrak I_{7/2}=\frac25\mathfrak i_0^{-5/2}$, $\mathfrak o^{\mathrm{up}}_1=\mathfrak s_1w^{1/2}$, $\mathfrak o^{\mathrm{up}}_2=(2\pi)^{-1/2}\frac23(w+1)^{3/2}$:
$$
\begin{aligned}
\mathrm{TA}&=1.5\sqrt{2/\pi}\,\bigl[\mathfrak I_{3/2}+\mathfrak o^{\mathrm{up}}_1\mathfrak I_{5/2}+\mathfrak I_{1/2}/(w+1)+\mathfrak o^{\mathrm{up}}_1\mathfrak I_{3/2}/(w+1)\bigr],\\
\mathrm{TB}&=\frac{1.3\sqrt{2/\pi}}y\bigl[\mathfrak I_{1/2}+\mathfrak I^{\mathrm{up}}_{1/2}/(w+1)+2\mathfrak o^{\mathrm{up}}_1(\mathfrak I_{3/2}+\mathfrak I_{1/2}/(w+1))+\mathfrak o^{\mathrm{up}}_2(\mathfrak I_{5/2}+\mathfrak I_{3/2}/(w+1))\bigr],\\
\mathrm{TC}&=4\sqrt{2/\pi}\,\Upsilon_{\mathrm{III},1}\bigl[1.5w^2\mathfrak I_3/y+2.6w^2\mathfrak I_2/y^2+2.6\mathfrak o^{\mathrm{up}}_1w^2\mathfrak I_3/y^2\bigr],\\
\mathrm{TD}&=\frac{1.3}{y^2}\Upsilon_{\mathrm{III},2}w^{3/2}\sqrt{2/\pi}\cdot2w\,\mathfrak I_{5/2},\qquad
\mathrm{TE}=\frac{1.3}{y^2}\Upsilon_{\mathrm{III},1}^2w\cdot8w^2\sqrt{2/\pi}\,\mathfrak I_{7/2},
\end{aligned}
$$
영역 III의 합은 $e^{\mathfrak h^3/12}(\mathrm{TA}+\mathrm{TB}+\mathrm{TC}+\mathrm{TD}+\mathrm{TE})$이고 $C_{\mathrm{III}}=\sup_{0<\mathfrak h\le\mathfrak h_0}e^{\mathfrak h^3/12}(\mathrm{TA}+\dots+\mathrm{TE})/\mathfrak h$다. $\mathrm{TC}$의 첫 항 $1.5w^2\mathfrak I_3/y$는 실행 코드에서 `c3_iv.py`의 43행 `0.75*h**3/(p*q*q)`를 `0.75/(p*q*q)`로 둔 것에 해당한다.

**알고리즘.** 영역 I: $\theta\in[0,40]$의 $4000$개 셀과 조각마다 $\varkappa$의 $120$개 셀에서, 거듭제곱 인자 $\mathfrak R_\alpha(\varkappa)$와 $(\theta+\mathfrak h_0)^{1+p}$는 셀 위에서 정확히 적분하고, $\bar{\mathcal P}_i$의 감소 부분은 셀의 왼쪽 끝 $\theta_a-\mathfrak h_0$에서, 증가 부분 $e^{(\log2/3)\mathfrak h_0\theta^2}$은 $\theta_b+\mathfrak h_0$에서, $\Xi_i$는 $(\theta_a,\varkappa_j)$에서 평가한다(정리 {{5:old-5-37}} 증명 셋째 단계). $\mathsf z_{3/2}$는 D.{{D:zeta-constants}}의 구간으로 둔다. 영역 II: 같은 $\theta$-격자. 영역 III: $(0,\mathfrak h_0]$을 $2000$개 구간으로 나누어 $\mathfrak h$의 식을 구간마다 직접 평가하며, $\mathfrak h$에 대한 단조성은 쓰지 않는다.

**범위.** $w\ge25000$($\mathfrak h\le\mathfrak h_0=0.0342$).

**산술 등급.** 방향 반올림 구간(mpmath `iv`, 소수 $30$자리).

**결과.** $C_{\mathrm I}\le6.096116$, $\mathfrak h_0C_{\mathrm{II}}\le0.115308$, $C_{\mathrm{III}}\le1.5033946$, 합 $\le7.7148$.

**독립 재계산.** 같은 격자로 다시 실행해 같은 값을 얻었다. 열다섯 단항식의 계수는 `emaj2.py`의 단항식 구조와 정리 {{5:old-5-37}} 증명 둘째 단계의 유도에서 따로 얻어 서로 같음을 확인했다. 세션이 43행을 바꾼 판(`원고_자료/세션_재계산/r8a9b11e/c3_iv_fixed.py`)을 $2000$구간(인자 `2000`; 기본값은 $4000$)으로 다시 실행해 $C_{\mathrm{III}}\le1.5033946$을 8자리까지 재현했다. 수정판 파일의 자체 점검 `check_against_float()`는 옛 float 식과 비교하므로 실패하며, 드라이버(`run_c3_fixed_nocheck.py`)가 본 루프만 실행한다.

**자료.** `records/r8a9b11e…/evidence/peer/cemaj_iv.py`, `outputs/cemaj_iv_4000x120.txt`, `emaj2.py`(단항식 구조), `c3_iv.py`(43행을 위와 같이 바꾼 판으로 실행), `c3sup.py`, `outputs/c3_iv_out.txt`, `outputs/c3sup_out.txt`; `원고_자료/세션_재계산/r8a9b11e/c3_iv_fixed.py`, `원고_자료/세션_재계산/r8a9b11e/run_c3_fixed_nocheck.py`.

**출처.** [r8a9b11e] §4.5, §6; `review/feedback.md` §4.3.

### D.{{D:zeta-constants}} Riemann 제타 상수 $\mathsf z_{-1/2}$·$\mathsf z_{3/2}$의 인증 구간 (보조정리 {{5:cumulant-bounds}})

**확인하는 진술.** $\mathsf z_{3/2}\in[2.61237,2.61238]$, $\mathsf z_{-1/2}\in[-0.20789,-0.20788]$.

**식.** $\mathsf z_{3/2}=\sum_{j\le N}j^{-3/2}+\sum_{j>N}j^{-3/2}$이고, 볼록 감소 함수 $x^{-3/2}$의 적분 비교(중점 규칙은 볼록 함수의 적분을 아래에서 막는다)로
$$
2(N+1)^{-1/2}=\int_{N+1}^\infty x^{-3/2}dx\ \le\ \sum_{j>N}j^{-3/2}\ \le\ \int_{N+1/2}^\infty x^{-3/2}dx=2\bigl(N+\tfrac12\bigr)^{-1/2}.
$$
$\mathsf z_{-1/2}=\lim_{N\to\infty}\bigl(\sum_{j\le N}\sqrt j-\frac23N^{3/2}-\frac12N^{1/2}\bigr)$이고, Euler–Maclaurin 공식으로
$$
\mathsf z_{-1/2}=\sum_{j\le N}\sqrt j-\frac23N^{3/2}-\frac12N^{1/2}-\frac1{24}N^{-1/2}+R_N,\qquad |R_N|\le\frac1{1920}N^{-5/2}
$$
다($\sqrt x$의 도함수들이 부호를 번갈므로 나머지는 첫 생략항 이하다).

**알고리즘.** $\mathsf z_{3/2}$: $N=2000$의 부분합을 구간 산술로 더하고 위의 두 꼬리 경계를 더한다(`cemaj_iv.py`의 함수 `zeta32`). $\mathsf z_{-1/2}$: 코드는 절댓값의 상수 구간 `[0.2078862250607212, 0.2078862250607213]`을 쓰며, 이 상수는 확인하는 진술의 구간 안에 있다. 두 구간은 위의 Euler–Maclaurin 식을 $N=4000$에서 소수 $30$자리로 평가해 다시 확인했다.

**범위.** 상수.

**산술 등급.** 방향 반올림 구간($\mathsf z_{3/2}$), 상수 구간($\mathsf z_{-1/2}$).

**결과.** $\mathsf z_{3/2}\in[2.6123697,2.6123754]$, $\mathsf z_{-1/2}=-0.20788622497\ldots$; 둘 다 확인하는 진술의 구간 안에 있다. 보조정리 {{5:cumulant-bounds}}와 정리 {{5:old-5-37}}이 쓰는 것은 $\mathsf z_{3/2}\le2.6124$, $\mathsf z_{-1/2}\ge-0.2079$뿐이다.

**독립 재계산.** Euler–Maclaurin 식의 $N=4000$ 평가($-0.2078862249779\ldots$, 나머지 $\le5.1\times10^{-13}$)와 $N=2000$ 부분합의 두 꼬리 경계가 위 구간을 준다.

**자료.** `records/r8a9b11e…/evidence/peer/cemaj_iv.py`(함수 `zeta32`, 상수 `ZM12_ABS`), `emaj_upper_fixed.py`(상수 `ZETA32`, `ZETAm12`).

**출처.** [r8a9b11e] §4.5.

### D.{{D:mass-envelope-U2}} 무게 포락선의 구간 산술 확인 (보조정리 {{5:mass-envelope-U2}})

**확인하는 진술.** $u\in[0,0.3]$에서 $\mathcal T(u)/u^2\ge0.4056$과 $g_1(u)\le-0.0235$, $u\in[0.3,1]$에서 $\mathcal T(u)\ge0.01625$. 여기서 $g_0(u)=(1+u)e^u-1-u/2$, $g_1(u)=-1+u(1+u)e^u+1.5u$, $g_2(u)=u(1+u)e^u$, $\mathcal T(u)=1.5u+1.3u^2-(1+u)^{-1/2}g_0(u)$다.

**식.** $\mathcal T(u)/u^2=\frac{1.5}{\sqrt{1+u}(1+\sqrt{1+u})}+1.3-(1+u)^{-1/2}\mathcal S(u)$, $\mathcal S(u):=\sum_{i\ge2}(i+1)u^{i-2}/i!$, $\mathcal S(u)\le1.5+\frac23u+\frac5{24}u^2+\frac1{20}u^3e^u$(꼬리 $i\ge5$의 경계). $[0.3,1]$의 $\epsilon$-항 계수는 $\sup_{[0.3,1]}\bigl[|g_1(u)|+g_2(u)\bigr](1+u)^{-1/2}$다.

**알고리즘.** $[0,0.3]$을 $3000$개, $[0.3,1]$을 $20000$개 구간으로 나누어 구간마다 식을 구간 산술로 평가한다.

**범위.** $y\ge25001$, $1\le d\le y-2$, $u=d/y$, $\epsilon=1/y$.

**산술 등급.** 방향 반올림 구간(mpmath `iv`, 소수 $30$자리).

**결과.** $\min_{[0,0.3]}\mathcal T/u^2\ge0.4056$, $\max_{[0,0.3]}g_1\le-0.0235$, $\min_{[0.3,1]}\mathcal T\ge0.01625$, $[0.3,1]$의 $\epsilon$-항 계수 $\le5.21$.

**독립 재계산.** 다시 실행해 같은 출력을 확인했다.

**자료.** `records/r8a9b11e…/evidence/peer/envelope_iv.py`, `outputs/envelope_iv_out.txt`.

**출처.** [r8a9b11e] §4.6.

### D.{{D:band-check}} 조립 범위의 포락선 검사 (명제 {{5:band-inequality}})

**확인하는 진술.** $\lambda\in[1/2,2/3]$의 $4000$개 소구간 $[\theta_a,\theta_b]$ 각각에서, 아래 여섯 포락선을 $n=50001$, $\mathsf w_0=0.71216$으로 평가한 $(5.53)$의 좌변 하계와 우변 상계의 비가 $1.0727$ 이상이다.

**식.** $\bar\varrho=0.75(1.1\theta_bn)^{2/3}+1$, $\bar{\mathfrak c}_0=\dfrac{1.5\bigl((2\theta_b-1)n+2\bar\varrho\bigr)}{\theta_an\,((1-\theta_b)n-\bar\varrho)}$, $\bar\epsilon_0=\dfrac{1.5\bar\varrho\bigl((2\theta_b-1)n+2\bar\varrho\bigr)}{(\theta_an-1)((1-\theta_b)n-\bar\varrho)}$에 대해
$$
\begin{aligned}
&\mathrm{hov}(\rho_0,Q_{\mathrm w})\ \ge\ \sum_{z\ge0}\Bigl(\theta_a-\frac1n\Bigr)^z\Bigl(1-\frac2{\sqrt\pi}z^{3/2}\bigl(\lfloor0.3(1-\theta_b)n-1\rfloor-1\bigr)^{-1/2}\Bigr)_+\quad(\text{양의 항이 끝날 때까지 더한다}),\\
&\sum_{i\le Q_2}\mathrm{Bor}(i)-Q_2\pi_n(t_0-1)\ \ge\ 1-\sqrt{2/\pi}\,\bigl(0.3(1-\theta_b)n-1\bigr)^{-1/2}-0.3(1-\theta_a)n\cdot(2\pi)^{-1/2}\Bigl[\frac{n+1}{\theta_an\,((1-\theta_b)n-\bar\varrho)}\Bigr]^{3/2}e^{1/(12(n+1))},\\
&\mathrm{top}_\pi\ \le\ (2\pi)^{-1/2}(1+\tfrac1n)^{3/2}\theta_a^{-1/2}(1-\theta_b)^{-3/2}n^{-1/2}e^{1/(12n)},\\
&\tilde K\ \ge\ \theta_a\exp\Bigl(-\frac1{12(0.4(1-\theta_b)n-6(\theta_bn)^{2/3}+1)}-\frac1{12\theta_an}-\frac1{12(n+1)}\Bigr),\\
&\mathcal W\ \le\ (2\pi)^{-1/2}\tfrac23(\bar\varrho+1)^{3/2}\,\bar{\mathfrak c}_0\,\Bigl(1+\frac{\bar\varrho}{\theta_an}\Bigr)^{3/2}e^{\bar\epsilon_0+1/(12\theta_an)},\\
&\mathcal E^+\ \le\ 7.72\,(\theta_an-1)^{-1/3},
\end{aligned}
$$
그리고 비는 $\dfrac{H^{\mathrm{lo}}\cdot\mathsf w_0\cdot\tilde K^{\mathrm{lo}}\cdot[2(\text{둘째 하계})-\mathrm{top}_\pi^{\mathrm{hi}}]-\mathcal W^{\mathrm{hi}}}{1+\mathcal E^{+,\mathrm{hi}}}$다.

**알고리즘.** 소구간 끝점을 정확한 다정밀도 수로 두고, 각 소구간에서 따름정리 {{5:old-5-34}}의 조건 $0.4(1-\theta_b)n\ge6(\theta_bn)^{2/3}+1$을 확인한 뒤, 하계 인자는 구간의 아래 끝, 상계 인자는 위 끝을 곱해 비의 하계를 구하고 소구간 전체의 최솟값을 낸다.

**범위.** $n=50001$(포락선의 $n$-단조성으로 모든 $n\ge50001$을 덮는다), $\lambda\in[1/2,2/3]$.

**산술 등급.** 방향 반올림 구간(mpmath `iv`, 소수 $30$자리).

**결과.** 최소 비 $1.072666$($\lambda\in[0.5,0.50004]$). 그 소구간의 값은 $\mathrm{hov}\ge1.957$, 꼭대기 무게의 합 $\ge0.989$, $\mathrm{top}_\pi\le0.0071$, $\tilde K\ge0.500$, $\mathcal W\le0.0169$, $\mathcal E^+\le0.264$다.

**독립 재계산.** $\mathsf w_0=0.71216$, $\mathcal E^+$의 상수 $7.72$로 다시 실행해 $1.072666$을 얻었다. 오른쪽 부분(보조정리 {{5:right-part}})의 다섯 상수는 손 계산이고, 그 상수를 넣은 격자 대조가 `rplus.py`에 있다.

**자료.** `records/r8a9b11e…/evidence/peer/band_iv.py`, `outputs/band_iv_out.txt`, `rplus.py`, `outputs/rplus_out.txt`.

**출처.** [r8a9b11e] §5.1, §5.2; `review/feedback.md` §0, §5.

### D.{{D:induction-rows}} 인증 행 자료의 첫 감소 수준 검사 (보조정리 {{5:old-5-38}})

**확인하는 진술.** 모든 $10001\le m\le20000$에서 행 $m$의 오른쪽 절반의 첫 감소 수준 $Y_0(m)$이 $m-\lfloor\frac34m^{2/3}\rfloor$ 이상이다.

**식.** 바닥 함수는 정수 산술 $\lfloor\frac34m^{2/3}\rfloor=\max\{f:64f^3\le27m^2\}$로 계산한다.

**알고리즘.** 정리 {{5:old-5-1}}의 인증 행 자료에서 행마다 첫 감소 수준을 읽어 문턱과 비교한다.

**범위.** $10001\le m\le20000$($10000$행).

**산술 등급.** 정확 정수·유리수.

**결과.** 위반 $0$, 최소 여유 $42$($m=10001$: $Y_0=9695$, 문턱 $9653$).

**독립 재계산.** 같은 자료를 다시 읽어 확인했다.

**자료.** 정리 {{5:old-5-1}}의 행 자료 `records/r19de912…/evidence/peer/cert/v2run20000-rows.tsv`(열 firstQ_ell, unimodal_right_cert); 검사는 [r58b4caa] §6·§9.5.

**출처.** [r58b4caa] §6, §9.5.

### D.{{D:lemma-H-interval}} 두 항 부등식의 전 영역 구간 산술 덮개 (정리 {{5:old-5-39}}, 보조정리 {{5:old-5-40}})

**확인하는 진술.** 영역 $\{0<\varsigma\le1,\ 0<\mathfrak K\le\min(1,\gamma^\ast/\varsigma)\}$, $\gamma^\ast=(1000/25001)^{1/6}$의 모든 점에서 $F\cdot\varsigma^7>0$이고 부호 조건 $\tilde I^{\mathrm{lo}}_0>\widetilde{\mathrm{arc}}_0$, $\tilde I^{\mathrm{lo}}_2>\widetilde{\mathrm{arc}}_2$(그리고 $y=k-1$에서의 같은 조건), $\tilde I^{\mathrm{lo}}_4>\widetilde{\mathrm{arc}}_4$, $\mathrm{lb}(\mathsf g^{\mathrm{lo}},k)>0$이 성립한다. 같은 사실이 $\gamma^\ast=(1000/10001)^{1/6}$의 영역에서도 성립한다.

**식.** $(5.55)$의 $F$. 보조정리 {{5:old-5-40}}의 정규화 구간: $\tilde I^{\mathrm{lo}}_{2j}=1-\frac35(2j+5)\frac{\varepsilon^2}\eta-\frac{(1+\eta)^2\varepsilon^2}{54\eta^3}(2j+5)(2j+7)(2j+9)-\tilde{\mathcal T}_{2j}-\tilde{\mathcal O}_{2j}$, $\tilde I^{\mathrm{hi}}_{2j}=1+e^{\mathfrak c_{\mathrm H}}\frac{(1+\eta)\varepsilon^2}{4\eta^2}(2j+5)(2j+7)+\tilde{\mathcal O}_{2j}$, $\mathfrak c_{\mathrm H}=\frac{6^{4/3}}4(\varepsilon^2/(1+\eta))^{1/3}$, 꼬리 $\tilde{\mathcal T}_{2j}=4(2\mathrm{ex}_{\mathrm H})^{(2j+3)/2}e^{-\mathrm{ex}_{\mathrm H}}/((2j+3)!!\sqrt{2\pi})$, $\mathrm{ex}_{\mathrm H}=Q_k\upsilon^{\ast2}/2=5\cdot6^{2/3}(1+\eta)^{-2/3}/\mathfrak K^2$, 외부 꼬리 $\tilde{\mathcal O}_{2j}$는 세 조각(지수 $-(Q_k/2-(n+1)\upsilon^{\ast2})\upsilon^2$, $-3Q_k\upsilon^2/8$, $-Q_k\upsilon^2/4$의 홀수 거듭제곱 닫힌 꼴을 $Q_k^{3/2}/(n+1)=10\sqrt{10}/((1+\eta)\mathfrak K^3)$으로 정규화한 것), 호 $\widetilde{\mathrm{arc}}_{2j}=2\pi\,\mathrm{rad}(1+\mathrm{rad})^{2j+1}\cdot3/((2j+3)!!\sqrt{2\pi})\cdot\frac{Q_k^{3/2}}{n+1}Q_k^{(2j+2)/2}e^{-\mathrm{ex}_3}$, $\mathrm{ex}_3=Q_k^2/(4(n+1))=250/((1+\eta)\varsigma^2\mathfrak K^6)$, $\mathrm{rad}^2=1+\eta/(1+\eta)$. $\mathcal M^{\mathrm{lo}}_0\varsigma^5=\mathsf n^{\mathrm{lo}}_k\sqrt{2\pi}(1+\eta)(\tilde I^{\mathrm{lo}}_0-\widetilde{\mathrm{arc}}_0)$, $\mathsf g^{\mathrm{lo}}\varsigma^2=2\eta+5(\tilde I^{\mathrm{lo}}_2-\widetilde{\mathrm{arc}}_2)/(\tilde I^{\mathrm{hi}}_0+\widetilde{\mathrm{arc}}_0)$, Stirling 인자 $\mathsf n_k\in[(2\pi)^{-1/2}(1+\eta)^{3/2}(1-\frac32\varepsilon^2/(1+\eta)),\ (2\pi)^{-1/2}(1+\eta)^{3/2}e^{19\varepsilon^2/12}]$, $\mathrm{Bor}(k)k^{3/2}\ge(2\pi)^{-1/2}(1-\varepsilon^2/12)$, $\mathsf a_0\le12879/10000$, $\mathsf a_1\le939/1000$. 보조정리 {{5:old-5-41}}의 항은 D.{{D:lemma-V-coefficients}}의 식이다. $y=k-1$의 부호 조건은 $\eta$를 $\eta+\varepsilon^2$로 바꾼 다항 부분과 $y=k$의 꼬리·호(둘 다 $Q_y$에 감소하므로 보수적)로 확인한다.

**알고리즘.** $\varsigma$-격자는 $[0,10^{-3}]$과 $10^{-3}$부터 $1$까지의 기하 $40$등분에 $\sqrt{1/2}$를 더한 것이고, $\mathfrak K$-격자는 각 $\varsigma$-띠에서 $[0,\min(1,0.58480/\varsigma_{\mathrm{lo}})]$의 $4$등분으로 시작해 상자의 하계가 양이 아니거나 부호 조건이 확인되지 않으면 긴 변을 이분한다(깊이 $\le14$). 호 매개변수의 분지는 상자의 $\eta$ 범위로 정한다($\eta\le1/2$이면 $\eta/8$, $\eta\ge1/3$이면 $1/16$; 두 범위에 걸친 상자는 분할). 다항 조각은 정확한 기호식을 구간으로 평가하고, 지수적으로 작은 조각은 $u^me^{-u}$($u\ge m$)를 상자의 $u$ 하계에서 평가한다. $k\ge10001$ 판은 $\varsigma$ 기하 $60$등분, $\mathfrak K$ $6$등분, 깊이 $\le18$로 시작하고 $\varsigma_{\mathrm{lo}}\mathfrak K_{\mathrm{lo}}>(1000/10001)^{1/6}$인 상자를 정확 유리수 판정으로 버린다.

**범위.** $k\ge25001$, $\hat x\ge10$, $\eta\le1$(그리고 $k\ge10001$ 판).

**산술 등급.** 방향 반올림 구간(mpmath `iv`, $53$비트와 $113$비트 재평가).

**결과.** $k\ge25001$: $218$회 평가, 잎 상자 $193$개 모두 통과, 실패 $0$, 상자 하계의 최솟값 $0.0466028$(중앙 근처의 큰 상자). $k\ge10001$: $437$회 평가, 잎 $402$개 통과, 영역 밖으로 버린 상자 $5$개, 실패 $0$, 최솟값 $0.00283$. 잎 감사: 잎들이 영역을 정확 유리수로 빈틈없이 덮고($51$개와 $72$개 $\varsigma$-칸, 문제 $0$), 분지 조건이 정확 유리수로 성립하며($\theta_{\mathrm{arc}}=\eta/8$ 잎 $153$개는 $\varsigma_{\mathrm{hi}}^2\le1/2$, $1/16$ 잎 $40$개는 $\varsigma_{\mathrm{lo}}^2\ge1/3$), $113$비트 재평가에서 같은 결과다. 코드의 두 `assert`(꼬리 부등식의 조건)는 필요한 조건보다 약하지만, 전 영역에서 $\mathrm{ex}_{\mathrm H}\ge10.40>7$, $\sigma\upsilon_{\mathrm L}^2\ge31.25>13$으로 필요한 조건이 성립한다.

**독립 재계산.** 덮개와 감사를 재실행해 같은 값을 얻었고, 인증 성분 $\mathcal M^{\mathrm{lo}}_0\le\mathcal M_0$, $\mathsf g^{\mathrm{lo}}\le\mathsf g_k(n)$, $[k^{5/2}\mathsf b_D]^{\mathrm{lo}}\le k^{5/2}\mathsf b_D$, $[k^{5/2}\mathsf b_J]^{\mathrm{hi}}\ge k^{5/2}\mathsf b_J$를 $k=25001$, $10^5$, $10^6$의 표본점에서 정확 수직선 적분과 대조했으며, $k=10001$, $25001$의 $\hat x\ge10$ 전 범위에서 $F$가 독립 재귀로 구한 참값 $k^{5/2}(e_n-B_{n,k-1})/p_n$보다 작음(비 $0.55$ 이하)을 확인했다.

**자료.** `records/r5f5cf73…/evidence/producer/code/certify2.py`(SHA-256 `758c357c…`), `lemmaH_bounds.py`, `logs/certify_cover_full2.log`; `evidence/peer/code/leaf_audit.py`, `cover_pruned.py`, `audit_pruned.py`, `compare_components.py`, `compare_F_truth.py`, `vertical_indep.py`, `logs/leaf_audit.log`, `logs/cover_pruned_k10001.log`, `logs/audit_pruned_k10001.log`, `logs/leaves.json`, `logs/leaves_k10001.json`. 재현: `cd evidence/producer/code; python -I certify2.py cover 40 4 1e-3 14`.

**출처.** [r5f5cf73] §5, §7, §7.1, §8; `review/feedback.md` §2.4, §2.8.

### D.{{D:lemma-V-coefficients}} 두 보정 경계의 계수 생성 알고리즘 (보조정리 {{5:old-5-41}})

**확인하는 진술.** 보조정리 {{5:old-5-41}}의 항 $\mathrm{Main}_D$, $\mathrm{First}_D$, $\mathrm{Second}_D$, $\mathrm{Dg}_D$, $\mathrm{Rem}_D$, $\mathrm{Tail}_D$, $\mathrm{Arc}_D$, $\mathrm{Main}_J$, $\mathrm{Err}_J$, $\mathrm{Tail}_J$, $\mathrm{Arc}_J$의 닫힌 꼴. 단항식 계수표는 어느 파일에도 저장되어 있지 않고, 실행 때 정확 유리수로 생성된다.

**식.** 기본 변수 $\varsigma$, $\mathfrak K$와 $\eta=\varsigma^2$, $\varepsilon=\varsigma^3\mathfrak K^3/(10\sqrt{10})$, $k^{-1/3}=\varsigma^2\mathfrak K^2/10$. 적분 변수 $\upsilon$, $\rho$의 다항식 $p(\upsilon,\rho)=\sum c_{m,p}\upsilon^m\rho^p$와 Gauss 무게 $e^{-\sigma\upsilon^2}$에 대해 $\int_0^\infty\!\!\int_0^1p\,e^{-\sigma\upsilon^2}d\rho\,d\upsilon=\sum c_{m,p}\frac{\Gamma((m+1)/2)}{2\sigma^{(m+1)/2}}\cdot\frac1{p+1}$(기법 (ㄱ): 반모멘트). $e^{-\varrho^2/2}=e^{-\rho^2\upsilon^2/2}$가 붙은 항은 $\rho$를 먼저 적분한다(기법 (ㄴ)): $\int_0^1\rho^{2i+1}e^{-\rho^2\upsilon^2/2}d\rho=\frac{i!}{(\upsilon^2/2)^{i+1}}\bigl(1-e^{-\upsilon^2/2}\sum_{l\le i}\frac{(\upsilon^2/2)^l}{l!}\bigr)$이고, 결과의 다항 부분은 무게 $e^{-\sigma\upsilon^2}$로, $e^{-\upsilon^2/2}$ 부분은 무게 $e^{-(\sigma+1/2)\upsilon^2}$으로 (ㄱ)을 쓴다. 그 밖의 항에는 $\varrho^2e^{-\varrho^2/2}\le2/e$를 쓴다(기법 (ㄷ)). Dawson 가중 모멘트 $\mathfrak j_m(\eta)=(-2)^m\mathfrak F^{(m)}(\eta)$, $\mathfrak F(\sigma)=\sqrt{\pi/2}\sqrt\sigma/(\sigma+1)$는 기호 미분으로 얻고, $\mathcal Y_j(\eta)=4\sum_m\gamma_m(\eta)\mathfrak j_{m+1}(\eta)$의 $\gamma_m$은 $(s+\varrho^2)^{j/2}(s+s^2/4)/2$를 $s$의 다항식으로 펼쳐 $\int_0^\infty s^pe^{-\eta s/2}ds=p!(2/\eta)^{p+1}$로 적분해 얻는다. $\mathfrak C_{\mathrm I}(\eta)=8\sqrt{2\pi}\,\eta^{-3}(1+\eta)^{-3/2}-\frac{2(1+\eta)}3\bigl[\text{(ㄴ)으로 적분한 } \upsilon^4\cdot\tfrac12(\upsilon\,\mathfrak I_1(\upsilon)+\tfrac{\upsilon^2}4\mathfrak I_2(\upsilon))\bigr]$, $\mathfrak I_i(\upsilon)=\int_0^1\rho(1-\rho)^ie^{-\upsilon^2\rho/2}d\rho$. $\mathrm{Rem}_D$의 세 부분은 $|\mathcal Q_3|(1+\epsilon_{\mathfrak f})$, $\epsilon_{\mathfrak f}(|\mathcal Q_1|+|\mathcal Q_2|)$, $2(2\pi)^{-1/2}|\epsilon_{\mathfrak f}-\frac{(n+1)\upsilon^4}{4k^2}|$에 무게 $\upsilon^4\rho^2Q_0e^{-\eta\upsilon^2/2}$($\epsilon_{\mathfrak f}$가 붙으면 $e^{\gamma_7\upsilon^2}$만큼 약해진 무게 $e^{-7\eta\upsilon^2/16}$)를 곱한 것이고, 상수는 $P_6$의 계수 $\frac59,\frac7{18},\frac{13}{12}\cdot\frac{49}{144}$, $\mathfrak c_{\mathrm T}=\frac19+\frac1{256}$, $\mathsf d_{\mathrm I}=\frac{204}{100}$, Dawson 경계 $8/\varrho^2$다. 꼬리의 단항식 $\upsilon^m\rho^p$ 계수 $c_{m,p}$는 네 조각의 피적분함수 $\upsilon^4\rho^2Q_0(2(2\pi)^{-1/2}+\frac43\varepsilon\varrho^2+\varrho\psi_1+(2\pi)^{-1/2}\psi_1^2+2(2\pi)^{-1/2}\frac{(1+\eta)\varepsilon^2\upsilon^4}4)$에서 나오며, 꼬리 부등식의 매개변수는 분지 $\eta/8$에서 $\mathrm{ex}_4=\sigma\upsilon_{\mathrm L}^2=62.5/(\varsigma^2\mathfrak K^6)$, 분지 $1/16$에서 $\mathrm{ex}_4=31.25/(\varsigma^4\mathfrak K^6)$이고, 호의 $\mathrm{ex}_5=Q_k\theta_{\mathrm{arc}}/4$는 각각 $31.25/(\varsigma^2\mathfrak K^6)$, $15.625/(\varsigma^4\mathfrak K^6)$다. $\mathrm{Err}_J$의 세 조각은 $\rho^5\upsilon^4|\mathrm{ph}_\rho|\varepsilon^2/4$, $\rho(1+\eta)\varepsilon^2\upsilon^5/5$, $\rho\varepsilon^2(|\mathrm{ph}_\rho|+(1+\eta)\varepsilon^2\upsilon^5/5)^3/6$에 $\upsilon^3$을 곱한 것이고, $\gamma_6$의 상계 $(1+\eta)/6-1/15+\varepsilon^2/15$를 쓴다.

**알고리즘.** sympy로 $(\varsigma,\mathfrak K)$의 정확한 기호식을 만들고(`Float` 상수 금지), 항별로 약분해 $\varsigma=0$에서 정칙한 꼴로 바꾼 뒤, 상자마다 mpmath 구간 산술로 평가한다. 부호가 정해지지 않은 조각($\mathrm{First}_D$, $\mathrm{Second}_D$, $\mathrm{Dg}_D$)은 $\mathsf n_k$의 두 끝 값을 곱한 구간의 합집합을 쓰고, $\mathrm{Main}_D$와 주항은 $\mathsf n_k$, $\mathrm{Bor}(k)k^{3/2}$의 하계를, 빼는 조각은 상계를 쓴다.

**범위.** D.{{D:lemma-H-interval}}과 같다.

**산술 등급.** 정확 유리수(계수 생성), 방향 반올림 구간(평가).

**결과.** 닫힌 꼴 조각 $\mathrm{Main}_D$, $\mathrm{First}_D$, $\mathrm{Second}_D$, $\mathrm{Dg}_D$, $\mathrm{Rem}_D$, $\mathrm{Main}_J$, $\mathrm{Err}_J$와 $\epsilon_{\mathfrak f}$ 교차항이 $(\varsigma,\mathfrak K)$의 여섯 표본점($\eta\in[0.01,1]$, $\hat x\in[10,62.5]$)에서 직접 구적과 상대 $2\times10^{-13}$ 안에서 같다. $k=25001$, $\hat x=10$에서 $k^{5/2}\mathsf b_D\in[51.7,88.1]$(정확값 $70.6$), $k^{5/2}\mathsf b_J\le57.0$(정확값 $52.8$)이다.

**독립 재계산.** $\mathrm{Main}$, $\mathrm{First}$, $\mathrm{Second}$, $\mathrm{Dg}$, $\mathrm{Rem}$의 기호식을 독립 구적으로 $10^{-14}$ 안에서 재현했고, 본문이 쓰는 상수 $\mathsf d_{\mathrm I}=2.04$와 호의 앞인자 $3$이 코드의 값과 같음을 확인했다.

**자료.** `records/r5f5cf73…/evidence/producer/code/certify2.py`(함수 `int_poly`, `int_poly_rhoexp`, `J_m`, `D_j`, `C1_closed`, `regularise`, `IVEval`, `Xm_exp_dec`, `evaluate_box`), `closed_forms4.py`, `lemmaV2.py`, `vertical_exact2.py`; `evidence/peer/code/check_pieces.py`, `logs/check_pieces.log`.

**출처.** [r5f5cf73] §6.1–6.7, §7, §9; `review/feedback.md` §2.5–2.8.
