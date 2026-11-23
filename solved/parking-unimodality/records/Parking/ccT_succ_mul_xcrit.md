---
weight: step
short: consecutive tilted Cayley masses and the critical tilt of the upper index
---
## Description

$c_{j+1} x^{j+1} \cdot x_{j+1} = x \cdot c_j x^j$, where $x_{j+1}$ is the critical tilt of the index $j+1$. For a tilt $x > 0$ this says that the ratio of the tilted Cayley masses of the indices $j+1$ and $j$ is $x / x_{j+1}$.

## Statement

For every real number $x$ and every natural number $j$,
$$c_{j+1}\, x^{j+1} \cdot x_{j+1} \;=\; x \cdot c_j\, x^j ,$$
where $c_n = (n+1)^{n-1}/n!$ (`Parking.cc`, tilted: `Parking.ccT`) and $x_{j+1} = ((j+1)/(j+2))^{j}$ is the critical tilt of the index $j+1$ (`Parking.xcrit`).

## Explanation

This is the ratio formula `Parking.ccT_succ` with the factor $(1+1/(j+1))^j$ written as $1/x_{j+1}$. It shows directly that, for a tilt $x > 0$, the masses of the indices $j$ and $j+1$ are equal exactly when $x = x_{j+1}$, and it is the form used in the first-layer analysis of the left half, where the tilt is $x_k$ and masses of indices near $k$ are compared.

## Proof

By `Parking.ccT_succ`, $c_{j+1} x^{j+1} = x\,(1+1/(j+1))^{j}\, c_j x^j$. By `Parking.xcrit_mul_psi` for the index $j+1 \ge 1$, $x_{j+1}\,(1+1/(j+1))^{j} = 1$. Multiplying the first identity by $x_{j+1}$ gives the claim.
