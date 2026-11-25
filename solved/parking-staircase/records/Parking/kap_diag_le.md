---
weight: unit
short: the kernel deficit along the diagonal
---
## Description

For $k \ge 1$ and $2a \le k$ the normalised kernel deficit grows on a diagonal step by at most the factor $1 + \mathsf T(k,a)/k$: $\kappa_{k+1}(k+a+1)/a_{k+a+1} \le \bigl(1 + \mathsf T(k,a)/k\bigr)\,\kappa_k(k+a)/a_{k+a}$.

## Statement

Let $a_j = j^{j-1}/j!$ for $j \ge 1$ and $a_0 = 0$ (`Parking.cay`), let $\kappa_k(t) = a_t - \sum_{k<i<t} a_i\,a_{t-i}$ be the kernel deficit (`Parking.kap`), and for natural numbers $k \ge 1$, $a$ with $\xi = a/k$ let

$$\mathsf T(k,a) = \frac{\frac32\,\xi\,\bigl(1+\frac{2}{3(k+2)}\bigr)\bigl(1+\frac32\xi+\frac38\xi^2\bigr)}{\frac{23}{24}-\frac32\,\xi\,\bigl(1+\frac\xi4\bigr)}$$

(`Parking.kapStepBound`). Let $k$ and $a$ be natural numbers with $k \ge 1$ and $2a \le k$. Then

$$\frac{\kappa_{k+1}(k+a+1)}{a_{k+a+1}} \;\le\; \Bigl(1 + \frac{\mathsf T(k,a)}{k}\Bigr)\,\frac{\kappa_k(k+a)}{a_{k+a}} .$$

## Explanation

**Its place.** The curvature term of the step at a position $(k+r,k)$ is $\sum_m \frac{\kappa_k(N-m)}{N-m}\,\mathsf C_m(k;N)$ with $N = k+r+1$ (`Parking.dq_curv_sub_boundary`). The coefficient of the term $m$ is $\kappa_k(k+a)/(k+a)$ with $a = r+1-m$, and at the position one row down and one column to the right it is $\kappa_{k+1}(k+a+1)/(k+a+1)$: the level $k$ and the argument grow by one each, and their difference $a$ stays. The statement compares the two, after division by the Cayley coefficients; `Parking.term_step` converts it with $a_{M+1}/(M+1) = \gamma_M\,a_M/M$ into the comparison of the coefficients.

**The normalised deficit.** Write $M = k+a$. Reflecting the sum, $\kappa_k(M)/a_M = 1 - \sum_{0<j<a} a_j\,a_{M-j}/a_M$: the sum runs over the short parts $j$ with $0 < j < a$, and the level $k$ enters only through $M$. On a diagonal step each term $a_j\,a_{M-j}/a_M$ decreases, because the ratio of successive Cayley coefficients increases with the index; so the normalised deficit increases. The statement bounds the increase by a multiple of the deficit itself.

**The sizes.** For $j$ small against $M$ the term $a_j\,a_{M-j}/a_M$ is close to the Borel weight $e^{-j}a_j = P(j)/j$, where $P(j) = e^{-j}j^j/j!$ is the Poisson mass. So the normalised deficit is close to the Borel tail $B = 1 - \sum_{0<j<a}P(j)/j$, which is of the order $a^{-1/2}$. Raising both indices of $a_{M-j}/a_M$ by one lowers that ratio by a relative amount of about $\frac{j}{M}\cdot\frac{3}{2k}$, so the increase of the deficit is about $\frac{3}{2kM}\,S$ with $S = \sum_{0<j<a}P(j)$, of the order $a^{1/2}$. The quotient of the two is of the order $a/k^2$: the comparison $\frac{23}{24}S \le a\,B$ of the proof makes this exact, and it is the reason why the bound is relative with a factor $\mathsf T/k$, $\mathsf T \approx \frac32\cdot\frac{24}{23}\cdot\frac ak$.

**What the proof does not use.** Two estimates of the proof are cruder than necessary: the factor $k/(k+a)$ is bounded by $1$, and the comparison of $S$ with $a\,B$ holds with $1$ in the place of $\frac{23}{24}$, since the two bounds of Step 5 below give $S \le c_0(2a-1)/\sqrt a \le a\,B$. The closed form $\mathsf T$ is kept as it is because the constants of `Parking.ledger` are fitted to it. A floating-point evaluation at $k = 265$, $a = 26$, which is not part of the proof, finds the true relative increase at about six tenths of the bound.

**The hypotheses.** $2a \le k$ makes the denominator of $\mathsf T(k,a)$ positive. The value $a = 0$ is admitted: there the sums of both deficits are empty, both normalised deficits are $1$, and $\mathsf T(k,0) = 0$, so the statement reads $1 \le 1$. The statement has no hypothesis on a curve; in `Parking.term_step` the condition $2a \le k$ follows from $r^3 \le k^2$.

