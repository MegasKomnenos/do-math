---
weight: step
short: the homogeneous total as a polynomial in the weight of a cut
---
## Description

The total weight of the compositions of $m$ for the constant cut profile $h$ is $\tau_m(h) = \sum_{q=1}^{m} T_{m,q}\, h^{q-1}$.

## Statement

For every natural number $m$ and every real number $h$,

$$\tau_m(h) = \sum_{q=1}^{m} T_{m,q}\, h^{q-1},$$

where $\tau_m(h)$ is the total weight of the compositions of $m$ when every cut weighs $h$ (`Parking.tau`) and $T_{m,q}$ is the total Cayley weight of the compositions of $m$ with $q$ parts (`Parking.Tq`).

## Explanation

The definition of $\tau_m(h)$ is the total weight for the constant profile $h$; the statement is the form in which it is used, a polynomial in $h$ whose coefficients are the weights of the homogeneous model. In this form $\tau_m(h)$ is the normalising constant of the law that gives the number of parts the probability $T_{m,q} h^{q-1}/\tau_m(h)$, and the statements about that law (`Parking.tau_pos`, `Parking.mu0_le_muh`) start from it.

## Proof

By definition $\tau_m(h) = \sum_{q=1}^{m} V_q(m; h)$ with the weights of `Parking.Vc` for the constant profile $h$. A composition with $q$ parts has $q - 1$ cuts, so $V_q(m; h) = h^{q-1} V_q(m; \mathbf{1}) = h^{q-1} T_{m,q}$. This is the homogeneity of the weights in the profile, $V_q(m; y f) = y^{q-1} V_q(m; f)$, applied to the constant profile $f = \mathbf{1}$ and $y = h$; its proof, an induction on $q$ through `Parking.Vc_succ_succ`, is given in the record of `Parking.Vc_thr`.
