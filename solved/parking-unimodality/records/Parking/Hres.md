---
weight: step
short: the resolvent sequence before the Borel scaling
---
## Description

The sequence $H_s = \sum_{j=0}^{s} 2^{-j}\,[X^s]\,X^jP^{j+1}$, where $P = \sum_n c_nX^n$, $c_n = (n+1)^{n-1}/n!$. It satisfies $H_0 = 1$ and $H_s = \sum_{m=1}^{s}\varepsilon_mH_{s-m} + \frac12H_{s-1}$.

## Statement

For a natural number $s$,

$$H_s = \sum_{j=0}^{s} 2^{-j}\,h_{j,s}, \qquad h_{j,s} = [X^s]\;X^jP(X)^{j+1},$$

where $h_{j,s}$ is the coefficient of `Parking.hcoef` and $P = \sum_n c_nX^n$ is the series of `Parking.TreeSeries.Pser`. In Lean: `Hres s`.

## Explanation

The sequence is the solution of the renewal equation

$$H_0 = 1, \qquad H_s = \sum_{m=1}^{s}\varepsilon_m H_{s-m} + \tfrac12 H_{s-1} \quad (s\ge1),$$

in which $\varepsilon_m = (m-1)^{m-1}/m!$ is the prime kernel of `Parking.eps`. This identity is what the library proves about $H$ (inside `Parking.Gres_isRenewal`), and it explains the definition. The series $E = 1/P$ has the coefficients $1, -\varepsilon_1, -\varepsilon_2, \dots$ (`Parking.TreeSeries.coeff_Eser_mul`). A sequence that satisfies the renewal equation has the generating function $1/(E - X/2)$, and

$$\frac{1}{E - X/2} = \frac{P}{1 - XP/2} = \sum_{j\ge0}\Bigl(\frac X2\Bigr)^{j}P^{j+1}.$$

Reading the coefficient of $X^s$, to which only the terms $j \le s$ contribute, gives the definition. The library does not state this identity of power series; it defines $H$ by the coefficients and verifies the renewal equation coefficient by coefficient.

The point of the definition by coefficients is that each $h_{j,s}$ has a closed form (see `Parking.hcoef`), so that $H_s$ can be bounded from below explicitly: $H_s \ge c_s\,(4 - \frac{21}{s+1})$ for $s \ge 6$, which is proved inside `Parking.Gres_lower`. A renewal sequence defined only by its recursion would give no such handle.

The additional term $\frac12H_{s-1}$, and the scaling by $e^{-s}$ that turns $H$ into the sequence $G$ of `Parking.Gres`, are explained in the record of `Parking.fker`.
