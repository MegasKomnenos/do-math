---
weight: step
short: weighted Chebyshev inequality on an interval
---
## Description

Weighted Chebyshev inequality on $\{1, \dots, n\}$: if $u(q')\,v(q) \le u(q)\,v(q')$ for $1 \le q \le q' \le n$ and $\varphi$ is nondecreasing there, then $(\sum u\varphi)(\sum v) \le (\sum v\varphi)(\sum u)$.

## Statement

Let $n$ be a natural number and let $u, v, \varphi$ be real-valued functions on the natural numbers. Assume that for all $q, q'$ with $1 \le q \le q' \le n$

$$u(q')\,v(q) \;\le\; u(q)\,v(q') \qquad\text{and}\qquad \varphi(q) \;\le\; \varphi(q').$$

Then

$$\Bigl(\sum_{q=1}^{n} u(q)\,\varphi(q)\Bigr)\Bigl(\sum_{q=1}^{n} v(q)\Bigr) \;\le\; \Bigl(\sum_{q=1}^{n} v(q)\,\varphi(q)\Bigr)\Bigl(\sum_{q=1}^{n} u(q)\Bigr).$$

## Explanation

This is `Parking.lr_sum_le_finset` for the set $\{1, \dots, n\}$, the range of the number $q$ of parts of a composition of $n$; the record of that statement explains how the inequality reads when $u$ and $v$ are positive weights. Its first hypothesis is usually obtained from a comparison of consecutive quotients by `Parking.lr_of_consecutive`.

It is used in two places. In `Parking.lr_factorial_moment_le` the function $\varphi$ is $q - 2$ and the weights are multiplied by $q(q-1)$. In the proof of `Parking.Lam_raise` the weights are $u(q) = T_{r,q}\,h^{q-1}$ (the homogeneous law, see `Parking.Tq` and `Parking.tau`) and $v(q) = k^{q-1}\,V_q(r;\lambda^{1,N})$ with $N = k + r + 1$ (the threshold profile, see `Parking.Vc` and `Parking.thr`), and $\varphi(q) = (1 + 2/k)^{q-1}$.

## Proof

Apply `Parking.lr_sum_le_finset` to $S = \{1, \dots, n\}$. Its two hypotheses for $q, q' \in S$ with $q \le q'$ are the present hypotheses, since $q \in S$ gives $1 \le q$ and $q' \in S$ gives $q' \le n$.
