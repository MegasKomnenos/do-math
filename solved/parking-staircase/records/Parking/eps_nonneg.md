---
weight: step
short: ε_m ≥ 0
---
## Description

The kernel $\varepsilon_m = (m-1)^{m-1}/m!$ ($\varepsilon_0 = 0$) is nonnegative for every $m \ge 0$.

## Statement

For every natural number $m$, $\varepsilon_m \ge 0$, where $\varepsilon$ is the sequence of `Parking.eps`.

## Explanation

For $m \ge 1$ the value is in fact positive; that stronger statement is `Parking.eps_pos`, in another part of the library.

## Proof

If $m = 0$, then $\varepsilon_0 = 0$. Otherwise write $m = i + 1$; by `Parking.eps_succ`, $\varepsilon_{i+1} = i^i/(i+1)!$, a quotient of a nonnegative and a positive number.
