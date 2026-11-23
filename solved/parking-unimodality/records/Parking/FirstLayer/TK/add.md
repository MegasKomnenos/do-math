---
weight: step
short: property K of a sum of two triples
---
## Description

If two triples have property K at $k$, so does their componentwise sum.

## Statement

Let $k$ be a real number and let $(a,b,c)$ and $(a',b',c')$ be triples of real numbers that have property K at $k$ (`Parking.FirstLayer.TK`). Then $(a+a',\,b+b',\,c+c')$ has property K at $k$.

## Explanation

The defining inequality $2e^{\mu/k}b\le e^{\mu}c+e^{-\mu}a$ is linear in $(a,b,c)$ for each fixed $\mu$. In `Parking.FirstLayer.kernel_TK` this lets the chain part and the direct term of the last-car recursion be treated separately.

## Proof

For each $\mu\ge 0$, add the two defining inequalities.
