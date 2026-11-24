---
weight: step
short: threshold profile
---
## Description

The threshold profile $\lambda^{y,N}$ is the cut profile $s \mapsto y/(N-s)$, for real numbers $y$ and $N$.

## Statement

For real numbers $y$ and $N$ and a natural number $s$,

$$\lambda^{y,N}(s) = \frac{y}{N-s}.$$

## Explanation

A cut profile assigns a weight to each cut point of a composition (`Parking.Vc`). The threshold profile is the one that the parking problem produces. In the chain expansion of `Parking.Kpoly` a composition is read from a top size $N$ downwards: a cut at the position $s$ means that the chain visits the size $t = N - s$, and every visited size $t$ contributes the factor $y/t$, where $y$ is the threshold on the displacements. The total weight $\Lambda_m[\lambda^{y,N}]$ of the compositions of $m$ for this profile (`Parking.Lam`) is written $\Lambda_m(y;N)$ and called a chain sum.

Two features of the profile are used. The number $y$ enters every cut once, so the weight of the compositions with $q$ parts is $y^{q-1}$ times its value at $y = 1$ (`Parking.Vc_thr`), and $\Lambda_m(y;N)$ is a polynomial in $y$ (`Parking.Lam_thr`). And the profile increases with $s$: a cut far from the top, where the remaining size $N - s$ is small, weighs more. The comparison with a constant profile in `Parking.Lam_gain` takes the value of the threshold profile at the first cut point, which is its smallest value on the cut points.

In Lean the profile is `thr y N`. Wherever it is used, the cut points satisfy $s < N$, so the denominator is positive. At $s = N$ the Lean division gives the value $0$, which plays no role.
