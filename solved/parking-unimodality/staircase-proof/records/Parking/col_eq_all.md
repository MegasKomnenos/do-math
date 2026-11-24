---
weight: unit
short: the column inequality on all rows
---
## Description

For a column $k \ge 2$ and every row $n \ge k+1$: $(k+1)\,\delta_{n-1} + 2\,\beta^{(k-1)}_{n-1} \le n\,\bigl(\delta_n - \sum_{m=1}^{n-k} \kappa^{(k)}_m\, \delta_{n-m}\bigr)$, where $\delta_n = (b(n,k) - b(n,k-1))/n!$ is the normalised step of the column, $\beta^{(k-1)}_n = b(n,k-1)/n!$, and $\kappa^{(k)}$ is the prime kernel of the threshold $k$.

## Statement

Let $k \ge 2$ and $n \ge k+1$ be natural numbers. Then
$$(k+1)\,\delta_{n-1} + 2\,\beta^{(k-1)}_{n-1} \;\le\; n\,\Bigl(\delta_n - \sum_{m=1}^{n-k} \kappa^{(k)}_m\, \delta_{n-m}\Bigr).$$
Here $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$; $\beta^{(\ell)}_n = b(n,\ell)/n!$ (`Parking.bq`); $\delta_n = \beta^{(k)}_n - \beta^{(k-1)}_n$ is the normalised step of the column $k$ in the row $n$ (`Parking.dq`); and $\kappa^{(k)}_m = [X^m](1 - 1/Z_k)$ is the prime kernel of the threshold $k$ (`Parking.kq`, with $Z_k$ the series `Parking.Zs`).

## Explanation

Divided by $n$, the inequality is a lower bound for the step of the row $n$ by quantities of the earlier rows:
$$\delta_n \;\ge\; \frac{k+1}{n}\,\delta_{n-1} + \frac{2}{n}\,\beta^{(k-1)}_{n-1} + \sum_{m=1}^{n-k} \kappa^{(k)}_m\, \delta_{n-m} .$$
The second term is a nonnegative source, and the other terms feed the earlier steps of the same column back with nonnegative coefficients. On the rows $k+1 \le n \le 2k-1$ the two sides are equal: this is the column equation `Parking.dq_col`, in which the kernel is written as $\varepsilon_m = (m-1)^{m-1}/m!$ (`Parking.eps`); there $m \le n-k \le k-1$, and $\kappa^{(k)}_m = \varepsilon_m$ in that range (`Parking.kq_eq_eps`). The present statement says what survives of the column equation beyond the row $2k-1$: the kernel $\varepsilon$ is replaced by the prime kernel of the threshold $k$, and the equation becomes an inequality in the direction that bounds the step from below. The proof of `Parking.step_pos_large` uses it, multiplied by $x_k^n$ with the critical tilt $x_k$ (`Parking.xcrit`), to prove $\delta_n > 0$ row by row for $n \ge 2k$ in the columns $k \ge 82$.

The inequality is one of three that hold on all rows and come from a single identity of power series. Let $Z_y$ be the series of the threshold $y$ (`Parking.Zs`), $D = Z_{k+1} - 2Z_k + Z_{k-1}$ the series with coefficients $\delta_n$, $K = K_k$ the prime kernel series (`Parking.Ks`), and $\Gamma_y$ the series with $\Gamma_y' = Z_y'/Z_y$, $\Gamma_y(0) = 0$ (it is written out in the record of `Parking.Gp`, the series that is its derivative). Put $L_+ = \Gamma_{k+1} - \Gamma_k$ and $L_0 = \Gamma_k - \Gamma_{k-1}$. Then
$$D\,(1-K) \;=\; (L_+ - L_0) \;+\; Y_+ \;+\; Y_0, \qquad Y_+ = \frac{Z_{k+1}}{Z_k} - 1 - L_+, \quad Y_0 = L_0 - \Bigl(1 - \frac{Z_{k-1}}{Z_k}\Bigr),$$
and the two series $Y_+$ and $Y_0$ have nonnegative coefficients. Dropping them gives a coefficientwise inequality $D(1-K) \succeq L_+ - L_0$, where the coefficients of $L_+ - L_0 = \Gamma_{k+1} - 2\Gamma_k + \Gamma_{k-1}$ are the tree curvatures $\xi_t$ (`Parking.xi`). The three inequalities are three ways of reading this:

