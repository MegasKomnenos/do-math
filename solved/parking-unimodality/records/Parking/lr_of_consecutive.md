---
weight: step
short: likelihood-ratio order from consecutive ratios
---
## Description

If $v > 0$ on $\{1, \dots, n\}$ and $u(q+1)\,v(q) \le u(q)\,v(q+1)$ for consecutive indices, then $u(q')\,v(q) \le u(q)\,v(q')$ for all $1 \le q \le q' \le n$.

## Statement

Let $n$ be a natural number and let $u, v$ be real-valued functions on the natural numbers. Assume that $v(q) > 0$ for $1 \le q \le n$ and that

$$u(q+1)\,v(q) \;\le\; u(q)\,v(q+1) \qquad\text{for all } q \text{ with } 1 \le q \text{ and } q + 1 \le n.$$

Then

$$u(q')\,v(q) \;\le\; u(q)\,v(q') \qquad\text{for all } q, q' \text{ with } 1 \le q \le q' \le n.$$

No sign condition is imposed on $u$.

## Explanation

Divided by the positive values of $v$, the hypothesis says that the quotient $u/v$ does not increase from each index to the next, and the conclusion says that it does not increase from $q$ to any later $q'$. The statement converts a comparison of consecutive terms into the hypothesis of `Parking.lr_sum_le` and of `Parking.lr_factorial_moment_le`. This is the form in which the comparisons of compositions are available: `Parking.Tq_ratio`, `Parking.Vc_ratio_le` and `Parking.Vc_thr_ratio_ge` each relate the total weight of the compositions with $q+1$ parts to that of the compositions with $q$ parts.

It is used in the proof of `Parking.curv_ratio`, with $u(q) = V_q(m;\lambda^{y,N})$ and $v(q) = T_{m,q}$ (positive by `Parking.Tq_pos`), and in the proof of `Parking.Lam_raise`, with $u(q) = T_{r,q}\,h^{q-1}$ and $v(q) = k^{q-1}\,V_q(r;\lambda^{1,N})$, $N = k + r + 1$; for the notation see `Parking.Vc`, `Parking.thr` and `Parking.Tq`.

## Proof

Fix $q \ge 1$ and argue by induction on $q'$, starting at $q' = q$, where the two sides are equal.

For the step from $q' = k$ to $q' = k+1$, assume $q \le k$, $k + 1 \le n$ and $u(k)\,v(q) \le u(q)\,v(k)$. The hypothesis at the index $k$ gives $u(k+1)\,v(k) \le u(k)\,v(k+1)$. Multiply this by $v(q) > 0$, and multiply the induction hypothesis by $v(k+1) > 0$:

$$u(k+1)\,v(k)\,v(q) \;\le\; u(k)\,v(k+1)\,v(q) \;\le\; u(q)\,v(k)\,v(k+1).$$

Dividing the outer terms by $v(k) > 0$ gives $u(k+1)\,v(q) \le u(q)\,v(k+1)$.
