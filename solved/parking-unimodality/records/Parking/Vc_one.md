---
weight: step
short: weight of the composition with one part
---
## Description

The only composition of $m$ with one part has the weight $a_m = m^{m-1}/m!$, whatever the cut profile: $V_1(m;f) = a_m$.

## Statement

For every function $f : \mathbb{N} \to \mathbb{R}$ and every natural number $m$, $V_1(m;f) = a_m$, where $V_q(m;f)$ is the total weight of the compositions of $m$ with $q$ parts (`Parking.Vc`) and $a_m$ is the Cayley number $m^{m-1}/m!$, with $a_0 = 0$ (`Parking.cay`).

## Explanation

A composition with one part has no cut, so the profile does not enter. The statement is the second clause of the recursive definition of `Parking.Vc`, and it is the base case of every induction on the number of parts.

## Proof

This is the clause $q = 1$ of the definition of $V_q(m;f)$.
