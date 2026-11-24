---
weight: unit
short: the steps of the columns k ≥ 82 beyond the first layer are positive
---
## Description

For every column $k\ge82$ and every row $n\ge2k$: $b(n,k-1)<b(n,k)$, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k\ge82$ and $n\ge2k$ be natural numbers. Then $b(n,k-1)<b(n,k)$.

## Explanation

**Its place.** Write $d_{n,k}=b(n,k)-b(n,k-1)$ for the step of the column $k$ in the row $n$. The rows $k+1\le n\le2k-1$ are the *first layer* of the column $k$ (some records call them the chain range of the column), and the rows $n\ge2k$ lie beyond it. The statement says that in a column $k\ge82$ every step beyond the first layer is positive. It is used in one place. `Parking.step_pos_beyond` gives the sign of the steps beyond the first layer in all the columns $k\ge1$, with eleven exceptions that lie in the columns $k\le7$, and the present statement is its source for the columns $k\ge82$.

The rows from $k$ to $2k-1$ of such a column are described by `Parking.one_sign_change`: there is a row $q$ with $k+1\le q\le k+27k/100$ such that the step is not positive in the rows $k\le j<q$ and positive in the rows $q\le j\le2k-1$. The present statement continues the positive sign to all the later rows, by induction on the row. The bound $82$ is the column from which `Parking.one_sign_change` is available, and the estimates of the induction step close from the same column on.

**The difficulty.** Fix the critical tilt $x=x_k=(k/(k+1))^{k-1}$ and write $\eta_j=x^j\,d_{j,k}/j!$ for the tilted step of the column in the row $j$, $U_j=x^j\,b(j,k-1)/j!$ for the tilted count of the column $k-1$, and $\kappa_m$ for the tilted prime kernel of the threshold $k$; the proof below gives the definitions. The column inequality on all rows (`Parking.col_eq_all`) gives
$$n\,\eta_n\ \ge\ (k+1)\,x\,\eta_{n-1}+2x\,U_{n-1}+n\sum_{j=k}^{n-1}\kappa_{n-j}\,\eta_j .$$
The first two terms on the right are a positive source. The sum is the feedback of the earlier rows, and it contains the rows $k\le j<q$ above the first positive row, where $\eta_j\le0$. These terms never disappear: every later row $n$ receives them, with the kernel weights $\kappa_{n-j}$. Nothing is known about the size of the single $\eta_j$ in those rows, so the negative part of the feedback cannot be bounded term by term.

**The idea.** Two facts are available. The first is the pattern of the signs: not positive up to the row $q-1$, positive from the row $q$ on. The second is a lower bound for one particular weighted sum of the $\eta_j$. With the weight $\Psi'(j)=\max(j,2k-1)$, the sum $\sum_{j=k}^{J}\Psi'(j)\,\eta_j$ is at least minus a quantity made of terms of the last two rows, the weighted debt (`Parking.weighted_debt`); this comes from a convexity of the tilted environments along the diagonal and uses no information on where the sign changes. What joins the two facts is a statement on the order of the kernel weights. With $L=n-q+1$ and $\theta=\kappa_L/(2k-1)$,
$$\frac{\kappa_{n-j}}{\Psi'(j)}\le\theta\quad(j<q),\qquad\frac{\kappa_{n-j}}{\Psi'(j)}\ge\theta\quad(q\le j\le n-1)$$
(`Parking.order_neg`, `Parking.order_pos`). In the rows $j<q$, where the ratio is at most $\theta$, the step $\eta_j$ is not positive, and in the rows $j\ge q$, where the ratio is at least $\theta$, it is positive. So $\kappa_{n-j}\,\eta_j\ge\theta\,\Psi'(j)\,\eta_j$ in every row, and the feedback is at least $-\theta$ times the weighted debt. The debt consists of quantities of the rows $n-1$ and $n-2$, which are comparable with the source, and $\theta$ is small: $n(n-1)\,\kappa_L$ is of the order $\sqrt k$, against a coefficient of the source of the order $k$.

The bound $100(q-k)\le27k$ on the row $q$ enters here. It puts the row $q$ at a distance of at least $73k/100$ from every row $n\ge2k$, and both the order of the kernel weights and the bound for $\kappa_L$ use that distance.

The weight $\Psi'$ has to serve both facts at once: the weighted second differences of the tilted environments along the diagonal must be nonnegative, and the kernel must be ordered against the weight at the row $q$. The record of `Parking.PsiW` explains why $\max(N,2k-1)$ does both, and why neither the weight $N$ on all rows nor a constant weight would.

