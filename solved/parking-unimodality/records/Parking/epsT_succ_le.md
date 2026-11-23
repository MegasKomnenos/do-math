---
weight: unit
short: the tilted free prime kernel does not increase up to the critical index
---
## Description

At the critical tilt $x_k$ the tilted free prime kernel does not increase on $1 \le m \le k$: $\varepsilon_{m+1} x_k^{m+1} \le \varepsilon_m x_k^m$ for $1 \le m < k$.

## Statement

For all natural numbers $k$ and $m$ with $1 \le m < k$,
$$\varepsilon_{m+1}\, x_k^{\,m+1} \;\le\; \varepsilon_m\, x_k^{\,m} ,$$
where $\varepsilon_m = (m-1)^{m-1}/m!$ (`Parking.eps`, tilted: `Parking.epsT`) and $x_k = (k/(k+1))^{k-1}$ is the critical tilt (`Parking.xcrit`).

## Explanation

This is exactly the hypothesis of `Parking.kqT_succ_le` and `Parking.kqT_harmonic` for the threshold $y = k$ and the tilt $x = x_k$. With it, for $k \ge 2$, the tilted prime kernel (`Parking.kqT`) $\kappa^{(k)}_m x_k^m$ of the threshold $k$ does not increase on $m \ge 1$, and $m\,\kappa^{(k)}_m x_k^m$ does not increase on $m \ge k$. The left half of the argument obtains its bounds of the kernel from these two facts.

The critical tilt was chosen for the tilted Cayley masses $c_n x^n$ (`Parking.ccT`), not for the kernel. That the same tilt works for the free kernel comes from the relation between the two sequences: with $\chi_m = (1+1/m)^m$, one has $\varepsilon_{m+1}\,\chi_m = a_{m+1}$ for the tree numbers $a_n = n^{n-1}/n! = c_{n-1}$. The tilted tree numbers do not increase up to the index $k+1$ at the critical tilt (`Parking.ccT_succ_le`), and the correction factor $\chi_m$ increases with $m$, which only helps.

## Proof

Put $x = x_k > 0$ (`Parking.xcrit_pos`) and $\chi_m = (1 + 1/m)^m$ for $m \ge 1$, $\chi_0 = 1$. Two facts are used.

First, $\varepsilon_{m+1} x^{m+1}\, \chi_m = a_{m+1} x^{m+1}$ for every $m \ge 0$. For $m = 0$ both sides are $x$, since $\varepsilon_1 = a_1 = 1$. For $m \ge 1$, $\varepsilon_{m+1} = m^m/(m+1)!$ (`Parking.eps_succ`) and $a_{m+1} = (m+1)^m/(m+1)!$ (`Parking.cay_succ`), whose quotient is $(m/(m+1))^m = 1/\chi_m$. This is a routine calculation.

Second, $\chi_{m-1} \le \chi_m$ for $m \ge 1$: for $m = 1$ it is $1 \le 2$, and for $m \ge 2$ it is `Parking.chi_mono`.

Now let $1 \le m < k$. Then
$$\varepsilon_{m+1} x^{m+1}\, \chi_m \;=\; a_{m+1} x^{m+1} \;\le\; a_m x^m \;=\; \varepsilon_m x^m\, \chi_{m-1} \;\le\; \varepsilon_m x^m\, \chi_m .$$
The two equalities are the first fact. The first inequality is the monotonicity of the tilted Cayley masses: $a_{n+1} x^{n+1} = x \cdot c_n x^n$ (`Parking.x_mul_ccT`), and $c_m x^m \le c_{m-1} x^{m-1}$ by `Parking.ccT_succ_le`, which applies because $m \le k$; multiply by $x \ge 0$. The last inequality is the second fact, multiplied by $\varepsilon_m x^m \ge 0$ (`Parking.eps_nonneg`). Dividing by $\chi_m > 0$ gives the claim.
