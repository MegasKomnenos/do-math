---
weight: unit
short: moment ratio of the birthday law
---
## Description

The number $D_m = \dfrac{3((m+2)s_m - 3m)}{2(m - s_m)}$ formed from the mean $s_m$ of the birthday law of $m$; for $m \ge 2$ it is the ratio of the third to the second factorial moment of that law.

## Statement

For a natural number $m \ge 2$,

$$D_m \;=\; \frac{3\bigl((m+2)\,s_m - 3m\bigr)}{2\,(m - s_m)},$$

where $s_m = \sum_{j=1}^{m} P_{m,j}$ is the mean of the birthday law (`Parking.sbirth`, with $P_{m,j}$ from `Parking.Pb`). The denominator is positive because $s_m < m$ (`Parking.sbirth_lt`). For $m = 0$ and $m = 1$ the numerator and the denominator of this formula are both $0$, and the Lean definition, in which a quotient by $0$ is $0$, gives $D_0 = D_1 = 0$.

## Explanation

**What $D_m$ measures.** Let $Q$ follow the birthday law of $m$ (see `Parking.Pb`), so that $\Pr(Q = q) = \frac{q}{m} P_{m,q}$ for $1 \le q \le m$. The identities `Parking.Pb_sum3` and `Parking.Pb_sum4`, divided by $m$, give the second and the third factorial moment of $Q$:

$$\mathbb{E}[Q(Q-1)] = 2(m - s_m), \qquad \mathbb{E}[Q(Q-1)(Q-2)] = 3\bigl((m+2)s_m - 3m\bigr).$$

Hence $D_m = \mathbb{E}[Q(Q-1)(Q-2)]\,/\,\mathbb{E}[Q(Q-1)]$ for $m \ge 2$. The library states this for the weights of compositions as `Parking.Dbirth_spec`: $\sum_q q(q-1)(q-2)\,T_{m,q} = D_m \sum_q q(q-1)\,T_{m,q}$, where $T_{m,q}$ is the total weight of the compositions of $m$ with $q$ parts (`Parking.Tq`). For example $D_2 = 0$, because $Q \le 2$ when $m = 2$, and $D_3 = 3/5$: for $m = 3$ the point masses of $Q$ are $\frac13, \frac49, \frac29$, so $\mathbb{E}[Q(Q-1)] = \frac{20}{9}$ and $\mathbb{E}[Q(Q-1)(Q-2)] = \frac{12}{9}$.

**Why it is defined by the closed formula.** The definition is the formula in $m$ and $s_m$ and not the quotient of two sums, so that a bound for $s_m$ turns directly into a bound for $D_m$. The criterion function `Parking.Gfun` contains the term $-\frac{k}{k-1} D_r$, and its positivity (`Parking.Gfun_pos`) is proved from the upper bound `Parking.sbirth_le` for $s_r$ together with `Parking.Dbirth_le`, `Parking.Dbirth_mono` and `Parking.Dbirth_nonneg`.

**Where it is used.** For a polynomial $p(y) = \sum_q p_q y^q$ with nonnegative coefficients, the inequality $\sum_q q(q-1)(q-2)\,p_q y^q \le D \sum_q q(q-1)\,p_q y^q$ says that $y\,p'''(y) \le D\,p''(y)$, which limits how fast the second derivative of $p$, and with it the second difference of $p$, can grow. The proof of `Parking.curv_ratio` establishes this inequality with $D = D_r$ for the frozen polynomial of a first-layer position $n = k + r$, by comparing the law of the number of parts under each threshold profile with the birthday law, and concludes that the second differences at $k+1$ and at $k$ satisfy $C_+ \le e^{D_r/(k-1)} C_-$. The monotonicity `Parking.Dbirth_mono` is what allows the one constant $D_r$ to serve for all the compositions of the integers $m \le r$ that occur there.

**The values at $m \le 1$.** The statement of `Parking.curv_ratio` admits $r = 0$ and $r = 1$, and there $D_r$ has the value $0$ given above. Every statement about $D_m$ in this part of the library assumes $m \ge 2$.

**The Lean form.** `Dbirth m` is `3 * ((m + 2) * sbirth m - 3 * m) / (2 * (m - sbirth m))` with $m$ cast to a real number.
