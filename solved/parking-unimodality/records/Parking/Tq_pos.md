---
weight: step
short: positivity of the weight of the compositions with q parts
---
## Description

The total weight $T_{m,q}$ of the compositions of $m$ with $q$ parts is positive for $1 \le q \le m$.

## Statement

For natural numbers $m$ and $q$ with $1 \le q \le m$, $T_{m,q} > 0$, where $T_{m,q}$ is the total weight of the compositions of $m$ with exactly $q$ parts, each part of size $p$ weighted by $a_p = p^{p-1}/p!$ (`Parking.Tq`).

## Explanation

For $1 \le q \le m$ there is at least one composition of $m$ with $q$ parts, and every composition has a positive weight. The closed form of `Parking.Tq_eq` shows the same. The positivity is needed where $T_{m,q}$ is divided out: it is the hypothesis $v > 0$ of `Parking.lr_of_consecutive` in the proof of `Parking.curv_ratio`, where the birthday weights $T_{m,q}$ are the weights of comparison, and it gives the positive term of `Parking.tau_pos`.

## Proof

$T_{m,q}$ is $V_q(m;f)$ of `Parking.Vc` for the constant profile $f = 1$, which is positive at every cut point, so `Parking.Vc_pos` applies: for a profile that is positive at the cut points $1, \dots, m-1$, the total weight of the compositions of $m$ with $q$ parts is positive whenever $1 \le q \le m$.
