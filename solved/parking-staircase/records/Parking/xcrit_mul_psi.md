---
weight: unit
short: defining equation of the critical tilt
---
## Description

For $k \ge 1$ the critical tilt satisfies $x_k\,(1 + 1/k)^{k-1} = 1$.

## Statement

For every natural number $k \ge 1$,
$$x_k \,\Bigl(1 + \frac{1}{k}\Bigr)^{k-1} \;=\; 1 ,$$
where $x_k = (k/(k+1))^{k-1}$ is the critical tilt (`Parking.xcrit`).

## Explanation

The number $(1+1/k)^{k-1}$ is the ratio $c_k/c_{k-1}$ of consecutive Cayley numbers $c_n = (n+1)^{n-1}/n!$ (`Parking.cay_ratio`). The equation therefore says $c_k x_k^k = c_{k-1} x_k^{k-1}$: at the critical tilt the tilted Cayley masses of the indices $k-1$ and $k$ are equal. This is the property that defines the critical tilt, and the statements about it are derived from this equation and not from the closed formula: the monotonicity of the tilted Cayley masses on both sides of $k$ (`Parking.ccT_succ_le`, `Parking.ccT_le_succ`), the bound $e\,x_k \le e^{3/(2k)}$ (`Parking.exp_one_mul_xcrit_le`), and, for $k \ge 2$, with $(1+1/k)^{k-1} = \gamma_k (1 + 1/k)$, the relation $(k+1)\, x_k \gamma_k = k$ to the diagonal factor $\gamma_k = (1+1/k)^{k-2}$, which `Parking.Ut_diag_lower` uses to carry the diagonal lower bound `Parking.bq_diag_lower` to the critical tilt.

## Proof

$\frac{k}{k+1} \cdot \bigl(1 + \frac{1}{k}\bigr) = 1$ for $k \ge 1$. Raising this to the power $k-1$ gives the claim.
