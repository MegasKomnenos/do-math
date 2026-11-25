---
weight: unit
short: recursion of the numbers c_n
---
## Description

The numbers $c_n = (n+1)^{n-1}/n!$ satisfy $(n+1)\,c_{n+1} = \sum_{j=0}^{n} (j+1)\,c_j\,c_{n-j}$ for every $n \ge 0$: the last-car recursion of parking functions without a displacement bound, divided by $n!$.

## Statement

For every natural number $n$,

$$(n+1)\,c_{n+1} = \sum_{j=0}^{n} (j+1)\,c_j\,c_{n-j},$$

where $c_n = (n+1)^{n-1}/n!$ (`Parking.cc`).

## Explanation

Multiplied by $n!$, and with $p_n = n!\,c_n = (n+1)^{n-1}$, the identity reads $p_{n+1} = \sum_{j=0}^{n} (j+1) \binom{n}{j}\, p_j\, p_{n-j}$. This is the form that the last-car recursion `Parking.A_succ` takes when the bound on the displacement excludes nothing: if the last car finds the spot $j+1$ empty, the $j$ cars to its left and the $n-j$ cars to its right form parking functions, their arrivals interleave in $\binom{n}{j}$ ways, and the last car has $j+1$ possible preferences. The theorem says that the explicit numbers $(n+1)^{n-1}/n!$ solve this recursion. Since the recursion and the value $c_0 = 1$ determine the sequence, any sequence that satisfies them is $c$. This is how the library shows, without a bijection, that the normalised counts of parking functions equal $c_n$ where the displacement bound is not effective (`Parking.zr_eq_cc`): the counts satisfy the recursion by `Parking.A_succ`, and $c$ satisfies it by the present theorem.

In terms of the series $P = \sum_n c_n X^n$ and $T = XP$ (`Parking.TreeSeries.Pser`, `Parking.TreeSeries.Tser`) the identity is the differential equation $P' = T'P$, the derivative form of the classical relation $P = e^{T}$. From it come the convolution identities `Parking.eps_conv` and `Parking.ren_conv`. Rewritten with the Cayley coefficients $a_j = c_{j-1}$ it is `Parking.cay_conv`. It is also an input of the diagonal monotonicity `Parking.zr_diag_mono`.

The identity is an instance of Abel's binomial identity, which is where its proof comes from.

## Proof

Let $w_k(1)$ be the Abel weight at $x = 1$ (`Parking.abelW`), so that $c_k = w_k(1)/k!$ by `Parking.cc_eq_abelW`.

Reverse the order of summation, $j = n - k$, so that the right-hand side becomes $\sum_{k=0}^{n} (n-k+1)\,c_{n-k}\,c_k$. From `Parking.cc_eq`, $(j+1)\,c_j = (j+1)^j/j!$ for every $j$; at $j = n-k$ this is $(n+1-k)^{n-k}/(n-k)!$. Hence the term of index $k$ is

$$\frac{(n+1-k)^{n-k}}{(n-k)!} \cdot \frac{w_k(1)}{k!} = \frac{1}{n!} \binom{n}{k}\, w_k(1)\,(n+1-k)^{n-k}.$$

By `Parking.abel_identity` with $x = 1$ and $y = n + 1$, the sum of $\binom{n}{k}\, w_k(1)\,(n+1-k)^{n-k}$ over $0 \le k \le n$ is $(n+2)^n$. So the right-hand side of the claim equals $(n+2)^n/n!$.

For the left-hand side, `Parking.cc_eq` gives $c_{n+1} = (n+2)^{n+1}/(n+2)!$, and $(n+2)! = (n+2)(n+1)\,n!$, so $(n+1)\,c_{n+1} = (n+2)^n/n!$ as well.
