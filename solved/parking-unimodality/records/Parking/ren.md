---
weight: unit
short: the sequence n^n/n!
---
## Description

The sequence $\operatorname{ren}(n) = n^n/n!$ for $n \ge 0$, with $\operatorname{ren}(0) = 1$.

## Statement

For a natural number $n$,

$$\operatorname{ren}(n) = \frac{n^n}{n!},$$

where $0^0 = 1$, so that $\operatorname{ren}(0) = 1$.

## Explanation

The name stands for "renewal". Let $a_j = j^{j-1}/j!$ be the Cayley coefficients (`Parking.cay`) and $T = \sum_{j \ge 1} a_j X^j$ the tree series (`Parking.TreeSeries.Tser`). The numbers $\operatorname{ren}(n)$ are the coefficients of the power series $1 + X T'$, and this series is the inverse of $1 - T$; both facts are shown in the proof of `Parking.ren_conv`. Comparing coefficients gives $\operatorname{ren}(n) = \sum_{j=1}^{n} a_j \operatorname{ren}(n-j)$ for $n \ge 1$, which says that $\operatorname{ren}$ is the renewal sequence of the kernel $a$.

Two further relations make the sequence useful. First, $m\,\varepsilon_m = \operatorname{ren}(m-1)$ for $m \ge 1$ (`Parking.mul_eps`), where $\varepsilon_m = (m-1)^{m-1}/m!$ (`Parking.eps`); estimates of $\operatorname{ren}$ thus become estimates of the kernel $\varepsilon$. Second, $e^{-n} \operatorname{ren}(n)$ is the mass at $n$ of the Poisson law with mean $n$ (`Parking.poissonMass`), which Stirling's formula bounds from both sides by multiples of $1/\sqrt{n}$ (`Parking.poissonMass_le`, `Parking.poissonMass_ge`).

In Lean, `Parking.ren n` is the real number `(n : ℝ) ^ n / n!`; at $n = 0$ Lean's convention $0^0 = 1$ gives the value $1$.
