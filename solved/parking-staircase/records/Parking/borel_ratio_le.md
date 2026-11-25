---
weight: unit
short: ratio of two Borel weights
---
## Description

For natural numbers $1 \le i \le j$ and $z = (j-i)/i$: $e^{j-i}\, a_i / a_j \le 1 + \tfrac32 z + \tfrac38 z^2$, where $a_m = m^{m-1}/m!$. The left side is the ratio of the Borel weights $e^{-i} a_i$ and $e^{-j} a_j$.

## Statement

Let $a_m = m^{m-1}/m!$ for $m \ge 1$ (the Cayley coefficients, `Parking.cay`). For all natural numbers $i$ and $j$ with $1 \le i \le j$, and with $z = (j-i)/i$,

$$\frac{e^{\,j-i}\; a_i}{a_j} \;\le\; 1 + \tfrac32\, z + \tfrac38\, z^2 .$$

## Explanation

**What is bounded.** The numbers $e^{-m} a_m$, $m \ge 1$, are the probabilities of the Borel distribution with parameter $1$; we call them the Borel weights. The left side of the statement is the quotient $e^{-i} a_i / (e^{-j} a_j)$ of two of them, the weight of the smaller index divided by the weight of the larger. Since the Borel weights behave like $m^{-3/2}/\sqrt{2\pi}$, this quotient is close to $(j/i)^{3/2} = (1+z)^{3/2}$. `Parking.borel_log_mono` shows that $(1+z)^{3/2}$ is an upper bound, and the statement replaces it by the Taylor polynomial of degree two of $(1+z)^{3/2}$ at $z = 0$, which lies above the function for $z \ge 0$.

**Why a polynomial.** In both places where the bound is used, it is multiplied by nonnegative weights and summed over one of the two indices, and the sums of those weights against $1$, against the index and against its square are known in closed form or are easily bounded. A polynomial of degree two in $z$ is therefore a bound that can be summed, while $(1+z)^{3/2}$ is not.

**Where it is used.** The module that contains this statement and `Parking.borel_log_mono` serves two separate arguments of the proof, the curve increase and the diagonal step behind the curve.

- *The curve increase.* In the lower bound of the pair sum, `Parking.pairSum_ge`, the statement is applied with $i = N - c$ and $j = N - b$, where $N = k + R$ and $b < c < R$ are cut points. It gives $\operatorname{ren}(c-b)\, a_{N-c}/a_{N-b} \le P(c-b)\,\bigl(1 + \tfrac32 z + \tfrac38 z^2\bigr)$ with $z = (c-b)/(N-c)$, where $\operatorname{ren}(m) = m^m/m!$ and $P(m) = e^{-m} m^m/m!$. After the summation over $b$, the terms in $z$ and $z^2$ become the correction $\varrho_c = c/(2(N-c)) + c^2/(8(N-c)^2)$ that appears in that bound (`Parking.rhoC`). The same argument also uses `Parking.borel_log_mono` directly.
- *The diagonal step.* In the comparison of the kernel deficit along the diagonal, `Parking.kap_diag_le`, the statement is applied with $j = i + g$. It gives $a_g\, a_i / a_{i+g} \le \bigl(P(g)/g\bigr)\bigl(1 + \tfrac32 z + \tfrac38 z^2\bigr)$ with $z = g/i$, which bounds the terms of the sum $\sum_g a_g\, a_{M-g}/a_M$ by Poisson masses. The diagonal step takes only the present statement from this module.

**The Lean form.** The statement is `Real.exp ((j : ℝ) - i) * cay i / cay j ≤ 1 + 3 / 2 * (((j : ℝ) - i) / i) + 3 / 8 * (((j : ℝ) - i) / i) ^ 2`; the subtraction $j - i$ is taken in the real numbers.

## Proof

Put $\rho = e^{j-i} a_i / a_j$ and $z = (j-i)/i$. Then $z \ge 0$, $1 + z = j/i$, and $\rho > 0$ because $a_i, a_j > 0$ (`Parking.cay_pos`).

*First step: $\rho^2 \le (1+z)^3$.* Both sides are positive, so it suffices to compare logarithms. We have $2\log\rho = 2\bigl((j - i) + \log a_i - \log a_j\bigr)$ and $3\log(1+z) = 3(\log j - \log i)$. `Parking.borel_log_mono` states $\log a_i - i + \tfrac32\log i \le \log a_j - j + \tfrac32 \log j$, which rearranges to $(j-i) + \log a_i - \log a_j \le \tfrac32(\log j - \log i)$. Multiplying by $2$ gives the claim.

*Second step: $(1+z)^3 \le \bigl(1 + \tfrac32 z + \tfrac38 z^2\bigr)^2$.* Expanding the square gives $1 + 3z + 3z^2 + \tfrac98 z^3 + \tfrac9{64} z^4$, and $(1+z)^3 = 1 + 3z + 3z^2 + z^3$. The difference is $\tfrac18 z^3 + \tfrac9{64} z^4$, which is nonnegative because $z \ge 0$.

*Conclusion.* The two steps give $\rho^2 \le \bigl(1 + \tfrac32 z + \tfrac38 z^2\bigr)^2$. Since $\rho > 0$ and $1 + \tfrac32 z + \tfrac38 z^2 > 0$, taking square roots gives the statement.
