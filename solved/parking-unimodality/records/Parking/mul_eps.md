---
weight: step
short: m ε_m = (m-1)^(m-1)/(m-1)!
---
## Description

For $m \ge 1$, $m\,\varepsilon_m = (m-1)^{m-1}/(m-1)!$: the kernel $\varepsilon$ times its index is the sequence $n^n/n!$ shifted by one.

## Statement

For every natural number $m$,

$$(m+1)\,\varepsilon_{m+1} = \operatorname{ren}(m),$$

where $\varepsilon_m = (m-1)^{m-1}/m!$ for $m \ge 1$ (`Parking.eps`) and $\operatorname{ren}(n) = n^n/n!$ with $\operatorname{ren}(0) = 1$ (`Parking.ren`). Equivalently, $m\,\varepsilon_m = \operatorname{ren}(m-1)$ for every $m \ge 1$.

## Explanation

The identity is how every estimate of $\varepsilon$ in the library is obtained: $\operatorname{ren}(m)$, multiplied by $e^{-m}$, is the Poisson mass that Stirling's formula bounds (`Parking.poissonMass_le`, `Parking.poissonMass_ge`), so $\varepsilon_{m+1} = \operatorname{ren}(m)/(m+1)$ is of order $e^{m}\,m^{-3/2}$. It is also the step that identifies the coefficients of $1/P$ with $-\varepsilon_m$ in the proof of `Parking.TreeSeries.coeff_Eser_mul`.

The Lean statement is the form with the index $m + 1$, which holds for all $m \ge 0$ and avoids subtraction.

## Proof

By `Parking.eps_succ`, $\varepsilon_{m+1} = m^m/(m+1)!$. Since $(m+1)! = (m+1)\,m!$, multiplying by $m + 1$ gives $m^m/m! = \operatorname{ren}(m)$.
