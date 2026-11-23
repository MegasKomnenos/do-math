---
weight: unit
short: crossing criterion
---
## Description

The crossing criterion: for a column $k\ge2$ and $1\le R\le k-1$, two explicit inequalities in $k$ and $R$ (the kernel deficit $\bar\kappa_R$ is nonnegative, and a product of two explicit sums is smaller than a third) imply that $b(j,k)>b(j,k-1)$ in some row $j$ with $k<j\le k+R$.

## Statement

Let $k\ge2$ and $R$ be natural numbers with $1\le R\le k-1$, put $N=k+R$, and let $x=1/\gamma_k$ be the diagonal tilt of the column $k$ (`Parking.xk`). Let $\bar\kappa_R$ be the kernel deficit (`Parking.kbar`), $\mathsf e_{N-1}$ the tilt correction of the row $N-1$ (`Parking.ecor`), $\Sigma_\omega=\Sigma_\omega(k,R)$ the weighted sum of the flow factors (`Parking.Somg`), $S_R$ the sum `Parking.SR`, and $\mathsf E=\mathsf E(k,R)$ the accumulated tilt correction (`Parking.ecorSum`), all for the column $k$. Suppose that
$$\bar\kappa_R\ge0$$
and
$$\Bigl(\bar\kappa_R+\frac{x\,(R+1)}{N}\Bigr)\bigl(\mathsf e_{N-1}+\Sigma_\omega\bigr)<x\,\Bigl(\frac{R(R+1)}{N}-1-S_R-\mathsf E\Bigr).$$
Then there is a natural number $j$ with $k<j\le N$ and $d_{j,k}>0$, where $d_{j,k}=b(j,k)-b(j,k-1)$ and $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`).

## Explanation

**What the statement gives.** The step $d_{n,k}$ of the column $k$ is negative in the diagonal row $n=k$ (`Parking.dq_base`). The criterion bounds the row in which the column first becomes positive: it lies at most $R$ rows below the diagonal, provided $k$ and $R$ satisfy two inequalities between finite sums that involve only $k$ and $R$. No quantity of the parking problem remains in the hypotheses: the five sums are built from the tilt $x$, the numbers $\varepsilon_m=(m-1)^{m-1}/m!$ (`Parking.eps`), $a_n=n^{n-1}/n!$ (`Parking.cay`) and $\gamma_i=(1+1/i)^{i-2}$ (`Parking.gam`). The criterion is applied through its closed-form version `Parking.cross_of_bounds`, and then with $R$ of order $k^{2/3}$ in `Parking.crossing_strip`.

**Why it can be expected to hold.** Suppose the column $k$ is not positive in any of the rows $k+1,\dots,N$. Then the tilted profile $u_j=x^j\beta^{(k-1)}_j$ of the column $k-1$ (`Parking.profD`; $\beta^{(k-1)}_j=b(j,k-1)/j!$) is nondecreasing up to the row $N$; this is the reason for the choice of the tilt. The profile satisfies a linear equation in each row (the column equation `Parking.bq_L0`), whose source term is $\pi_nF_{n-1}$, where $\pi_n=x^na_n/n$ is the weight `Parking.pix` and $F_n$ is the proportion of parking functions of length $n$ with maximum displacement at most $k-1$. The proof uses this one equation twice. Read in the top row $N$, with every earlier value of the profile replaced by the largest value $u_N$, it bounds $u_N$ from above by a multiple of $\pi_NF_{N-1}$. Summed over the rows $k,\dots,N$, again with every value replaced by $u_N$, it bounds $u_N$ from below by a multiple of $\pi_NF_{N-1}$, up to a term that is controlled separately. The unknown sizes of $u_N$ and $F_{N-1}$ cancel when the two bounds are combined, and an inequality between explicit sums remains, which is the negation of the second hypothesis. So the criterion never estimates how large the counts of the column $k-1$ are. Besides the column equations it uses two comparisons along the diagonal, the lower bound `Parking.bq_diag_lower` and the monotonicity `Parking.zr_diag_mono`, and otherwise only the signs of the quantities involved.

**How to read the second hypothesis.** Its leading part is the comparison of $R(R+1)/N$ with $1+S_R$. The first comes from the product of the two bounds: the sum over the rows $k,\dots,N$ contributes their number $R+1$, and the top row contributes its coefficient, which is $x(R+1)/N$ up to the deficit $\bar\kappa_R$. The second is the truncated first moment of the kernel, $x(1+S_R)=x+\sum_{m\le R}m\kappa_m$ with $\kappa_m=x^m\varepsilon_m$ (`Parking.kapx`); it arises as the sum of the deficits $\bar\kappa_M$, $M\le R$, which are the coefficients of the summed equation. Since $S_R$ grows like $\sqrt{2R/\pi}$ (see `Parking.SR`) and $R(R+1)/N$ like $R^2/k$, the hypothesis can hold once $R^{3/2}$ exceeds a multiple of $k$. All other terms are corrections, and each has one identifiable source:

- $\mathsf e_{N-1}$ and $\mathsf E$ exist because the weights $\pi_n$ are not constant in $n$; the diagonal tilt makes the ratio $\pi_{n+1}/\pi_n=x\gamma_n$ equal to $1$ only at $n=k$.
- $\Sigma_\omega$ bounds the flow $J_i$ (defined in the proof below): the part of the decrease $F_{i-1}-F_i$ from one row to the next that is not accounted for by the proportion of parking functions of length $i-1$ with maximum displacement exactly $k-1$.
- The flow term is not proportional to $F_{N-1}$, so $F_{N-1}$ does not simply cancel, and bounds for the proportions themselves are needed. They all come from one inequality, the budget of Step 6: as long as the column $k$ is not positive, the proportions of parking functions with maximum displacement exactly $k-1$, summed over the rows $k,\dots,N-1$, are at most $\frac12$. The budget is used twice. It gives $1-F^-_{i-1}\le\frac12$, which is the factor $\frac12$ in the passage from the flow to $\Sigma_\omega$, and it gives $F_{N-1}\ge\frac12$, which settles the case distinction at the end of the proof; the two factors $\frac12$ cancel there. The budget is the only place where the column equation of the step of the column $k$ itself is used.

**The hypotheses.** $R\le k-1$ keeps all rows up to $N$ within $n\le2k-1$, the range in which the column equations `Parking.bq_L0` (for the column $k-1$) and `Parking.dq_col` hold. The hypothesis $\bar\kappa_R\ge0$ is used four times in the proof: it makes the factor $\Theta$ of the top row positive, it makes the coefficients of the summed equation of the step nonnegative (Step 6), it makes the coefficients of the summed equation of the profile nonnegative (Step 7), and it gives $x\le\frac12$. Because of the last point the criterion can only apply to columns with $x\le\frac12$, which means $k\ge8$.

**The Lean form.** The conclusion is `∃ j, k < j ∧ j ≤ k + R ∧ 0 < dq k j`, where `dq k j` is the normalised step $\delta_j=d_{j,k}/j!$ (`Parking.dq`); by `Parking.dq_pos_iff`, $\delta_j>0$ is the same as $b(j,k-1)<b(j,k)$. The hypothesis $R\le k-1$ is written with the subtraction of natural numbers, which is the ordinary one since $k\ge2$; the row $N-1$ is written `k + R - 1`.

## Proof

**Notation.** $k$, $R$, $N$, $x$ are as in the statement. We write $\beta^{(k-1)}_n=b(n,k-1)/n!$ (`Parking.bq`), $\delta_n=d_{n,k}/n!$ (`Parking.dq`), $z^{(y)}_n=A(n,y-1)/n!$ (`Parking.zr`), $c_n=(n+1)^{n-1}/n!$ (`Parking.cc`), $\gamma_n=(1+1/n)^{n-2}$ (`Parking.gam`), $\kappa_m=x^m\varepsilon_m$ (`Parking.kapx`), $\pi_n=x^na_n/n$ (`Parking.pix`), $\Pi_i=\sum_{n=k}^{i}\pi_n$ (`Parking.pixSum`), $u_n=x^n\beta^{(k-1)}_n$ (`Parking.profD`), $\eta_n=x^n\delta_n$ (`Parking.stepD`), and
$$F_n=\frac{z^{(k)}_n}{c_n},\qquad F^-_n=\frac{z^{(k-1)}_n}{c_n},\qquad P_n=\frac{\beta^{(k-1)}_n}{c_n},\qquad J_i=F_i-F^-_{i-1}\quad(i\ge1).$$
Since $c_n\,n!$ is the number of all parking functions of length $n$, the numbers $F_n$, $F^-_n$, $P_n$ are the proportions of parking functions of length $n$ with maximum displacement at most $k-1$, at most $k-2$, and exactly $k-1$. We also write
$$\Theta=\bar\kappa_R+\frac{x\,(R+1)}{N}.$$

**Organisation.** We assume that the conclusion fails,
$$\text{(N)}\qquad\delta_j\le0\quad\text{for all }k<j\le N,$$
and derive
$$(\mathrm K^{\ast})\qquad x\Bigl(\frac{R(R+1)}{N}-1-S_R-\mathsf E\Bigr)\le\Theta\,\bigl(\mathsf e_{N-1}+\Sigma_\omega\bigr),$$
which contradicts the second hypothesis. Step 1 writes the two column equations in tilted form. Step 2 shows that under (N) the profile is largest in the row $N$. Step 3 reads the equation of the row $N$ and gives an upper bound for $u_N$. Step 4 sums the equations of the rows $k,\dots,N$; this is an identity and uses no hypothesis on signs. Steps 5 and 6 bound the two quantities in that identity which are not multiples of the profile: the flow $J_i$ and the proportion $F_{N-1}$. Step 7 combines everything and evaluates the constants.

**Elementary facts.** (a) $F_n=F^-_n+P_n$, because $\beta^{(k-1)}_n=z^{(k)}_n-z^{(k-1)}_n$ (`Parking.bq_eq`). (b) $F_n=1$ for $n\le k$ and $F^-_n=1$ for $n\le k-1$, because $z^{(y)}_n=c_n$ for $n\le y$ (`Parking.zr_eq_cc`); consequently $P_n=0$ and $u_n=0$ for $n\le k-1$ (`Parking.bq_eq_zero`), and $J_k=F_k-F^-_{k-1}=0$. (c) $J_i\ge0$ for all $i\ge1$: this is the monotonicity along the diagonal `Parking.zr_diag_mono`, $z^{(k-1)}_{i-1}/c_{i-1}\le z^{(k)}_i/c_i$. (d) From (a), $F_n-F_{n+1}=P_n-J_{n+1}$. (e) $\pi_n>0$ for $n\ge1$ (`Parking.CrossCrit.pix_pos`), and $\pi_{n+1}=x\gamma_n\pi_n\ge\pi_n$ for $n\ge k$ (`Parking.CrossCrit.pix_succ`, `Parking.CrossCrit.one_le_xk_mul_gam`); so the weights are nondecreasing from the index $k$ on, and $\Pi_i\le(i-k+1)\pi_i$ for $i\ge k$. (f) $\kappa_m\ge0$ and $\kappa_1=x$, so the deficits $\bar\kappa_M$ are nonincreasing in $M$, with $\bar\kappa_0=1-x$ and $\bar\kappa_1=1-2x$. Since $R\ge1$ and $\bar\kappa_R\ge0$, this gives $\bar\kappa_M\ge0$ for all $M\le R$ and $x\le\frac12$.

**Step 1: the tilted column equations.** For $k\le n\le2k-1$,
$$u_n=\pi_n\,F_{n-1}+\frac{(k-1)\,x}{n}\,u_{n-1}+\sum_{m=1}^{n-k}\kappa_m\,u_{n-m}.\tag{1}$$
This is the column equation `Parking.bq_L0` of the column $k-1$, namely $\beta^{(k-1)}_n=z^{(k)}_{n-1}/n+\frac{k-1}{n}\beta^{(k-1)}_{n-1}+\sum_{m=1}^{n-k}\varepsilon_m\beta^{(k-1)}_{n-m}$, multiplied by $x^n$; in the convolution $x^n=x^m x^{n-m}$, and in the source term $x^nz^{(k)}_{n-1}/n=\pi_nF_{n-1}$ because $a_n=c_{n-1}$. For $n=k$ the equation reads $u_k=\pi_k$. In the same way the column equation of the step `Parking.dq_col`, $\delta_n=\frac{k+1}{n}\delta_{n-1}+\frac2n\beta^{(k-1)}_{n-1}+\sum_{m=1}^{n-k}\varepsilon_m\delta_{n-m}$, gives for $k+1\le n\le2k-1$
$$\eta_n=2\,\pi_n\,P_{n-1}+\frac{(k+1)\,x}{n}\,\eta_{n-1}+\sum_{m=1}^{n-k}\kappa_m\,\eta_{n-m},\tag{2}$$
and `Parking.dq_base`, $\delta_k=-a_k/k$, gives $\eta_k=-\pi_k$. All rows $n\le N$ are in the range of (1) and (2) because $N=k+R\le2k-1$.

**Step 2: under (N) the profile is largest in the row $N$.** Let $k\le n<N$. By (N), $\delta_{n+1}\le0$, that is $\beta^{(k)}_{n+1}\le\beta^{(k-1)}_{n+1}$. The diagonal lower bound `Parking.bq_diag_lower` gives $\gamma_k\beta^{(k-1)}_n\le\beta^{(k)}_{n+1}$. Since $x\gamma_k=1$ (`Parking.CrossCrit.xk_mul_gam`),
$$u_n=x^{n+1}\gamma_k\,\beta^{(k-1)}_n\le x^{n+1}\beta^{(k)}_{n+1}\le x^{n+1}\beta^{(k-1)}_{n+1}=u_{n+1}.$$
Together with $u_j=0\le u_N$ for $j\le k-1$ this shows $u_j\le u_N$ for every $j\le N$.

**Step 3: the top row.** In (1) with $n=N$ every value of $u$ on the right is at most $u_N$ by Step 2, and the coefficients are nonnegative. Hence $u_N\le\pi_NF_{N-1}+\bigl(\frac{(k-1)x}{N}+\sum_{m=1}^{R}\kappa_m\bigr)u_N$. Since $1-\frac{(k-1)x}{N}-\sum_{m=1}^{R}\kappa_m=\bar\kappa_R+x-\frac{(k-1)x}{N}=\Theta$,
$$u_N\,\Theta\le\pi_N\,F_{N-1}.\tag{3}$$
Moreover $\Theta>0$, because $\bar\kappa_R\ge0$ and $x(R+1)/N>0$.

**Step 4: the summed identity.** Without any hypothesis on signs,
$$F_{N-1}\,\Pi_N=u_N+u_{N-1}\Bigl(1-x-\frac{(k-1)x}{N}\Bigr)+\sum_{j=k}^{N-2}u_j\Bigl(\bar\kappa_{N-j}+\frac{x\,\mathsf e_j}{j+1}\Bigr)+\sum_{i=k}^{N-1}\Pi_i\,J_i.\tag{4}$$
To see this, add the equations (1) for $n=k,\dots,N$. On the right, the terms with $u_{n-1}$ are collected by $j=n-1$ and those of the convolution by $j=n-m$, where for a fixed $j$ the index $m$ runs from $1$ to $N-j$; $u_{k-1}=0$. This gives
$$\sum_{n=k}^{N}\pi_n\,F_{n-1}=u_N+\sum_{j=k}^{N-1}u_j\Bigl(1-\frac{(k-1)x}{j+1}-\sum_{m=1}^{N-j}\kappa_m\Bigr).$$
On the left, summation by parts (write $F_{n-1}=F_{N-1}+\sum_{i=n}^{N-1}(F_{i-1}-F_i)$ and count that $i$ occurs for $n=k,\dots,i$) and fact (d) give
$$\sum_{n=k}^{N}\pi_n\,F_{n-1}=F_{N-1}\,\Pi_N+\sum_{i=k}^{N-1}\Pi_i\,(P_{i-1}-J_i).$$
The terms with $P$ are multiples of the profile. Indeed $P_{k-1}=0$, and for $j\ge k$ the definitions give $\pi_{j+1}P_j=x^{j+1}\beta^{(k-1)}_j/(j+1)=x\,u_j/(j+1)$ (again by $a_{j+1}=c_j$) and $\Pi_{j+1}=\pi_{j+1}\,(j-k+2-\mathsf e_j)$, which is the definition of $\mathsf e_j$; so
$$\sum_{i=k}^{N-1}\Pi_i\,P_{i-1}=\sum_{j=k}^{N-2}u_j\cdot\frac{x\,(j-k+2-\mathsf e_j)}{j+1}.$$
Equating the two expressions for $\sum_n\pi_nF_{n-1}$ and collecting the coefficient of each $u_j$: for $k\le j\le N-2$ it is
$$1-\frac{(k-1)x}{j+1}-\sum_{m=1}^{N-j}\kappa_m-\frac{x\,(j-k+2)}{j+1}+\frac{x\,\mathsf e_j}{j+1}=\bar\kappa_{N-j}+\frac{x\,\mathsf e_j}{j+1},$$
since $(k-1)+(j-k+2)=j+1$; for $j=N-1$ it is $1-\frac{(k-1)x}{N}-\kappa_1=1-x-\frac{(k-1)x}{N}$. This is (4).

**Step 5: the flow bound.** For $k\le i\le N-1$,
$$J_i\le\omega_i\,(1-F^-_{i-1}),\qquad\omega_i=1-\frac{i}{(i+1)\,x\gamma_i}\ \text{(`Parking.omg`)}.\tag{5}$$
(The argument does not use the upper end of the range.)
First, $c_{i-1}-z^{(k-1)}_{i-1}=\sum_{s=0}^{i-k-1}\beta^{(k-1+s)}_{i-1}$ and $c_i-z^{(k)}_i=\sum_{s=0}^{i-k-1}\beta^{(k+s)}_i$: both are telescoping sums of `Parking.bq_eq`, which end at $z^{(i-1)}_{i-1}=c_{i-1}$ and $z^{(i)}_i=c_i$ (`Parking.zr_eq_cc`). The diagonal lower bound `Parking.bq_diag_lower` in the column $k+s$ gives $\gamma_{k+s}\beta^{(k-1+s)}_{i-1}\le\beta^{(k+s)}_i$, and $\gamma_k\le\gamma_{k+s}$ (`Parking.gam_mono`). Summing over $s$,
$$\gamma_k\,\bigl(c_{i-1}-z^{(k-1)}_{i-1}\bigr)\le c_i-z^{(k)}_i .$$
Now $J_i=(1-F^-_{i-1})-(1-F_i)$, where $1-F^-_{i-1}=(c_{i-1}-z^{(k-1)}_{i-1})/c_{i-1}$ and $1-F_i=(c_i-z^{(k)}_i)/c_i\ge\gamma_k\,(c_{i-1}-z^{(k-1)}_{i-1})/c_i$. Since $c_i=\gamma_i\,\frac{i+1}{i}\,c_{i-1}$ (from `Parking.cay_ratio`, as in `Parking.CrossCrit.pix_succ`) and $\gamma_k=1/x$, the last quantity is $\frac{i}{(i+1)x\gamma_i}\,(1-F^-_{i-1})$, and (5) follows.

**Step 6: the budget.** Under (N) and $\bar\kappa_R\ge0$,
$$\sum_{j=k}^{N-1}P_j\le\frac12.\tag{6}$$
Add the equations (2) for $n=k+1,\dots,N$ and rearrange as in Step 4:
$$2\sum_{n=k+1}^{N}\pi_n\,P_{n-1}=\eta_N-\eta_k+\sum_{i=k}^{N-1}\eta_i\Bigl(1-\frac{(k+1)\,x}{i+1}-\sum_{m=1}^{N-i}\kappa_m\Bigr).$$
For $k\le i\le N-1$ the coefficient in the last sum is at least $1-x-\sum_{m=1}^{R}\kappa_m=\bar\kappa_R\ge0$, because $(k+1)/(i+1)\le1$ and $N-i\le R$. The values $\eta_i$, $k\le i\le N$, are nonpositive: $\eta_k=-\pi_k<0$, and the others by (N). So the sum is $\le0$ and $\eta_N\le0$, whence $2\sum_{n=k+1}^{N}\pi_nP_{n-1}\le-\eta_k=\pi_k$. Finally $\pi_n\ge\pi_k$ for $n\ge k$ by (e) and $P\ge0$, so $2\pi_k\sum_{j=k}^{N-1}P_j\le\pi_k$, which is (6).

Two consequences. By (d) and (c), $F_n-F_{n+1}\le P_n$, and $F_k=1$; hence $1-F_n\le\sum_{j=k}^{n-1}P_j$ for $n\ge k$. With (6) this gives
$$F_{N-1}\ge\frac12,\qquad 1-F^-_n=1-F_n+P_n\le\sum_{j=k}^{n}P_j\le\frac12\quad(k\le n\le N-1).\tag{7}$$

**Step 7: combination.** *The profile terms of (4).* The coefficients of $u_{N-1}$ and of $u_j$, $k\le j\le N-2$, in (4) are nonnegative: $1-x-\frac{(k-1)x}{N}\ge1-2x\ge0$ by (f), and $\bar\kappa_{N-j}\ge0$ by (f) together with $\mathsf e_j\ge0$ (`Parking.CrossCrit.ecor_nonneg`). So Step 2 allows us to replace every $u_j$ by $u_N$, and the profile terms of (4) are at most $u_N\,C$ with
$$C=1+\Bigl(1-x-\frac{(k-1)x}{N}\Bigr)+\sum_{M=2}^{R}\bar\kappa_M+x\,\mathsf E\ \ge0 .$$
*The flow term of (4).* The term $i=k$ vanishes by (b). For $k<i<N$ we have $\omega_i\ge0$, because $x\gamma_i\ge1$ (`Parking.CrossCrit.one_le_xk_mul_gam`); so (5) and (7) give $0\le J_i\le\omega_i/2$, and (e) gives $\Pi_i\le(i-k+1)\pi_i\le(i-k+1)\pi_N$. Hence $\sum_{i=k}^{N-1}\Pi_iJ_i\le\frac{\pi_N}{2}\,\Sigma_\omega$. Altogether
$$F_{N-1}\,\Pi_N\le u_N\,C+\frac{\pi_N}{2}\,\Sigma_\omega .\tag{8}$$
*Elimination of $u_N$ and $F_{N-1}$.* By the definition of $\mathsf e_{N-1}$, $\Pi_N=\pi_N\,(R+1-\mathsf e_{N-1})$. Multiply (8) by $\Theta>0$ and use (3) in the form $u_N\Theta\,C\le\pi_NF_{N-1}C$ (here $C\ge0$); after division by $\pi_N>0$,
$$F_{N-1}\,\bigl[(R+1-\mathsf e_{N-1})\,\Theta-C\bigr]\le\frac{\Theta\,\Sigma_\omega}{2}.$$
If the bracket is $\le0$, then it is $\le\Theta\Sigma_\omega$ because $\Theta\Sigma_\omega\ge0$ (`Parking.CrossCrit.Somg_nonneg`). If it is positive, then $F_{N-1}\ge\frac12$ from (7) gives $\frac12[\dots]\le\frac12\Theta\Sigma_\omega$. In both cases
$$(R+1)\,\Theta-C\le\Theta\,\bigl(\mathsf e_{N-1}+\Sigma_\omega\bigr).\tag{9}$$
*The constants.* It remains to evaluate $(R+1)\Theta-C$. The deficits satisfy $\sum_{M=0}^{R}\bar\kappa_M=(R+1)\bar\kappa_R+x\,S_R$: indeed $\sum_{M=0}^{R}(\bar\kappa_M-\bar\kappa_R)=\sum_{m=1}^{R}m\,\kappa_m$, and $m\,\kappa_m=x\,((m-1)x)^{m-1}/(m-1)!$ by `Parking.mul_eps`, so that $\sum_{m=1}^{R}m\kappa_m=x\,S_R$. Removing $\bar\kappa_0=1-x$ and $\bar\kappa_1=1-2x$ gives $\sum_{M=2}^{R}\bar\kappa_M=(R+1)\bar\kappa_R+xS_R-2+3x$, hence
$$C=(R+1)\,\bar\kappa_R+x\,S_R+2x-\frac{(k-1)\,x}{N}+x\,\mathsf E,$$
and, with $(R+1)^2+(k-1)-2N=R(R+1)-N$,
$$(R+1)\,\Theta-C=\frac{x\,(R+1)^2}{N}-x\,S_R-2x+\frac{(k-1)\,x}{N}-x\,\mathsf E=x\Bigl(\frac{R(R+1)}{N}-1-S_R-\mathsf E\Bigr).$$
Inserted into (9) this is $(\mathrm K^{\ast})$, which contradicts the second hypothesis. Hence (N) is false: some $j$ with $k<j\le N$ has $\delta_j>0$, that is $d_{j,k}>0$.

**Where the argument is sensitive.** Steps 1 and 4 are exact identities; their difficulty is bookkeeping, and the point to check is that the coefficient of $u_j$ in (4) simplifies to $\bar\kappa_{N-j}+x\mathsf e_j/(j+1)$. The inequalities are all of one kind: a quantity is replaced by a bound that has the right sign. The steps at which a sign could fail are the nonnegativity of the coefficients in Steps 6 and 7, which is where $\bar\kappa_R\ge0$ enters, and the last step, in which the factor $F_{N-1}$ has to be removed from the left side; this is why the budget (6), and with it the lower bound $F_{N-1}\ge\frac12$, is needed.
