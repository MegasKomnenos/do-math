---
weight: unit
short: order of the kernel weights on the rows before the crossing
---
## Description

For a column $k\ge 2$, a row $q\le k+\frac{27}{100}k$, a row $n\ge 2k$ and every $j<q$: $\kappa_{n-j}\,(2k-1)\le\kappa_{n-q+1}\,\Psi'(j)$, where $\kappa$ is the prime kernel of the threshold $k$ at the critical tilt and $\Psi'(j)=\max(j,2k-1)$.

## Statement

Let $k\ge 2$, $q$, $n$, $j$ be natural numbers with $100\,(q-k)\le 27\,k$, $n\ge 2k$ and $j<q$. Let $x_k=(k/(k+1))^{k-1}$ (`Parking.xcrit`), $\kappa_m=x_k^{\,m}\,[X^m]K_k$ the tilted prime kernel of the threshold $k$ (`Parking.kqT k (xcrit k) m`), and $\Psi'(j)=\max(j,2k-1)$ (`Parking.PsiW`). Then
$$\kappa_{n-j}\,(2k-1)\ \le\ \kappa_{n-q+1}\,\Psi'(j).$$

## Explanation

Put $L=n-q+1$ and $\theta=\kappa_L/(2k-1)$. The statement says $\kappa_{n-j}/\Psi'(j)\le\theta$ for the rows $j<q$. Its companion `Parking.order_pos` says $\kappa_{n-j}/\Psi'(j)\ge\theta$ for the rows $q\le j\le n-1$. In the application $q$ is the crossing row of column $k$: the tilted step $\eta_j$ of the column is nonpositive for $k\le j<q$ and positive for $j\ge q$. The two statements together therefore give $\kappa_{n-j}\,\eta_j\ge\theta\,\Psi'(j)\,\eta_j$ in every row $k\le j\le n-1$, which converts the kernel-weighted feedback $\sum_j\kappa_{n-j}\eta_j$ of the column inequality into the $\Psi'$-weighted sum that `Parking.weighted_debt` bounds. This is the step of the proof of `Parking.step_pos_large` in which the sign pattern of the column is used; the record of `Parking.PsiW` explains the choice of the weight.

On the rows before the crossing the matter is simple, because the weight is constant there: $j<q\le 2k-1$. The kernel index $n-j$ is at least $L$, and the kernel does not increase.

The Lean hypothesis `100 * (q - k) ≤ 27 * k` uses truncated subtraction, so it also holds for $q\le k$; this agrees with reading it as $q\le k+\frac{27}{100}k$. The statement does not assume $j\ge k$.

## Proof

From $100(q-k)\le 27k$ and $k\ge 2$, $q\le 2k-1$, so $j\le 2k-1$ and $\Psi'(j)=2k-1$ (`Parking.PsiW_low`). Also $q\le n$, so $1\le n-q+1\le n-j$. The kernel does not increase on the indices $m\ge 1$: this is `Parking.kqT_succ_le` for the threshold $k\ge 2$ and the tilt $x_k$, whose hypothesis, that the free kernel $\varepsilon_mx_k^{\,m}$, $\varepsilon_m=(m-1)^{m-1}/m!$, does not increase on $1\le m\le k$, is `Parking.epsT_succ_le`. Hence $\kappa_{n-j}\le\kappa_{n-q+1}$; multiply by $2k-1>0$.
