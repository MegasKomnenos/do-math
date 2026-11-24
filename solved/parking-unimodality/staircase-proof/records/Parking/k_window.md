---
weight: step
short: window of the column k around R^{3/2}
---
## Description

For real $s > 0$, $R = s^2 \ge 42$ and $k \ge 0$: if $(R-2)^3 \le k^2 \le (R-1)^3$, then $k \le s^3 \le 1.07593\,k$.

## Statement

Let $s$, $k$ and $R$ be real numbers with $s > 0$, $R = s^2$, $R \ge 42$ and $k \ge 0$. If

$$(R-2)^3 \le k^2 \le (R-1)^3,$$

then

$$k \le s^3 \qquad\text{and}\qquad s^3 \le 1.07593\,k.$$

## Explanation

The statement is used once, in the proof of `Parking.curve_step_pos`, with $k$ a column, $R = r + 1$ a natural number and $s = \sqrt{R}$, where $(k + r, k)$ is the position at which the step is shown to be positive. The hypothesis $(r-1)^3 \le k^2 \le r^3$ of that theorem says that the position lies between the curve $k^2 = (n-k)^3$ and its translate by one row, and in terms of $R$ it is the window $(R-2)^3 \le k^2 \le (R-1)^3$. The conclusion says that $k$ and $s^3 = R^{3/2}$ agree up to the factor $1.07593$: the ratio $x = s^3/k$ lies in $[1,\,1.07593]$. This is what allows every estimate that depends on the column $k$ and on $R$ to be reduced to an estimate in $s$ alone.

Both inequalities are used further on. The upper one, $s^3 \le 1.07593\,k$, is a hypothesis of `Parking.Gsum_le` and `Parking.Asum_le` (which pass it to `Parking.rho_bound`) and of `Parking.pair_numeric`; the lower one, $k \le s^3$, is the other hypothesis on $k$ of `Parking.pair_numeric`. In the proof of `Parking.curve_step_pos` the upper one also gives $R + 2 \le k$, because $s^3 = R s \ge 6.48\,R$; this places the position in the first layer of the column, the rows $k+1 \le n \le 2k-1$, and gives the condition $R \le k-2$ under which the pair–impulse criterion `Parking.dq_pos_of_pair` applies.

The constant comes from the lower end of the window. For $R \ge 42$ one has $R \le \frac{21}{20}(R-2)$, with equality at $R = 42$, so $R^{3/2} \le (21/20)^{3/2} (R-2)^{3/2} \le (21/20)^{3/2} k$, and $(21/20)^{3/2} = 1.0759298\ldots \le 1.07593$. The hypothesis $R \ge 42$ is therefore used at full strength.

The Lean statement assumes of $s$ only that it is positive. The proof uses this to know that $s^3$ is positive, and it uses the hypothesis $R \ge 42$ in the two places described below.

## Proof

Substitute $R = s^2$. Then $s^2 \ge 42$, $s^3 > 0$ because $s > 0$, and $(s^2)^3 = (s^3)^2$.

*The inequality $k \le s^3$.* Since $0 \le s^2 - 1 \le s^2$, we have $(s^2-1)^3 \le (s^2)^3 = (s^3)^2$. Suppose $k > s^3$. Then $k - s^3 > 0$ and $k + s^3 > 0$, so $k^2 > (s^3)^2 \ge (s^2-1)^3$, which contradicts the hypothesis $k^2 \le (s^2-1)^3$.

*The inequality $s^3 \le 1.07593\,k$.* Because $s^2 \ge 42$, we have $s^2 \le \frac{21}{20}(s^2 - 2)$; this is the linear inequality $\frac{1}{20} s^2 \ge \frac{21}{10}$. Both sides are nonnegative, so cubing gives $(s^2)^3 \le (21/20)^3 (s^2-2)^3$. With the hypothesis $(s^2-2)^3 \le k^2$ and the inequality $(21/20)^3 = 1.157625 \le 1.07593^2 = 1.1576253649$ between rational numbers,

$$(s^3)^2 = (s^2)^3 \le \Bigl(\frac{21}{20}\Bigr)^3 (s^2-2)^3 \le \Bigl(\frac{21}{20}\Bigr)^3 k^2 \le (1.07593\,k)^2.$$

Suppose $s^3 > 1.07593\,k$. Since $s^3 > 0$ and $k \ge 0$, both $s^3 - 1.07593\,k$ and $s^3 + 1.07593\,k$ are positive, so $(s^3)^2 > (1.07593\,k)^2$, a contradiction. This is the one place where $k \ge 0$ is used.
