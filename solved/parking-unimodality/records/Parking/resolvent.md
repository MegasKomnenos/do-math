---
weight: unit
short: resolvent representation of a renewal-type equation
---
## Description

If $G$ is the renewal sequence of a kernel $f$ and $v_s=\iota_s+\sum_{i=1}^{s}f_iv_{s-i}$ for all $s$, then $v$ is the convolution of $G$ with $\iota$: $v_s=\sum_{c=0}^{s}G_{s-c}\,\iota_c$.

## Statement

Let $f,G,v,\iota$ be sequences of real numbers. Suppose that $G$ is the renewal sequence of the kernel $f$ (`Parking.IsRenewal`): $G_0=1$ and $G_n=\sum_{i=1}^{n}f_iG_{n-i}$ for $n\ge1$. Suppose that for every $s\ge0$
$$v_s=\iota_s+\sum_{i=1}^{s}f_i\,v_{s-i}.$$
Then for every $s\ge0$
$$v_s=\sum_{c=0}^{s}G_{s-c}\,\iota_c.$$

## Explanation

The numbers $\iota_s=v_s-\sum_{i=1}^{s}f_iv_{s-i}$ are the *innovations* of $v$ with respect to the kernel $f$: what $v_s$ contains beyond the feedback of its earlier values. The statement solves the equation for $v$: each innovation $\iota_c$ is propagated to the later times by the renewal sequence, which is in this sense the resolvent kernel of $f$. In generating series it reads $V=I/(1-F)$. No sign condition and no convergence is involved; the statement is an identity for each $s$.

It is used twice. In the extreme-column bound (`Parking.extreme_column_le`) a sequence with nonnegative innovations is written as a combination of shifted copies of $G$ with nonnegative coefficients, which reduces an inequality for $v$ to inequalities for $G$. With $v\equiv1$ it gives $1=\sum_{c\le N}G_{N-c}\bigl(1-\sum_{i=1}^{c}f_i\bigr)$, from which the bound $\sum_{s<N}G_s\le2e$ for the renewal sequence of the frozen kernel is obtained (`Parking.Gres_sum_le`).

## Proof

By strong induction on $s$. Assume the formula for all indices smaller than $s$. In $v_s=\iota_s+\sum_{i=1}^{s}f_iv_{s-i}$ replace each $v_{s-i}$, $1\le i\le s$, by $\sum_{c=0}^{s-i}G_{s-i-c}\,\iota_c$. The resulting double sum runs over the pairs $(i,c)$ with $i\ge1$, $c\ge0$ and $i+c\le s$; summing first over $i$ gives
$$\sum_{i=1}^{s}f_iv_{s-i}=\sum_{c=0}^{s-1}\Bigl(\sum_{i=1}^{s-c}f_i\,G_{s-c-i}\Bigr)\iota_c=\sum_{c=0}^{s-1}G_{s-c}\,\iota_c,$$
where the inner sum is $G_{s-c}$ by the renewal equation, as $s-c\ge1$. Adding $\iota_s=G_0\,\iota_s$ gives $v_s=\sum_{c=0}^{s}G_{s-c}\,\iota_c$.
