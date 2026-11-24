---
weight: unit
short: the diagonal step behind the curve
---
## Description

In a column $k \ge 265$, at a position $(k+r,k)$ with $r \ge 1$ and $r^3 \le k^2$: if the step is not positive, $b(k+r,k) \le b(k+r,k-1)$, then the step one row down and one column to the right is negative, $b(k+r+1,k+1) < b(k+r+1,k)$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k$ and $r$ be natural numbers with $k \ge 265$, $r \ge 1$ and $r^3 \le k^2$. If

$$b(k+r,\,k) \;\le\; b(k+r,\,k-1),$$

then

$$b(k+r+1,\,k+1) \;<\; b(k+r+1,\,k).$$

In terms of the step $d_{n,k} = b(n,k) - b(n,k-1)$: $d_{k+r,k} \le 0$ implies $d_{k+r+1,k+1} < 0$.

## Explanation

**What it is for.** The staircase rests on two rules for the step $d_{n,k}$. The diagonal rule says that a step that is not positive is followed by a negative step one row down and one column to the right. Call $r = n - k$ the deficit of a position $(n,k)$ and say that the position lies behind the curve when $r^3 \le k^2$. The present statement is the diagonal rule at the positions behind the curve of the columns $k \ge 265$. These are the positions that matter in those columns: the column is positive in some row $j > k$ with $(j-k-1)^3 \le k^2$ (`Parking.curve_crossing`), a positive step of the first layer persists in the later rows of the layer, and so a step that is not positive in the first layer lies behind the curve. `Parking.diagonal_rule` combines the two; the columns up to $264$ and the positions beyond the first layer are treated by tables and by other arguments.

**The shape of the argument.** Both positions lie in the first layer of their columns and have the same deficit $r$. There the step is a curvature term minus a boundary term, $d_{k+r,k}/(k+r)! = C - B$ and $d_{k+r+1,k+1}/(k+r+1)! = C' - B'$, with $B, B' > 0$ (`Parking.dq_curv_sub_boundary`). The hypothesis is $C \le B$ and the claim is $C' < B'$. The proof shows the cross product

$$C'\,B \;<\; C\,B' ,$$

that is, the ratio of the curvature term to the boundary term decreases strictly along the diagonal. With $C \le B$ this gives $C'B < CB' \le BB'$, hence $C' < B'$. The cross product does not use the hypothesis; it is a statement about the two positions alone, and it is what makes the conclusion strict although the hypothesis is not.

**Where the work is.** The curvature term is a sum over the sizes $m \le r$ of the compositions, and the cross product is proved for each term (`Parking.term_step`): the coefficient, the curvature sum and the boundary term are each followed along the diagonal (`Parking.kap_diag_le`, `Parking.curvSum_step`, `Parking.Lam_gain`), and what the three comparisons leave is an inequality between closed forms (`Parking.scalar_step`, `Parking.ledger`). The two sides of the cross product are very close: an evaluation of the exact quantities at $k = 265$, which is not part of the proof, finds the ratio $CB'/(C'B)$ between $1.004$ and $1.002$ at the positions behind the curve with $r \ge 2$. Each comparison therefore has to be exact to the relative order $1/k$, which is why the constants of `Parking.ledger` leave little room.

**The role of the curve.** The hypothesis $r^3 \le k^2$ is the range in which the closed bounds of the three comparisons still fit together; it enters through `Parking.term_step`, and to see that $2r \le k$, so that both positions lie in the first layer. The threshold $265$ is the column from which the analytic arguments take over from the tables.

**Deficit one.** For $r = 1$ the curvature term $C'$ is zero, so $d_{k+2,k+1} < 0$ holds without the hypothesis.

**The Lean form.** The statement is `b (k + r) k ≤ b (k + r) (k - 1) → b (k + r + 1) (k + 1) < b (k + r + 1) k`, a statement about natural numbers; $k - 1$ is the ordinary difference because $k \ge 265$. The proof works with the real numbers `dq k n` $= d_{n,k}/n!$ and passes between the two forms by `Parking.dq_nonpos_iff` and `Parking.dq_neg_iff`.

## Proof

Let $N = k + r + 1$. Write $\delta = d_{k+r,k}/(k+r)!$ and $\delta' = d_{k+r+1,k+1}/(k+r+1)!$ (`Parking.dq`). By `Parking.dq_nonpos_iff` the hypothesis is $\delta \le 0$, and by `Parking.dq_neg_iff` the claim is $\delta' < 0$.

**The range.** From $r^3 \le k^2$ and $k \ge 8$: $2r \le k$ (if $k < 2r$ then $k^3 < 8r^3 \le 8k^2 \le k^3$), hence $r \le k - 1$.

**Curvature minus boundary.** `Parking.dq_curv_sub_boundary` at $(k,r)$ and at $(k+1,r)$, both in its range, gives $\delta = C - B$ and $\delta' = C' - B'$ with

$$C = \sum_{m=1}^{r} c_m, \quad c_m = \frac{\kappa_k(N-m)}{N-m}\,\mathsf C_m(k;N), \qquad B = \frac{a_k}{k}\,\Lambda_{r+1}(k-1;N),$$

$$C' = \sum_{m=1}^{r} c'_m, \quad c'_m = \frac{\kappa_{k+1}(N+1-m)}{N+1-m}\,\mathsf C_m(k+1;N+1), \qquad B' = \frac{a_{k+1}}{k+1}\,\Lambda_{r+1}(k;N+1).$$

Here $a_j = j^{j-1}/j!$ (`Parking.cay`), $\kappa$ is the kernel deficit (`Parking.kap`), $\Lambda_m(y;N)$ the chain sum for the threshold profile $s \mapsto y/(N-s)$ (`Parking.Lam`, `Parking.thr`) and $\mathsf C_m(y;N)$ the curvature sum (`Parking.curvSum`). Both boundary terms are positive: $a_k/k > 0$, $a_{k+1}/(k+1) > 0$ (`Parking.cay_pos`), and the chain sums are positive by `Parking.Lam_thr_pos`.

**The case $r = 1$.** The sum $C'$ has the single term $m = 1$, and $\mathsf C_1 = 0$ by `Parking.curvSum_one`. So $\delta' = -B' < 0$.

**The case $r \ge 2$.** For $m = 1$, $c_1 = c'_1 = 0$ by `Parking.curvSum_one`, so $c'_1 B = c_1 B'$. For $2 \le m \le r$, `Parking.term_step` gives $c'_m\,B < c_m\,B'$. Summing over $1 \le m \le r$, with at least the term $m = 2$ strict,

$$C'\,B \;<\; C\,B' .$$

The hypothesis $\delta \le 0$ is $C \le B$, so $C\,B' \le B\,B'$ because $B' > 0$. Hence $C'\,B < B'\,B$, and dividing by $B > 0$, $C' < B'$, that is $\delta' < 0$.