**The Lean form.** The statement is `kap (k + 1) (k + a + 1) / cay (k + a + 1) ≤ (1 + kapStepBound k a / k) * (kap k (k + a) / cay (k + a))`, with real numbers on both sides.

## Proof

Write $M = k + a$, $\xi = a/k$, so $0 \le \xi \le \frac12$, and

$$P(j) = e^{-j}\frac{j^j}{j!}, \qquad S = \sum_{0<j<a} P(j), \qquad B = 1 - \sum_{0<j<a}\frac{P(j)}{j}, \qquad \sigma = \frac{\kappa_k(M)}{a_M}, \qquad \sigma' = \frac{\kappa_{k+1}(M+1)}{a_{M+1}},$$

where $P$ is the Poisson mass (`Parking.poissonMass`); $S \ge 0$. Let $D = \frac{23}{24} - \frac32\xi(1+\frac\xi4)$, the denominator of $\mathsf T(k,a)$; $D > 0$ because $\frac32\xi + \frac38\xi^2 \le \frac{27}{32}$ for $\xi \le \frac12$. Let $c_0 = 1/\sqrt{2\pi}$ (`Parking.c0`).

**Step 1: the deficit as a sum over the short side.** For $t = k' + a$ with $t \ge 1$, the substitution $i \mapsto t - i$ maps the indices $k' < i < t$ onto $0 < j < a$, so