**The numerical margin.** The constants of the proof leave little room at the first column. At $k=82$ the decisive inequality of the induction step reads $12.66\sqrt k\le0.7356\,(2k-1)$, which is about $114.6\le119.9$.

**The Lean form.** The statement is `(k n : ℕ) (hk : 82 ≤ k) (hn : 2 * k ≤ n) : b n (k - 1) < b n k`. The sign of the step is a comparison of natural numbers, and `k - 1` is the ordinary difference. The proof works with the real number $d_{n,k}/n!$ (`Parking.dq`) and passes to the counts by `Parking.dq_pos_iff`.

## Proof

**Notation.** Throughout, $k\ge82$ is fixed and

- $x=x_k=(k/(k+1))^{k-1}$ is the critical tilt (`Parking.xcrit`); $x>0$ (`Parking.xcrit_pos`);
- $\delta_j=d_{j,k}/j!$ is the normalised step of the column $k$ in the row $j$ (`Parking.dq`), and $\eta_j=\delta_j\,x^j$;
- $z^{(y)}_N=A(N,y-1)/N!$, where $A(N,l)$ is the number of parking functions of length $N$ with maximum displacement at most $l$ (`Parking.zr`, `Parking.A`); $u_N=z^{(k)}_N\,x^N$ and $u^-_N=z^{(k-1)}_N\,x^N$ are the tilted environments of the thresholds $k$ and $k-1$ (`Parking.zrT`), with $0\le u^-_N\le u_N$ (`Parking.zrT_nonneg`, `Parking.zrT_le_zrT`);
- $U_N=u_N-u^-_N$ (`Parking.Ut`), which equals $\beta^{(k-1)}_N\,x^N$ with $\beta^{(\ell)}_N=b(N,\ell)/N!$ (`Parking.Ut_eq_bq`, `Parking.bq`), so that $U_N\ge0$ (`Parking.bq_nonneg`);
- $\kappa_m=\kappa^{(k)}_m\,x^m$ is the tilted prime kernel of the threshold $k$ (`Parking.kqT`), where $\kappa^{(k)}_m$ is the coefficient of $X^m$ in $1-1/Z_k$ and $Z_k=\sum_n z^{(k)}_nX^n$ (`Parking.kq`); $\kappa_m\ge0$ (`Parking.kqT_nonneg`);
- $\omega_j=c_j\,x^j$ with $c_j=(j+1)^{j-1}/j!$ (`Parking.ccT`, `Parking.cc`);
- $\Psi'(N)=\max(N,2k-1)$ (`Parking.PsiW`).

By `Parking.dq_pos_iff` the claim is $\delta_n>0$.

**Reduction to a row step.** `Parking.one_sign_change` gives a row $q$ with $k+1\le q$ and $100\,(q-k)\le27\,k$ such that $\delta_j\le0$ for $k\le j<q$ and $\delta_m>0$ for $q\le m\le2k-1$. We show $\delta_m>0$ for every $m\ge q$, by strong induction on $m$. For $m\le2k-1$ this is given. For $m\ge2k$ it is the row step below, applied to the row $m$; the hypothesis of the row step on the rows $q\le j\le m-1$ is the induction hypothesis. The row $n$ of the statement is one of the rows $m\ge q$, because $q\le k+27k/100<2k\le n$.

**The row step.** Let $q$ be a row with $k+1\le q$ and $100\,(q-k)\le27\,k$, and let $n\ge2k$. Suppose that $\delta_j\le0$ for $k\le j<q$ and $\delta_j>0$ for $q\le j\le n-1$. Then $\delta_n>0$.

In the Lean source the row step is a private lemma, and the facts established in the parts 1 and 3 to 6 below are private lemmas that it uses; their arguments are given here in full.

Put $L=n-q+1$, $\theta=\kappa_L/(2k-1)\ge0$ and $T=n(n-1)\,\kappa_L$, so that $n(n-1)\,\theta=T/(2k-1)$. Since $q<2k\le n$, the row $n-1$ is one of the rows $q\le j\le n-1$, and so $\eta_{n-1}>0$.

*1. The tilted column inequality.* `Parking.col_eq_all` states, for $k\ge2$ and $n\ge k+1$,
$$(k+1)\,\delta_{n-1}+2\,\beta^{(k-1)}_{n-1}\ \le\ n\Bigl(\delta_n-\sum_{m=1}^{n-k}\kappa^{(k)}_m\,\delta_{n-m}\Bigr).$$
Multiply by $x^n$ and index the sum by the row $j=n-m$. Since $\kappa^{(k)}_m\,\delta_{n-m}\,x^n=\kappa_m\,\eta_{n-m}$ and $\beta^{(k-1)}_{n-1}\,x^{n-1}=U_{n-1}$, this gives
$$(k+1)\,x\,\eta_{n-1}+2x\,U_{n-1}\ \le\ n\,(\eta_n-S),\qquad S=\sum_{j=k}^{n-1}\kappa_{n-j}\,\eta_j .\tag{1}$$