- the coefficient of $X^n$, multiplied by $n$, is the column inequality (this record);
- after multiplication by $Z_k$, which has nonnegative coefficients and cancels $1-K$, the coefficient of $X^n$ is the one-tree bound `Parking.one_tree_bound`;
- the same decomposition for the series $(Z_{k+1}-Z_k) - \gamma_k X (Z_k - Z_{k-1})$ in place of $D$, with $\gamma_k = (1+1/k)^{k-2}$ (`Parking.gam`), gives, by an induction, the diagonal lower bound `Parking.bq_diag_lower`.

Why the decomposition has this form can be seen formally. Since $Z_y' = \Gamma_y' Z_y$, one has $Z_y = \exp \Gamma_y$, hence $Z_{k+1}/Z_k = e^{L_+}$ and $Z_{k-1}/Z_k = e^{-L_0}$, and
$$D\,(1-K) = e^{L_+} - 2 + e^{-L_0}, \qquad Y_+ = e^{L_+} - 1 - L_+, \qquad Y_0 = e^{-L_0} - 1 + L_0 .$$
The decomposition separates the part of first order in $L_\pm$ from the rest. Since $L_+$ has nonnegative coefficients, so has $e^{L_+} - 1 - L_+ = \sum_{j\ge2} L_+^j/j!$. For $e^{-L_0} - 1 + L_0$ the expansion alternates and shows nothing. The library does not form exponentials at all. It proves both positivity statements from differential equations, by one principle: a series $F$ with $F(0) \ge 0$ whose derivative is $G F + S$ with $G$ and $S$ coefficientwise nonnegative is coefficientwise nonnegative. For $Y_0$ the equation is $Y_0' = u\,L_0'$ with $u = 1 - Z_{k-1}/Z_k$, so the question becomes whether $u$ has nonnegative coefficients, and that follows from a linear equation for $u$ whose coefficients are nonnegative. This is the step of the proof that is not routine.

In Lean the statement is written with `dq k (n - 1)`, `bq (k - 1) (n - 1)` and the sum over `Finset.Icc 1 (n - k)`; under the hypotheses $k \ge 2$, $n \ge k+1$ the natural-number subtractions are ordinary ones. The kernel sum stops at $m = n-k$ because $\delta_j = 0$ for $j < k$.

## Proof

Throughout, $k \ge 2$ is fixed, and for a power series $F$ with real coefficients $F \succeq 0$ means that every coefficient of $F$ is nonnegative. We write $Z_+ = Z_{k+1}$, $Z_0 = Z_k$, $Z_- = Z_{k-1}$ for the series of the three thresholds (`Parking.Zs`), $K = K_k$, and $z^{(y)}_n = [X^n] Z_y$ (`Parking.coeff_Zs`; this is the sequence `Parking.zr`, $z^{(y)}_n = A(n,y-1)/n!$). The proof has four parts: a principle for nonnegative coefficients, the comparison of two adjacent thresholds, the decomposition, and the reading of one coefficient.

### 1. Series with nonnegative coefficients

Sums and products of series $\succeq 0$ are $\succeq 0$, and so are their multiples by a nonnegative constant and by $X$. Two further facts are used.

(P1) If $F(0) \ge 0$ and $F' \succeq 0$, then $F \succeq 0$; indeed $[X^{n+1}] F = [X^n] F'/(n+1)$.

(P2) If $F' = G F + S$ with $G \succeq 0$, $S \succeq 0$ and $F(0) \ge 0$, then $F \succeq 0$. The coefficient of $X^n$ in the equation is $(n+1) F_{n+1} = \sum_{j=0}^{n} G_j F_{n-j} + S_n$, and the claim follows by strong induction on the index.

### 2. Two adjacent thresholds

