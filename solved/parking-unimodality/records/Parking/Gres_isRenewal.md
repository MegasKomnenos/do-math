---
weight: unit
short: the resolvent sequence is the renewal sequence of the frozen kernel
---
## Description

The sequence $G$ is the renewal sequence of the frozen kernel $f$: $G_0 = 1$ and $G_n = \sum_{i=1}^{n}f_iG_{n-i}$ for $n \ge 1$.

## Statement

Let $f$ be the frozen kernel of `Parking.fker` ($f_1 = \frac32e^{-1}$, $f_i = e^{-i}\varepsilon_i$ for $i\ge2$) and $G$ the sequence of `Parking.Gres`, $G_s = e^{-s}\sum_{j=0}^{s}2^{-j}[X^s]X^jP^{j+1}$. Then $G_0 = 1$ and, for every natural number $n \ge 1$,

$$G_n = \sum_{i=1}^{n} f_i\,G_{n-i}.$$

In Lean: `IsRenewal fker Gres`, with the predicate of `Parking.IsRenewal`.

## Explanation

This statement connects the definition of $G$ by explicit coefficients with the role $G$ has in the argument. All general facts about renewal sequences become available for $G$: positivity (`Parking.renewal_pos`, giving `Parking.Gres_pos`), log-convexity (`Parking.renewal_logConvex`, used inside `Parking.extreme_column_le`), and the representation of a solution of a convolution equation through its innovations (`Parking.resolvent`, used for `Parking.Gres_sum_le` and inside `Parking.extreme_column_le`).

The identity behind it is $E\cdot X^jP^{j+1} = X^jP^{j}$ for the series $E = 1/P$, whose coefficients are $1, -\varepsilon_1, -\varepsilon_2, \dots$: convolving the $j$-th family of coefficients with the prime kernel lowers $j$ by one and shifts the index by one, and the weights $2^{-j}$ turn this into the term $\frac12H_{s-1}$.

## Proof

Write $h_{j,s} = [X^s]X^jP^{j+1}$ (`Parking.hcoef`) and $H_s = \sum_{j=0}^{s}2^{-j}h_{j,s}$ (`Parking.Hres`), so that $G_s = e^{-s}H_s$. Two elementary facts are used: $h_{j,s} = 0$ for $s < j$, since $X^j$ divides the series, so that $H_s = \sum_{j<N}2^{-j}h_{j,s}$ for every $N \ge s+1$; and $h_{0,s} = [X^s]P = c_s$.

*The value at $0$.* $H_0 = h_{0,0} = c_0 = 1$, so $G_0 = 1$.

*The renewal identity of one family.* Fix $j$ and $s \ge 1$. By `Parking.TreeSeries.coeff_Eser_mul`, applied to the series $X^jP^{j+1}$,

$$h_{j,s} - \sum_{m=1}^{s}\varepsilon_m\,h_{j,s-m} = [X^s]\;E\cdot X^jP^{j+1}.$$

Since $E\,P = 1$ (`Parking.TreeSeries.Eser_mul_Pser`), the series on the right is $X^jP^j$. For $j = 0$ it is the constant $1$, whose coefficient at $s \ge 1$ is $0$. For $j \ge 1$ it is $X\cdot X^{j-1}P^{j}$, whose coefficient at $s$ is $h_{j-1,s-1}$.

*The renewal identity of $H$.* Let $s \ge 1$. Multiply the identity of the $j$-th family by $2^{-j}$ and sum over $0 \le j \le s$, extending all sums over $j$ to this common range by the first elementary fact. The left side becomes $H_s - \sum_{m=1}^{s}\varepsilon_mH_{s-m}$, and the right side becomes $\sum_{j=1}^{s}2^{-j}h_{j-1,s-1} = \frac12H_{s-1}$. Hence

$$H_s = \sum_{m=1}^{s}\varepsilon_m H_{s-m} + \tfrac12 H_{s-1}.$$

*The scaling.* Multiply by $e^{-s}$. Since $e^{-s} = e^{-m}e^{-(s-m)}$, the term $e^{-s}\varepsilon_mH_{s-m}$ is $e^{-m}\varepsilon_m\,G_{s-m}$, and $e^{-s}\cdot\frac12H_{s-1} = \frac12e^{-1}G_{s-1}$. The sum of the two contributions at each index $i$ is $f_iG_{s-i}$, because $f_i = e^{-i}\varepsilon_i$ plus $\frac12e^{-1}$ at $i = 1$. This is the renewal equation at $n = s$.
