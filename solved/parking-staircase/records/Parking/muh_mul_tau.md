---
weight: step
short: the mean number of cuts without the division
---
## Description

The mean number of cuts times the total weight: $\mu_r(h)\,\tau_r(h) = \sum_{q=1}^{r}(q-1)\,T_{r,q}\,h^{q-1}$ for $r \ge 1$ and $h \ge 0$.

## Statement

For every natural number $r \ge 1$ and every real number $h \ge 0$,

$$\mu_r(h)\;\tau_r(h) \;=\; \sum_{q=1}^{r}(q-1)\;T_{r,q}\;h^{q-1}.$$

Here $T_{r,q}$ is the total weight of the compositions of $r$ with $q$ parts, each part of size $p$ weighted by $a_p = p^{p-1}/p!$ (`Parking.Tq`); $\tau_r(h) = \sum_{q=1}^{r} T_{r,q}\,h^{q-1}$ is the total weight of all compositions of $r$ when every cut weighs $h$ (`Parking.tau`, `Parking.tau_eq`); and $\mu_r(h)$ is the quotient of the sum on the right by $\tau_r(h)$ (`Parking.muh`).

## Explanation

A composition with $q$ parts has $q - 1$ cuts. Under the homogeneous law with parameter $h$, in which a composition of $r$ has probability proportional to its weight with cut weight $h$, the number of parts $Q$ satisfies $\Pr(Q = q) = T_{r,q}\,h^{q-1}/\tau_r(h)$, and $\mu_r(h) = \mathbb{E}[Q - 1]$ is the mean number of cuts. The identity is the definition of $\mu_r(h)$ with the division removed, which is the form the proofs work with: `Parking.mu0_le_muh` inserts `Parking.Tq_eq` into the sum on the right, and the proof of `Parking.Lam_gain` arrives at the sum on the right as the total weight of the compositions of $r$ with one marked cut, for the constant cut weight $h$, and uses the identity to write it as $\mu_r(h)\,\tau_r(h)$.

The hypotheses $r \ge 1$ and $h \ge 0$ serve only to make $\tau_r(h) \ne 0$. In Lean the exponent $q - 1$ is a natural number, so for $h = 0$ the term with $q = 1$ has the factor $0^0 = 1$.

## Proof

By definition $\mu_r(h)$ is the sum on the right divided by $\tau_r(h)$, and $\tau_r(h) > 0$ by `Parking.tau_pos`.
