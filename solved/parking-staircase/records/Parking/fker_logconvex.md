---
weight: step
short: log-convexity of the frozen kernel
---
## Description

The frozen kernel is log-convex: $f_{i+1}^2 \le f_i\,f_{i+2}$ for every $i \ge 1$.

## Statement

For every natural number $i \ge 1$, $f_{i+1}^2 \le f_i\,f_{i+2}$, where $f$ is the frozen kernel of `Parking.fker` ($f_1 = \frac32e^{-1}$, $f_i = e^{-i}\varepsilon_i$ for $i \ge 2$). In Lean, with $i = j + 1$: `fker (j + 2) ^ 2 ≤ fker (j + 1) * fker (j + 3)` for every natural number $j$.

## Explanation

The sequence $e^{-i}\varepsilon_i$ is log-convex because $\varepsilon$ is (`Parking.eps_logconvex`) and a geometric factor does not affect log-convexity. The frozen kernel differs from it only at $i = 1$, where it is larger, and enlarging the first term of a log-convex sequence can only help the single inequality in which it appears, $f_2^2 \le f_1f_3$. Together with `Parking.fker_pos` this is the hypothesis under which the renewal sequence $G$ of $f$ is log-convex (`Parking.renewal_logConvex`), as `Parking.extreme_column_le` requires.

## Proof

By `Parking.fker_of_two_le`, $f_{i+1} = e^{-(i+1)}\varepsilon_{i+1}$ and $f_{i+2} = e^{-(i+2)}\varepsilon_{i+2}$. Using `Parking.eps_logconvex`,

$$f_{i+1}^2 = e^{-i}e^{-(i+2)}\,\varepsilon_{i+1}^2 \le e^{-i}\varepsilon_i\cdot e^{-(i+2)}\varepsilon_{i+2} \le f_i\,f_{i+2}.$$

The last step uses $e^{-i}\varepsilon_i \le f_i$, which holds for every $i$ with equality unless $i = 1$, and the nonnegativity of $e^{-(i+2)}\varepsilon_{i+2}$.