Let $y \ge 2$. Recall $\Gamma_y = \sum_{t \ge 1} \frac{\min(t,y)}{t} z^{(y)}_{t-1} X^t$, with $[X^j]\Gamma_y' = \min(j+1,y)\, z^{(y)}_j$ (`Parking.coeff_Gp`), and put
$$R_y \;=\; \sum_{j \ge y-1} z^{(y-1)}_j X^j, \qquad L_y \;=\; \Gamma_y - \Gamma_{y-1} .$$

(T1) $L_y' = \Gamma_y' - \Gamma_{y-1}' = y\,(Z_y - Z_{y-1}) + R_y$. Compare the coefficients of $X^j$. If $j + 1 \ge y$, the left side is $y\, z^{(y)}_j - (y-1)\, z^{(y-1)}_j = y\,(z^{(y)}_j - z^{(y-1)}_j) + z^{(y-1)}_j$. If $j + 1 < y$, both minima are $j+1$ and $z^{(y)}_j = z^{(y-1)}_j = c_j$, where $c_j = (j+1)^{j-1}/j!$ (`Parking.cc`), by `Parking.zr_eq_cc` ($j$ lies in the free range of both thresholds), so both sides vanish.

(T2) $L_y' \succeq 0$ and $L_y \succeq 0$. The series $Z_y - Z_{y-1}$ is $\succeq 0$ because $z^{(y)}_n$ does not decrease in the threshold (`Parking.zr_mono`), and $R_y \succeq 0$ because $z^{(y-1)}_j \ge 0$ (`Parking.zr_nonneg`). So $L_y' \succeq 0$ by (T1), and $L_y(0) = 0$, so $L_y \succeq 0$ by (P1).

(T3) Let $u_y = 1 - Z_{y-1}\,(1 - K_y)$, that is, $u_y = 1 - Z_{y-1}/Z_y$ (`Parking.inv_Zs`). Then $u_y(0) = 0$,
$$u_y' = (1 - u_y)\, L_y', \qquad u_y' = (y Z_{y-1} - R_y)\, u_y + R_y, \qquad u_y \succeq 0 .$$
The constant term is $1 - z^{(y-1)}_0 \cdot 1 = 0$ (`Parking.zr_zero`, `Parking.coeff_one_sub_Ks_zero`). For the first equation, differentiate the product: $u_y' = -Z_{y-1}'\,(1-K_y) + Z_{y-1}\, K_y'$, and insert $Z_{y-1}' = \Gamma_{y-1}' Z_{y-1}$ (`Parking.deriv_Zs`) and $K_y' = (1-K_y)\,\Gamma_y'$ (`Parking.deriv_Ks`); this gives $u_y' = Z_{y-1}(1-K_y)\,(\Gamma_y' - \Gamma_{y-1}') = (1-u_y)\, L_y'$. The first equation does not show the sign of the coefficients of $u_y$: written as $u_y' = -L_y'\, u_y + L_y'$, it multiplies $u_y$ by a series whose coefficients are nonpositive, so (P2) does not apply to it. The second equation removes this difficulty. Since $Z_y (1-K_y) = 1$ (`Parking.Zs_mul_one_sub_Ks`), one has $Z_y - Z_{y-1} = u_y Z_y$ and therefore $(1-u_y)(Z_y - Z_{y-1}) = Z_{y-1}(1-K_y)\, u_y Z_y = Z_{y-1}\, u_y$. Inserting (T1) into the first equation,
$$u_y' = y\,(1-u_y)(Z_y - Z_{y-1}) + (1-u_y) R_y = y\, Z_{y-1}\, u_y + R_y - R_y\, u_y .$$
In this linear equation the coefficient series $y Z_{y-1} - R_y$ is $\succeq 0$: its $j$-th coefficient is $y\, z^{(y-1)}_j$ for $j < y-1$ and $(y-1)\, z^{(y-1)}_j$ for $j \ge y-1$. The inhomogeneous term $R_y$ is $\succeq 0$. By (P2), $u_y \succeq 0$.

