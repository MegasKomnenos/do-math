---
weight: unit
short: the resolvent sequence of the frozen kernel
---
## Description

The sequence $G_s = e^{-s}\sum_{j=0}^{s}2^{-j}\,[X^s]\,X^jP^{j+1}$, where $P = \sum_n c_nX^n$ and $c_n = (n+1)^{n-1}/n!$. It is the renewal sequence of the frozen kernel.

## Statement

For a natural number $s$,

$$G_s = e^{-s}\,H_s, \qquad H_s = \sum_{j=0}^{s}2^{-j}\,[X^s]\;X^jP(X)^{j+1},$$

where $P = \sum_{n\ge0}c_nX^n$ is the power series of `Parking.TreeSeries.Pser`, $c_n = (n+1)^{n-1}/n!$, and $H$ is the sequence of `Parking.Hres`. In Lean: `Gres s`.

## Explanation

$G$ is the renewal sequence of the frozen kernel $f$ of `Parking.fker`: $G_0 = 1$ and $G_s = \sum_{i=1}^{s}f_iG_{s-i}$ for $s \ge 1$ (`Parking.Gres_isRenewal`). This is the property through which it is used, and it would serve as a definition. The library defines $G$ by the explicit coefficients instead, because the argument needs numerical information about $G$ that the recursion does not give directly: the lower bound of `Parking.Gres_lower`, which comes from the closed form of the coefficients $[X^s]X^jP^{j+1} = (j+1)(s+1)^{s-j-1}/(s-j)!$ for $j<s$ (and $1$ for $j = s$). The record of `Parking.Hres` explains how the formula is found from the recursion.

In the persistence argument $G$ plays the role of an extreme column. A sequence $v$ with nonnegative innovations with respect to $f$ is a nonnegative combination of shifted copies of $G$ (`Parking.resolvent`), and `Parking.extreme_column_le` shows that the weighted feedback through the far part of the kernel, relative to the last value, is largest for $G$ itself, the sequence whose only innovation is at time $0$. The far rows of a column $k \ge 82$ (`Parking.caseFar`) are then settled by three facts about $G$: it is positive (`Parking.Gres_pos`), its partial sums are at most $2e$ (`Parking.Gres_sum_le`), and $G_s$ is at least an explicit multiple of $(s+1)^{-3/2}$ (`Parking.Gres_lower`).
