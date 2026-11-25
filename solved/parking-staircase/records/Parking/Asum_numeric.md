---
weight: step
short: arithmetic of the upper bound of the sum 𝒜
---
## Description

For real $s \ge 6.48$, $R = s^2$ and $0 \le a \le 0.39894229$: if five real numbers $S_1,\dots,S_4,S_T$ satisfy the bounds of the power sums of $b^{-1/2}$, $b^{-3/2}$, $b^{1/2}$, $b^{3/2}$ and $c^{3/2}(R-c)$, then $a\bigl(-2S_4 + (3R+\frac23)S_3 + (\frac R3-\frac1{15})S_1 + \frac R6 S_2\bigr) - (R^2 - \frac32R + \frac12) + \frac{0.560302\,a}{s^3}S_T \le 0.478731\,s^5 - 0.974453\,s^4 + 0.642741\,s^3$.

## Statement

Let $s$, $a$, $R$, $S_1$, $S_2$, $S_3$, $S_4$ and $S_T$ be real numbers with $s \ge 6.48$, $R = s^2$, $0 \le a \le 0.39894229$ and

- $S_1 \le 2s + \dfrac{1}{2s} - 2.44948$,
- $S_2 \le 1.63300$,
- $S_3 \le \dfrac23\,R s + \dfrac12\,s - 1.17851$,
- $\dfrac25\,R^2 s + \dfrac12\,R s - 0.84853 \le S_4$,
- $S_T \le \dfrac{4}{35}\,(R+1)^3\sqrt{R+1}$.

Then

$$a\Bigl(-2S_4 + \Bigl(3R+\frac23\Bigr)S_3 + \Bigl(\frac R3-\frac1{15}\Bigr)S_1 + \frac R6\,S_2\Bigr) - \Bigl(R^2 - \frac32 R + \frac12\Bigr) + \frac{a \cdot 0.560302}{s^3}\,S_T \le 0.478731\,s^5 - 0.974453\,s^4 + 0.642741\,s^3.$$

## Explanation

The statement is the arithmetic behind `Parking.Asum_le`, the upper bound of the sum $\mathcal{A}(k,R)$ (`Parking.Asum`), one of the three sums in the lower bound `Parking.pairSum_ge` of the pair sum. There $R \ge 42$ is a natural number, $s = \sqrt{R}$, $a = c_0 = 1/\sqrt{2\pi}$, and the five numbers are

$$S_1 = \sum_{b=2}^{R} b^{-1/2}, \quad S_2 = \sum_{b=2}^{R} b^{-3/2}, \quad S_3 = \sum_{b=2}^{R} b^{1/2}, \quad S_4 = \sum_{b=2}^{R} b^{3/2}, \quad S_T = \sum_{0<c<R} c^{3/2}(R-c).$$

The hypotheses are, in this order, the bounds `Parking.sum_Icc_two_inv_sqrt_le`, `Parking.sum_Icc_two_inv_sqrt_cube_le`, `Parking.sum_Icc_two_sqrt_le`, `Parking.sum_Icc_two_sqrt_cube_ge` and `Parking.sum_Ioo_sqrt_cube_mul_le`; the fourth is a lower bound because $S_4$ has a negative coefficient. The left side is the bound of $\mathcal{A}$ that the proof of `Parking.Asum_le` assembles. Its first two terms come from summing `Parking.term_A` over $2 \le b \le R$. Its last term bounds the correction $\sum_{0<c<R}(R-c)\kappa_3(c)\varrho_c$, where $\kappa_3$ is the convolution `Parking.kc3` and $\varrho_c$ the correction `Parking.rhoC` at $N = k + R$, with $\kappa_3(c) \le c_0\sqrt{c}$ and $\varrho_c \le 0.560302\,c/s^3$ from `Parking.rho_bound`.

The right side is the polynomial

$$A_0(s) = 0.478731\,s^5 - 0.974453\,s^4 + 0.642741\,s^3 = s^3 q_0(s), \qquad q_0(s) = 0.478731\,s^2 - 0.974453\,s + 0.642741,$$