(T4) Let $y \ge 1$ and $Q_y = Z_{y+1}\,(1-K_y)$, that is, $Q_y = Z_{y+1}/Z_y$. Then $Q_y(0) = 1$ (`Parking.zr_zero`, `Parking.coeff_one_sub_Ks_zero`) and $Q_y' = Q_y\, L_{y+1}'$. Indeed $Q_y' = Z_{y+1}'(1-K_y) - Z_{y+1} K_y' = \Gamma_{y+1}' Z_{y+1}(1-K_y) - Z_{y+1}(1-K_y)\Gamma_y'$ by `Parking.deriv_Zs` and `Parking.deriv_Ks`.

### 3. The decomposition

Put $L_+ = L_{k+1}$, $L_0 = L_k$, $u = u_k$, $Q = Q_k$, and
$$D = (Z_+ - Z_0) - (Z_0 - Z_-), \qquad Y_+ = Q - 1 - L_+, \qquad Y_0 = L_0 - u .$$

(D1) $Y_+ \succeq 0$. By (T4), $Y_+(0) = 1 - 1 - 0 = 0$ and $Y_+' = Q L_+' - L_+' = (Q - 1) L_+' = L_+'\, Y_+ + L_+ L_+'$. Here $L_+' \succeq 0$ and $L_+ L_+' \succeq 0$ by (T2) for $y = k+1$, so (P2) applies.

(D2) $Y_0 \succeq 0$. By (T3), $Y_0(0) = 0$ and $Y_0' = L_0' - (1-u) L_0' = u\, L_0'$, a product of two series $\succeq 0$ by (T3) and (T2) for $y = k$. So (P1) applies.

(D3) $D\,(1-K) = (L_+ - L_0) + Y_+ + Y_0$. Both sides equal $Q - 1 - u$: on the left, $Z_+(1-K) = Q$, $Z_0(1-K) = 1$ and $Z_-(1-K) = 1 - u$; on the right, the terms $L_+$ and $L_0$ cancel.

### 4. The coefficient of $X^n$

Let $n \ge k+1$ and compare the coefficients of $X^n$ in (D3).

*Left side.* The coefficients of $D$ are $[X^j] D = \delta_j$, because $\beta^{(\ell)}_j = z^{(\ell+1)}_j - z^{(\ell)}_j$ for $\ell \ge 1$ (`Parking.bq_eq`, used for $\ell = k$ and $\ell = k-1$). The coefficients of $1 - K$ are $1$ at $X^0$ and $-\kappa^{(k)}_m$ at $X^m$, $m \ge 1$ (`Parking.coeff_one_sub_Ks_zero`, `Parking.coeff_one_sub_Ks_of_pos`). Hence
$$[X^n]\bigl(D(1-K)\bigr) = \delta_n - \sum_{m=1}^{n} \kappa^{(k)}_m\, \delta_{n-m} = \delta_n - \sum_{m=1}^{n-k} \kappa^{(k)}_m\, \delta_{n-m},$$
the last step because $\delta_j = 0$ for $j < k$ (`Parking.dq_eq_zero`, with `Parking.sum_Icc_trunc`).

*Right side.* $L_+ - L_0 = \Gamma_{k+1} - 2\Gamma_k + \Gamma_{k-1}$, and its coefficient at $X^t$, $t \ge 1$, is $\frac1t\bigl(\min(t,k+1)\, z^{(k+1)}_{t-1} - 2\min(t,k)\, z^{(k)}_{t-1} + \min(t,k-1)\, z^{(k-1)}_{t-1}\bigr)$, which is the tree curvature $\xi_t$ by its definition (`Parking.xi`). The coefficients of $Y_+$ and $Y_0$ are nonnegative by (D1) and (D2).

Therefore $\delta_n - \sum_{m=1}^{n-k} \kappa^{(k)}_m \delta_{n-m} \ge \xi_n$. By `Parking.succ_mul_xi_succ`, applied at the index $n-1 \ge k$, $n\,\xi_n = (k+1)\,\delta_{n-1} + 2\,\beta^{(k-1)}_{n-1}$. Multiplying the inequality by $n > 0$ gives the statement.
