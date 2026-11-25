---
weight: unit
short: mean of the birthday law
---
## Description

The number $s_m = \sum_{j=1}^{m} P_{m,j}$, where $P_{m,j} = \prod_{i<j}(1 - i/m)$: the mean of the birthday law of $m$, that is the expected number of uniform draws from $m$ values before the first repetition.

## Statement

For a natural number $m$,

$$s_m \;=\; \sum_{j=1}^{m} P_{m,j},$$

where $P_{m,j}$ is the birthday tail of `Parking.Pb`. In particular $s_0 = 0$, the empty sum.

## Explanation

**What $s_m$ measures.** Let $Q$ follow the birthday law of $m$, described in the record of `Parking.Pb`: $Q$ takes the values $1, \dots, m$ and $\Pr(Q \ge j) = P_{m,j}$. The mean of a variable with values in the positive integers is the sum of its tail probabilities, so $\mathbb{E}[Q] = \sum_{j \ge 1} \Pr(Q \ge j) = s_m$; the terms with $j > m$ vanish. Written with the point masses $\Pr(Q = q) = \frac{q}{m} P_{m,q}$, this is the identity $\sum_{q=1}^{m} q^2 P_{m,q} = m\, s_m$, which is `Parking.Pb_moment` applied to $g(j) = j$. By `Parking.Tq_eq`, $s_m$ is therefore the mean number of parts of a composition of $m$ drawn with probability proportional to the product of the weights $a_p = p^{p-1}/p!$ of its parts. The first values are $s_1 = 1$, $s_2 = 3/2$ and $s_3 = 17/9$.

**Why this one number is kept.** The next two factorial moments of $Q$ are expressed through $m$ and $s_m$ alone: $\mathbb{E}[Q(Q-1)] = 2(m - s_m)$ and $\mathbb{E}[Q(Q-1)(Q-2)] = 3((m+2)s_m - 3m)$, which are `Parking.Pb_sum3` and `Parking.Pb_sum4` divided by $m$. Their quotient is $D_m$ (`Parking.Dbirth`), and $D_m + 1$ is the factor in the exponent of the bound `Parking.curvSum_step`. A numerical bound for $s_m$ thus gives a numerical bound for that exponent (`Parking.Dbirth_add_one_le`).

**What is proved about it.** For $m \ge 2$, $s_m < m$ (`Parking.sbirth_lt`). The sharp upper bound is `Parking.sbirth_le`: $s_m \le \sqrt{\pi m/2}\; e^{1/(12m)} - \tfrac13$ for $m \ge 1$.

**Name in the literature.** The sum $1 + \frac{m-1}{m} + \frac{(m-1)(m-2)}{m^2} + \cdots$ is known as Ramanujan's $Q$-function $Q(m)$. The library uses nothing about it beyond what it proves.

**The Lean form.** `sbirth m` is the sum of `Pb m j` over `Finset.Icc 1 m`.
