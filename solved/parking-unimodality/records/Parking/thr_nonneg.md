---
weight: step
short: nonnegativity of the threshold profile
---
## Description

The threshold profile $s \mapsto y/(N-s)$ is nonnegative at every point $s \le N$ when $y \ge 0$.

## Statement

Let $y$ and $N$ be real numbers and $s$ a natural number. If $0 \le y$ and $s \le N$, then $0 \le \lambda^{y,N}(s)$, where $\lambda^{y,N}(s) = y/(N-s)$ is the threshold profile of `Parking.thr`.

## Explanation

Sign statements about the weights $V_q(m;f)$ of `Parking.Vc` need a profile that is nonnegative at the cut points. For the threshold profile this is the present statement, used in `Parking.Lam_thr_pos` and in the proofs of `Parking.curv_ratio` and `Parking.Vc_thr_ratio_ge`. The case $s = N$ is included because the Lean division gives $y/0 = 0$.

## Proof

The numerator $y$ and the denominator $N - s$ are both nonnegative, so the quotient is nonnegative.
