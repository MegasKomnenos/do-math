---
weight: step
short: a sum from 1 to n as a sum over 0 to n-1
---
## Description

$\sum_{m=1}^{n}g(m)=\sum_{i=0}^{n-1}g(i+1)$.

## Statement

Let $g$ be a real-valued function on the natural numbers and let $n$ be a natural number. Then
$$\sum_{m=1}^{n}g(m)=\sum_{i=0}^{n-1}g(i+1).$$

## Explanation

A change of the summation index, $m=i+1$. It passes between a sum over `Finset.Icc 1 n` and a sum over `Finset.range n`, and it is used in the renewal equations (`Parking.IsRenewal`), in the sums of the birthday law and of compositions, and in the estimate of the tilted Cayley sum (`Parking.cayleySum_le_one`, `Parking.zrT_anti_crit`). A mathematical text uses it without mention.

## Proof

The sum over $0\le i<n$ of $g(i+1)$ is the sum of $g$ over the shifted range $1\le m<n+1$, which is the interval $1\le m\le n$.
