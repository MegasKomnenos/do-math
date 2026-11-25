---
weight: step
short: Poisson mass at 0
---
## Description

The Poisson mass $e^{-n} n^n/n!$ takes the value $1$ at $n = 0$.

## Statement

$e^{-0} \cdot 0^0/0! = 1$, with the convention $0^0 = 1$; that is, the Poisson mass of `Parking.poissonMass` at $n = 0$ equals $1$.

## Explanation

The value is the initial value $1$ that a renewal sequence has at the index $0$; the Poisson masses are used as a renewal sequence in the proof of `Parking.hasSum_borel`.

## Proof

Unfold the definitions: $e^{0} = 1$, $0^0 = 1$ and $0! = 1$.
