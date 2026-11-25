---
weight: step
short: A at length zero
---
## Description

$A(0,k)=1$ for every $k$: the empty sequence is the one parking function of length $0$, and its maximum displacement counts as $0$.

## Statement

For every natural number $k$, $A(0,k)=1$, where $A(n,k)$ (`Parking.A`) is the number of parking functions of length $n$ with maximum displacement at most $k$.

## Explanation

This is the initial value of the last-car recursion `Parking.A_succ`. It depends on a convention of the definitions: the maximum displacement of a parking function is the largest entry of its list of displacements, and for the empty list this is taken to be $0$ (`Parking.maxDisp`). With this convention the empty parking function has maximum displacement $0$, so $b(0,0)=1$ and $A(0,k)=1$ for every $k$.

## Proof

The proof of `Parking.A_succ` identifies $A(n,k)$ with the number of preference sequences of length $n$ on the street with the spots $0,\dots,n-1$ that park, occupy all the spots, and have all displacements at most $k$ (Step 4 there; the identification is a private lemma of the same module). For $n=0$ the only sequence of length $0$ is the empty one. It parks, it occupies the empty set of spots, and it has no displacement that could exceed $k$. So the count is $1$.
