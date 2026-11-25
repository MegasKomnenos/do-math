---
weight: step
short: truncated Cayley convolution defect
---
## Description

$\kappa_k(t) = a_t - \sum_{k<i<t} a_i\, a_{t-i}$, where $a_j = j^{j-1}/j!$: the constant term of the Volterra equation of column $k$ and the coefficient sequence of the frozen polynomial.

## Statement

For natural numbers $k$ and $t$,

$$\kappa_k(t) = a_t - \sum_{k < i < t} a_i\, a_{t-i},$$

where $a_j = j^{j-1}/j!$ for $j \ge 1$ and $a_0 = 0$ (`Parking.cay`).

## Explanation

The numbers $\kappa_k(t)$ appear when the single-chain formula is written for a threshold $y \in \{k, k+1\}$. In the size coordinate $M = n + 1$, the normalised count $u(M) = z^{(y)}_{M-1}$ of `Parking.zr` satisfies $u(M) = \kappa_k(M) + \sum_{k<t<M} a_{M-t}\,(y/t)\,u(t)$ for $M \le 2k+2$ (see the proof of `Parking.dq_frozen`). So $\kappa_k(M)$ is the part of $u(M)$ that does not depend on $y$, and it is the value at $y = 0$ of the frozen polynomial: $K_{n,k}(0) = \kappa_k(n+1)$ (`Parking.Kpoly`). The numbers $\kappa_k(N-m)/(N-m)$ are the coefficients with which the chain sums enter that polynomial.

For $t \le k+1$ the sum is empty and $\kappa_k(t) = a_t$. Lowering $k$ by one adds the term of index $i = k$: $\kappa_{k-1}(t) = \kappa_k(t) - a_k a_{t-k}$ for $1 \le k < t$, and $\kappa_{k-1}(k) = a_k$. These two relations are what the comparison of the frozen polynomials of two consecutive columns in `Parking.dq_frozen` rests on. In the range $1 \le t \le 2k+1$ the number $\kappa_k(t)$ is positive (`Parking.kap_pos`).

In Lean the definition is `kap k t`.
