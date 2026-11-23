---
weight: step
short: the total composition weight depends on the profile at the cut points only
---
## Description

Two cut profiles that agree at the points $1, \dots, m-1$ give the same total weight of the compositions of $m$: $\Lambda_m[f] = \Lambda_m[g]$.

## Statement

Let $f, g : \mathbb{N} \to \mathbb{R}$ and let $m$ be a natural number such that $f(s) = g(s)$ for every $s$ with $0 < s < m$. Then $\Lambda_m[f] = \Lambda_m[g]$, where $\Lambda_m[f]$ is defined in `Parking.Lam`.

## Explanation

The statement is `Parking.Vc_congr` summed over the number of parts. It is used in the proof of `Parking.Lam_first_cell`, where the threshold profile is replaced by a profile that agrees with it at the cut points and satisfies a lower bound at all natural numbers.

## Proof

By `Parking.Vc_congr`, $V_q(m;f) = V_q(m;g)$ for every $q$, and $\Lambda_m$ is the sum of these over $1 \le q \le m$.
