---
weight: unit
short: the columns k ≥ 82 increase strictly in the rows n ≥ 2k
---
## Description

For every column $k\ge 82$ and every row $n\ge 2k$: $b(n,k-1)<b(n,k)$, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$.

## Statement

Let $k\ge 82$ and $n\ge 2k$ be natural numbers. Then $b(n,k-1)<b(n,k)$.

## Explanation

**Place in the argument.** This is the left half (`Parking.left_half`) for the large columns, with strict inequality. The rows $k\le n\le 2k-1$ of such a column are handled before: `Parking.single_crossing` gives a crossing row $q$ with $k+1\le q\le k+\frac{27}{100}k$ such that the step $d_{j,k}=b(j,k)-b(j,k-1)$ is nonpositive for $k\le j<q$ and positive for $q\le j\le 2k-1$. The present statement continues the positivity to all rows, by induction on the row. The threshold $82$ is the one from which `Parking.single_crossing` is available; the columns $k\le 81$ are treated with a table (`Parking.small_columns`).

**The difficulty.** Fix the critical tilt $x=x_k=(k/(k+1))^{k-1}$ and write $\eta_j=x^{j}d_{j,k}/j!$ for the tilted step, $U_j=x^{j}b(j,k-1)/j!$ for the tilted mass of the level $k-1$, and $\kappa_m$ for the tilted prime kernel of the threshold $k$. The column inequality on all rows (`Parking.col_eq_all`) gives
$$n\,\eta_n\ \ge\ (k+1)\,x\,\eta_{n-1}+2x\,U_{n-1}+n\sum_{j=k}^{n-1}\kappa_{n-j}\,\eta_j .$$
The first two terms are a positive source. The sum is the feedback of the earlier rows, and it contains the rows $k\le j<q$ before the crossing, where $\eta_j\le 0$. These negative terms never disappear: every later row $n$ feels them, with the kernel weights $\kappa_{n-j}$. Nothing is known about the size of each $\eta_j$ in those rows, so the negative part cannot be bounded term by term.

**The idea.** Two facts are available. First, the sign pattern: nonpositive up to the row $q-1$, positive from $q$ on. Second, a lower bound for one particular weighted sum of the $\eta_j$: with $\Psi'(j)=\max(j,2k-1)$, the sum $\sum_{j=k}^{J}\Psi'(j)\eta_j$ is at least minus a boundary quantity, the weighted debt (`Parking.weighted_debt`); this comes from the convexity of the tilted environments along the diagonal and uses no information about the crossing. The step that joins them is an order statement for the kernel: with $L=n-q+1$ and $\theta=\kappa_L/(2k-1)$,
$$\frac{\kappa_{n-j}}{\Psi'(j)}\le\theta\ \ (j<q),\qquad\frac{\kappa_{n-j}}{\Psi'(j)}\ge\theta\ \ (q\le j\le n-1)$$
(`Parking.order_neg`, `Parking.order_pos`). Because $\eta_j$ is nonpositive exactly where the ratio is below $\theta$ and positive where it is above, $\kappa_{n-j}\eta_j\ge\theta\,\Psi'(j)\,\eta_j$ in every row, and the feedback is at least $-\theta$ times the weighted debt. The debt consists of masses of the rows $n-1$ and $n-2$, which are comparable with the source, and $\theta$ is small: $n(n-1)\kappa_L$ is of the order $\sqrt{k}$, against a source coefficient of the order $k$.

The weight $\Psi'$ has to serve both facts at once: its weighted second differences along the diagonal must be nonnegative, and the kernel must be ordered against it at the crossing row. The record of `Parking.PsiW` explains why $\max(N,2k-1)$ does both, and why neither the weight $N$ on all rows nor a constant weight would: with the weight $N$ the order fails between the rows $q-1$ and $q$ when $n$ is close to $2k$, and with a constant weight the required convexity is not known beyond the first layer.

**The numerical margin.** The constants of the proof leave little room at the first column: at $k=82$ the decisive inequality of the row step reads $12.66\sqrt{k}\le 0.7356\,(2k-1)$, that is, about $114.6\le 119.9$.

## Proof

