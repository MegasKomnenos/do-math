---
weight: step
short: convolution from index one
---
## Description

For real sequences $g$, $v$ and a natural number $N$, the convolution $\sum_{\gamma=1}^{N} g(\gamma)\,v(N-\gamma)$, in which the term $\gamma = 0$ is left out.

## Statement

For $g, v : \mathbb{N} \to \mathbb{R}$ and $N \in \mathbb{N}$,
$$\operatorname{rconv}(g,v)(N) \;=\; \sum_{\gamma=1}^{N} g(\gamma)\,v(N-\gamma).$$
For $N = 0$ the sum is empty and the value is $0$.

## Explanation

The definition is a way of writing one expression that occurs repeatedly: the right-hand side of the recursion of the prime kernel beyond its free range. In `Parking.kq_rec` (and in `Parking.kqT_rec`, its tilted form) the sequence $g$ is the weight $(y-\gamma)^+ a_\gamma$ with $a_\gamma = \gamma^{\gamma-1}/\gamma!$ (`Parking.kqW`, and `Parking.kqWT` in tilted form) and $v$ is the prime kernel itself. The estimates of the tilted prime kernel in the left half of the argument start from these two recursions and use the same expression. The sum begins at $\gamma = 1$ because the weight at $\gamma = 0$ plays no role there.

In Lean the sum runs over $j = \gamma - 1$ with $0 \le j < N$ and has the summand $g(j+1)\,v(N-1-j)$. This is the same sum.
