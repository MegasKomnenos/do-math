---
weight: unit
short: the diagonal lower bound on all rows
---
## Description

For $k \ge 2$ and every row $n \ge 1$: $\gamma_k\, \beta^{(k-1)}_{n-1} \le \beta^{(k)}_n$, where $\beta^{(\ell)}_n = b(n,\ell)/n!$ and $\gamma_k = (1+1/k)^{k-2}$. In terms of the counts, $\gamma_k \cdot n \cdot b(n-1,k-1) \le b(n,k)$.

## Statement

Let $k \ge 2$ and $n \ge 1$ be natural numbers. Then
$$\gamma_k\; \beta^{(k-1)}_{n-1} \;\le\; \beta^{(k)}_n ,$$
where $\beta^{(\ell)}_n = b(n,\ell)/n!$ (`Parking.bq`), $b(n,\ell)$ is the number of parking functions of length $n$ whose maximum displacement is exactly $\ell$, and $\gamma_k = (1 + 1/k)^{k-2}$ (`Parking.gam`).

## Explanation

The inequality compares two entries of the triangle $b(n,\ell)$ that are neighbours along a diagonal, $(n-1,k-1)$ and $(n,k)$: one more car and one more unit of displacement multiply the normalised count by at least $\gamma_k$, a factor between $1$ and $e$. For $n \le k$ both sides are zero, since $b(n,\ell) = 0$ for $n \le \ell$ (`Parking.bq_eq_zero`). The factor is the one that comes out of the proof: the stochastic monotonicity `Parking.zr_diag_mono`, $z^{(y)}_n/c_n \le z^{(y+1)}_{n+1}/c_{n+1}$, for $z^{(y)}_n = A(n,y-1)/n!$ (`Parking.zr`) and $c_n = (n+1)^{n-1}/n!$ (`Parking.cc`), involves the ratio $c_i/c_{i-1} = (1+1/i)^{i-1} = \gamma_i\,(1+1/i)$ of consecutive Cayley numbers, and $\gamma_i \ge \gamma_k$ for $i \ge k$.

The bound relates the column $k$ to the column $k-1$ and is used in every part of the argument that follows a column along its rows. In the crossing criterion (`Parking.cross_criterion`) it shows that the tilted profile of the level $k-1$ is largest at the last row considered. In the chain column it bounds the step from below by a difference of the profile (`Parking.dq_diag_lower` is that form), in the near rows and in the far rows. In the left half it is carried to the critical tilt $x_k$ (`Parking.xcrit`), where $(k+1)\, x_k \gamma_k = k$, as $k\,U_{n-1} \le (k+1)\,U^+_n$ (`Parking.Ut_diag_lower`).

The proof is the third reading of the decomposition of the series of a column that is established in the record of `Parking.col_eq_all`. Unlike the column inequality and the one-tree bound, the present statement is not the coefficient of one identity: it is the nonnegativity of all coefficients of the series $\mathfrak D = (Z_{k+1} - Z_k) - \gamma_k X\,(Z_k - Z_{k-1})$, and it is obtained by an induction along the rows. The product $\mathfrak D\,(1-K_k)$ has the coefficients $\mathfrak D_n - \sum_{m\ge1} \kappa^{(k)}_m \mathfrak D_{n-m}$ with the nonnegative prime kernel $\kappa^{(k)}$ of the threshold $k$ (`Parking.kq`), so $\mathfrak D_n$ is a nonnegative combination of earlier coefficients plus the $n$-th coefficient of $\mathfrak D(1-K_k)$. The decomposition writes $\mathfrak D(1-K_k)$ as two series with nonnegative coefficients plus a series $\mathfrak L$ whose coefficient at $X^{i+1}$ is at least $\frac{k}{i+1}\mathfrak D_i$. The induction hypothesis therefore enters twice, through the kernel and through $\mathfrak L$.

In Lean the statement is `gam k * bq (k - 1) (n - 1) ≤ bq k n`; with $k \ge 2$ and $n \ge 1$ the subtractions are ordinary.