which from here on stands for $\mathcal{A}$: it is the upper bound assumed in `Parking.pair_numeric`. Its three coefficients are the three leading coefficients of the assembled bound, rounded up at the sixth decimal place. The assembled bound is a polynomial of degree $5$ in $s$ whose coefficients of $s^5$, $s^4$, $s^3$ are $\frac65 \cdot 0.39894229 = 0.478730748$, $-\bigl(1 - 0.39894229 \cdot 0.560302 \cdot \frac{4}{35}\bigr) = -0.97445392\ldots$ and $\frac{29}{18} \cdot 0.39894229 = 0.64274035\ldots$. The difference between $A_0$ and the assembled bound is therefore a polynomial with three very small leading coefficients and a quadratic part, approximately

$$2.52 \cdot 10^{-7}\,s^5 + 9.24 \cdot 10^{-7}\,s^4 + 6.44 \cdot 10^{-7}\,s^3 + 0.035406\,s^2 - 0.146279\,s + 0.071263$$

(the first coefficient is exactly $2.52 \cdot 10^{-7}$; the others are rounded). Its value at $s = 6.48$ is about $0.6148$. So $A_0$ is the assembled bound up to rounding in its three leading terms, and what the statement gives away is of the order of $s^2$ against a leading term of the order of $s^5$.

The proof uses three polynomial inequalities on the half-line $s \ge 6.48$, and each is shown in the same way: one writes $s = 6.48 + t$ with $t \ge 0$, expands the polynomial in powers of $t$, and finds that every coefficient is positive. An expansion of this kind is an identity between polynomials with rational coefficients, since $6.48 = \frac{162}{25}$.

## Proof

Substitute $R = s^2$ and write $q = \frac{1}{2s}$, so that $q > 0$ and $s^2 q = \frac s2$. Note $s^2 \ge 6.48^2 \ge 41.99$. The left side of the claim is $a\,\mathcal{B} - \bigl(s^4 - \frac32 s^2 + \frac12\bigr) + \frac{0.560302\,a}{s^3} S_T$ with the bracket

$$\mathcal{B} = -2S_4 + \Bigl(3s^2+\frac23\Bigr)S_3 + \Bigl(\frac{s^2}{3}-\frac1{15}\Bigr)S_1 + \frac{s^2}{6}\,S_2.$$

The proof bounds $a\,\mathcal{B}$ and the correction term separately and then compares the result with $A_0(s)$.

*Step 1: the bracket.* The coefficients $3s^2 + \frac23$, $\frac{s^2}{3} - \frac{1}{15}$ and $\frac{s^2}{6}$ are nonnegative, and the coefficient of $S_4$ is negative. Replacing $S_3$, $S_1$, $S_2$ by their upper bounds and $S_4$ by its lower bound gives

$$\mathcal{B} \le -2\Bigl(\frac25 s^5 + \frac12 s^3 - 0.84853\Bigr) + \Bigl(3s^2+\frac23\Bigr)\Bigl(\frac23 s^3 + \frac12 s - 1.17851\Bigr) + \Bigl(\frac{s^2}{3}-\frac1{15}\Bigr)(2s + q - 2.44948) + \frac{s^2}{6} \cdot 1.63300.$$

The only term that is not a polynomial in $s$ is $\bigl(\frac{s^2}{3} - \frac{1}{15}\bigr) q = \frac s6 - \frac{q}{15} \le \frac s6$. Hence $\mathcal{B} \le U_A(s)$, where

$$U_A(s) = -2\Bigl(\frac25 s^5 + \frac12 s^3 - 0.84853\Bigr) + \Bigl(3s^2+\frac23\Bigr)\Bigl(\frac23 s^3 + \frac12 s - 1.17851\Bigr) + \Bigl(\frac{s^2}{3}-\frac1{15}\Bigr)(2s - 2.44948) + \frac{s^2}{6} \cdot 1.63300 + \frac s6.$$

