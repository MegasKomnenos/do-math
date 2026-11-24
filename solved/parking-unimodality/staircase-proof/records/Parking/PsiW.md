---
weight: unit
short: the weight Ψ′(N) = max(N, 2k−1) of the rows of column k
---
## Description

The weight $\Psi'(N)=\max(N,\,2k-1)$ given to the row (or size) $N$ in the argument for a column $k$: constant $2k-1$ up to the row $2k-1$, and equal to $N$ afterwards.

## Statement

For natural numbers $k$ and $N$,
$$\Psi'(N)=\max(N,\,2k-1),$$
regarded as a real number. The weight depends on the column $k$, which is fixed wherever $\Psi'$ is used.

## Explanation

Notation for this explanation: $x_k=(k/(k+1))^{k-1}$ is the critical tilt (`Parking.xcrit`); $u^{(y)}_N=z^{(y)}_Nx_k^{\,N}$ is the tilted environment of the threshold $y$ (`Parking.zrT`); $\eta_j=x_k^{\,j}\,(b(j,k)-b(j,k-1))/j!$ is the tilted step of column $k$ in the row $j$; and $\kappa_m=x_k^{\,m}[X^m]K_k\ge 0$ is the tilted prime kernel of the threshold $k$ (`Parking.kqT`), which on the free range $1\le m\le k$ equals $\varepsilon_mx_k^{\,m}$ with $\varepsilon_m=(m-1)^{m-1}/m!$.

**What the weight is for.** For a column $k\ge 82$ the positive sign of the step in the rows $n\ge 2k$ is proved row by row (`Parking.step_pos_large`). The column inequality bounds $\eta_n$ from below by a positive source plus the feedback $\sum_{j=k}^{n-1}\kappa_{n-j}\,\eta_j$ of the earlier rows. The column has one crossing row $q$: $\eta_j\le 0$ for $k\le j<q$ and $\eta_j>0$ for $j\ge q$. So the feedback contains negative terms, and nothing is known about their sizes individually.

What is known about the negative rows is a bound for a *weighted sum*: if a weight $\psi$ makes the weighted second differences along the diagonal nonnegative, summation by parts bounds $\sum_{j=k}^{J}\psi(j)\,\eta_j$ from below by boundary terms at the rows $J$ and $J-1$ (`Parking.weighted_debt`). To use this for the feedback, the kernel weights $\kappa_{n-j}$ have to be exchanged for the weights $\psi(j)$, and this is possible term by term, without knowing the sizes of the $\eta_j$, exactly when one constant $\theta$ separates the ratios:
$$\frac{\kappa_{n-j}}{\psi(j)}\le\theta\ \text{ for }j<q,\qquad \frac{\kappa_{n-j}}{\psi(j)}\ge\theta\ \text{ for }q\le j\le n-1 .$$
Then $\kappa_{n-j}\eta_j\ge\theta\,\psi(j)\,\eta_j$ in every row, because $\eta_j$ is nonpositive in the first range and positive in the second. The sign pattern of the column is played against the order of the kernel's weights.

**The two requirements on a weight.** (A) The weighted second differences $\psi(N+1)\,u^{(k+1)}_{N+1}-2\psi(N)\,u^{(k)}_N+\psi(N-1)\,u^{(k-1)}_{N-1}$ of the tilted environments must be nonnegative for all sizes $N\ge k$. (B) For every row $n\ge 2k$ the ratios $\kappa_{n-j}/\psi(j)$ must be separated at the crossing row as above. $\Psi'$ is chosen so that both can be proved.

For (A) the library has two results. Plain convexity, the case of a constant weight, is proved on the sizes $k\le N\le 2k-2$ of the first layer (`Parking.FirstLayer.zrT_diag_convex`). Beyond the first layer what is proved is the convexity with the weight $\psi(N)=N$ (`Parking.DeltaId_nonneg`); this is the form the last-car recursion produces, since its left side is $(N+1)$ times the mass of the size $N+1$. $\Psi'$ is constant where the first is available and equal to $N$ where the second is, and at the junction $N=2k-1$ the three weights are $N+1$, $N$, $N$, which only adds a nonnegative term (`Parking.DeltaPsi_nonneg`).

For (B), all rows before the crossing satisfy $j<q\le k+\frac{27}{100}k\le 2k-1$, so there the weight is constant and the separation is the monotonicity of the kernel: $\kappa_{n-j}\le\kappa_{n-q+1}$ (`Parking.order_neg`). On the positive rows up to $2k-1$ it is monotonicity again; on the positive rows $j\ge 2k$ the weight grows like $j$ and the kernel has to grow at least as fast in $j$, which is what the decay estimates of the kernel give (`Parking.order_pos`).

**What fails with another weight.** With the weight $\psi(N)=N$ on all sizes, requirement (A) would become easier in the first layer, but (B) breaks down next to the crossing, as the following first-order computation shows. For the neighbouring rows $j=q-1$ and $j=q$ the separation requires $\kappa_L/\kappa_{L-1}\le\psi(q-1)/\psi(q)=1-1/q$ with $L=n-q+1$. In the rows $2k\le n\le k+q-1$ the indices $L-1$, $L$ lie in the free range, where the kernel is known in closed form, and
$$\frac{\kappa_L}{\kappa_{L-1}}=\frac{(1-\frac1L)\,(1+\frac{1}{L-2})^{L-2}}{(1+\frac1k)^{k-1}}\approx 1-\frac32\Big(\frac1L-\frac1k\Big)$$
to first order in $1/L$ and $1/k$. The requirement then reads $\frac32(\frac1L-\frac1k)\ge\frac1q$, and with $q\le 1.27k$ it can hold only for $L$ below about $0.66k$, whereas $n\ge 2k$ and $q\le 1.27k$ force $L\ge 0.73k$. With a weight that is constant on the rows up to $2k-1$ the right side of the requirement is $1$, and monotonicity suffices.

With a constant weight on all sizes, (B) would hold by monotonicity alone in every row, but (A) would require the plain diagonal convexity for all sizes $N\ge k$, and beyond the first layer the library proves only the form with the weight $N$.

The constant part has a price: on the first layer, (A) with a constant weight is the plain convexity itself, which is why the argument for the rows $n\ge 2k$ needs `Parking.FirstLayer.zrT_diag_convex` and with it the whole of property K (`Parking.FirstLayer.kernel_TK`). With the break at $2k-1$, the bound of `Parking.weighted_debt` at $J=n-1$ has $\Psi'(J)=J$ already for $n=2k$, the first row to which `Parking.step_pos_large` applies it.

**The Lean form.** `PsiW k N` is the real cast of the natural number `max N (2 * k - 1)` with truncated subtraction. For $k=0$ the truncated $2k-1$ is $0$ instead of $-1$, and the maximum is $N$ in either reading, so the two forms agree for all $k$. The four statements `Parking.PsiW_of_ge`, `Parking.PsiW_low`, `Parking.PsiW_mono`, `Parking.PsiW_ge_self` unfold it.
