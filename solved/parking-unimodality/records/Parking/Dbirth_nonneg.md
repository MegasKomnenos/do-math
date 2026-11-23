---
weight: step
short: nonnegativity of the moment ratio
---
## Description

The moment ratio of the birthday law is nonnegative: $D_m \ge 0$ for $m \ge 2$.

## Statement

For every natural number $m \ge 2$, $D_m \ge 0$, where $D_m = 3((m+2)s_m - 3m)/(2(m - s_m))$ and $s_m$ is the mean of the birthday law (`Parking.Dbirth`, `Parking.sbirth`).

## Explanation

In the closed formula the sign is not visible: it amounts to $s_m \ge 3m/(m+2)$. It is visible in the description of $D_m$ as a quotient of two factorial moments (`Parking.Dbirth_spec`), both of which are sums of nonnegative terms. The sign is used in the proof of `Parking.Gfun_pos`, where the coefficient $k/(k-1)$ of $D_r$ in the criterion function `Parking.Gfun` is replaced by its upper bound $265/264$.

## Proof

The sum $\sum_{q=1}^{m} q(q-1)(q-2)\,T_{m,q}$, with $T_{m,q}$ from `Parking.Tq`, is nonnegative: $T_{m,q} \ge 0$ by `Parking.Tq_nonneg`, and for an integer $q \ge 1$ the product $q(q-1)(q-2)$ is $0$ if $q = 1$ and a product of three nonnegative numbers if $q \ge 2$. By `Parking.Dbirth_spec` this sum equals $D_m \sum_{q=1}^{m} q(q-1)\,T_{m,q}$, and the second factor is positive by `Parking.sum_qq_Tq_pos`. Hence $D_m \ge 0$.
