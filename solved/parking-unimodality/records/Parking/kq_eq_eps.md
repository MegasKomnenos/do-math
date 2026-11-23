---
weight: unit
short: the prime kernel in the free range
---
## Description

In the free range $1 \le m \le y$ the prime kernel of the threshold $y$ is the free prime kernel: $\kappa^{(y)}_m = \varepsilon_m = (m-1)^{m-1}/m!$.

## Statement

Let $y \ge 1$ and $1 \le m \le y$ be natural numbers. Then
$$\kappa^{(y)}_m \;=\; \varepsilon_m ,$$
where $\kappa^{(y)}_m = [X^m](1 - 1/Z_y)$ is the prime kernel of the threshold $y$ (`Parking.kq`, with $Z_y$ the series `Parking.Zs`), and $\varepsilon_m = (m-1)^{m-1}/m!$ (`Parking.eps`; $\varepsilon_1 = 1$).

## Explanation

A parking function of length $n \le y$ cannot have a displacement $\ge y$, so up to the length $y$ the threshold is no restriction: $z^{(y)}_n = c_n = (n+1)^{n-1}/n!$ for $n \le y$ (`Parking.zr_eq_cc`). The statement says that the same holds for the kernel, and it holds for the same reason: the coefficients of $1 - 1/Z_y$ up to the degree $y$ depend only on the coefficients of $Z_y$ up to the degree $y$, and those are the coefficients of the series $P = \sum c_n X^n$ of all parking functions, whose inverse has the coefficients $-\varepsilon_m$. The sequence $\varepsilon$ is thus the prime kernel of the problem without a bound on the displacement, and it is called the free prime kernel.

The statement is what connects the kernel $\kappa^{(k)}$ of the inequalities on all rows with the kernel $\varepsilon$ of the column equations on the rows $n \le 2k-1$ (`Parking.dq_col`): there the kernel is evaluated only at indices $m \le k-1$. It is also the starting point of every estimate of the kernel beyond the free range, since the recursion `Parking.kq_rec` produces $\kappa^{(y)}_N$, $N > y$, from the values in the free range. The range cannot be extended: for $y = 2$, $\kappa^{(2)}_3 = 1/6$ while $\varepsilon_3 = 2/3$.

## Proof

By strong induction on $m$. Fix $m$ with $1 \le m \le y$ and suppose $\kappa^{(y)}_i = \varepsilon_i$ for all $1 \le i < m$.

Write $K_y = 1 - 1/Z_y$ (`Parking.Ks`) and $z^{(y)}_n = [X^n] Z_y = A(n,y-1)/n!$ (`Parking.zr`). The identity $(1 - K_y)\, Z_y = 1$ (`Parking.Zs_mul_one_sub_Ks`), read at the coefficient of $X^m$ with the coefficients of $1 - K_y$ given by `Parking.coeff_one_sub_Ks_zero` and `Parking.coeff_one_sub_Ks_of_pos`, is the renewal equation
$$z^{(y)}_m \;=\; \sum_{i=1}^{m} \kappa^{(y)}_i\, z^{(y)}_{m-i}.$$
All indices $m$ and $m - i$ that occur are at most $y$, so by `Parking.zr_eq_cc` every $z^{(y)}$ may be replaced by $c$:
$$c_m \;=\; \sum_{i=1}^{m} \kappa^{(y)}_i\, c_{m-i}.$$
On the other hand `Parking.eps_conv` states $\sum_{i=1}^{m} \varepsilon_i\, c_{m-i} = c_m$ for $m \ge 1$; this is the same renewal equation for the unrestricted counts. Subtracting,
$$\sum_{i=1}^{m} \bigl(\kappa^{(y)}_i - \varepsilon_i\bigr)\, c_{m-i} \;=\; 0 .$$
By the induction hypothesis the terms with $i < m$ vanish, and the term $i = m$ is $(\kappa^{(y)}_m - \varepsilon_m)\, c_0$ with $c_0 = 1$ (`Parking.cc_zero`). Hence $\kappa^{(y)}_m = \varepsilon_m$.
