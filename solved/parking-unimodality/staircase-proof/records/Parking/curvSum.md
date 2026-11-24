---
weight: unit
short: curvature sum
---
## Description

The curvature sum $\mathsf C_m(y;N) = (y+1)\,\Lambda_m(y+1;N) - 2y\,\Lambda_m(y;N) + (y-1)\,\Lambda_m(y-1;N)$: the second difference, in the threshold $y$, of $y$ times the chain sum $\Lambda_m(y;N)$.

## Statement

For real numbers $y$, $N$ and a natural number $m$ let $\Lambda_m(y;N)$ be the chain sum: the total weight of the compositions of $m$ in which a part of size $p$ weighs $a_p = p^{p-1}/p!$ and a cut at the position $s$ weighs $y/(N-s)$ (`Parking.Lam` for the threshold profile `Parking.thr`). The curvature sum is

$$\mathsf C_m(y;N) \;=\; (y+1)\,\Lambda_m(y+1;N) \;-\; 2\,y\,\Lambda_m(y;N) \;+\; (y-1)\,\Lambda_m(y-1;N).$$

## Explanation

**Where it comes from.** At a position $(n,k)$ of the first layer of a column, $k + 1 \le n \le 2k - 1$, the normalised step $d_{n,k}/n!$ is a second difference of the frozen polynomial $K_{n,k}$ at the threshold $k$ minus a boundary term (`Parking.dq_frozen`). The frozen polynomial is, with $N = n + 1$,

$$K_{n,k}(y) = \kappa_k(N) + \sum_{m=1}^{n-k} \frac{\kappa_k(N-m)}{N-m}\; y\,\Lambda_m(y;N)$$

(`Parking.Kpoly`). Its dependence on the threshold is through the functions $y \mapsto y\,\Lambda_m(y;N)$ alone, so its second difference at $y$ is $\sum_m \frac{\kappa_k(N-m)}{N-m}\,\mathsf C_m(y;N)$ (`Parking.Kpoly_second_diff`). The curvature sum is the contribution of the compositions of one size $m$ to the curvature term of a step, apart from the coefficient. `Parking.dq_curv_sub_boundary` states the step in this form.

**By the number of parts.** A cut of the threshold profile carries the factor $y$, so a composition with $Q$ parts contributes $y^{Q-1}$ times its weight for the threshold $1$: $y\,\Lambda_m(y;N) = \sum_{Q=1}^{m} y^{Q}\,V_Q(m;\lambda^{1,N})$, where $V_Q(m;f)$ is the weight of the compositions of $m$ with $Q$ parts for the profile $f$ (`Parking.Vc`) and $\lambda^{1,N}(s) = 1/(N-s)$; this is `Parking.Lam_thr`. Hence

$$\mathsf C_m(y;N) = \sum_{Q=1}^{m} \bigl((y+1)^Q - 2y^Q + (y-1)^Q\bigr)\,V_Q\bigl(m;\lambda^{1,N}\bigr)$$

(`Parking.curvSum_eq_sum`). The second difference of $y \mapsto y^Q$ is $2\sum_{j \ge 1}\binom{Q}{2j}\,y^{Q-2j}$: it is $0$ for $Q = 1$, it is $2$ for $Q = 2$, and for $y > 0$ it is positive for every $Q \ge 2$. So the compositions with one part do not contribute, $\mathsf C_1(y;N) = 0$ (`Parking.curvSum_one`), and $\mathsf C_m(y;N) > 0$ for $m \ge 2$, $y > 0$ and $N \ge m$ (`Parking.curvSum_pos`). To leading order the weight of a composition with $Q$ parts is $Q(Q-1)\,y^{Q-2}$: the curvature sum weighs a composition by the number of ordered pairs of its parts.

**Why it is a definition of its own.** Two arguments treat the curvature term of a step size by size. The diagonal step compares the curvature term of a position with that of the position one row down and one column to the right, term by term in $m$; the comparison of the two curvature sums is `Parking.curvSum_step`. The pair–impulse criterion bounds the curvature term from below, and the proof of `Parking.curv_ge_pair` does so by bounding each curvature sum from below by the weight of the compositions of $m$ with one or two marked cut points. In both, what is proved about one curvature sum is a statement about compositions and profiles in which the kernel coefficients $\kappa$ play no part. Defining the curvature sum as the second difference, and not as the sum over $Q$, makes the passage from the frozen polynomial, `Parking.Kpoly_second_diff`, a matter of the definition of `Parking.Kpoly`; the expansion over $Q$ is the separate statement `Parking.curvSum_eq_sum`, from which the proofs about the curvature sum start.

**The Lean form.** `Parking.curvSum y N m` takes real numbers $y$ and $N$ and a natural number $m$; it is the expression above with `Lam (thr y N) m` for $\Lambda_m(y;N)$. In the uses $y$ is a column $k$ or $k+1$ and $N$ is $n + 1$ for a row $n$, both cast to real numbers. The profile $y/(N-s)$ is read only at the cut points $0 < s < m$, where $N - s > 0$ in every use.
