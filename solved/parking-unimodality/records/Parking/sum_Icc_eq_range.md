---
weight: step
short: shifting the index of a sum over an interval
---
## Description

$\sum_{j=a+1}^{a+n}f(j)=\sum_{r=0}^{n-1}f(a+r+1)$.

## Statement

Let $f$ be a real-valued function on the natural numbers and let $a,n$ be natural numbers. Then
$$\sum_{j=a+1}^{a+n}f(j)=\sum_{r=0}^{n-1}f(a+r+1).$$

## Explanation

A change of the summation index, $j=a+r+1$. It passes between the two ways in which Lean writes a finite sum, over an interval `Finset.Icc (a+1) (a+n)` and over `Finset.range n`, and it is used in the crossing criterion and its bounds (modules `Parking.Crossing.Criterion`, `Parking.Crossing.Bounds`), where sums over the rows $k+1,\dots,k+R$ of a column are rewritten as sums over $r<R$. A mathematical text uses it without mention.

## Proof

By induction on $n$. For $n=0$ both sums are empty. For the step, the last term $f(a+n+1)$ is split off on both sides.
