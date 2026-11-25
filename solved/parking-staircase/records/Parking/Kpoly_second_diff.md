---
weight: unit
short: second difference of the frozen polynomial
---
## Description

For all natural numbers $k$, $n$ and every real $y$, with $N = n+1$: the second difference of the frozen polynomial in the threshold is a sum of curvature sums with the kernel deficits as coefficients, $K_{n,k}(y+1) - 2K_{n,k}(y) + K_{n,k}(y-1) = \sum_{m=1}^{n-k}\frac{\kappa_k(N-m)}{N-m}\,\mathsf C_m(y;N)$.

## Statement

Let $a_j = j^{j-1}/j!$ (`Parking.cay`) and $\kappa_k(t) = a_t - \sum_{k<i<t} a_i\,a_{t-i}$ (`Parking.kap`). For real numbers $y$, $N$ and a natural number $m$ let $\Lambda_m(y;N)$ be the chain sum, the total weight of the compositions of $m$ in which a part of size $p$ weighs $a_p$ and a cut at the position $s$ weighs $y/(N-s)$ (`Parking.Lam` for the threshold profile `Parking.thr`), and let

$$\mathsf C_m(y;N) = (y+1)\,\Lambda_m(y+1;N) - 2y\,\Lambda_m(y;N) + (y-1)\,\Lambda_m(y-1;N)$$

be the curvature sum (`Parking.curvSum`). For natural numbers $k$ and $n$, with $N = n + 1$, let

$$K_{n,k}(y) = \kappa_k(N) + \sum_{m=1}^{n-k} \frac{\kappa_k(N-m)}{N-m}\; y\,\Lambda_m(y;N)$$

be the frozen polynomial of the column $k$ and the row $n$ (`Parking.Kpoly`); its sum is empty when $n \le k$.

For all natural numbers $k$ and $n$ and every real number $y$, with $N = n + 1$,

$$K_{n,k}(y+1) - 2\,K_{n,k}(y) + K_{n,k}(y-1) \;=\; \sum_{m=1}^{n-k} \frac{\kappa_k(N-m)}{N-m}\;\mathsf C_m(y;N).$$

## Explanation

**What it says.** The frozen polynomial depends on the threshold $y$ only through the functions $y \mapsto y\,\Lambda_m(y;N)$, $1 \le m \le n-k$, each multiplied by a coefficient $\kappa_k(N-m)/(N-m)$ that does not contain $y$, and through nothing else: its remaining term $\kappa_k(N)$ is constant. A second difference is linear and vanishes on constants, and the second difference of $y\,\Lambda_m(y;N)$ is the curvature sum by definition. So the second difference of $K_{n,k}$ is the sum of the curvature sums with the same coefficients. The statement is an identity between the two definitions and has no hypothesis on $k$, $n$ or $y$. For $n \le k$ the frozen polynomial is the constant $\kappa_k(N)$ and both sides are $0$.

**What it is for.** By `Parking.dq_frozen` the normalised step of a column is a second difference of a frozen polynomial, called the curvature term of the step, minus a boundary term. The present statement writes the curvature term as a sum over the sizes $m$ of the compositions, in which the kernel deficits enter only as coefficients and everything that depends on the threshold is collected in the curvature sums. Two arguments start from this form.

- `Parking.dq_curv_sub_boundary` applies it to the column $k$, the row $n = k + r$ and the threshold $y = k$, and so states the step at a position of the first layer as $\sum_{m=1}^{r}\frac{\kappa_k(N-m)}{N-m}\,\mathsf C_m(k;N)$ minus the boundary term. In this form the diagonal step compares two positions term by term in $m$ (`Parking.term_step`, `Parking.diagonal_step_curve`).
- `Parking.curv_ge_pair` applies it to the column $k - 1$, the row $n = k + R - 1$ and the threshold $y = k$, and bounds each curvature sum from below by the weight of the compositions with one or two marked cut points. This gives the pair–impulse criterion `Parking.dq_pos_of_pair`.

In both uses the coefficients are positive, because the arguments $N - m$ of the kernel deficit lie in the range of `Parking.kap_pos`; the sign and the size of each term of the curvature term are then those of its curvature sum.

**The Lean form.** The statement is `Kpoly j n (y + 1) - 2 * Kpoly j n y + Kpoly j n (y - 1) = ∑ m ∈ Icc 1 (n - j), kap j (n + 1 - m) / ((n : ℝ) + 1 - m) * curvSum y ((n : ℝ) + 1) m`, with the column as the argument `j`. The upper limit $n - j$ is a subtraction of natural numbers, so the sum is empty for $n \le j$. The argument $n + 1 - m$ of `kap` is a subtraction of natural numbers as well, exact because $m \le n$, and the denominator is the real number $n + 1 - m$. The size of the curvature sum is the real number $n + 1$.

## Proof

Write $K = K_{n,k}$ and $c_m = \kappa_k(N-m)/(N-m)$ for $1 \le m \le n - k$. By the definition `Parking.Kpoly`, for every real number $t$,

$$K(t) = \kappa_k(N) + \sum_{m=1}^{n-k} c_m\; t\,\Lambda_m(t;N).$$

Take this at $t = y+1$, $t = y$ and $t = y-1$ and form $K(y+1) - 2K(y) + K(y-1)$. The constant term contributes $\kappa_k(N) - 2\kappa_k(N) + \kappa_k(N) = 0$. The three sums run over the same indices $m$, and the term $m$ contributes

$$c_m\,\bigl((y+1)\,\Lambda_m(y+1;N) - 2y\,\Lambda_m(y;N) + (y-1)\,\Lambda_m(y-1;N)\bigr) = c_m\;\mathsf C_m(y;N),$$

by the definition `Parking.curvSum`. Summing over $m$ gives the statement.
