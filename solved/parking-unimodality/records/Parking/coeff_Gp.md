---
weight: step
short: coefficients of the logarithmic derivative
---
## Description

The coefficient of $X^j$ in the series $\Gamma_y'$ of a threshold $y$ is $\min(j+1,y)\, z^{(y)}_j$.

## Statement

For all natural numbers $y$ and $j$,
$$[X^j]\,\Gamma_y' \;=\; \min(j+1,y)\; z^{(y)}_j ,$$
where $\Gamma_y'$ is the series `Parking.Gp`, the formal derivative of $\Gamma_y = \sum_{t\ge1} \frac{\min(t,y)}{t} z^{(y)}_{t-1} X^t$, and $z^{(y)}_j = A(j,y-1)/j!$ (`Parking.zr`).

## Explanation

The coefficient is the weight $\min(j+1,y)$ of the last-car recursion, the number of admissible preferences of a last car with $j$ cars to its left, times the normalised count $z^{(y)}_j$. The formula is what the comparisons of $\Gamma_y'$ for different thresholds are computed from: $\Gamma_y' = y Z_y - \sum_{j\le y-2}(y-1-j)\,c_j X^j$ (with $Z_y$ the series `Parking.Zs` and $c_j = (j+1)^{j-1}/j!$, `Parking.cc`) in the proof of `Parking.kq_rec`, and $\Gamma_k' - \Gamma_{k-1}' = k (Z_k - Z_{k-1}) + \sum_{j\ge k-1} z^{(k-1)}_j X^j$ in the proof of `Parking.col_eq_all`.

## Proof

The coefficient of $X^j$ in the derivative of a power series $F$ is $(j+1)\,[X^{j+1}] F$. The coefficient of $X^{j+1}$ in $\Gamma_y$ is $\frac{\min(j+1,y)}{j+1}\, z^{(y)}_j$ by definition, and the factor $j+1$ cancels.
