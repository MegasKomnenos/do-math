---
weight: unit
short: propagation of nonnegative steps from nonnegative suffix sums of the tree curvature
---
## Description

Let $k\ge 2$, $n_0\ge k$ and $x>0$. If $z^{(k)}_Nx^N$ does not increase in $N$ and the sums $\sum_{t=s}^{n_0}\xi_t\,x^t$ are nonnegative for all $k\le s\le n_0$, where $\xi_t$ is the tree curvature of column $k$, then the step of column $k$ is nonnegative in every row $n\ge n_0$: $b(n,k-1)\le b(n,k)$.

## Statement

Let $k\ge 2$ and $n_0\ge k$ be natural numbers and $x>0$ a real number. Let $z^{(y)}_N=A(N,y-1)/N!$ (`Parking.zr`), let $\delta_n=\big(b(n,k)-b(n,k-1)\big)/n!$ be the normalised step of column $k$ (`Parking.dq k n`), and let $\xi_t$ be the tree curvature of column $k$ (`Parking.xi k t`), defined for $t\ge 1$ by
$$t\,\xi_t=\min(t,k+1)\,z^{(k+1)}_{t-1}-2\min(t,k)\,z^{(k)}_{t-1}+\min(t,k-1)\,z^{(k-1)}_{t-1}$$
and $\xi_0=0$. Assume

1. $z^{(k)}_{N+1}\,x^{N+1}\le z^{(k)}_N\,x^{N}$ for every $N\ge 0$;
2. $\displaystyle\sum_{t=s}^{n_0}\xi_t\,x^{t}\ge 0$ for every $s$ with $k\le s\le n_0$.

Then $\delta_n\ge 0$ for every $n\ge n_0$.

## Explanation

The statement turns finitely many inequalities at one row $n_0$ into the sign of the step in all later rows. It is how the columns $2\le k\le 81$ are completed in `Parking.small_columns`: the table `Parking.Tab.small_table` supplies hypothesis 2 at the critical tilt $x=x_k$ and at a row $n_0=n_0(k)$ chosen for each column, and `Parking.zrT_anti_crit` supplies hypothesis 1.

Why it works. The one-tree bound `Parking.one_tree_bound` bounds the step from below by a convolution of the tree curvature with the environment, $\delta_n\ge\sum_{t\le n}\xi_t\,z^{(k)}_{n-t}$. The curvature $\xi_t$ may be negative for small $t$ (the column has not crossed yet) and is nonnegative once the step is: for $n\ge k$, $(n+1)\xi_{n+1}=(k+1)\delta_n+2\beta^{(k-1)}_n$ with $\beta^{(k-1)}_n=b(n,k-1)/n!\ge 0$. After tilting, the weights $z^{(k)}_{n-t}x^{n-t}$ in the convolution increase with $t$ by hypothesis 1, so they put more weight on the late, positive curvatures than on the early, negative ones, and summation by parts reduces the positivity of the convolution to that of the suffix sums of $\xi_tx^t$. The suffix sums are an invariant: once they are nonnegative at a row, the step is nonnegative there, the next curvature is nonnegative, and the suffix sums at the next row are nonnegative again. The tilt $x$ is free in the statement; it must be one for which hypothesis 1 holds, and the critical tilt is such a tilt.

The conclusion $\delta_n\ge 0$ is equivalent to $b(n,k-1)\le b(n,k)$ (`Parking.dq_nonneg_iff`).

## Proof

For $n\ge k$ let $I(n)$ be the assertion that $\sum_{t=s}^{n}\xi_tx^t\ge 0$ for all $k\le s\le n$. Hypothesis 2 is $I(n_0)$.

**(i) $I(n)$ implies $\delta_n\ge 0$, for $n\ge k$.** `Parking.one_tree_bound` gives $\sum_{t=0}^{n}\xi_t\,z^{(k)}_{n-t}\le\delta_n$. Multiply by $x^n>0$ and drop the terms $t<k$, which vanish because $\xi_t=0$ for $t<k$ (`Parking.xi_eq_zero`):
$$\sum_{t=k}^{n}\big(\xi_tx^t\big)\,w_t\le\delta_nx^n,\qquad w_t=z^{(k)}_{n-t}x^{n-t}.$$
By hypothesis 1 the weights satisfy $w_s\le w_{s+1}$ for $k\le s<n$, and $w_t\ge 0$ (`Parking.zrT_nonneg`). Summation by parts: if all suffix sums $\sum_{t=s}^{n}a_t$, $k\le s\le n$, are nonnegative and $w$ is nondecreasing on $[k,n]$, then $w_s\sum_{t=s}^{n}a_t\le\sum_{t=s}^{n}a_tw_t$ for every such $s$. (Downward induction on $s$: $\sum_{t\ge s}a_tw_t=a_sw_s+\sum_{t\ge s+1}a_tw_t\ge a_sw_s+w_{s+1}\sum_{t\ge s+1}a_t\ge a_sw_s+w_s\sum_{t\ge s+1}a_t$, the last step because the suffix sum from $s+1$ is nonnegative.) With $a_t=\xi_tx^t$ and $s=k$: $0\le w_k\sum_{t=k}^{n}\xi_tx^t\le\delta_nx^n$.

**(ii) $\delta_n\ge 0$ implies $\xi_{n+1}\ge 0$, for $n\ge k$.** `Parking.succ_mul_xi_succ` states $(n+1)\,\xi_{n+1}=(k+1)\,\delta_n+2\beta^{(k-1)}_n$, and $\beta^{(k-1)}_n\ge 0$ (`Parking.bq_nonneg`).

**(iii) $I(n)$ implies $I(n+1)$, for $n\ge k$.** By (i) and (ii), $\xi_{n+1}x^{n+1}\ge 0$. For $s\le n$ the suffix sum from $s$ to $n+1$ is the suffix sum from $s$ to $n$ plus this term; for $s=n+1$ it is this term.

By induction $I(n)$ holds for all $n\ge n_0$, and (i) gives $\delta_n\ge 0$.
