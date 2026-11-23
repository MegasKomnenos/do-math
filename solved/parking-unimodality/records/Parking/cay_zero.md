---
weight: step
short: a_0 = 0
---
## Description

The Cayley coefficient of index $0$ is $a_0 = 0$.

## Statement

$a_0 = 0$, where $a_j$ is the Cayley coefficient (`Parking.cay`).

## Explanation

This is the convention built into the definition of the Cayley coefficients $a_j = j^{j-1}/j!$ ($j \ge 1$); the record of `Parking.cay` says why the value $0$ is chosen. The statement is used wherever a sum over $\alpha + \beta = t$ contains a term with $a_0$, which then vanishes.

## Proof

It is the first case of the definition.
