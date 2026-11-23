---
weight: step
short: symmetric convolution of the Cayley coefficients
---
## Description

The symmetric form of the convolution identity of the Cayley coefficients $a_j = j^{j-1}/j!$ ($a_0 = 0$): $t \sum_{\alpha+\beta=t} a_\alpha a_\beta = 2\,(t-1)\,a_t$ for every $t \ge 0$.

## Statement

For every natural number $t$,

$$t \sum_{\alpha=0}^{t} a_\alpha\, a_{t-\alpha} = 2\,(t-1)\,a_t,$$

where $a_0 = 0$ and $a_j = j^{j-1}/j!$ for $j \ge 1$ (`Parking.cay`). The terms $\alpha = 0$ and $\alpha = t$ are zero.

## Explanation

The identity `Parking.cay_conv` carries the weight $\alpha$ on one of the two factors. Adding it to its mirror image, in which the weight is $t - \alpha$, gives the unweighted self-convolution of the Cayley coefficients: for $t \ge 1$, $\sum_{\alpha+\beta=t} a_\alpha a_\beta = \frac{2(t-1)}{t}\, a_t$, which is less than $2 a_t$. The library uses this to show that the quantity $a_t - \sum_{k<i<t} a_i a_{t-i}$ is positive for $1 \le t \le 2k+1$ (`Parking.kap_pos`): in that range the indices $k < i < t$ and their reflections $t - i$ are disjoint, so the partial sum is at most half of the full convolution.

## Proof

By `Parking.cay_conv`, $\sum_{\alpha=0}^{t-1} \alpha\, a_\alpha\, a_{t-\alpha} = (t-1)\,a_t$. The term $\alpha = t$ may be added to the sum, since it contains the factor $a_0 = 0$; so $\sum_{\alpha=0}^{t} \alpha\, a_\alpha\, a_{t-\alpha} = (t-1)\,a_t$. Replacing $\alpha$ by $t - \alpha$ in this sum gives $\sum_{\alpha=0}^{t} (t-\alpha)\, a_{t-\alpha}\, a_\alpha = (t-1)\,a_t$. Adding the two equations, and using $\alpha + (t - \alpha) = t$ in each term, yields $t \sum_{\alpha=0}^{t} a_\alpha a_{t-\alpha} = 2\,(t-1)\,a_t$.
