---
weight: unit
short: convolution identity of the Cayley coefficients
---
## Description

The convolution identity of the Cayley coefficients $a_j = j^{j-1}/j!$ ($a_0 = 0$): $\sum_{\alpha=1}^{t-1} \alpha\, a_\alpha\, a_{t-\alpha} = (t-1)\, a_t$ for every $t \ge 0$.

## Statement

For every natural number $t$,

$$\sum_{\alpha=0}^{t-1} \alpha\, a_\alpha\, a_{t-\alpha} = (t-1)\, a_t,$$

where $a_0 = 0$ and $a_j = j^{j-1}/j!$ for $j \ge 1$ (`Parking.cay`). The term $\alpha = 0$ is zero, so for $t \ge 2$ the sum runs over $1 \le \alpha \le t-1$. For $t = 0$ the sum is empty and the right-hand side is $(-1) \cdot a_0 = 0$; for $t = 1$ both sides are $0$.

## Explanation

This is the recursion `Parking.cc_rec` of the numbers $c_n = a_{n+1}$, written with the Cayley coefficients themselves. In terms of the tree series $T = \sum_{j \ge 1} a_j X^j$ (`Parking.TreeSeries.Tser`) it says $X T' \cdot T = X T' - T$, that is, $X T'(1 - T) = T$: the derivative form of the classical functional equation $T = X e^{T}$ of the tree function. Combinatorially, $(t-1)\,a_t \cdot t!$ counts the rooted labelled trees on $t$ vertices with a distinguished vertex other than the root, and the identity sorts them by the size $\alpha$ of the branch that contains the distinguished vertex and is cut off at the first edge of the path from the root to it; the library does not use this reading.

The identity is the only relation among the Cayley coefficients that the comparison of composition weights in the next-column argument needs: the three ratio statements `Parking.Tq_ratio`, `Parking.Vc_ratio_le` and `Parking.Vc_thr_ratio_ge` are derived from it. Its symmetric form is `Parking.cay_conv_sym`.

In Lean the sum runs over $0 \le \alpha < t$ and the factor on the right is the real number $t - 1$, so the statement holds for $t = 0$ as described.

## Proof

For $t = 0$ and $t = 1$ both sides vanish, as said in the statement. Let $t = n + 2$. In $\sum_{\alpha=0}^{n+1} \alpha\, a_\alpha\, a_{n+2-\alpha}$ the term $\alpha = 0$ is zero; put $\alpha = j + 1$ with $0 \le j \le n$ in the others. With $c_j = a_{j+1}$ (`Parking.cc`) the sum becomes

$$\sum_{j=0}^{n} (j+1)\, c_j\, c_{n-j},$$

because $a_{n+2-(j+1)} = a_{(n-j)+1} = c_{n-j}$. By `Parking.cc_rec` this equals $(n+1)\,c_{n+1} = (n+1)\,a_{n+2} = (t-1)\,a_t$.
