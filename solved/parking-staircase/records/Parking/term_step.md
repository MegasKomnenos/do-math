---
weight: unit
short: one term of the diagonal cross product
---
## Description

For $k \ge 265$, $r^3 \le k^2$ and $2 \le m \le r$: the term $m$ of the curvature term at the position $(k+r+1,k+1)$ times the boundary term at $(k+r,k)$ is smaller than the term $m$ of the curvature term at $(k+r,k)$ times the boundary term at $(k+r+1,k+1)$.

## Statement

Let $a_j = j^{j-1}/j!$ (`Parking.cay`), $\kappa_k(t) = a_t - \sum_{k<i<t}a_i\,a_{t-i}$ (`Parking.kap`), let $\Lambda_m(y;N)$ be the chain sum, the total weight of the compositions of $m$ for the threshold profile $s \mapsto y/(N-s)$ (`Parking.Lam`, `Parking.thr`), and let $\mathsf C_m(y;N) = (y+1)\Lambda_m(y+1;N) - 2y\,\Lambda_m(y;N) + (y-1)\Lambda_m(y-1;N)$ be the curvature sum (`Parking.curvSum`).

Let $k$, $r$, $m$ be natural numbers with $k \ge 265$, $r^3 \le k^2$ and $2 \le m \le r$, and put $N = k + r + 1$. Then

$$\frac{\kappa_{k+1}(N+1-m)}{N+1-m}\;\mathsf C_m(k+1;N+1)\cdot\frac{a_k}{k}\,\Lambda_{r+1}(k-1;N) \;<\; \frac{\kappa_k(N-m)}{N-m}\;\mathsf C_m(k;N)\cdot\frac{a_{k+1}}{k+1}\,\Lambda_{r+1}(k;N+1).$$

## Explanation

**What it compares.** By `Parking.dq_curv_sub_boundary` the step at the position $(k+r,k)$ is $C - B$ with $C = \sum_{m=1}^{r} c_m$, $c_m = \frac{\kappa_k(N-m)}{N-m}\mathsf C_m(k;N)$, and $B = \frac{a_k}{k}\Lambda_{r+1}(k-1;N)$; the step at $(k+r+1,k+1)$ is $C' - B'$ with the same expressions for $k+1$ and $N+1$. The statement is $c'_m\,B < c_m\,B'$: for each $m \ge 2$ the term of the curvature term grows along the diagonal by a smaller factor than the boundary term. Summed over $m$ it gives the cross product $C'B < CB'$, from which `Parking.diagonal_step_curve` concludes.

**Why term by term.** The curvature term is a sum over the sizes $m$ of the compositions, and the two positions have the same index set, because they have the same deficit $r$. For a fixed $m$ the two terms have the same structure, with the short side $a = r+1-m$ of the coefficient unchanged, and each of their three factors can be followed along the diagonal by itself. The inequality for each term is more than the sum needs; a floating-point evaluation of the exact quantities, which is not part of the proof, finds it true for every term at all positions behind the curve of the columns $265$, $400$ and $1000$, and well beyond the curve.

**The four inputs.** With $a = r + 1 - m$, $M = k + a = N - m$ and $q = r+1$:

- the coefficient: $\frac{\kappa_{k+1}(M+1)}{M+1} \le \gamma_M\bigl(1+\frac{\mathsf T(k,a)}{k}\bigr)\frac{\kappa_k(M)}{M}$, from `Parking.kap_diag_le`;
- the curvature sum: $\mathsf C_m(k+1;N+1) \le \frac{k}{k+1}e^{E_m}\,\mathsf C_m(k;N)$, `Parking.curvSum_step`;
- the boundary term: $(1+x)^{E_0}\Lambda_q(k-1;N) \le \Lambda_q(k;N+1)$, `Parking.Lam_gain`, and $\frac{a_{k+1}}{k+1} = \gamma_k\frac{a_k}{k}$;
- the scalars: $\gamma_M\bigl(1+\frac{\mathsf T(k,a)}{k}\bigr)\frac{k}{k+1}e^{E_m} < \gamma_k(1+x)^{E_0}$, `Parking.scalar_step`.

Here $\gamma_j = (1+1/j)^{j-2}$, and $\mathsf T$, $E_m$, $x$, $E_0$ are as in `Parking.scalar_step`.

**Where the hypothesis on the curve is used.** $r^3 \le k^2$ is used three times: for the scalar inequality, where it is the hypothesis $(q-1)^3 \le k^2$; to see $2r \le k$, which gives $2a \le k$ for `Parking.kap_diag_le` and places the arguments of $\kappa$ in the range where it is positive; and to see $401\,m^2 \le 12\,k^2$ for `Parking.curvSum_step`.