Expanded, $U_A(s) = \frac65 s^5 + \frac{29}{18} s^3 - \frac{1223957}{300000} s^2 + \frac{11}{30} s + \frac{403007}{375000}$.

*Step 2: $U_A(s) \ge 0$ for $s \ge 6.48$.* With $s = 6.48 + t$, $U_A$ becomes a polynomial of degree $5$ in $t$ whose six coefficients are positive; they are, from the constant term upward, $\frac{8192056522379}{585937500} \approx 13981.1$, $\frac{100590070099}{9375000}$, $\frac{4938620471}{1500000}$, $\frac{5686829}{11250}$, $\frac{972}{25}$ and $\frac65$. So $U_A(s) > 0$ for $t \ge 0$.

Since $a \ge 0$, Step 1 gives $a\,\mathcal{B} \le a\,U_A(s)$, and since $U_A(s) \ge 0$ and $a \le 0.39894229$,

$$a\,\mathcal{B} \le 0.39894229 \cdot U_A(s).$$

The positivity of $U_A$ is needed exactly here, to replace $a$ by its upper bound.

*Step 3: the correction term.* First, $\sqrt{s^2+1} \le s + q$, because $s + q \ge 0$ and $(s+q)^2 = s^2 + 2sq + q^2 = s^2 + 1 + q^2 \ge s^2 + 1$. Next,

$$(s^2+1)^3 (s+q) \le s^7 + 3.61\,s^5.$$

To see this, multiply both sides by $2s > 0$. Since $(s+q) \cdot 2s = 2s^2 + 1$, the left side becomes $(s^2+1)^3(2s^2+1) = 2s^8 + 7s^6 + 9s^4 + 5s^2 + 1$ and the right side $2s^8 + 7.22\,s^6$, so the inequality is equivalent to

$$0.22\,s^6 - 9s^4 - 5s^2 - 1 \ge 0.$$

With $s = 6.48 + t$ this polynomial becomes a polynomial of degree $6$ in $t$ whose seven coefficients are positive, from the constant term $\frac{1272525763187}{6103515625} \approx 208.49$ to the leading coefficient $\frac{11}{50}$; so it is positive for $s \ge 6.48$. The hypothesis on $S_T$ now gives

$$S_T \le \frac{4}{35}(s^2+1)^3\sqrt{s^2+1} \le \frac{4}{35}(s^2+1)^3(s+q) \le \frac{4}{35}\bigl(s^7 + 3.61\,s^5\bigr).$$

Multiplying by $\frac{0.560302\,a}{s^3} \ge 0$ and then using $a \le 0.39894229$ on a nonnegative factor,

$$\frac{0.560302\,a}{s^3}\,S_T \le a \cdot 0.560302 \cdot \frac{4}{35}\bigl(s^4 + 3.61\,s^2\bigr) \le 0.39894229 \cdot 0.560302 \cdot \frac{4}{35}\bigl(s^4 + 3.61\,s^2\bigr).$$

*Step 4: the comparison.* By Steps 2 and 3 the left side of the claim is at most

$$0.39894229 \cdot U_A(s) - \Bigl(s^4 - \frac32 s^2 + \frac12\Bigr) + 0.39894229 \cdot 0.560302 \cdot \frac{4}{35}\bigl(s^4 + 3.61\,s^2\bigr),$$

a polynomial of degree $5$ in $s$. It remains to show that $A_0(s)$ minus this polynomial is nonnegative for $s \ge 6.48$. The difference is the polynomial of degree $5$ described in the explanation. With $s = 6.48 + t$ it becomes a polynomial in $t$ whose six coefficients are positive: the constant term is $\frac{315191231381025000293}{512695312500000000000} \approx 0.6148$, the next four are approximately $0.3159$, $0.03634$, $1.304 \cdot 10^{-4}$ and $9.089 \cdot 10^{-6}$, and the leading coefficient is $\frac{63}{250000000}$. Hence the difference is positive for $t \ge 0$, which proves the claim.
