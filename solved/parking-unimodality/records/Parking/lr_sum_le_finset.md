---
weight: step
short: weighted Chebyshev inequality on a finite set
---
## Description

Weighted Chebyshev inequality on a finite set $S$ of natural numbers: if $u(q')\,v(q) \le u(q)\,v(q')$ for $q \le q'$ in $S$ and $\varphi$ is nondecreasing on $S$, then $(\sum_S u\varphi)(\sum_S v) \le (\sum_S v\varphi)(\sum_S u)$.

## Statement

Let $S$ be a finite set of natural numbers and let $u, v, \varphi$ be real-valued functions on the natural numbers. Assume that for all $q, q' \in S$ with $q \le q'$

$$u(q')\,v(q) \;\le\; u(q)\,v(q') \qquad\text{and}\qquad \varphi(q) \;\le\; \varphi(q').$$

Then

$$\Bigl(\sum_{q\in S} u(q)\,\varphi(q)\Bigr)\Bigl(\sum_{q\in S} v(q)\Bigr) \;\le\; \Bigl(\sum_{q\in S} v(q)\,\varphi(q)\Bigr)\Bigl(\sum_{q\in S} u(q)\Bigr).$$

No sign condition is imposed on $u$, $v$ or $\varphi$.

## Explanation

When $u$ and $v$ are positive, the first hypothesis says that the quotient $u/v$ does not increase on $S$; one says that the weight $u$ is smaller than the weight $v$ in likelihood-ratio order. The conclusion, divided by the two total weights, then says that the average of a nondecreasing function $\varphi$ with respect to $u$ is at most its average with respect to $v$: a weight that leans toward small indices gives a smaller average of an increasing function. The hypothesis and the conclusion are written without division, and in this form the statement is a plain inequality between sums that needs no positivity.

The statement is the common tool of this part of the library for comparing two laws of the number of parts of a composition. On an interval $\{1, \dots, n\}$ it is `Parking.lr_sum_le`. The general finite set is needed in the proof of `Parking.mu0_le_muh`, which applies the inequality twice on the set $\{0, \dots, r-1\}$ to obtain a negative correlation.

## Proof

Let $\Delta$ be the left-hand side minus the right-hand side. Expanding the products of sums,

$$\Delta \;=\; \sum_{q\in S}\sum_{q'\in S} u(q)\,v(q')\,\bigl(\varphi(q) - \varphi(q')\bigr).$$

Exchanging the names of the two summation indices gives $\Delta = \sum_{q}\sum_{q'} u(q')\,v(q)\,(\varphi(q') - \varphi(q))$. Adding the two expressions,

$$2\Delta \;=\; \sum_{q\in S}\sum_{q'\in S}\bigl(u(q)\,v(q') - u(q')\,v(q)\bigr)\bigl(\varphi(q) - \varphi(q')\bigr).$$

Every term of this double sum is nonpositive. If $q \le q'$, the first factor is nonnegative by the first hypothesis and the second factor is nonpositive by the second. If $q' \le q$, the hypotheses applied to the pair $(q', q)$ show that the first factor is nonpositive and the second nonnegative. Hence $2\Delta \le 0$.