*2. The order of the kernel weights and the weighted debt.* For $k\le j<q$, `Parking.order_neg` gives $\kappa_{n-j}\,(2k-1)\le\kappa_L\,\Psi'(j)$, that is, $\kappa_{n-j}\le\theta\,\Psi'(j)$, and $\eta_j\le0$. For $q\le j\le n-1$, `Parking.order_pos` gives $\kappa_L\,\Psi'(j)\le\kappa_{n-j}\,(2k-1)$, that is, $\kappa_{n-j}\ge\theta\,\Psi'(j)$, and $\eta_j>0$. In both cases $\kappa_{n-j}\,\eta_j\ge\theta\,\Psi'(j)\,\eta_j$. Summing over $j$ and applying `Parking.weighted_debt`, which states for $k\ge7$ and $J\ge k$ that $\sum_{j=k}^{J}\Psi'(j)\,\eta_j\ge-\bigl(\Psi'(J)\,U_J+\Psi'(J-1)\,U_{J-1}+(\Psi'(J)-\Psi'(J-1))\,u_J\bigr)$, with $J=n-1$:
$$S\ \ge\ \theta\sum_{j=k}^{n-1}\Psi'(j)\,\eta_j\ \ge\ -\theta\,\mathfrak D,\qquad\mathfrak D=\Psi'(n-1)\,U_{n-1}+\Psi'(n-2)\,U_{n-2}+\bigl(\Psi'(n-1)-\Psi'(n-2)\bigr)\,u_{n-1}.\tag{2}$$
Since $n-1\ge2k-1$, $\Psi'(n-1)=n-1$ (`Parking.PsiW_of_ge`), and $n-2\le\Psi'(n-2)\le n-1$ (`Parking.PsiW_ge_self`, `Parking.PsiW_mono`). As $U_{n-2}\ge0$ and $u_{n-1}\ge0$, it follows that $\mathfrak D\le(n-1)\,(U_{n-1}+U_{n-2})+u_{n-1}$.

*3. The debt in terms of $U_{n-1}$ and $\eta_{n-1}$.* Two bounds are used.

(a) `Parking.Ut_diag_lower` states, for $k\ge2$ and a row $N\ge1$, that $k\,U_{N-1}\le(k+1)\,U^+_N$, where $U^+_N=z^{(k+1)}_N\,x^N-z^{(k)}_N\,x^N$. By `Parking.Ut_eq_bq`, applied to the columns $k+1$ and $k$, $U^+_N=\beta^{(k)}_N\,x^N$ and $U_N=\beta^{(k-1)}_N\,x^N$, so $U^+_N-U_N=\delta_N\,x^N=\eta_N$. With $N=n-1$ this gives $U_{n-2}\le\bigl(1+\tfrac1k\bigr)\,(U_{n-1}+\eta_{n-1})$.

(b) *The tilted count of the column $k-1$ dominates the environment:* $x\,W\,u_{n-1}\le(n-1)\,U_{n-1}$ with $W=\sum_{j=0}^{8}\omega_j$. This is a case of the following fact, in which $u$, $u^-$, $U$ and $\omega$ may be formed with any tilt $x\ge0$ in the place of $x_k$. Let $k\ge2$, suppose that $u_N$ does not increase in $N$, and let $J\le k-1$ and $M\ge k-1+J$. Then
$$x\,\Bigl(\sum_{j=0}^{J}\omega_j\Bigr)\,u_M\ \le\ (M+1)\,U_{M+1}.$$
To see this, subtract the tilted last-car recursions (`Parking.zrT_succ`: $(N+1)\,u_{N+1}=x\sum_{i=0}^{N}\min(i+1,k)\,u_i\,u_{N-i}$, and the same with $k-1$ and $u^-$ in the place of $k$ and $u$) of the thresholds $k$ and $k-1$ at the size $M+1$:
$$(M+1)\,U_{M+1}=x\sum_{i=0}^{M}F_i,\qquad F_i=\min(i+1,k)\,u_i\,u_{M-i}-\min(i+1,k-1)\,u^-_i\,u^-_{M-i}.$$
Every $F_i$ is nonnegative, because $0\le u^-\le u$ and $\min(i+1,k-1)\le\min(i+1,k)$. For $i=M-j$ with $j\le J$ one has $i+1\ge k$, so
$$F_{M-j}=k\,u_{M-j}\,u_j-(k-1)\,u^-_{M-j}\,u^-_j\ \ge\ u_{M-j}\,u_j\ \ge\ u_M\,\omega_j,$$
where the last step uses $u_j=\omega_j$ for $j\le k$ (`Parking.zrT_eq_ccT`) and $u_{M-j}\ge u_M$. Keeping only these $J+1$ terms of the sum gives the fact. It is applied with $J=8$ and $M=n-2$, which is allowed because $8\le k-1$ and $n-2\ge k+7$. The monotonicity of $u$ at the critical tilt is `Parking.zrT_anti_crit`, and it also gives $u_{n-1}\le u_{n-2}$.

