# 수학 차이: `대조v2/퇴고_기준/부록D_장5B.md` → `장v2/부록D_장5B.md`

## (1) 수식 구간: 기준 406개 → 현재 406개; 사라짐 0, 새로 생김 0

### 사라진 수식(기준 판의 자리)


### 새로 생긴 수식(현재 판의 자리)


## (2) 산문의 숫자 토큰: 사라짐 ['2.5', '6.1', '6.7'] / 새로 생김 []

## (3) 라벨: 사라짐 [] / 새로 생김 []

## (3) 기록 식별자: 사라짐 [] / 새로 생김 []

## (3) 식 번호: 사라짐 [] / 새로 생김 []

## (4) 진술 머리: 기준 0 → 현재 0


## (5) †: 0→0, ∎: 0→0, 절 머리: 6→6


## (6) 수식·숫자·라벨이 든 행의 통합 diff(산문만 바뀐 행은 뺌)

```diff
@@ 기준 141-141 / 현재 141-141 @@
- **식.** 기본 변수 $\varsigma$, $\mathfrak K$와 $\eta=\varsigma^2$, $\varepsilon=\varsigma^3\mathfrak K^3/(10\sqrt{10})$, $k^{-1/3}=\varsigma^2\mathfrak K^2/10$. 적분 변수 $\upsilon$, $\rho$의 다항식 $p(\upsilon,\rho)=\sum c_{m,p}\upsilon^m\rho^p$와 Gauss 무게 $e^{-\sigma\upsilon^2}$에 대해 $\int_0^\infty\!\!\int_0^1p\,e^{-\sigma\upsilon^2}d\rho\,d\upsilon=\sum c_{m,p}\frac{\Gamma((m+1)/2)}{2\sigma^{(m+1)/2}}\cdot\frac1{p+1}$(기법 (ㄱ): 반모멘트). $e^{-\varrho^2/2}=e^{-\rho^2\upsilon^2/2}$가 붙은 항은 $\rho$를 먼저 적분한다(기법 (ㄴ)): $\int_0^1\rho^{2i+1}e^{-\rho^2\upsilon^2/2}d\rho=\frac{i!}{2(\upsilon^2/2)^{i+1}}\bigl(1-e^{-\upsilon
+ **식.** 상자의 기본 변수는 $\varsigma$, $\mathfrak K$이고 앞 절의 식에 나온 보조 변수들은 $\eta=\varsigma^2$, $\varepsilon=\varsigma^3\mathfrak K^3/(10\sqrt{10})$, $k^{-1/3}=\varsigma^2\mathfrak K^2/10$으로 이 둘에서 정해진다. 적분 변수 $\upsilon$, $\rho$의 다항식 $p(\upsilon,\rho)=\sum c_{m,p}\upsilon^m\rho^p$와 Gauss 무게 $e^{-\sigma\upsilon^2}$에 대해 $\int_0^\infty\!\!\int_0^1p\,e^{-\sigma\upsilon^2}d\rho\,d\upsilon=\sum c_{m,p}\frac{\Gamma((m+1)/2)}{2\sigma^{(m+1)/2}}\cdot\frac1{p+1}$(기법 (ㄱ), 반모멘트). $e^{-\varrho^2/2}=e^{-\rho^2\upsilon^2/2}$가 붙은 항은 $\rho$를 먼저 적분한다(기법 (ㄴ)). 그 적분은 $\int_0^1\rho^{2i+1}e^{-\rho^2\upsilon^2/2}d\rho=\frac{i!
@@ 기준 143-143 / 현재 143-151 @@
- **알고리즘.** sympy로 $(\varsigma,\mathfrak K)$의 정확한 기호식을 만들고(`Float` 상수 금지), 항별로 약분해 $\varsigma=0$에서 정칙한 꼴로 바꾼 뒤, 상자마다 mpmath 구간 산술로 평가한다. 부호가 정해지지 않은 조각($\mathrm{First}_D$, $\mathrm{Second}_D$, $\mathrm{Dg}_D$)은 $\mathsf n_k$의 두 끝 값을 곱한 구간의 합집합을 쓰고, $\mathrm{Main}_D$와 주항은 $\mathsf n_k$, $\mathrm{Bor}(k)k^{3/2}$의 하계를, 빼는 조각은 상계를 쓴다.
+ Dawson 가중 모멘트 $\mathfrak j_m(\eta)=(-2)^m\mathfrak F^{(m)}(\eta)$, $\mathfrak F(\sigma)=\sqrt{\pi/2}\sqrt\sigma/(\sigma+1)$는 기호 미분으로 얻고 $\mathcal Y_j(\eta)=4\sum_m\gamma_m(\eta)\mathfrak j_{m+1}(\eta)$의 $\gamma_m$은 $(s+\varrho^2)^{j/2}(s+s^2/4)/2$를 $s$의 다항식으로 펼쳐 $\int_0^\infty s^pe^{-\eta s/2}ds=p!(2/\eta)^{p+1}$로 적분해 얻는다. $\mathfrak C_{\mathrm I}(\eta)=8\sqrt{2\pi}\,\eta^{-3}(1+\eta)^{-3/2}-\frac{2(1+\eta)}3\bigl[\text{(ㄴ)으로 적분한 } \upsilon^4\cdot\tfrac12(\upsilon\,\mathfrak I_1(\upsilon)+\tfrac{\upsilon^2}4\mathfrak I_2(\upsilon))\bigr]$, $\mathfrak I_i(\upsilon)=\int_0^1\rho(1-\rho)^ie^{-\up
+ $\mathrm{Rem}_D$의 세 부분은 $|\mathcal Q_3|(1+\epsilon_{\mathfrak f})$, $\epsilon_{\mathfrak f}(|\mathcal Q_1|+|\mathcal Q_2|)$, $2(2\pi)^{-1/2}|\epsilon_{\mathfrak f}-\frac{(n+1)\upsilon^4}{4k^2}|$에 무게 $\upsilon^4\rho^2Q_0e^{-\eta\upsilon^2/2}$를 곱한 것이다. $\epsilon_{\mathfrak f}$가 붙은 항에서는 무게가 $e^{\gamma_7\upsilon^2}$만큼 약해진 $e^{-7\eta\upsilon^2/16}$이 된다. 여기에 쓰는 상수는 $P_6$의 계수 $\frac59,\frac7{18},\frac{13}{12}\cdot\frac{49}{144}$, $\mathfrak c_{\mathrm T}=\frac19+\frac1{256}$, $\mathsf d_{\mathrm I}=\frac{204}{100}$, Dawson 경계 $8/\varrho^2$다.
+ 꼬리의 단항식 $\upsilon^m\rho^p$ 계수 $c_{m,p}$는 보조정리의 증명에서 정확히 적분한 네 조각의 피적분함수 $\upsilon^4\rho^2Q_0(2(2\pi)^{-1/2}+\frac43\varepsilon\varrho^2+\varrho\psi_1+(2\pi)^{-1/2}\psi_1^2+2(2\pi)^{-1/2}\frac{(1+\eta)\varepsilon^2\upsilon^4}4)$에서 나온다. 꼬리 부등식의 매개변수는 분지 $\eta/8$에서 $\mathrm{ex}_4=\sigma\upsilon_{\mathrm L}^2=62.5/(\varsigma^2\mathfrak K^6)$, 분지 $1/16$에서 $\mathrm{ex}_4=31.25/(\varsigma^4\mathfrak K^6)$이고, 호의 $\mathrm{ex}_5=Q_k\theta_{\mathrm{arc}}/4$는 각각 $31.25/(\varsigma^2\mathfrak K^6)$, $15.625/(\varsigma^4\mathfrak K^6)$다.
+ $\mathrm{Err}_J$의 세 조각은 $\rho^5\upsilon^4|\mathrm{ph}_\rho|\varepsilon^2/4$, $\rho(1+\eta)\varepsilon^2\upsilon^5/5$, $\rho\varepsilon^2(|\mathrm{ph}_\rho|+(1+\eta)\varepsilon^2\upsilon^5/5)^3/6$에 $\upsilon^3$을 곱한 것이고 $\gamma_6$의 상계 $(1+\eta)/6-1/15+\varepsilon^2/15$를 쓴다.
+ **알고리즘.** sympy로 $(\varsigma,\mathfrak K)$의 정확한 기호식을 만들고(`Float` 상수 금지), 항별로 약분해 $\varsigma=0$에서 정칙한 꼴로 바꾼 뒤 상자마다 mpmath 구간 산술로 평가한다. 부호가 정해지지 않은 조각($\mathrm{First}_D$, $\mathrm{Second}_D$, $\mathrm{Dg}_D$)은 $\mathsf n_k$의 두 끝 값을 곱한 구간의 합집합을 쓰고 $\mathrm{Main}_D$와 주항은 $\mathsf n_k$, $\mathrm{Bor}(k)k^{3/2}$의 하계를, 빼는 조각은 상계를 쓴다.
@@ 기준 155-155 / 현재 163-163 @@
- **출처.** [r5f5cf73] §6.1–6.7, §7, §9; `review/feedback.md` §2.5–2.8.
+ **출처.** [r5f5cf73] §6.1에서 §6.7까지, §7, §9; `review/feedback.md` §2.5에서 §2.8까지.
```
