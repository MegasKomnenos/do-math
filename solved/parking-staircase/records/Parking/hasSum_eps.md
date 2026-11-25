---
weight: unit
short: total mass of the kernel ε at the tilt 1/e
---
## Description

The series $\sum_{m \ge 1} e^{-m} \varepsilon_m$, with $\varepsilon_m = (m-1)^{m-1}/m!$, converges and has the sum $1 - e^{-1}$.

## Statement

The series of nonnegative real numbers

$$\sum_{m \ge 0} e^{-m}\, \varepsilon_m$$

converges, and its sum is $1 - e^{-1}$. Here $\varepsilon_0 = 0$ and $\varepsilon_m = (m-1)^{m-1}/m!$ for $m \ge 1$, with $\varepsilon_1 = 1$ (`Parking.eps`), so the term $m = 0$ is zero.

## Explanation

The numbers $c_n = (n+1)^{n-1}/n!$ (`Parking.cc`) form the renewal sequence of the kernel $\varepsilon$ (`Parking.eps_conv`), and this stays true after both are multiplied by $e^{-n}$. A renewal sequence with the finite sum $S$ belongs to a kernel of total mass $1 - 1/S$; formally, this is the relation $1 - \sum_m \varepsilon_m x^m = 1/P(x)$ between the generating series (`Parking.TreeSeries.coeff_Eser_mul`) evaluated at $x = e^{-1}$. Since $\sum_n e^{-n} c_n = e$ (`Parking.hasSum_cc`), the mass is $1 - e^{-1}$. So at the tilt $e^{-1}$ the kernel $\varepsilon$ is defective, and its defect is exactly $e^{-1}$. As with `Parking.hasSum_borel`, the point $e^{-1}$ is on the boundary of convergence, and the library proves the statement with partial sums in place of analytic functions.

The value is used as the bound $\sum_{i \le N} e^{-i}\varepsilon_i \le 1 - e^{-1}$ for the partial sums, from which the bound for the total mass of the frozen kernel follows (in the proof of `Parking.Gres_sum_le`).

In Lean the statement is `HasSum (fun m : ℕ => Real.exp (-m) * eps m) (1 - Real.exp (-1))`: the family indexed by all natural numbers is summable with that sum, which for nonnegative terms is the convergence of the partial sums.

## Proof

Let $f_m = e^{-m}\varepsilon_m$ and $g_n = e^{-n} c_n$, with partial sums $F_M = \sum_{m=0}^{M} f_m$ and $G_M = \sum_{n=0}^{M} g_n$, and let $S = e$ denote the sum of the series $\sum_n g_n$.

*The properties used.* We have $f_m \ge 0$ (`Parking.eps_nonneg`), $g_n > 0$ (`Parking.cc_pos`), $f_0 = 0$, $g_0 = c_0 = 1$ (`Parking.cc_zero`), and

$$g_n = \sum_{m=0}^{n} f_m\, g_{n-m} \qquad (n \ge 1),$$

which is `Parking.eps_conv`, $\sum_{m=1}^{n} \varepsilon_m c_{n-m} = c_n$, multiplied by $e^{-n} = e^{-m}\,e^{-(n-m)}$; the term $m = 0$ may be added because $\varepsilon_0 = 0$. Finally $\sum_n g_n = S$ by `Parking.hasSum_cc`.

*The two inequalities.* Steps 1 and 2 of the proof of `Parking.hasSum_borel` use only the first five of these properties, and give for all $M, k \ge 0$

$$1 - \frac{1}{G_M} \le F_M \qquad\text{and}\qquad F_M\, G_k \le G_{M+k} - 1 .$$

(They come from the summed renewal equation $\sum_{m \le M} f_m G_{M-m} = G_M - 1$ and the monotonicity of $G$.)

*The upper bound.* The partial sums of a convergent series of nonnegative terms are at most its sum, so $G_{M+k} \le S$, and $S \ge G_0 = 1 > 0$. The second inequality gives $F_M\, G_k \le S - 1$ for every $k$. Letting $k \to \infty$, $G_k \to S$, so $F_M\, S \le S - 1$, that is,

$$F_M \le 1 - \frac{1}{S} \qquad (M \ge 0).$$

*Conclusion.* Since $G_M \to S > 0$, the lower bounds $1 - 1/G_M$ tend to $1 - 1/S$. Hence $F_M \to 1 - 1/S = 1 - e^{-1}$, and because the terms $f_m$ are nonnegative, the series converges to this value.
