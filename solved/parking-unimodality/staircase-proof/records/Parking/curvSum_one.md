---
weight: step
short: the curvature sum of size one vanishes
---
## Description

For $m = 1$ the curvature sum vanishes, $\mathsf C_1(y;N) = 0$ for all real $y$ and $N$: the only composition of $1$ has one part, and $y\,\Lambda_1(y;N) = y$ is linear in $y$.

## Statement

For all real numbers $y$ and $N$,

$$\mathsf C_1(y;N) = 0,$$

where $\mathsf C_m(y;N) = (y+1)\,\Lambda_m(y+1;N) - 2y\,\Lambda_m(y;N) + (y-1)\,\Lambda_m(y-1;N)$ is the curvature sum (`Parking.curvSum`) and $\Lambda_m(y;N)$ is the chain sum, the total weight of the compositions of $m$ for the threshold profile $s \mapsto y/(N-s)$ (`Parking.Lam`, `Parking.thr`).

## Explanation

The curvature term of a step is $\sum_{m=1}^{r} \frac{\kappa_k(N-m)}{N-m}\,\mathsf C_m(k;N)$ (`Parking.dq_curv_sub_boundary`). By this statement its term $m = 1$ is always zero. Two consequences are used in `Parking.diagonal_step_curve`. At a position of deficit $r = 1$ the curvature term is zero altogether, so the step is minus the boundary term and is negative without any hypothesis. And for $r \ge 2$ the term-by-term comparison `Parking.term_step` has to be made for $m \ge 2$ only, where the curvature sum is positive (`Parking.curvSum_pos`).

## Proof

A composition with $Q$ parts has $Q - 1$ cuts, each with a factor $y$, so $y\,\Lambda_m(y;N) = \sum_{Q=1}^{m} y^Q\,V_Q(m;\lambda^{1,N})$ with $V_Q(m;\lambda^{1,N})$ the weight of the compositions of $m$ with $Q$ parts for the profile $s \mapsto 1/(N-s)$ (`Parking.Lam_thr`, multiplied by $y$). Taking the second difference in $y$ term by term gives `Parking.curvSum_eq_sum`,

$$\mathsf C_m(y;N) = \sum_{Q=1}^{m}\bigl((y+1)^Q - 2y^Q + (y-1)^Q\bigr)\,V_Q\bigl(m;\lambda^{1,N}\bigr).$$

For $m = 1$ the sum has the single term $Q = 1$, whose first factor is $(y+1) - 2y + (y-1) = 0$.
