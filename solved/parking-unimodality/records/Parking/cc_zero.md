---
weight: step
short: c_0 = 1
---
## Description

The normalised parking number of length $0$ is $c_0 = 1$.

## Statement

$c_0 = 1$, where $c_n = (n+1)^{n-1}/n!$ (`Parking.cc`).

## Explanation

This is the initial value of the recursion `Parking.cc_rec`, and it says that the series $P = \sum_n c_n X^n$ (`Parking.TreeSeries.Pser`) has constant coefficient $1$, so that it has an inverse.

## Proof

By definition $c_0 = a_1$, where $a$ denotes the Cayley coefficients (`Parking.cay`), and $a_1 = 1^0/1! = 1$.
