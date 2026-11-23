---
weight: step
short: dropping a vanishing tail of a sum
---
## Description

If $f(m)=0$ for $a<m\le n$, then $\sum_{m=1}^{n}f(m)=\sum_{m=1}^{a}f(m)$.

## Statement

Let $f$ be a real-valued function on the natural numbers and let $a\le n$ be natural numbers. If $f(m)=0$ for every $m$ with $a<m\le n$, then
$$\sum_{m=1}^{n}f(m)=\sum_{m=1}^{a}f(m).$$

## Explanation

The single-chain formula gives the coefficients of a product of series as a convolution $\sum_{m=1}^{n}\varepsilon_m\,w_{n-m}$ over all $m\le n$, with $\varepsilon_m=(m-1)^{m-1}/m!$ (`Parking.eps`), in which the terms with $n-m$ below the column vanish, because the sequences $\beta^{(k)}_j=b(j,k)/j!$ and $\delta_j=(b(j,k)-b(j,k-1))/j!$ (`Parking.bq`, `Parking.dq`) are zero for small $j$ (`Parking.bq_eq_zero`, `Parking.dq_eq_zero`). The statement removes these terms and leaves the sums over $1\le m\le n-k-1$ and $1\le m\le n-k$ in which the column equations are stated (`Parking.bq_L0`, `Parking.dq_col`, and on all rows `Parking.col_eq_all`). A mathematical text uses it without mention.

## Proof

The interval $1\le m\le a$ is contained in $1\le m\le n$, and the terms of the larger sum with $m>a$ are zero by hypothesis.
