---
weight: step
short: positivity of a renewal sequence
---
## Description

The renewal sequence of a kernel with positive terms $f_1,f_2,\dots$ is positive.

## Statement

Let $f$ and $u$ be real sequences such that $u$ is the renewal sequence of the kernel $f$ (`Parking.IsRenewal`): $u_0=1$ and $u_n=\sum_{i=1}^{n}f_iu_{n-i}$ for $n\ge1$. If $f_i>0$ for every $i\ge1$, then $u_n>0$ for every $n\ge0$.

## Explanation

Positivity is what allows the inequalities about ratios of consecutive terms of $u$ to be written in cross-multiplied form and divided out again; it is the first step of the proof that $u$ is log-convex (`Parking.renewal_logConvex`) and a hypothesis of the cross-ratio inequality `Parking.logConvex_cross` when that is applied to $u$, as in the proof of `Parking.extreme_column_le`. Applied to the frozen kernel it gives the positivity of its renewal sequence (`Parking.Gres_pos`).

## Proof

By strong induction on $n$. $u_0=1>0$. For $n\ge1$, $u_n=\sum_{i=1}^{n}f_iu_{n-i}$ is a nonempty sum of products of a positive $f_i$ and, by the induction hypothesis, a positive $u_{n-i}$.
