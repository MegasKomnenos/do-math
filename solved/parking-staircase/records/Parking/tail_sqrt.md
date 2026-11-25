---
weight: step
short: telescoping lower bound for a sum with terms of order i^(-3/2)
---
## Description

If $G_i \ge c\,(i+1)^{-3/2}$ for all $i \ge a$, with $c \ge 0$, then $\sum_{a\le i<b}G_i \ge 2c\,\bigl(\frac1{\sqrt{a+1}} - \frac1{\sqrt{b+1}}\bigr)$ for every $b \ge a$.

## Statement

Let $G$ be a sequence of real numbers indexed by the natural numbers, $c \ge 0$ a real number and $a$ a natural number such that $G_i \ge \dfrac{c}{(i+1)\sqrt{i+1}}$ for every $i \ge a$. Then for every natural number $b \ge a$,

$$\sum_{i=a}^{b-1} G_i \;\ge\; 2c\,\Bigl(\frac1{\sqrt{a+1}} - \frac1{\sqrt{b+1}}\Bigr).$$

## Explanation

The right side is the integral $\int_{a+1}^{b+1}c\,y^{-3/2}\,dy$; the statement is the comparison of a sum of a decreasing function with its integral, in discrete form. It is stated for an abstract sequence, and it is used once, in `Parking.caseFar`, for the resolvent sequence $G$ of `Parking.Gres` with $c = 1.12\,e$ and $b + 1 = 16(a+1)$: there a lower bound of the tail $\sum_{i\ge a}G_i$ is subtracted from the bound $2e$ of the whole sum (`Parking.Gres_sum_le`).

## Proof

By induction on $b$. For $b = a$ both sides are $0$. For the step from $b = n$ to $n + 1$ the sum gains the term $G_n \ge c\,(n+1)^{-3/2}$, and the right side gains $2c\bigl(\frac1{\sqrt{n+1}} - \frac1{\sqrt{n+2}}\bigr)$. By the second inequality of `Parking.inv_sqrt_diff_bounds`, $2\bigl(\frac1{\sqrt y} - \frac1{\sqrt{y+1}}\bigr) \le \frac{1}{y\sqrt y}$ for $y > 0$; with $y = n + 1$ and $c \ge 0$ the gain of the right side is at most the gain of the sum.
