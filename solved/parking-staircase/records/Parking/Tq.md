---
weight: unit
short: Cayley weight of the compositions with q parts
---
## Description

$T_{m,q}$ is the total weight of the compositions of $m$ with exactly $q$ parts when each part of size $p$ weighs $a_p = p^{p-1}/p!$ and every cut weighs $1$.

## Statement

For natural numbers $m$ and $q$,

$$T_{m,q} = V_q(m;\mathbf{1}),$$

the quantity of `Parking.Vc` for the constant cut profile $\mathbf{1}(s) = 1$. Explicitly, for $q \ge 1$,

$$T_{m,q} = \sum_{\substack{p_1 + \dots + p_q = m \\ p_i \ge 1}} a_{p_1} \cdots a_{p_q},$$

and $T_{m,0} = 0$.

## Explanation

The numbers $T_{m,q}$ are the weights of the homogeneous model, in which a composition is weighted by its parts only. They are the reference against which the weights $V_q(m;f)$ for other profiles are measured. For this model everything is explicit: `Parking.Tq_ratio` gives the ratio of consecutive values, $q\,m\,T_{m,q+1} = (q+1)(m-q)\,T_{m,q}$, and `Parking.Tq_eq` gives the closed form $T_{m,q} = a_m\, q\, P_{m,q}$ with the birthday tail $P_{m,q}$ of `Parking.Pb`. Normalised over $q$, the numbers $T_{m,q}$ are therefore the law of the number of parts that the library calls the birthday law. The generating polynomial of the $T_{m,q}$ in the weight of a cut is $\tau_m(h)$ (`Parking.tau`).

In Lean the definition is `Tq m q`, with the size first and the number of parts second, the reverse of the order in `Vc`.