**The Lean form.** The arguments are written `kap (k + 1) (k + 1 + r + 1 - m) / ((k : ℝ) + 1 + r + 1 - m)` and so on; the subtractions inside `kap` are those of natural numbers, ordinary because $m \le r$.

## Proof

Let $a = r + 1 - m$, so $1 \le a \le r - 1$, and $M = k + a = N - m$, $q = r + 1$; then $N + 1 - m = M + 1$ and $a + 2 \le q$.

**The range.** From $r^3 \le k^2$ and $k \ge 8$: $2r \le k$ (if $k < 2r$ then $k^3 < 8r^3 \le 8k^2 \le k^3$). Hence $r < k$ and $2a \le k$. Also $401\,m^2 \le 12\,k^2$: if $r \le 41$ then $m \le 41$ and $401\cdot41^2 = 674081 \le 842700 = 12\cdot265^2$; if $r \ge 42$ then $m^2 \le r^2 \le r^3/42 \le k^2/42$ and $401 \le 12\cdot42$.

**The four comparisons.**

(F0) *The coefficient.* `Parking.kap_diag_le` (for $k \ge 1$ and $2a \le k$) gives $\kappa_{k+1}(M+1)/a_{M+1} \le \bigl(1 + \mathsf T(k,a)/k\bigr)\kappa_k(M)/a_M$. By `Parking.cay_ratio` and `Parking.psi_eq_gam`, $a_{M+1} = \gamma_M\bigl(1 + \frac1M\bigr)a_M$, that is $\frac{a_{M+1}}{M+1} = \gamma_M\frac{a_M}{M}$. Multiplying,

$$\frac{\kappa_{k+1}(M+1)}{M+1} \;\le\; \gamma_M\Bigl(1+\frac{\mathsf T(k,a)}{k}\Bigr)\frac{\kappa_k(M)}{M}.$$

(F1) *The curvature sum.* `Parking.curvSum_step` with $q = r+1$ (so $m + 1 \le q$, and $k + q = N$): $\mathsf C_m(k+1;N+1) \le \frac{k}{k+1}\,e^{E_m}\,\mathsf C_m(k;N)$ with $E_m = (1+\frac1{400})(D_m+1)(q-\frac m2)/(k(k+1))$.

(F2) *The boundary term.* `Parking.Lam_gain` with $q = r+1$: $(1+x)^{E_0}\,\Lambda_{r+1}(k-1;N) \le \Lambda_{r+1}(k;N+1)$. And $\frac{a_{k+1}}{k+1} = \gamma_k\frac{a_k}{k}$ as in (F0).

(F3) *The scalars.* `Parking.scalar_step` for $k$, $q = r+1$, $a$ (its hypothesis $(q-1)^3 \le k^2$ is $r^3 \le k^2$, and $q - a = m$): $\gamma_M\bigl(1+\frac{\mathsf T(k,a)}{k}\bigr)\frac{k}{k+1}\,e^{E_m} < \gamma_k\,(1+x)^{E_0}$.

**Positivity.** $\kappa_k(M) > 0$ and $\kappa_{k+1}(M+1) > 0$ by `Parking.kap_pos`, since $1 \le M \le 2k+1$ and $1 \le M + 1 \le 2k + 3$. $\mathsf C_m(k;N) > 0$ by `Parking.curvSum_pos` ($m \ge 2$, $k > 0$, $m \le N$). $\Lambda_{r+1}(k-1;N) > 0$ by `Parking.Lam_thr_pos`, and $a_k/k > 0$.

**Multiplying.** Write $c = \kappa_k(M)/M$, $c' = \kappa_{k+1}(M+1)/(M+1)$, $\mathsf C = \mathsf C_m(k;N)$, $\mathsf C' = \mathsf C_m(k+1;N+1)$, $\beta = a_k/k$, $\Lambda = \Lambda_{r+1}(k-1;N)$, $\Lambda' = \Lambda_{r+1}(k;N+1)$, and $u = \gamma_M(1+\mathsf T(k,a)/k)$, $v = \frac{k}{k+1}e^{E_m}$, $g = (1+x)^{E_0}$. The claim is $c'\,\mathsf C'\,\beta\Lambda < c\,\mathsf C\,\gamma_k\,\beta\,\Lambda'$. By (F1), (F0), (F3) and (F2) in turn, all factors being nonnegative and $c\,\mathsf C\,\beta\Lambda > 0$,

$$c'\,\mathsf C'\,\beta\Lambda \;\le\; c'\,v\,\mathsf C\,\beta\Lambda \;\le\; u\,v\cdot c\,\mathsf C\,\beta\Lambda \;<\; \gamma_k\,g\cdot c\,\mathsf C\,\beta\Lambda \;\le\; c\,\mathsf C\,\gamma_k\,\beta\,\Lambda' .$$
