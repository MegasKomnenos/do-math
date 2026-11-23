---
weight: unit
short: Cayley coefficients a_j
---
## Description

The Cayley coefficients $a_j = j^{j-1}/j!$ for $j \ge 1$, with $a_0 = 0$.

## Statement

For a natural number $j$, the Cayley coefficient $a_j$ is the real number defined by $a_0 = 0$ and

$$a_j = \frac{j^{\,j-1}}{j!} \qquad (j \ge 1).$$

## Explanation

By Cayley's formula there are $j^{j-1}$ rooted labelled trees on $j$ vertices, so $a_j$ is that number divided by $j!$: the coefficient of $X^j$ in the exponential generating function of rooted labelled trees, the tree series $T$ (`Parking.TreeSeries.Tser`). The library never speaks of trees. The numbers $a_j$ enter through their formula alone, and everything that is known about them is derived from Abel's identity (`Parking.abel_identity`): the convolution identity `Parking.cay_conv`, the ratio of consecutive coefficients `Parking.cay_ratio`, and the log-convexity `Parking.cay_logconvex`. The first values are $a_1 = 1$, $a_2 = 1$, $a_3 = 3/2$, $a_4 = 8/3$.

The formula has no meaning at $j = 0$, and the value $a_0 = 0$ is a convention. It is the value that makes the tree series have no constant term, and it lets a sum over the pairs $\alpha + \beta = t$ run over all $0 \le \alpha \le t$: the two extreme terms contain $a_0$ and vanish.

The shifted sequence $c_n = a_{n+1}$ (`Parking.cc`) is the one that counts parking functions; most statements of the library use whichever of the two indexings is convenient.

In Lean, `Parking.cay j` is a real number, and the exponent `j - 1` is a subtraction of natural numbers. Since the case $j = 0$ is treated separately, the subtraction is exact wherever it is used.