Throughout, $x=x_k$ (`Parking.xcrit`), $\delta_j=d_{j,k}/j!$ (`Parking.dq k j`), $\eta_j=\delta_jx^{j}$, $u_N=z^{(k)}_Nx^{N}$ and $u^{-}_N=z^{(k-1)}_Nx^{N}$ (`Parking.zrT`), $U_N=u_N-u^{-}_N=\beta^{(k-1)}_Nx^{N}$ with $\beta^{(\ell)}_N=b(N,\ell)/N!$ (`Parking.Ut`, `Parking.Ut_eq_bq`), $\kappa_m=x^{m}[X^m]K_k$ (`Parking.kqT`), $\omega_j=c_jx^{j}$ with $c_j=(j+1)^{j-1}/j!$ (`Parking.ccT`) and $\Psi'(N)=\max(N,2k-1)$ (`Parking.PsiW`). By `Parking.dq_pos_iff` the claim is $\delta_n>0$.

**Reduction to a row step.** `Parking.single_crossing` gives $q$ with $k+1\le q$, $100(q-k)\le 27k$, $\delta_j\le 0$ for $k\le j<q$ and $\delta_m>0$ for $q\le m\le 2k-1$. We show $\delta_m>0$ for all $m\ge q$ by strong induction on $m$. For $m\le 2k-1$ this is given. For $m\ge 2k$ it is the following row step, applied with $n=m$; its hypothesis on the rows $q\le j\le n-1$ is the induction hypothesis.

**Row step.** Let $n\ge 2k$, and suppose $\delta_j\le 0$ for $k\le j<q$ and $\delta_j>0$ for $q\le j\le n-1$. Then $\delta_n>0$. Put $L=n-q+1$, $\theta=\kappa_L/(2k-1)\ge 0$ (`Parking.kqT_nonneg`) and $T=n(n-1)\kappa_L$.

*1. The tilted column inequality.* `Parking.col_eq_all` states $(k+1)\delta_{n-1}+2\beta^{(k-1)}_{n-1}\le n\big(\delta_n-\sum_{m=1}^{n-k}[X^m]K_k\,\delta_{n-m}\big)$. Multiply by $x^{n}$ and index the sum by the row $j=n-m$:
$$(k+1)\,x\,\eta_{n-1}+2x\,U_{n-1}\ \le\ n\,(\eta_n-S),\qquad S=\sum_{j=k}^{n-1}\kappa_{n-j}\,\eta_j .\tag{1}$$

*2. The order of the kernel and the weighted debt.* For $k\le j<q$, `Parking.order_neg` gives $\kappa_{n-j}\le\theta\,\Psi'(j)$ and $\eta_j\le 0$; for $q\le j\le n-1$, `Parking.order_pos` gives $\kappa_{n-j}\ge\theta\,\Psi'(j)$ and $\eta_j>0$. In both cases $\kappa_{n-j}\eta_j\ge\theta\,\Psi'(j)\,\eta_j$. Summing and applying `Parking.weighted_debt` with $J=n-1$,
$$S\ \ge\ \theta\sum_{j=k}^{n-1}\Psi'(j)\,\eta_j\ \ge\ -\theta\,\mathfrak{D},\qquad\mathfrak{D}=\Psi'(n-1)U_{n-1}+\Psi'(n-2)U_{n-2}+\big(\Psi'(n-1)-\Psi'(n-2)\big)u_{n-1}.\tag{2}$$
Since $n-1\ge 2k-1$, $\Psi'(n-1)=n-1$ (`Parking.PsiW_of_ge`), and $n-2\le\Psi'(n-2)\le n-1$ (`Parking.PsiW_ge_self`, `Parking.PsiW_mono`). As $U_{n-2},u_{n-1}\ge 0$, $\ \mathfrak{D}\le(n-1)(U_{n-1}+U_{n-2})+u_{n-1}$.

*3. The debt in terms of $U_{n-1}$ and $\eta_{n-1}$.* Two bounds are used.

(a) `Parking.Ut_diag_lower` gives $k\,U_{n-2}\le(k+1)\,U^{+}_{n-1}$, where $U^{+}_{n-1}=x^{n-1}\beta^{(k)}_{n-1}=U_{n-1}+\eta_{n-1}$. So $U_{n-2}\le(1+\frac1k)(U_{n-1}+\eta_{n-1})$.

