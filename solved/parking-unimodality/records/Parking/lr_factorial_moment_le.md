---
weight: step
short: likelihood-ratio order orders the ratio of factorial moments
---
## Description

For two weights on $\{1, \dots, n\}$ with $u(q')\,v(q) \le u(q)\,v(q')$ for $q \le q'$, the ratio of the third to the second factorial moment of $u$ is at most that of $v$, in cross-multiplied form.

## Statement

Let $n$ be a natural number and let $u, v$ be real-valued functions on the natural numbers such that

$$u(q')\,v(q) \;\le\; u(q)\,v(q') \qquad\text{for all } q, q' \text{ with } 1 \le q \le q' \le n.$$

Then

$$\Bigl(\sum_{q=1}^{n} q(q-1)(q-2)\,u(q)\Bigr)\Bigl(\sum_{q=1}^{n} q(q-1)\,v(q)\Bigr) \;\le\; \Bigl(\sum_{q=1}^{n} q(q-1)(q-2)\,v(q)\Bigr)\Bigl(\sum_{q=1}^{n} q(q-1)\,u(q)\Bigr).$$

## Explanation

Think of $u$ and $v$ as two unnormalised laws of a number $Q \in \{1, \dots, n\}$, with $u$ smaller than $v$ in likelihood-ratio order. When the sums of $q(q-1)\,u(q)$ and of $q(q-1)\,v(q)$ are positive, the conclusion says

$$\frac{\mathbb{E}_u[Q(Q-1)(Q-2)]}{\mathbb{E}_u[Q(Q-1)]} \;\le\; \frac{\mathbb{E}_v[Q(Q-1)(Q-2)]}{\mathbb{E}_v[Q(Q-1)]}.$$

The reason is that the weights $q(q-1)\,u(q)$ and $q(q-1)\,v(q)$ are in the same order as $u$ and $v$, and the two quotients are the averages of the increasing function $q - 2$ with respect to these two weights.

The statement is used with the birthday law in the place of $v$, for which the quotient on the right is the number $D_m$ (`Parking.Dbirth`, `Parking.Dbirth_spec`). In the proof of `Parking.curv_ratio`, $u(q) = V_q(m;\lambda^{y,N})$ is the weight of the compositions of $m$ with $q$ parts under a threshold profile (`Parking.Vc`, `Parking.thr`) and $v(q) = T_{m,q}$ (`Parking.Tq`). In the proof of `Parking.Dbirth_mono`, $u(q) = T_{m,q}$ and $v(q) = T_{m+1,q}$.

## Proof

Put $u'(q) = q(q-1)\,u(q)$, $v'(q) = q(q-1)\,v(q)$ and $\varphi(q) = q - 2$, and apply `Parking.lr_sum_le` to $u'$, $v'$, $\varphi$; its conclusion is the assertion, since $u'(q)\,\varphi(q) = q(q-1)(q-2)\,u(q)$ and likewise for $v'$.

Its two hypotheses hold. For $1 \le q \le q' \le n$ the number $q(q-1)\,q'(q'-1)$ is nonnegative, and multiplying the hypothesis $u(q')\,v(q) \le u(q)\,v(q')$ by it gives $u'(q')\,v'(q) \le u'(q)\,v'(q')$. The function $\varphi$ is nondecreasing.