## Proof

Fix $k \ge 2$ and write $\mu = \gamma_k \ge 0$. We use the notation of the record of `Parking.col_eq_all`: $F \succeq 0$ means that all coefficients of $F$ are nonnegative; $Z_+ = Z_{k+1}$, $Z_0 = Z_k$, $Z_- = Z_{k-1}$ are the series of the thresholds (`Parking.Zs`) with coefficients $z^{(y)}_n$; $K = K_k$ (`Parking.Ks`); $\Gamma_y = \sum_{t\ge1} \frac{\min(t,y)}{t} z^{(y)}_{t-1} X^t$ (see `Parking.Gp`, which is $\Gamma_y'$); $L_+ = \Gamma_{k+1} - \Gamma_k$, $L_0 = \Gamma_k - \Gamma_{k-1}$; $Q = Z_+(1-K)$, $u = 1 - Z_-(1-K)$; $Y_+ = Q - 1 - L_+$ and $Y_0 = L_0 - u$. That record proves $Y_+ \succeq 0$ (D1) and $Y_0 \succeq 0$ (D2), in the parts 1 to 3 of its proof.

In brief, the argument there is as follows. For $y \ge 2$ the series $L_y = \Gamma_y - \Gamma_{y-1}$ satisfies $L_y' = y\,(Z_y - Z_{y-1}) + R_y$ with $R_y = \sum_{j \ge y-1} z^{(y-1)}_j X^j$, so $L_y' \succeq 0$ and $L_y \succeq 0$; this applies to $L_+$ and $L_0$. The quotient $Q = Z_{k+1}(1-K)$ satisfies $Q' = Q\,L_+'$, hence $Y_+' = L_+'\,Y_+ + L_+ L_+'$ with $Y_+(0) = 0$. The series $u = 1 - Z_{k-1}(1-K)$ satisfies $u' = (1-u)\,L_0' = (k Z_{k-1} - R_k)\,u + R_k$ with $u(0) = 0$, and the series $k Z_{k-1} - R_k$ and $R_k$ are $\succeq 0$; hence $u \succeq 0$, and $Y_0' = u\,L_0'$ with $Y_0(0) = 0$. In each case the conclusion comes from one principle: a series $F$ with $F(0) \ge 0$ and $F' = G F + S$, where $G \succeq 0$ and $S \succeq 0$, is $\succeq 0$.

Define
$$\mathfrak D = (Z_+ - Z_0) - \mu X\,(Z_0 - Z_-), \qquad \mathfrak L = L_+ - \mu X L_0 ,$$
and write $\mathfrak D_n$, $\mathfrak L_n$ for their coefficients. Then $\mathfrak D_0 = 0$ (`Parking.zr_zero`) and, for $n \ge 1$,
$$\mathfrak D_n = \bigl(z^{(k+1)}_n - z^{(k)}_n\bigr) - \mu\,\bigl(z^{(k)}_{n-1} - z^{(k-1)}_{n-1}\bigr) = \beta^{(k)}_n - \mu\,\beta^{(k-1)}_{n-1}$$
by `Parking.bq_eq`. The statement is $\mathfrak D_n \ge 0$ for $n \ge 1$. We prove $\mathfrak D \succeq 0$ in four steps.

*Step 1: $\mathfrak D_n = 0$ for $n \le k$.* For $1 \le n \le k$ all four indices lie in the free ranges of their thresholds, so $z^{(k+1)}_n = z^{(k)}_n = c_n$ and $z^{(k)}_{n-1} = z^{(k-1)}_{n-1} = c_{n-1}$ by `Parking.zr_eq_cc`.

*Step 2: the decomposition.*
$$\mathfrak D\,(1-K) \;=\; \mathfrak L \;+\; Y_+ \;+\; \mu X\, Y_0 .$$
Both sides equal $Q - 1 - \mu X u$: on the left, $(Z_+ - Z_0)(1-K) = Q - 1$ and $(Z_0 - Z_-)(1-K) = 1 - (1-u) = u$, using $Z_0(1-K) = 1$ (`Parking.Zs_mul_one_sub_Ks`); on the right, $L_+$ and $\mu X L_0$ cancel.

*Step 3: for $i \ge k$, $\;k\,\mathfrak D_i \le (i+1)\,\mathfrak L_{i+1}$.* For $t \ge y$ the coefficient of $X^t$ in $\Gamma_y$ is $\frac{y}{t}\, z^{(y)}_{t-1}$. Since $i \ge k$, this applies to all four series that occur, and
$$(i+1)\,\mathfrak L_{i+1} = (k+1)\, z^{(k+1)}_i - k\, z^{(k)}_i - \mu\,\frac{i+1}{i}\,\bigl(k\, z^{(k)}_{i-1} - (k-1)\, z^{(k-1)}_{i-1}\bigr).$$
Comparing with the formula for $\mathfrak D_i$, one finds by a routine calculation
$$(i+1)\,\mathfrak L_{i+1} \;=\; k\,\mathfrak D_i \;+\; \Bigl[\, z^{(k+1)}_i - \mu\,\frac{i+1}{i}\, z^{(k)}_{i-1} \Bigr] \;+\; \mu\,\frac{i+1-k}{i}\,\bigl(z^{(k)}_{i-1} - z^{(k-1)}_{i-1}\bigr).$$
The last term is nonnegative because $i + 1 - k \ge 0$ and $z^{(k-1)}_{i-1} \le z^{(k)}_{i-1}$ (`Parking.zr_mono`). The bracket is nonnegative by stochastic monotonicity. Indeed `Parking.zr_diag_mono` (threshold $k$, index $i-1$) gives $z^{(k)}_{i-1}/c_{i-1} \le z^{(k+1)}_i/c_i$; by `Parking.cay_ratio` and `Parking.psi_eq_gam` (for $i \ge 2$), $c_i = (1+1/i)^{i-1} c_{i-1} = \gamma_i\,\frac{i+1}{i}\, c_{i-1}$; hence, the numbers $c_{i-1}$ and $c_i$ being positive (`Parking.cc_pos`), $\gamma_i\,\frac{i+1}{i}\, z^{(k)}_{i-1} \le z^{(k+1)}_i$. Finally $\gamma_k \le \gamma_i$ because $2 \le k \le i$ (`Parking.gam_mono`), and $z^{(k)}_{i-1} \ge 0$.

*Step 4: induction.* We show $\mathfrak D_n \ge 0$ by strong induction on $n$. For $n \le k$ this is Step 1. Let $n = i + 1$ with $i \ge k$, and suppose $\mathfrak D_j \ge 0$ for all $j \le i$. The coefficients of $1-K$ are $1$ at $X^0$ and $-\kappa^{(k)}_m$ at $X^m$, $m \ge 1$ (`Parking.coeff_one_sub_Ks_zero`, `Parking.coeff_one_sub_Ks_of_pos`), so the coefficient of $X^{i+1}$ in Step 2 reads
$$\mathfrak D_{i+1} \;=\; \sum_{m=1}^{i+1} \kappa^{(k)}_m\, \mathfrak D_{i+1-m} \;+\; \mathfrak L_{i+1} \;+\; [X^{i+1}]\,Y_+ \;+\; \mu\,[X^{i}]\,Y_0 .$$
The prime kernel is nonnegative, $\kappa^{(k)}_m \ge 0$ (`Parking.kqT_nonneg` with the tilt $x = 1$; this needs $k \ge 2$), and the coefficients $\mathfrak D_{i+1-m}$, $m \ge 1$, are nonnegative by the induction hypothesis; so the sum is nonnegative. By Step 3 and the induction hypothesis, $(i+1)\,\mathfrak L_{i+1} \ge k\,\mathfrak D_i \ge 0$. The last two terms are nonnegative by (D1) and (D2). Hence $\mathfrak D_{i+1} \ge 0$.
