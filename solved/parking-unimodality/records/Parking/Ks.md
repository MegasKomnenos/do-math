---
weight: unit
short: prime kernel series of a threshold
---
## Description

The prime kernel series $K_y = 1 - 1/Z_y$ of a threshold $y$, where $Z_y$ is the series of the threshold $y$ (`Parking.Zs`).

## Statement

For a natural number $y$, let $Z_y = \sum_{n\ge0} z^{(y)}_n X^n$ be the series of the threshold $y$ (`Parking.Zs`; $z^{(y)}_n = A(n,y-1)/n!$ is the sequence `Parking.zr`). The prime kernel series of the threshold $y$ is the formal power series
$$K_y \;=\; 1 - Z_y^{-1}.$$

## Explanation

For $y \ge 1$ the constant term of $Z_y$ is $1$, so $Z_y$ is invertible, $K_y$ has constant term $0$ (`Parking.kq_zero`), and $Z_y\,(1 - K_y) = 1$ (`Parking.Zs_mul_one_sub_Ks`). Read coefficient by coefficient, this identity is a renewal equation: $z^{(y)}_n = \sum_{m=1}^{n} \kappa^{(y)}_m\, z^{(y)}_{n-m}$ for $n \ge 1$, where $\kappa^{(y)}_m$ is the coefficient of $X^m$ in $K_y$ (`Parking.kq`). The series $K_y$ is the kernel of that equation.

Combinatorially, $m!\,\kappa^{(y)}_m$ is the number of prime parking functions of length $m$ all of whose displacements are smaller than $y$, that is, of those that cannot be cut into two; the identity $Z_y = 1/(1-K_y)$ then expresses the decomposition of a parking function into a sequence of prime ones. The library does not define prime parking functions and does not prove this interpretation. It takes the algebraic definition above as the definition, and the name records where the series comes from. The reason for this choice is that every property of the kernel that the argument needs follows from the differential equation $Z_y' = \Gamma_y' Z_y$ of the last-car recursion (`Parking.deriv_Zs`; $\Gamma_y'$ is the series `Parking.Gp`) by the algebra of power series: the value of the kernel in the free range (`Parking.kq_eq_eps`), the differential equation $K_y' = (1-K_y)\,\Gamma_y'$ (`Parking.deriv_Ks`), and the recursion beyond the free range (`Parking.kq_rec`). A combinatorial definition would have required a formal proof of the prime decomposition and would have added nothing to these.

Multiplication by $1 - K_y$ is division by $Z_y$. This is how the kernel enters the inequalities of a column on all rows (`Parking.col_eq_all`, `Parking.bq_diag_lower`): the second difference $Z_{k+1} - 2Z_k + Z_{k-1}$ is multiplied by $1 - K_k$, and the quotients $Z_{k+1}/Z_k$ and $Z_{k-1}/Z_k$ that result satisfy differential equations with nonnegative coefficients.

In Lean, `Ks y` is `1 - (Zs y)⁻¹`, with Mathlib's inverse of a power series over a field. That inverse is defined for every series and is the true inverse when the constant coefficient is not zero, which is the case here.
