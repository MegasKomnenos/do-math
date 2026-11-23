---
weight: step
short: positivity of the weights
---
## Description

The weights $\pi_n=x^na_n/n$ of a column $k$ are positive for $n\ge1$.

## Statement

For every natural number $k$ and every natural number $n\ge1$, $\pi_n>0$, where $\pi_n=x^na_n/n$ is the weight `Parking.pix` of the column $k$ ($x$ is the diagonal tilt `Parking.xk`, $a_n=n^{n-1}/n!$ is `Parking.cay`).

## Explanation

Positivity is needed wherever the proofs divide by a weight, in particular in the definition of the correction $\mathsf e_j=(j-k+2)-\Pi_{j+1}/\pi_{j+1}$ (`Parking.ecor`) and in the last step of the crossing criterion, where an inequality is divided by $\pi_N$.

## Proof

The three factors are positive: $x^n>0$ since $x>0$ (`Parking.CrossCrit.xk_pos`), $a_n>0$ for $n\ge1$ (`Parking.cay_pos`), and $n>0$.
