---
weight: step
short: recursion of the tilted prime kernel
---
## Description

For $N \ge y \ge 2$ and any tilt $x$, the tilted prime kernel $q_m = \kappa^{(y)}_m x^m$ satisfies $N q_N = \sum_{\gamma=1}^{y-1} (y-\gamma)\, a_\gamma x^\gamma\, q_{N-\gamma}$.

## Statement

Let $y \ge 2$ and $N \ge y$ be natural numbers, $x$ a real number, and $q_m = \kappa^{(y)}_m x^m$ the tilted prime kernel of the threshold $y$ (`Parking.kqT`, `Parking.kq`). Then
$$N\, q_N \;=\; \sum_{\gamma=1}^{y-1} (y-\gamma)\; a_\gamma x^\gamma\; q_{N-\gamma},$$
where $a_\gamma = \gamma^{\gamma-1}/\gamma!$ (`Parking.cay`).

## Explanation

This is the recursion `Parking.kq_rec` multiplied by $x^N$. The indices $\gamma$ and $N-\gamma$ of each term add up to $N$, so the power $x^N$ splits between the weight and the kernel, and the recursion keeps its form with the tilted weights $(y-\gamma)^+ a_\gamma x^\gamma$ (`Parking.kqWT`). The estimates of the tilted kernel (`Parking.kqT_nonneg`, `Parking.kqT_harmonic`, `Parking.kqT_succ_le`, and those of the left half) all start from this form.

In Lean the right-hand side is `rconv (kqWT y x) (kqT y x) N` $= \sum_{\gamma=1}^{N} (y-\gamma)^+ a_\gamma x^\gamma\, q_{N-\gamma}$ (`Parking.rconv`). The weights vanish for $\gamma \ge y$ and $N \ge y$, so this is the sum of the statement.

## Proof

By `Parking.kq_rec`, $N \kappa^{(y)}_N = \sum_{\gamma=1}^{N} (y-\gamma)^+ a_\gamma\, \kappa^{(y)}_{N-\gamma}$. Multiply by $x^N$ and write $x^N = x^{\gamma} \cdot x^{N-\gamma}$ in the term of index $\gamma$.
