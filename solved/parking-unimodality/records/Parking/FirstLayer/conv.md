---
weight: step
short: self-convolution of a sequence
---
## Description

The self-convolution of a real sequence $f$ at the length $j$: $\sum_{a=0}^{j}f(a)\,f(j-a)$.

## Statement

For a sequence $f:\mathbb{N}\to\mathbb{R}$ and a natural number $j$,
$$\operatorname{conv} f\,(j)=\sum_{a=0}^{j}f(a)\,f(j-a).$$

## Explanation

The sum runs over the pairs of indices $(a,b)$ with $a+b=j$. The definition exists for `Parking.FirstLayer.conv_TK`, which is stated for an arbitrary sequence, and it is applied to the shifted sequence $a\mapsto\omega_{\rho+a}$ of tilted Cayley masses, for which it gives the pair sums of `Parking.FirstLayer.pairT`. The convolution is called truncated in that context because the shifted sequence is used only up to the index at which its tilted convexity is known.

In the Lean form the sum is over `Finset.range (j + 1)`.
