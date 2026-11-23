---
weight: unit
short: total weight of the compositions for a constant profile
---
## Description

$\tau_m(h)$ is the total weight of the compositions of $m$ when each part of size $p$ weighs $a_p = p^{p-1}/p!$ and every cut weighs the same real number $h$; it equals $\sum_q T_{m,q} h^{q-1}$.

## Statement

For a natural number $m$ and a real number $h$,

$$\tau_m(h) = \Lambda_m[h],$$

the total weight of `Parking.Lam` for the constant cut profile $s \mapsto h$.

## Explanation

Since every composition with $q$ parts has $q - 1$ cuts, $\tau_m(h) = \sum_{q=1}^{m} T_{m,q}\, h^{q-1}$ with the numbers $T_{m,q}$ of `Parking.Tq`; this is `Parking.tau_eq`. For $h \ge 0$ and $m \ge 1$ the polynomial is positive (`Parking.tau_pos`), and it is the normalising constant of the homogeneous law with parameter $h$ on the compositions of $m$, under which the number of parts $Q$ takes the value $q$ with probability $T_{m,q} h^{q-1} / \tau_m(h)$. For $h = 1$ this is the birthday law (`Parking.Tq_eq`).

The homogeneous law is the model with which the chain sums $\Lambda_m(y;N)$ of the threshold profile (`Parking.thr`) are compared. The threshold profile is not constant, but on the cut points of a segment it lies between constants, and the two comparisons of this part each choose one constant: `Parking.Lam_first_cell` takes $h = (k-1)/(k+r)$, the value of the profile at the first cut point, and `Parking.Lam_raise` takes $h = k/(k+1+r/2)$, its value at the middle of the segment. What is then needed about the homogeneous law is proved from the birthday law: the comparison of $\tau_{r+1}(h)$ with $\tau_r(h)$ (`Parking.tau_succ_le`) and a lower bound for the mean number of cuts (`Parking.mu0_le_muh`).

In Lean the definition is `tau m h`.
