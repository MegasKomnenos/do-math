---
weight: step
short: nonnegativity of the weight of the compositions with q parts
---
## Description

The total weight $T_{m,q}$ of the compositions of $m$ with $q$ parts is nonnegative for all $m$ and $q$.

## Statement

For all natural numbers $m$ and $q$, $T_{m,q} \ge 0$, where $T_{m,q}$ is the total weight of the compositions of $m$ with exactly $q$ parts, each part of size $p$ weighted by $a_p = p^{p-1}/p!$ (`Parking.Tq`).

## Explanation

Unlike `Parking.Tq_pos`, the statement has no condition on $q$: for $q = 0$ and for $q > m$ the value is $0$. It supplies the sign conditions in the arguments that multiply and add inequalities between weights of compositions: `Parking.tau_pos`, `Parking.muh_nonneg`, `Parking.Dbirth_nonneg`, and the proofs of `Parking.curv_ratio` and `Parking.Lam_raise`.

## Proof

$T_{m,q}$ is $V_q(m;f)$ of `Parking.Vc` for the constant profile $f = 1$, which is nonnegative, and `Parking.Vc_nonneg` states that $V_q(m;f) \ge 0$ for every $q$ when $f$ is nonnegative at the cut points $1, \dots, m-1$.
