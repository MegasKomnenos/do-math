---
weight: step
short: the mean of the birthday law is less than m
---
## Description

The mean of the birthday law of $m \ge 2$ is less than $m$: $s_m < m$.

## Statement

For every natural number $m \ge 2$, $s_m < m$, where $s_m = \sum_{j=1}^{m} P_{m,j}$ (`Parking.sbirth`) and $P_{m,j}$ is the birthday tail (`Parking.Pb`).

## Explanation

The statement is what makes the denominator $2(m - s_m)$ of $D_m$ (`Parking.Dbirth`) positive, and it is used for that purpose in `Parking.Dbirth_spec`, `Parking.Dbirth_add_one_le` and `Parking.sum_qq_Tq_pos`. In terms of the birthday law it says that the second factorial moment $2(m - s_m)$ of the number $Q$ of draws before the first repetition (`Parking.Pb_sum3`) is positive, that is, that $Q \ge 2$ has positive probability. For $m = 1$ the statement fails: $s_1 = 1$.

## Proof

Each of the $m$ terms $P_{m,j}$, $1 \le j \le m$, is at most $1$, and the term with $j = 2$, which occurs because $m \ge 2$, is $P_{m,2} = 1 - 1/m < 1$ by `Parking.Pb_succ` and `Parking.Pb_one`. Hence the sum is strictly less than $m$.

The bound $P_{m,j} \le 1$ holds for all $m$ and $j$: for $m = 0$ the value is $1$; for $m \ge 1$ and $j \le m$ every factor $1 - i/m$ of the product lies in $[0,1]$; and for $m \ge 1$ and $j > m$ the value is $0$ by `Parking.Pb_eq_zero`.