$$\frac{\kappa_{k'}(t)}{a_t} = 1 - \sum_{0<j<a}\frac{a_j\,a_{t-j}}{a_t}.$$

This applies to $(k', t) = (k, M)$ and to $(k+1, M+1)$.

**Step 2: two comparisons of Cayley coefficients.**

(i) For $i, j \ge 1$, with $z = j/i$: $\;a_j\,a_i/a_{i+j} \le \frac{P(j)}{j}\bigl(1 + \frac32 z + \frac38 z^2\bigr)$. Indeed $e^{-j}a_j = P(j)/j$ by the definitions, so $a_j\,a_i/a_{i+j} = \frac{P(j)}{j}\cdot e^{j}a_i/a_{i+j}$, and `Parking.borel_ratio_le` for the indices $i \le i+j$ bounds $e^{j}a_i/a_{i+j}$ by $1 + \frac32 z + \frac38 z^2$.

(ii) For $i \ge 2$ and $j \ge 0$:

$$\frac{a_i}{a_{i+j}} - \frac{a_{i+1}}{a_{i+j+1}} \;\le\; \frac{a_i}{a_{i+j}}\cdot\frac{j}{i+j}\Bigl(\frac{3}{2i}+\frac{1}{i(i+1)}\Bigr).$$

Let $\psi_n = (1+1/n)^{n-1}$, so that $a_{n+1} = \psi_n a_n$ (`Parking.cay_ratio`) and the left side is $\frac{a_i}{a_{i+j}}\bigl(1 - \psi_i/\psi_{i+j}\bigr)$. By $1 - 1/u \le \log u$ for $u > 0$, $1 - \psi_i/\psi_{i+j} \le \log\psi_{i+j} - \log\psi_i$. Since $\psi_n = \gamma_n(1+1/n)$ with $\gamma_n = (1+1/n)^{n-2}$ (`Parking.psi_eq_gam`), this difference is $\log\gamma_{i+j} - \log\gamma_i$ plus $\log\frac{1+1/(i+j)}{1+1/i}$. The first is at most $\frac52\bigl(\frac1i - \frac1{i+j}\bigr)$ by `Parking.log_gam_sub_le`, the second at most $\frac{1+1/(i+j)}{1+1/i} - 1$ by $\log u \le u - 1$. The sum of the two bounds is $\frac{j}{i+j}\bigl(\frac{5}{2i} - \frac{1}{i+1}\bigr) = \frac{j}{i+j}\bigl(\frac{3}{2i} + \frac{1}{i(i+1)}\bigr)$.

**Step 3: a lower bound for the deficit.**

$$\sigma \;\ge\; B - \frac32\Bigl(1+\frac\xi4\Bigr)\frac{S}{k+1}.$$

By Step 1 it suffices to bound each term $a_j\,a_{M-j}/a_M$, $0 < j < a$, from above. With $i = M - j \ge k+1$, (i) gives the bound $\frac{P(j)}{j}\bigl(1 + \frac32(1+\frac z4)z\bigr)$, $z = j/i$. Here $z \le j/(k+1)$ and $z \le a/k = \xi$, so the term is at most $\frac{P(j)}{j} + \frac32(1+\frac\xi4)\frac{P(j)}{k+1}$. Sum over $j$.

**Step 4: an upper bound for the increase.**

$$\sigma' - \sigma \;\le\; \Bigl(1+\frac32\xi+\frac38\xi^2\Bigr)\cdot\frac{\frac32\bigl(1+\frac{2}{3(k+2)}\bigr)}{(k+a)(k+1)}\cdot S .$$

By Step 1, $\sigma' - \sigma = \sum_{0<j<a} a_j\bigl(\frac{a_i}{a_{i+j}} - \frac{a_{i+1}}{a_{i+j+1}}\bigr)$ with $i = M - j \ge k+1 \ge 2$. By (ii) and then (i) the term $j$ is at most

$$\frac{P(j)}{j}\Bigl(1+\frac32 z+\frac38 z^2\Bigr)\cdot\frac{j}{i+j}\Bigl(\frac{3}{2i}+\frac{1}{i(i+1)}\Bigr), \qquad z = \frac ji \le \xi .$$

With $i + j = k + a$ and $i \ge k+1$ the last factor is at most $\frac{j}{k+a}\bigl(\frac{3}{2(k+1)} + \frac{1}{(k+1)(k+2)}\bigr) = \frac{j}{k+a}\cdot\frac{3}{2(k+1)}\bigl(1+\frac{2}{3(k+2)}\bigr)$. The factors $j$ cancel; sum over $j$.

**Step 5: the sum of the Poisson masses against the Borel tail.**

$$\frac{23}{24}\,S \;\le\; a\,B .$$

For $a \le 1$ both sums are empty and the claim is $0 \le a$. Let $a \ge 2$.

*The sum.* $P(j) \le c_0/\sqrt j$ for $j \ge 1$ (`Parking.poissonMass_le_c0`) and $\sum_{j=1}^{n} 1/\sqrt j \le 2\sqrt n - 1$ (`Parking.sum_range_inv_sqrt_le`); with $n = a - 1$, $S \le c_0\,(2\sqrt{a-1} - 1)$.

*The tail.* $B \ge 2c_0\bigl(1 - \frac{1}{12a}\bigr)/\sqrt a$. For $n \ge a$, Stirling's lower bound `Parking.poissonMass_ge_c0` gives $P(n) \ge c_0(1 - \frac{1}{12n})/\sqrt n \ge c_0(1-\frac{1}{12a})/\sqrt n$, and $n^{-3/2} \ge 2\bigl(n^{-1/2} - (n+1)^{-1/2}\bigr)$ (`Parking.inv_sqrt_diff_bounds`); so $P(n)/n \ge C\bigl(n^{-1/2} - (n+1)^{-1/2}\bigr)$ with $C = 2c_0(1 - \frac{1}{12a})$. These differences telescope: for every $N \ge a$,

$$\sum_{0<j<a}\frac{P(j)}{j} + C\Bigl(\frac{1}{\sqrt a} - \frac{1}{\sqrt N}\Bigr) \;\le\; \sum_{0<j<N}\frac{P(j)}{j} \;\le\; 1,$$

the last inequality because the numbers $P(j)/j = e^{-j}a_j$ are nonnegative and their series has the sum $1$ (`Parking.hasSum_borel`). Letting $N \to \infty$ gives the bound for $B$.

*Together.* Let $u = \sqrt{a-1}$ and $w = \sqrt a$. Then $2uw \le u^2 + w^2 = 2a - 1$, so $(2u-1)\,w \le 2a - 1$, and

$$\frac{23}{24}\,S \;\le\; \frac{23}{24}\,c_0\,(2u-1) \;\le\; \frac{c_0\,(2a - \frac16)}{w} = a\cdot\frac{2c_0\bigl(1-\frac{1}{12a}\bigr)}{\sqrt a} \;\le\; a\,B ,$$

the middle inequality because $\frac{23}{24}(2u-1)\,w \le \frac{23}{24}(2a-1) \le 2a - \frac16$.

**Step 6: the increase is a multiple of the deficit.** Multiply Step 3 by $\xi \ge 0$ and use Step 5 in the form $\frac{23}{24}\cdot\frac{S}{k+1} \le \frac{23}{24}\cdot\frac Sk \le \frac{a\,B}{k} = \xi\,B$:

$$D\cdot\frac{S}{k+1} = \frac{23}{24}\cdot\frac{S}{k+1} - \frac32\,\xi\Bigl(1+\frac\xi4\Bigr)\frac{S}{k+1} \;\le\; \xi\,B - \frac32\,\xi\Bigl(1+\frac\xi4\Bigr)\frac{S}{k+1} \;\le\; \xi\,\sigma .$$

Hence $\frac{S}{k+1} \le \xi\,\sigma/D$. Insert this into Step 4, written as

$$\sigma' \;\le\; \sigma + \frac{\frac32\bigl(1+\frac{2}{3(k+2)}\bigr)\bigl(1+\frac32\xi+\frac38\xi^2\bigr)}{k}\cdot\frac{k}{k+a}\cdot\frac{S}{k+1},$$

and bound $\frac{k}{k+a}$ by $1$:

$$\sigma' \;\le\; \sigma + \frac{\frac32\bigl(1+\frac{2}{3(k+2)}\bigr)\bigl(1+\frac32\xi+\frac38\xi^2\bigr)}{k}\cdot\frac{\xi\,\sigma}{D} = \Bigl(1 + \frac{\mathsf T(k,a)}{k}\Bigr)\,\sigma .$$
