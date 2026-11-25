---
weight: step
short: nonnegative step, in real and natural form
---
## Description

The normalised step is nonnegative exactly when the count does not decrease: $0\le\delta^{(k)}_n$ if and only if $b(n,k-1)\le b(n,k)$.

## Statement

For all natural numbers $k$ and $n$: $0\le\delta^{(k)}_n$ if and only if $b(n,k-1)\le b(n,k)$. Here $\delta^{(k)}_n=(b(n,k)-b(n,k-1))/n!$ (`Parking.dq`) and $b$ is `Parking.b`. The statement includes $k=0$ with $k-1$ read as $0$, as in the Lean definition; both sides then hold trivially.

## Explanation

The analytic parts of the proof establish inequalities for the real numbers $\delta^{(k)}_n$; the main theorem and the tables speak of the natural numbers $b(n,k)$. This record and its three companions `Parking.dq_pos_iff`, `Parking.dq_nonpos_iff`, `Parking.dq_neg_iff` are the passage between the two. In ordinary notation they say only that $d_{n,k}/n!$ has the sign of $d_{n,k}$; they are separate declarations because in Lean a comparison of natural numbers and an inequality between real quotients are different statements.

## Proof

$\delta^{(k)}_n=(b(n,k)-b(n,k-1))/n!$ with the difference taken in the real numbers, and $n!>0$. So $0\le\delta^{(k)}_n$ if and only if $b(n,k-1)\le b(n,k)$ as real numbers, which is the same as the inequality of natural numbers.
