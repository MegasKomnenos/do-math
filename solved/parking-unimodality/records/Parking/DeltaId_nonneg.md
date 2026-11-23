---
weight: unit
short: weighted diagonal convexity beyond the first layer
---
## Description

For $k\ge 7$ and every size $N\ge 2k-1$, at the critical tilt $x_k$: $(N+1)\,u^{(k+1)}_{N+1}-2N\,u^{(k)}_N+(N-1)\,u^{(k-1)}_{N-1}\ge 0$, where $u^{(y)}_M=z^{(y)}_Mx_k^{\,M}$ is the tilted environment of the threshold $y$.

## Statement

Let $k\ge 7$ and $N\ge 2k-1$ be natural numbers. Let $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`) and $u^{(y)}_M=z^{(y)}_M\,x_k^{\,M}$ with $z^{(y)}_M=A(M,y-1)/M!$, the number of parking functions of length $M$ with all displacements smaller than $y$, divided by $M!$ (`Parking.zrT y (xcrit k) M`). Then
$$\Delta_{\mathrm{id}}(N):=(N+1)\,u^{(k+1)}_{N+1}-2N\,u^{(k)}_N+(N-1)\,u^{(k-1)}_{N-1}\ \ge\ 0 .$$

## Explanation

$\Delta_{\mathrm{id}}(N)$ is the second difference along the diagonal of the sequence "size times tilted mass". With $\mathrm{DC}(N)=u^{(k+1)}_{N+1}-2u^{(k)}_N+u^{(k-1)}_{N-1}$ and $e_N=u^{(k+1)}_{N+1}-u^{(k-1)}_{N-1}\ge 0$ it equals $N\cdot\mathrm{DC}(N)+e_N$, so it is weaker than the plain convexity $\mathrm{DC}(N)\ge 0$. The plain convexity is proved only in the first layer (`Parking.FirstLayer.zrT_diag_convex`, sizes $k\le N\le 2k-2$); the present statement is what the library proves for all larger sizes, and together the two give the convexity with the weight $\Psi'(N)=\max(N,2k-1)$ on all sizes (`Parking.DeltaPsi_nonneg`).

The weight $N$ is the one the last-car recursion produces: the recursion gives $(N+1)$ times the tilted mass of the size $N+1$ as $x_k$ times a weighted convolution of the masses of smaller sizes. So $\Delta_{\mathrm{id}}(N)/x_k$ is a combination of three convolutions, for the thresholds $k+1$, $k$, $k-1$, and the proof shows that this combination is a sum of nonnegative pieces. The pieces in which one factor is a free mass of a size at most $k-2$ are weighted second differences at smaller sizes, of the form $(c+1)u^{(k+1)}_{M+1}-2c\,u^{(k)}_M+(c-1)u^{(k-1)}_{M-1}$ with $k+1\le c\le 2k-1$. For $M$ in the first layer these are nonnegative by `Parking.FirstLayer.zrT_weak_requirement`, which is where the first layer and the hypothesis $k\ge 7$ enter; for larger $M$ they follow from the statement itself at the size $M$, which makes the proof an induction on $N$. The remaining pieces, in which both factors have size at least $k-1$, are controlled by the diagonal lower bound `Parking.Ut_diag_lower`.

The Lean statement is written with $N=M+1$: for every $M$ with $2k-1\le M+1$, $(M+2)\,u^{(k+1)}_{M+2}-2(M+1)\,u^{(k)}_{M+1}+M\,u^{(k-1)}_M\ge 0$.

## Proof

Abbreviate $u^{+}_i=u^{(k+1)}_i$, $u_i=u^{(k)}_i$, $u^{-}_i=u^{(k-1)}_i$, $x=x_k$, $\omega_i=c_ix^{i}$ with $c_i=(i+1)^{i-1}/i!$ (`Parking.ccT`), $U_i=u_i-u^{-}_i$ and $U^{+}_i=u^{+}_i-u_i$. The following facts are used.

- (F1) $0\le u^{-}_i\le u_i\le u^{+}_i$ for all $i$ (`Parking.zrT_nonneg`, `Parking.zrT_le_zrT`); hence $U_i,U^{+}_i\ge 0$.
- (F2) $u^{-}_i=u_i=u^{+}_i=\omega_i$ for $i\le k-1$ (`Parking.zrT_eq_ccT`).
- (F3) Diagonal monotonicity at the critical tilt: $u_i\le u^{+}_{i+1}$ and $u^{-}_i\le u_{i+1}$ for $i\ge k-1$. More generally $u^{(y)}_i\le u^{(y+1)}_{i+1}$ for $y\ge 1$ and $i+1\ge k$: `Parking.zr_diag_mono` gives $z^{(y)}_i/c_i\le z^{(y+1)}_{i+1}/c_{i+1}$, and `Parking.ccT_le_succ` gives $\omega_i\le\omega_{i+1}$ for $i+1\ge k$; multiply the two.
- (F4) $k\,U_j\le(k+1)\,U^{+}_{j+1}$ for all $j\ge 0$ (`Parking.Ut_diag_lower`).
- (F5) $(k-1)\,\omega_{k-2}\le k\,\omega_{k-1}$. Indeed `Parking.ccT_succ` gives $\omega_{k-1}=x\,(1+\frac{1}{k-1})^{k-2}\omega_{k-2}$, so $k\,\omega_{k-1}=(k-1)\,x\,(1+\frac{1}{k-1})^{k-1}\,\omega_{k-2}$, and $x\,(1+\frac{1}{k-1})^{k-1}\ge x\,(1+\frac1k)^{k-1}=1$ by `Parking.xcrit_mul_psi`.
- (F6) $\omega_k\ge\omega_{k-1}$ and $\omega_{k-2}\ge\omega_{k-1}$ (`Parking.ccT_le_succ`, `Parking.ccT_succ_le`).

The proof is by strong induction on $N\ge 2k-1$. Write $N=2k-1+r$ with $r\ge 0$.

**Step 1: weighted second differences at smaller sizes.** For a size $M$ and a real $c$ put $W_c(M)=(c+1)u^{+}_{M+1}-2c\,u_M+(c-1)u^{-}_{M-1}$. Then $W_c(M)\ge 0$ for all $k\le M\le N-1$ and all real $k\le c\le 2k-1$. If $M\le 2k-2$ this is `Parking.FirstLayer.zrT_weak_requirement`. If $2k-1\le M\le N-1$, the induction hypothesis gives $\Delta_{\mathrm{id}}(M)\ge 0$, and
$$M\cdot W_c(M)=c\cdot\Delta_{\mathrm{id}}(M)+(M-c)\big(u^{+}_{M+1}-u^{-}_{M-1}\big),$$
where $M-c\ge 0$ and $u^{-}_{M-1}\le u_M\le u^{+}_{M+1}$ by (F3). Moreover $W_k(k-1)=(k+1)\omega_k-2k\,\omega_{k-1}+(k-1)\omega_{k-2}\ge 0$ by (F2) and (F6).

**Step 2: the three recursions.** `Parking.zrT_succ` for the thresholds $k+1$, $k$, $k-1$ gives
$$(N+1)u^{+}_{N+1}=x\sum_{i=0}^{N}\min(i+1,k+1)\,u^{+}_iu^{+}_{N-i},\quad N u_N=x\sum_{i=0}^{N-1}\min(i+1,k)\,u_iu_{N-1-i},\quad (N-1)u^{-}_{N-1}=x\sum_{i=0}^{N-2}\min(i+1,k-1)\,u^{-}_iu^{-}_{N-2-i}.$$
So $\Delta_{\mathrm{id}}(N)=x\,(\Sigma^{+}-2\Sigma^{0}+\Sigma^{-})$ with the three sums on the right, and it suffices to show $\Sigma^{+}-2\Sigma^{0}+\Sigma^{-}\ge 0$.

**Step 3: one split of each convolution.** In each sum separate the terms in which the first index is at most $k-2$, the terms in which the second index is at most $k-2$, and the terms in which both are at least $k-1$. Because $N\ge 2k-1$ these three sets are disjoint. An index $\ell\le k-2$ belongs to a free mass $\omega_\ell$, the same for the three thresholds (F2). In a term with first index $\ell$ the weight is $\ell+1$; in the term with second index $\ell$ the first index is so large that the weight is the full threshold $y\in\{k+1,k,k-1\}$. Together the two give the weight $\ell+1+y$. Therefore
$$\Sigma^{+}-2\Sigma^{0}+\Sigma^{-}=\underbrace{\sum_{\ell=0}^{k-2}\omega_\ell\;W_{\ell+k+1}(N-1-\ell)}_{\text{outer part}}\;+\;\text{middle part},$$
and the middle part, sorted by the second index $m_t=N-k-t$, $t=0,\dots,r$, is
$$\sum_{t=0}^{r}\Big((k+1)\,u^{+}_{k+t}u^{+}_{m_t}-2k\,u_{k-1+t}u_{m_t}+(k-1)\,u^{-}_{k-2+t}u^{-}_{m_t}\Big)+k\,\omega_{k-1}u^{+}_{N-k+1}-(k-1)\,\omega_{k-2}u^{-}_{N-k}.$$
The two boundary terms arise as follows: in $\Sigma^{+}$ the term with first index $k-1$ has the weight $k$, not $k+1$, and is written separately; in $\Sigma^{-}$ the middle terms have first indices $k-1,\dots,N-k-1$, and the term $t=0$ of the displayed sum, $(k-1)u^{-}_{k-2}u^{-}_{N-k}$, has been added and is subtracted again.

**Step 4: the outer part.** Each $W_{\ell+k+1}(N-1-\ell)$ has a weight $c=\ell+k+1\in[k+1,2k-1]$ and a size $N-1-\ell\in[N-k+1,N-1]\subseteq[k,N-1]$, so it is nonnegative by Step 1, and $\omega_\ell>0$.

**Step 5: the middle part.** For $0\le t\le r$ let $T_t=W_k(k-1+t)=(k+1)u^{+}_{k+t}-2k\,u_{k-1+t}+(k-1)u^{-}_{k-2+t}$; by Step 1, $T_t\ge 0$ (the size $k-1+t$ is at most $N-k\le N-1$, and for $t=0$ it is $k-1$). The $t$-th bracket of the middle part equals
$$u_{m_t}\,T_t+(k+1)\,u^{+}_{k+t}\,U^{+}_{m_t}-(k-1)\,u^{-}_{k-2+t}\,U_{m_t}\ \ge\ k\,u^{+}_{k+t}\,U_{m_t-1}-(k-1)\,u^{-}_{k-2+t}\,U_{m_t},$$
by $u_{m_t}T_t\ge 0$ and (F4) at $j=m_t-1$. Sum over $t$ and, in the subtracted sum, move the index by one (the term $t+1$ of the subtracted sum is $(k-1)u^{-}_{k-1+t}U_{m_t-1}$): the middle brackets are at least
$$\sum_{t=0}^{r-1}U_{m_t-1}\big(k\,u^{+}_{k+t}-(k-1)\,u^{-}_{k-1+t}\big)+k\,u^{+}_{k+r}\,U_{k-2}-(k-1)\,\omega_{k-2}\,U_{N-k}.$$
Each term of the sum is nonnegative, since $u^{-}_{k-1+t}\le u_{k+t}\le u^{+}_{k+t}$ by (F3) and (F1); and $U_{k-2}=0$ by (F2). Adding the two boundary terms of Step 3, the middle part is at least
$$k\,\omega_{k-1}u^{+}_{N-k+1}-(k-1)\,\omega_{k-2}\big(U_{N-k}+u^{-}_{N-k}\big)=k\,\omega_{k-1}u^{+}_{N-k+1}-(k-1)\,\omega_{k-2}\,u_{N-k}\ \ge 0,$$
because $u^{+}_{N-k+1}\ge u_{N-k}$ by (F3) (here $N-k\ge k-1$) and $k\,\omega_{k-1}\ge(k-1)\,\omega_{k-2}$ by (F5).

Steps 4 and 5 give $\Sigma^{+}-2\Sigma^{0}+\Sigma^{-}\ge 0$, and $x>0$.
