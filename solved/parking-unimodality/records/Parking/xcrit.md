---
weight: unit
short: critical tilt of a column
---
## Description

The critical tilt $x_k = (k/(k+1))^{k-1}$ of the column $k$: the tilt at which the tilted Cayley masses $c_n x^n$ of the indices $k-1$ and $k$ are equal.

## Statement

For a natural number $k$,
$$x_k \;=\; \Bigl(\frac{k}{k+1}\Bigr)^{k-1} .$$
For $k \ge 1$ this is the real number determined by $x_k\,(1 + 1/k)^{k-1} = 1$.

## Explanation

The ratio of consecutive tilted Cayley masses $c_n x^n$, $c_n = (n+1)^{n-1}/n!$ (`Parking.ccT`), is $c_{j+1} x^{j+1}/(c_j x^j) = x\,(1+1/(j+1))^{j}$ (`Parking.ccT_succ`), and $(1+1/i)^{i-1}$ increases with $i$. The critical tilt is the value of $x$ at which this ratio is $1$ for $j+1 = k$ (`Parking.xcrit_mul_psi`). At $x = x_k$ the masses therefore do not increase up to the index $k$ and do not decrease from the index $k-1$ on (`Parking.ccT_succ_le`, `Parking.ccT_le_succ`); in particular $c_k x_k^k = c_{k-1} x_k^{k-1}$ is their smallest value.

The tilted environment $z^{(k)}_N x^N$ of the threshold $k$ (`Parking.zrT`) equals $c_N x^N$ for $N \le k$. So $x_k$ is the largest tilt at which the tilted environment of the threshold $k$ does not increase on its free range: for a larger $x$ the step from $k-1$ to $k$ would be an increase. The theorem `Parking.zrT_anti_crit` states that at this tilt the tilted environment does not increase anywhere, for every $k \ge 2$. This is the reason for the choice, and the left half of the argument (the columns $k$ in the rows $n \ge 2k$) works at the critical tilt of the column throughout. At the same tilt the tilted free prime kernel $\varepsilon_m x_k^m$ does not increase on $1 \le m \le k$ (`Parking.epsT_succ_le`), which for $k \ge 2$ makes the tilted prime kernel of the threshold $k$ monotone (`Parking.kqT_succ_le`). Here $\varepsilon_m = (m-1)^{m-1}/m!$ (`Parking.eps`).

Some values: $x_2 = 2/3$, $x_3 = 9/16$, $x_4 = 64/125$. One has $0 < x_k \le 1$ (`Parking.xcrit_pos`, `Parking.xcrit_le_one`) and $e\,x_k \le e^{3/(2k)}$ (`Parking.exp_one_mul_xcrit_le`). Since also $(1+1/k)^{k-1} < e$, the critical tilt is slightly larger than $e^{-1}$ and tends to it as $k \to \infty$. The value $e^{-1}$ is the tilt at which the unrestricted sums are finite and explicit: $\sum_n c_n e^{-n} = e$ (`Parking.hasSum_cc`).

The library uses a second tilt for a column, the diagonal tilt $1/\gamma_k$ with $\gamma_k = (1+1/k)^{k-2}$ (`Parking.xk`, `Parking.gam`), in the crossing criterion and in the chain column. For $k \ge 2$ the two are related by $x_k \gamma_k = k/(k+1)$, which follows from `Parking.xcrit_mul_psi` and $(1+1/k)^{k-1} = \gamma_k (1+1/k)$.

In Lean, `xcrit k` is `((k : ℝ) / ((k : ℝ) + 1)) ^ (k - 1)` with natural-number subtraction in the exponent, so `xcrit 0 = xcrit 1 = 1`.
