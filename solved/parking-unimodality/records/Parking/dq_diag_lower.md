---
weight: step
short: the diagonal lower bound for the step
---
## Description

For $k \ge 2$ and every row $n \ge 1$: $\gamma_k\,\beta^{(k-1)}_{n-1} - \beta^{(k-1)}_n \le \delta_n$, where $\delta_n = \beta^{(k)}_n - \beta^{(k-1)}_n$ is the normalised step of the column $k$, $\beta^{(\ell)}_n = b(n,\ell)/n!$ and $\gamma_k = (1+1/k)^{k-2}$.

## Statement

Let $k \ge 2$ and $n \ge 1$ be natural numbers. Then
$$\gamma_k\; \beta^{(k-1)}_{n-1} - \beta^{(k-1)}_n \;\le\; \delta_n ,$$
where $\beta^{(\ell)}_n = b(n,\ell)/n!$ (`Parking.bq`), $\delta_n = \beta^{(k)}_n - \beta^{(k-1)}_n$ (`Parking.dq`) and $\gamma_k = (1+1/k)^{k-2}$ (`Parking.gam`).

## Explanation

This is the diagonal lower bound `Parking.bq_diag_lower` with $\beta^{(k-1)}_n$ subtracted on both sides. It bounds the step of the column $k$ in the row $n$ from below by the amount by which the profile $\beta^{(k-1)}$ of the neighbouring level, scaled by $\gamma_k$ per row, decreases from the row $n-1$ to the row $n$. In this form it is one of the hypotheses of the persistence inequality (`Parking.persistence_inequality`), which the far rows of the chain column supply from the present statement.

## Proof

By `Parking.bq_diag_lower`, $\gamma_k\,\beta^{(k-1)}_{n-1} \le \beta^{(k)}_n$. Subtract $\beta^{(k-1)}_n$ and use $\delta_n = \beta^{(k)}_n - \beta^{(k-1)}_n$, the definition of `Parking.dq`.
