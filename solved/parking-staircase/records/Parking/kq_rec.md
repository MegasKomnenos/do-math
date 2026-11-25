---
weight: unit
short: recursion of the prime kernel beyond the free range
---
## Description

For $N \ge y \ge 2$ the prime kernel of the threshold $y$ satisfies $N\,\kappa^{(y)}_N = \sum_{\gamma=1}^{y-1} (y-\gamma)\, a_\gamma\, \kappa^{(y)}_{N-\gamma}$, with $a_\gamma = \gamma^{\gamma-1}/\gamma!$.

## Statement

Let $y \ge 2$ and $N \ge y$ be natural numbers. Then
$$N\,\kappa^{(y)}_N \;=\; \sum_{\gamma=1}^{y-1} (y-\gamma)\, a_\gamma\, \kappa^{(y)}_{N-\gamma},$$
where $\kappa^{(y)}_m = [X^m](1 - 1/Z_y)$ is the prime kernel of the threshold $y$ (`Parking.kq`; $Z_y$ is the series `Parking.Zs` of the threshold $y$, with coefficients $z^{(y)}_n = A(n,y-1)/n!$, `Parking.zr`) and $a_\gamma = \gamma^{\gamma-1}/\gamma!$ (`Parking.cay`).

## Explanation

In the free range $m \le y$ the kernel is known explicitly (`Parking.kq_eq_eps`). The recursion determines it at every later index from the $y-1$ preceding values, with coefficients that are positive and do not depend on $N$, and with the factor $N$ on the left. Two consequences are drawn from this shape. The kernel is nonnegative (`Parking.kqT_nonneg`). And because the left-hand side carries the factor $N$ while the right-hand side is a fixed combination of earlier values, a kernel that does not increase on the free range keeps decreasing, at least like $1/N$ (`Parking.kqT_succ_le`, `Parking.kqT_harmonic`); the estimates of the kernel that the proof of `Parking.step_pos_large` uses start there. For $y = 2$ the recursion is $N \kappa^{(2)}_N = \kappa^{(2)}_{N-1}$, so $\kappa^{(2)}_N = 1/N!$.

The recursion is the coefficient form of the differential equation $K_y' = y - (1-K_y)\, H_y$ for the prime kernel series $K_y$ (`Parking.Ks`), where $H_y = \sum_{j \le y-2} (y-1-j)\, c_j X^j$ is a polynomial and $c_j = (j+1)^{j-1}/j! = a_{j+1}$. The polynomial measures the difference between the weight $\min(j+1,y)$ of the last-car recursion and the constant $y$; it is nonzero only below the threshold, where the environment is the free one. The lower bound $N \ge y$ is needed: the coefficient of $X^{N-1}$ in the constant $y$ vanishes only for $N \ge 2$, and for $N \le y-1$ the term of $H_y$ of degree $N-1$ contributes as well.

In Lean the right-hand side is `rconv (kqW y) (kq y) N` $= \sum_{\gamma=1}^{N} (y-\gamma)^+ a_\gamma\, \kappa^{(y)}_{N-\gamma}$ (`Parking.rconv`, `Parking.kqW`). The weight $(y-\gamma)^+ a_\gamma$ vanishes for $\gamma \ge y$, and $N \ge y$, so this is the sum over $1 \le \gamma \le y-1$ of the statement.

## Proof

Write $Z = Z_y$ for the series of the threshold (`Parking.Zs`), $K = K_y$, and $\Gamma' = \Gamma_y'$ for the series `Parking.Gp`.

*The polynomial $H_y$.* Let $H_y = \sum_{j \ge 0} (y-1-j)^+\, c_j X^j$, where $t^+ = \max(t,0)$ and $c_j = (j+1)^{j-1}/j! = a_{j+1}$ (`Parking.cc`). Then $\Gamma' = y Z - H_y$. Indeed the coefficient of $X^j$ in $\Gamma'$ is $\min(j+1,y)\, z^{(y)}_j$ (`Parking.coeff_Gp`). If $j+1 \le y$, it is $(j+1)\, c_j$ because $z^{(y)}_j = c_j$ in the free range (`Parking.zr_eq_cc`), and $(j+1) c_j = y c_j - (y-1-j) c_j$. If $j + 1 > y$, it is $y\, z^{(y)}_j$ and the coefficient of $H_y$ is $0$.

*The differential equation.* By `Parking.deriv_Ks`, $K' = (1-K)\,\Gamma' = y\,(1-K) Z - (1-K) H_y$, and $(1-K) Z = 1$ by `Parking.Zs_mul_one_sub_Ks`. Hence
$$K' \;=\; y - (1-K)\, H_y .$$

*The coefficient of $X^{N-1}$.* Put $n = N - 1$; since $N \ge y \ge 2$, $n \ge 1$. On the left the coefficient is $N \kappa^{(y)}_N$. On the right the constant $y$ contributes nothing because $n \ne 0$, and the product contributes $-\sum_{j=0}^{n} [X^j] H_y \cdot [X^{n-j}](1-K)$. For $j = n$ the factor $[X^n] H_y = (y-1-n)^+ c_n$ is $0$, because $n \ge y-1$. For $j < n$ the second factor is $-\kappa^{(y)}_{n-j}$ (`Parking.coeff_one_sub_Ks_of_pos`) and the first is $(y-1-j)^+ c_j = (y-(j+1))^+ a_{j+1}$. With $\gamma = j+1$ this gives
$$N \kappa^{(y)}_N \;=\; \sum_{\gamma=1}^{N-1} (y-\gamma)^+\, a_\gamma\, \kappa^{(y)}_{N-\gamma},$$
and the terms with $\gamma \ge y$ vanish. (The Lean sum has in addition the term $\gamma = N$, whose weight is zero.)