With (a) and (b), and with $B=2+\frac1k+\frac1{xW}$,
$$\mathfrak D\ \le\ (n-1)\Bigl(B\,U_{n-1}+\bigl(1+\tfrac1k\bigr)\,\eta_{n-1}\Bigr).\tag{3}$$

*4. Combination.* From (1), (2), (3) and $n(n-1)\,\theta=T/(2k-1)$,
$$n\,\eta_n\ \ge\ U_{n-1}\Bigl(2x-\frac{T}{2k-1}\,B\Bigr)+\eta_{n-1}\,(k+1)\Bigl(x-\frac{T}{(2k-1)\,k}\Bigr).$$
Here $U_{n-1}\ge0$ and $\eta_{n-1}>0$. So $\eta_n>0$, and with it $\delta_n>0$, as soon as
$$T\cdot B\le2x\,(2k-1)\qquad\text{and}\qquad T<x\,k\,(2k-1).\tag{4}$$

*5. The size of the kernel weight:* $T=n(n-1)\,\kappa_L\le3.762\,\sqrt k$. Note that $n=L+q-1\le L+1.27\,k-1$. There are three cases.

- $L\le k$. Then $100\,(L-1)=100\,(n-q)\ge73\,k$, so $\kappa_L\le0.73/(k\sqrt k)$ by `Parking.kap_far`, and $n\le2.27\,k$. Hence $T\le n^2\,\kappa_L\le2.27^2\cdot0.73\,\sqrt k\le3.762\,\sqrt k$.
- $k<L\le2k$. `Parking.kap_K3a` ($L\,\kappa_L\le k\,\kappa_k$ for $L\ge k$) and `Parking.kap_at_k` ($\kappa_k\le0.662/(k\sqrt k)$) give $L\,\kappa_L\le0.662/\sqrt k$, and $(L+1.27\,k)^2\le5.35\,k\,L$ for $k\le L\le2k$. Hence $T\le n^2\,\kappa_L\le5.35\cdot0.662\,\sqrt k=3.5417\,\sqrt k$.
- $L>2k$. `Parking.kap_K3b` ($(L-1)\,L\,\kappa_L\le2k(k-1)\,\kappa_k$ for $L\ge2k-1$) and `Parking.kap_at_k` give $(L-1)\,L\,\kappa_L\le2\cdot0.662\,\sqrt k$. From $q\le1.27\,k$ and $2k\le L-1$ one gets $n\le1.635\,L-1$, and then $n(n-1)\le2.675\,(L-1)\,L$. Hence $T\le2.675\cdot2\cdot0.662\,\sqrt k=3.5417\,\sqrt k$.

*6. The arithmetic of (4).* First, $x\ge0.3678$: by `Parking.xcrit_mul_psi`, $x\,(1+\frac1k)^{k-1}=1$, and $(1+\frac1k)^{k-1}\le e^{(k-1)/k}\le e$. Second, $W\ge2.01$: every $c_j$ is positive (`Parking.cc_pos`), so the sum $\sum_{j=0}^{8}c_j\,x^j$ does not decrease in $x\ge0$, and its value at the rational number $0.3678$, computed exactly from $c_j=(j+1)^j/(j+1)!$ (`Parking.cc_eq`), is at least $2.01$. Third, $\sqrt k\ge9.05$, since $9.05^2\le82$. Therefore $B\le2+\frac1{82}+\frac1{0.3678\cdot2.01}\le3.3652$, and
$$T\cdot B\ \le\ 3.762\cdot3.3652\,\sqrt k\ \le\ 2\cdot0.3678\,(2k-1)\ \le\ 2x\,(2k-1);$$
the middle inequality is a quadratic inequality in $s=\sqrt k$ that holds for $s\ge9.05$. The second condition of (4) holds with a large margin: $T\le3.762\,k<0.3678\,k\,(2k-1)\le x\,k\,(2k-1)$. These verifications are routine.

This proves the row step, and with it the statement.
