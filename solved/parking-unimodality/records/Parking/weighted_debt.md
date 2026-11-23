---
weight: unit
short: the weighted debt of a column
---
## Description

For $k\ge 7$ and $J\ge k$, at the critical tilt $x_k$, the weighted sum of the tilted steps of column $k$ over the rows $k,\dots,J$ is bounded below by boundary terms: $\sum_{n=k}^{J}\Psi'(n)\,\eta_n\ge-\big(\Psi'(J)U_J+\Psi'(J-1)U_{J-1}+(\Psi'(J)-\Psi'(J-1))\,u^{(k)}_J\big)$.

## Statement

Let $k\ge 7$ and $J\ge k$ be natural numbers and $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`). Let

- $\eta_n=\delta_n\,x_k^{\,n}$, where $\delta_n=\big(b(n,k)-b(n,k-1)\big)/n!$ is the normalised step of column $k$ in the row $n$ (`Parking.dq k n`);
- $u^{(y)}_N=z^{(y)}_N\,x_k^{\,N}$, $z^{(y)}_N=A(N,y-1)/N!$, the tilted environment of the threshold $y$ (`Parking.zrT y (xcrit k) N`);
- $U_N=u^{(k)}_N-u^{(k-1)}_N=x_k^{\,N}\,b(N,k-1)/N!$ (`Parking.Ut k (xcrit k) N`);
- $\Psi'(N)=\max(N,2k-1)$ (`Parking.PsiW`).

Then
$$\sum_{n=k}^{J}\Psi'(n)\,\eta_n\ \ge\ -\Big(\Psi'(J)\,U_J+\Psi'(J-1)\,U_{J-1}+\big(\Psi'(J)-\Psi'(J-1)\big)\,u^{(k)}_J\Big).$$

## Explanation

The steps $\eta_n$ of a column are nonpositive in the rows before its crossing row, so a sum of them can be negative; the statement says how negative a $\Psi'$-weighted sum can be. The bound involves only quantities of the last two rows $J-1$, $J$: two tilted masses of the level $k-1$ and, when $J\ge 2k$ (so that $\Psi'(J)-\Psi'(J-1)=1$), one tilted environment. No information on the individual rows is needed, and in particular no information on where the crossing is. The quantity in the bracket is called the weighted debt.

The reason is that the weighted sum telescopes. Since $\eta_n=u^{(k+1)}_n-2u^{(k)}_n+u^{(k-1)}_n$ is a second difference in the threshold, adding the terms of the rows $k,\dots,J$ and regrouping along diagonals turns the sum, up to boundary terms, into the sum of the weighted second differences along the diagonal, $\sum_{N=k}^{J-1}\Delta_{\Psi'}(N)$, and each of these is nonnegative by `Parking.DeltaPsi_nonneg`. This is the summation by parts for which the weight $\Psi'$ was chosen (`Parking.PsiW`).

It is used in the row step of `Parking.big_columns` with $J=n-1$: there the feedback of the earlier rows in the column inequality is bounded below by a multiple of $\sum_{j=k}^{n-1}\Psi'(j)\eta_j$, and the present statement bounds that sum by masses of the rows $n-1$ and $n-2$, which the source term of the column inequality can absorb.

## Proof

Write $u^{+}_N=u^{(k+1)}_N$, $u_N=u^{(k)}_N$, $u^{-}_N=u^{(k-1)}_N$ and $x=x_k$. From $\beta^{(\ell)}_n=z^{(\ell+1)}_n-z^{(\ell)}_n$ (`Parking.bq_eq`, for $\ell=k$ and $\ell=k-1$) one gets $\eta_n=u^{+}_n-2u_n+u^{-}_n$, and $U_N=u_N-u^{-}_N$ by definition.

**An identity with a nonnegative right side.** For $J\ge k$ put
$$Q(J)=\sum_{n=k}^{J}\Psi'(n)\eta_n+\Psi'(J)U_J+\Psi'(J-1)U_{J-1}-\Psi'(J-1)u_{J-1}+\Psi'(J)u_J .$$
Then $Q(J)\ge 0$, by induction on $J$.

*$J=k$.* The weights $\Psi'(k)$ and $\Psi'(k-1)$ both equal $2k-1$ (`Parking.PsiW_low`). Substituting $\eta_k$, $U_k$, $U_{k-1}$, all terms cancel except $Q(k)=(2k-1)\big(u^{+}_k-u^{-}_{k-1}\big)$. This is nonnegative: $u^{-}_{k-1}\le u_{k-1}$ (`Parking.zrT_le_zrT`) and $u_{k-1}\le u^{+}_k$, the diagonal monotonicity at the critical tilt, which follows from `Parking.zr_diag_mono` ($z^{(k)}_{k-1}/c_{k-1}\le z^{(k+1)}_k/c_k$, with $c_n=(n+1)^{n-1}/n!$) and `Parking.ccT_le_succ` ($c_{k-1}x^{k-1}\le c_kx^{k}$).

*$J\to J+1$.* A direct computation gives
$$Q(J+1)-Q(J)=\Psi'(J+1)\,u^{+}_{J+1}-2\Psi'(J)\,u_J+\Psi'(J-1)\,u^{-}_{J-1}=\Delta_{\Psi'}(J),$$
which is nonnegative by `Parking.DeltaPsi_nonneg` (applicable since $J\ge k$). The computation: the new terms $\Psi'(J+1)\big(\eta_{J+1}+U_{J+1}+u_{J+1}\big)$ add up to $\Psi'(J+1)u^{+}_{J+1}$; the terms $\Psi'(J)U_J$ cancel; the terms with $\Psi'(J)u_J$ add up to $-2\Psi'(J)u_J$; and $-\Psi'(J-1)U_{J-1}+\Psi'(J-1)u_{J-1}=\Psi'(J-1)u^{-}_{J-1}$.

**Conclusion.** From $Q(J)\ge 0$,
$$\sum_{n=k}^{J}\Psi'(n)\eta_n\ \ge\ -\Psi'(J)U_J-\Psi'(J-1)U_{J-1}+\Psi'(J-1)u_{J-1}-\Psi'(J)u_J .$$
The tilted environment of the threshold $k$ does not increase with the size at the critical tilt, $u_J\le u_{J-1}$ (`Parking.zrT_anti_crit`), and $\Psi'(J-1)\ge 0$, so $\Psi'(J-1)u_{J-1}-\Psi'(J)u_J\ge-\big(\Psi'(J)-\Psi'(J-1)\big)u_J$. This gives the claim.
