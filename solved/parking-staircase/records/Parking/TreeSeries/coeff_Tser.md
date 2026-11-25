---
weight: step
short: coefficients of the tree series
---
## Description

The coefficient of $X^n$ in the tree series $T = XP$ is the Cayley coefficient $a_n$, for every $n \ge 0$.

## Statement

For every natural number $n$, $[X^n]\,T = a_n$, where $T = XP$ is the tree series (`Parking.TreeSeries.Tser`) and $a_0 = 0$, $a_j = j^{j-1}/j!$ for $j \ge 1$ (`Parking.cay`).

## Explanation

The tree series is defined as $X$ times the series $P = \sum_n c_n X^n$ with $c_n = a_{n+1}$ (`Parking.TreeSeries.Pser`, `Parking.cc`). The statement says that this is the series $\sum_j a_j X^j$; the convention $a_0 = 0$ is what makes it hold at $n = 0$ as well.

## Proof

The coefficient of $X^0$ in $XP$ is $0 = a_0$. The coefficient of $X^{n+1}$ in $XP$ is the coefficient of $X^n$ in $P$, which is $c_n$ (`Parking.TreeSeries.coeff_Pser`), and $c_n = a_{n+1}$ by definition.
