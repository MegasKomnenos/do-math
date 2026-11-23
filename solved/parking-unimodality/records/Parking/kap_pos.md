---
weight: step
short: positivity of the coefficients of the frozen polynomial
---
## Description

$\kappa_k(t) = a_t - \sum_{k<i<t} a_i a_{t-i}$ is positive for $1 \le t \le 2k+1$.

## Statement

Let $k$ and $t$ be natural numbers with $1 \le t \le 2k+1$. Then $\kappa_k(t) > 0$, where $\kappa_k(t) = a_t - \sum_{k<i<t} a_i\, a_{t-i}$ (`Parking.kap`) and $a_j = j^{j-1}/j!$, $a_0 = 0$ (`Parking.cay`).

## Explanation

The range $t \le 2k+1$ is the single-chain range in the size coordinate. In it the indices $k < i < t$ of the sum and their reflections $t - i$ do not overlap, so the sum is at most half of the full convolution $\sum_i a_i a_{t-i}$, and the full convolution is less than $2a_t$. Beyond that range the two halves overlap and the argument is not available. The positivity makes the frozen polynomial `Parking.Kpoly` at a row $n \le 2k-1$ a polynomial with nonnegative coefficients, which is the hypothesis under which `Parking.curv_ratio` compares its second differences.

## Proof

The reflection $i \mapsto t - i$ maps the indices $k < i < t$ bijectively onto the indices $0 < j < t - k$ and leaves the product $a_i a_{t-i}$ unchanged, so

$$\sum_{k<i<t} a_i a_{t-i} = \sum_{0<j<t-k} a_j a_{t-j}.$$

Since $t \le 2k+1$, an index $j < t - k$ satisfies $j \le k$, so the two index sets are disjoint, and both lie in $\{0, \dots, t\}$. All terms are nonnegative (`Parking.cay_nonneg`), hence

$$2 \sum_{k<i<t} a_i a_{t-i} \le \sum_{i=0}^{t} a_i a_{t-i}.$$

By `Parking.cay_conv_sym`, $t \sum_{i=0}^{t} a_i a_{t-i} = 2(t-1)\,a_t$. Therefore $t \sum_{k<i<t} a_i a_{t-i} \le (t-1)\,a_t$, and $t\,\kappa_k(t) \ge a_t > 0$ by `Parking.cay_pos`. Dividing by $t > 0$ gives the claim.
