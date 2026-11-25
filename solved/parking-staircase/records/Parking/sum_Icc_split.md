---
weight: step
short: splitting a sum over an interval of integers
---
## Description

A sum over the integers $a\le m\le n$ splits after $s$ into the sums over $a\le m\le s$ and over $s+1\le m\le n$.

## Statement

Let $g$ be a real-valued function on the natural numbers and let $a,s,n$ be natural numbers with $a\le s+1$ and $s\le n$. Then
$$\sum_{m=a}^{n}g(m)=\sum_{m=a}^{s}g(m)+\sum_{m=s+1}^{n}g(m),$$
where a sum over an empty range is $0$.

## Explanation

The hypothesis $a\le s+1$ allows the first part to be empty ($s=a-1$), and $s\le n$ allows the second part to be empty ($s=n$). The statement is bookkeeping: the recursions of the library are written as sums over intervals `Finset.Icc` of natural numbers, and the persistence arguments (`Parking.two_point`, `Parking.persistence_inequality`, `Parking.extreme_column_le`, `Parking.caseFar`) repeatedly separate the part of a feedback sum that comes from one group of rows from the rest. A mathematical text uses it without mention.

## Proof

Both sides are sums over half-open intervals, $[a,n+1)=[a,s+1)\cup[s+1,n+1)$, and the two intervals on the right are consecutive because $a\le s+1\le n+1$.
