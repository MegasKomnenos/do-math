---
weight: step
short: Abel summation against the birthday law
---
## Description

Abel summation against the birthday law: for $m \ge 1$ and any real function $g$ on the natural numbers, $\sum_{q=1}^{m} g(q)\,q\,P_{m,q} = m\bigl(g(0) + \sum_{q=1}^{m}(g(q) - g(q-1))\,P_{m,q}\bigr)$.

## Statement

Let $m \ge 1$ be a natural number and let $g$ be a real-valued function on the natural numbers. Then

$$\sum_{q=1}^{m} g(q)\;q\,P_{m,q} \;=\; m\,\Bigl(g(0) + \sum_{q=1}^{m}\bigl(g(q) - g(q-1)\bigr)\,P_{m,q}\Bigr),$$

where $P_{m,j} = \prod_{i=0}^{j-1}(1 - i/m)$ is the birthday tail of `Parking.Pb`.

## Explanation

Let $Q$ follow the birthday law of $m$ (see `Parking.Pb`), so that $\Pr(Q = q) = \frac{q}{m} P_{m,q}$ and $\Pr(Q \ge j) = P_{m,j}$. After division by $m$ the identity reads

$$\mathbb{E}[g(Q)] \;=\; g(0) + \sum_{j \ge 1}\bigl(g(j) - g(j-1)\bigr)\,\Pr(Q \ge j),$$

the formula that expresses an expectation through the tail probabilities. It turns a sum against the point masses $q\,P_{m,q}$, which is the form in which the weights of compositions appear by `Parking.Tq_eq`, into a sum against the tails $P_{m,q}$, which is the form in which $s_m = \sum_j P_{m,j}$ (`Parking.sbirth`) is defined.

All the moment identities of the birthday law are instances. The function $g = 1$ gives $\sum_q q\,P_{m,q} = m$, which says that the point masses add up to $1$. The function $g(j) = j$ gives $\sum_q q^2 P_{m,q} = m\,s_m$, which says that the mean is $s_m$. The functions $g(j) = j(j-1)$ and $g(j) = j(j-1)(j-2)$ give `Parking.Pb_sum3` and `Parking.Pb_sum4`. In the proofs of `Parking.kc2_eq` and `Parking.kc3_eq` the identity is applied to $g(j) = j - 1$ and yields $\sum_{q=1}^{m}(q-1)\,q\,P_{m,q} = m\,(s_m - 1)$.

In the Lean statement the sums run over $i < m$ with $q = i + 1$, and $q\,P_{m,q}$ is written as $(i+1)\,P_{m,i+1}$ with real factors.

## Proof

Two facts are combined.

First, for every natural number $q$, $q\,P_{m,q} = m\,(P_{m,q} - P_{m,q+1})$. Indeed `Parking.Pb_succ` gives $P_{m,q} - P_{m,q+1} = P_{m,q}\cdot\frac{q}{m}$, and $m \cdot \frac{q}{m} = q$ because $m \ne 0$.

Second, summation by parts: for any real sequences $g$ and $p$ and any natural number $n$,

$$\sum_{q=1}^{n} g(q)\,\bigl(p(q) - p(q+1)\bigr) \;=\; \sum_{q=1}^{n}\bigl(g(q) - g(q-1)\bigr)\,p(q) \;+\; g(0)\,p(1) \;-\; g(n)\,p(n+1).$$

This is proved by induction on $n$: for $n = 0$ both sides are $0$, and adding the term with $q = n+1$ to both sides preserves the equality by a direct calculation.

By the first fact the left-hand side of the statement is $m \sum_{q=1}^{m} g(q)\,(P_{m,q} - P_{m,q+1})$. Applying the second fact with $p(q) = P_{m,q}$ and $n = m$, and inserting $P_{m,1} = 1$ (`Parking.Pb_one`) and $P_{m,m+1} = 0$ (`Parking.Pb_succ_self`), gives the right-hand side.
