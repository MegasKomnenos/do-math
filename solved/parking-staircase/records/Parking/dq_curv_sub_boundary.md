---
weight: unit
short: a first-layer step as curvature term minus boundary term
---
## Description

At a position $(k+r,k)$ of the first layer, $1 \le r \le k-1$, with $N = k+r+1$: $d_{k+r,k}/(k+r)! = \sum_{m=1}^{r}\frac{\kappa_k(N-m)}{N-m}\,\mathsf C_m(k;N) - \frac{a_k}{k}\,\Lambda_{r+1}(k-1;N)$, a sum of curvature sums with the kernel deficits as coefficients minus a multiple of a chain sum.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`) and $d_{n,k} = b(n,k) - b(n,k-1)$. Let $a_j = j^{j-1}/j!$ (`Parking.cay`), $\kappa_k(t) = a_t - \sum_{k<i<t} a_i\,a_{t-i}$ (`Parking.kap`), let $\Lambda_m(y;N)$ be the chain sum, the total weight of the compositions of $m$ for the threshold profile $s \mapsto y/(N-s)$ (`Parking.Lam`, `Parking.thr`), and let

$$\mathsf C_m(y;N) = (y+1)\,\Lambda_m(y+1;N) - 2y\,\Lambda_m(y;N) + (y-1)\,\Lambda_m(y-1;N)$$

be the curvature sum (`Parking.curvSum`).

Let $k \ge 2$ and $r$ be natural numbers with $1 \le r \le k - 1$, and put $N = k + r + 1$. Then

$$\frac{d_{k+r,k}}{(k+r)!} \;=\; \sum_{m=1}^{r} \frac{\kappa_k(N-m)}{N-m}\;\mathsf C_m(k;N) \;-\; \frac{a_k}{k}\;\Lambda_{r+1}(k-1;N).$$

## Explanation

**The two terms.** Call the sum the curvature term $C$ and $B = \frac{a_k}{k}\Lambda_{r+1}(k-1;N)$ the boundary term of the position $(k+r,k)$. Both have a sign: $B > 0$ (`Parking.Lam_thr_pos`), every coefficient $\kappa_k(N-m)$ is positive in this range (`Parking.kap_pos`), $\mathsf C_1 = 0$ (`Parking.curvSum_one`) and $\mathsf C_m(k;N) > 0$ for $m \ge 2$ (`Parking.curvSum_pos`). So the sign of the step is decided by the comparison of two positive quantities, and $d_{k+r,k} \le 0$ says $C \le B$.

**Where it comes from.** It is the first of the two equations of `Parking.dq_frozen`, in which the curvature term appears as the second difference $K(k+1) - 2K(k) + K(k-1)$ of the frozen polynomial $K = K_{k+r,k}$ (`Parking.Kpoly`). The present statement writes that second difference out. The form with the curvature sums is the one in which two positions on a diagonal can be compared: the position $(k+r+1,k+1)$ has the same deficit $r$, so its curvature term is a sum over the same indices $m$, and its boundary term is a chain sum of the same length $r+1$; `Parking.term_step` compares the two positions term by term, and `Parking.diagonal_step_curve` applies the present statement at both.

**The range.** $1 \le r \le k - 1$ is the first layer $k+1 \le n \le 2k-1$ of the column $k$, the range of `Parking.dq_frozen`.

**The Lean form.** The left side is `dq k (k + r)`, the real number $d_{k+r,k}/(k+r)!$ (`Parking.dq`). The coefficient is `kap k (k + r + 1 - m) / ((k : ℝ) + r + 1 - m)`; the subtraction in the argument of `kap` is that of natural numbers, ordinary because $m \le r$. The threshold and size of the curvature sum are the real numbers `(k : ℝ)` and `(k : ℝ) + r + 1`.

## Proof

By the first equation of `Parking.dq_frozen`, for $k \ge 2$ and $1 \le r \le k-1$,

$$\frac{d_{k+r,k}}{(k+r)!} = \bigl(K(k+1) - 2K(k) + K(k-1)\bigr) - \frac{a_k}{k}\,\Lambda_{r+1}(k-1;N), \qquad K = K_{k+r,k}.$$

By `Parking.Kpoly_second_diff`, for the column $k$, the row $n = k + r$ and the threshold $k$, with $n + 1 = N$ and $n - k = r$,

$$K(k+1) - 2K(k) + K(k-1) = \sum_{m=1}^{r}\frac{\kappa_k(N-m)}{N-m}\;\mathsf C_m(k;N):$$

the frozen polynomial is $K(y) = \kappa_k(N) + \sum_{m=1}^{r}\frac{\kappa_k(N-m)}{N-m}\,y\,\Lambda_m(y;N)$ for every real $y$, in its second difference the constant $\kappa_k(N)$ cancels, and the term $m$ contributes its coefficient times the second difference of $y\,\Lambda_m(y;N)$, which is the curvature sum. Substituting this into the first equation gives the statement.