(b) *The mass of the level $k-1$ dominates the environment:* $x\,W\,u_{n-1}\le(n-1)\,U_{n-1}$ with $W=\sum_{j=0}^{8}\omega_j$. More generally, for $k\ge 2$, a tilt $x\ge 0$ at which $u_N$ does not increase in $N$, $J\le k-1$ and $M\ge k-1+J$: $x\big(\sum_{j\le J}\omega_j\big)u_M\le(M+1)U_{M+1}$. To see this, subtract the tilted last-car recursions (`Parking.zrT_succ`) of the thresholds $k$ and $k-1$ at the size $M+1$: $(M+1)U_{M+1}=x\sum_{i=0}^{M}F_i$ with $F_i=\min(i+1,k)\,u_iu_{M-i}-\min(i+1,k-1)\,u^{-}_iu^{-}_{M-i}$. Every $F_i$ is nonnegative because $0\le u^{-}\le u$ (`Parking.zrT_nonneg`, `Parking.zrT_le_zrT`). For $i=M-j$ with $j\le J$ one has $i\ge k-1$, so $F_i=k\,u_{M-j}u_j-(k-1)\,u^{-}_{M-j}u^{-}_j\ge u_{M-j}u_j\ge u_M\,\omega_j$, using $u_j=\omega_j$ for $j\le k$ (`Parking.zrT_eq_ccT`) and $u_{M-j}\ge u_M$. Keeping only these $J+1$ terms gives the claim. Here it is applied with $J=8$ and $M=n-2$; the monotonicity of $u$ at the critical tilt is `Parking.zrT_anti_crit`, which also gives $u_{n-1}\le u_{n-2}$.

With (a) and (b), writing $B=2+\frac1k+\frac{1}{xW}$,
$$\mathfrak{D}\ \le\ (n-1)\Big(B\,U_{n-1}+\big(1+\tfrac1k\big)\eta_{n-1}\Big).\tag{3}$$

*4. Combination.* From (1), (2), (3) and $n(n-1)\theta=T/(2k-1)$,
$$n\,\eta_n\ \ge\ U_{n-1}\Big(2x-\frac{T}{2k-1}\,B\Big)+\eta_{n-1}\,(k+1)\Big(x-\frac{T}{(2k-1)\,k}\Big).$$
Here $U_{n-1}\ge 0$ and $\eta_{n-1}>0$, because $n-1\ge q$. So $\eta_n>0$ as soon as
$$T\cdot B\le 2x\,(2k-1)\qquad\text{and}\qquad T<x\,k\,(2k-1).\tag{4}$$

*5. The size of the kernel weight:* $T=n(n-1)\kappa_L\le 3.762\sqrt{k}$. Note $n=L+q-1\le L+1.27k-1$. Three cases.

- $L\le k$. Then $100(L-1)=100(n-q)\ge 73k$, so $\kappa_L\le 0.73/(k\sqrt k)$ by `Parking.kap_far`, and $n\le 2.27k$. Hence $T\le n^2\kappa_L\le 2.27^2\cdot 0.73\,\sqrt k\le 3.762\sqrt k$.
- $k<L\le 2k$. `Parking.kap_K3a` and `Parking.kap_at_k` give $L\,\kappa_L\le k\,\kappa_k\le 0.662/\sqrt k$, and $(L+1.27k)^2\le 5.35\,kL$ for $k\le L\le 2k$. Hence $T\le 5.35\cdot 0.662\sqrt k=3.5417\sqrt k$.
- $L>2k$. `Parking.kap_K3b` and `Parking.kap_at_k` give $(L-1)L\,\kappa_L\le 2k(k-1)\kappa_k\le 2\cdot 0.662\sqrt k$, and $n\le 1.635L-1$ gives $n(n-1)\le 2.675\,(L-1)L$. Hence $T\le 3.5417\sqrt k$.

*6. The arithmetic of (4).* $x\ge 0.3678$: by `Parking.xcrit_mul_psi`, $x(1+\frac1k)^{k-1}=1$, and $(1+\frac1k)^{k-1}\le e^{(k-1)/k}\le e$. $W\ge 2.01$: the sum $\sum_{j\le 8}c_jx^{j}$ is nondecreasing in $x$, and its value at the rational number $0.3678$ is computed exactly. $\sqrt k\ge 9.05$ since $9.05^2\le 82$. Therefore $B\le 2+\frac{1}{82}+\frac{1}{0.3678\cdot 2.01}\le 3.3652$, and $T\cdot B\le 3.762\cdot 3.3652\,\sqrt k\le 2\cdot 0.3678\,(2k-1)\le 2x(2k-1)$; the middle inequality is a quadratic inequality in $s=\sqrt k$ that holds for $s\ge 9.05$. The second condition of (4) holds with a large margin: $T\le 3.762\,k<0.3678\,k\,(2k-1)$. These verifications are routine.

This proves the row step, and with it the statement.
