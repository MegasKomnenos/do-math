---
weight: unit
short: the one-tree bound
---
## Description

For a column $k \ge 2$ and every row $n$: $\sum_{t=0}^{n} \xi_t\, z^{(k)}_{n-t} \le \delta_n$, where $\xi_t$ is the tree curvature of the column $k$, $z^{(k)}_n = A(n,k-1)/n!$ is the environment of the threshold $k$, and $\delta_n = (b(n,k) - b(n,k-1))/n!$ is the normalised step of the column.

## Statement

Let $k \ge 2$ and $n \ge 0$ be natural numbers. Then
$$\sum_{t=0}^{n} \xi_t\; z^{(k)}_{n-t} \;\le\; \delta_n .$$
Here $A(n,k)$ and $b(n,\ell)$ are the numbers of parking functions of length $n$ whose maximum displacement is at most $k$, respectively exactly $\ell$; $z^{(y)}_n = A(n,y-1)/n!$ (`Parking.zr`); $\delta_n = (b(n,k) - b(n,k-1))/n!$ is the normalised step of the column $k$ in the row $n$ (`Parking.dq`); and $\xi_t$ is the tree curvature of the column $k$ (`Parking.xi`): $\xi_0 = 0$ and, for $t \ge 1$,
$$t\,\xi_t = \min(t,k+1)\, z^{(k+1)}_{t-1} - 2\min(t,k)\, z^{(k)}_{t-1} + \min(t,k-1)\, z^{(k-1)}_{t-1} .$$

## Explanation

The step $\delta_n$ is the coefficient of $X^n$ in the second difference $D = Z_{k+1} - 2Z_k + Z_{k-1}$ of the series of a threshold (`Parking.Zs`) with respect to the threshold. Formally $Z_y = \exp\Gamma_y$, where $\Gamma_y$ is the series with $\Gamma_y' = Z_y'/Z_y$ and $\Gamma_y(0) = 0$ (it is written out in the record of `Parking.Gp`, the series that is its derivative); in the language of forests $\Gamma_y$ is the series of one tree and $Z_y$ that of forests of trees. The tree curvature $\xi_t$ is the coefficient of $X^t$ in $\Gamma_{k+1} - 2\Gamma_k + \Gamma_{k-1}$, the second difference of the one-tree series. With $L_+ = \Gamma_{k+1} - \Gamma_k$ and $L_0 = \Gamma_k - \Gamma_{k-1}$,
$$D \;=\; Z_k\,\bigl(e^{L_+} - 2 + e^{-L_0}\bigr) \;=\; Z_k\,(L_+ - L_0) \;+\; Z_k\,(e^{L_+} - 1 - L_+) \;+\; Z_k\,(e^{-L_0} - 1 + L_0) .$$
The first term is the convolution $\sum_t \xi_t z^{(k)}_{n-t}$ of the statement: it keeps the forests in which exactly one tree is counted differently by the three thresholds, the other trees being counted with the threshold $k$. The statement says that the remaining two terms, in which two or more trees are affected, have nonnegative coefficients, so that the step of the column is at least its one-tree part. This description is an interpretation; the proof uses the differential equations of the series and no exponentials.

The bound is one of the three inequalities read off from the decomposition $D(1-K_k) = (L_+ - L_0) + Y_+ + Y_0$ established in the record of `Parking.col_eq_all`; here the decomposition is multiplied by $Z_k$.

Its use is in the step bound `Parking.step_bound`. Since $\xi_t = 0$ for $t < k$ (`Parking.xi_eq_zero`), the sum starts at $t = k$. Multiplied by $x^n$, the bound reads $\delta_n x^n \ge \sum_{t=k}^{n} \xi_t x^t \cdot z^{(k)}_{n-t} x^{n-t}$; when the tilted environment does not increase (at the critical tilt, `Parking.zrT_anti_crit`), the weights $z^{(k)}_{n-t} x^{n-t}$ are nonnegative and nondecreasing in $t$, and Abel summation shows that $\delta_n \ge 0$ as soon as all the tail sums $\sum_{t=s}^{n} \xi_t x^t$ are nonnegative. The step bound makes the same summation after lowering the last weight from $1$ to $x$, and obtains $\delta_n \ge (1-x)\,\xi_n$. Moreover $(n+1)\,\xi_{n+1} = (k+1)\,\delta_n + 2\beta^{(k-1)}_n$, with $\beta^{(k-1)}_n = b(n,k-1)/n!$ (`Parking.bq`), for $n \ge k$ (`Parking.succ_mul_xi_succ`), so a positive step produces a positive next curvature. For a tilt $x < 1$ the step bound then makes the next step positive, and the nonnegativity of the tail sums passes from one row to the next; this is carried out in `Parking.propagate_pos`.

In Lean the sum is over `Finset.range (n + 1)`, that is, over $0 \le t \le n$.

## Proof

Fix $k \ge 2$. For a power series $F$, write $F \succeq 0$ if all its coefficients are nonnegative. Let $Z_y$ be the series of the threshold $y$ (`Parking.Zs`), $K = K_k$ its prime kernel series for $y = k$ (`Parking.Ks`), $\Gamma_y = \sum_{t\ge1} \frac{\min(t,y)}{t} z^{(y)}_{t-1} X^t$ (see `Parking.Gp`), and
$$D = Z_{k+1} - 2 Z_k + Z_{k-1}, \quad L_+ = \Gamma_{k+1} - \Gamma_k, \quad L_0 = \Gamma_k - \Gamma_{k-1}, \quad Y_+ = Z_{k+1}(1-K) - 1 - L_+, \quad Y_0 = L_0 - \bigl(1 - Z_{k-1}(1-K)\bigr).$$
The record of `Parking.col_eq_all` proves, in the parts 1 to 3 of its proof, the identity
$$D\,(1-K) \;=\; (L_+ - L_0) + Y_+ + Y_0 \tag{D3}$$
and the two facts $Y_+ \succeq 0$ (D1) and $Y_0 \succeq 0$ (D2); these come from the differential equation $Z_y' = \Gamma_y' Z_y$ of the last-car recursion (`Parking.deriv_Zs`) and from $K' = (1-K)\,\Gamma_k'$ (`Parking.deriv_Ks`).

In brief, the argument there is as follows. For $y \ge 2$ the series $L_y = \Gamma_y - \Gamma_{y-1}$ satisfies $L_y' = y\,(Z_y - Z_{y-1}) + R_y$ with $R_y = \sum_{j \ge y-1} z^{(y-1)}_j X^j$, so $L_y' \succeq 0$ and $L_y \succeq 0$; this applies to $L_+$ and $L_0$. The quotient $Q = Z_{k+1}(1-K)$ satisfies $Q' = Q\,L_+'$, hence $Y_+' = L_+'\,Y_+ + L_+ L_+'$ with $Y_+(0) = 0$. The series $u = 1 - Z_{k-1}(1-K)$ satisfies $u' = (1-u)\,L_0' = (k Z_{k-1} - R_k)\,u + R_k$ with $u(0) = 0$, and the series $k Z_{k-1} - R_k$ and $R_k$ are $\succeq 0$; hence $u \succeq 0$, and $Y_0' = u\,L_0'$ with $Y_0(0) = 0$. In each case the conclusion comes from one principle: a series $F$ with $F(0) \ge 0$ and $F' = G F + S$, where $G \succeq 0$ and $S \succeq 0$, is $\succeq 0$.

Multiply (D3) by $Z_k$. Since $Z_k (1-K) = 1$ (`Parking.Zs_mul_one_sub_Ks`),
$$D \;=\; (L_+ - L_0)\, Z_k \;+\; Z_k\, Y_+ \;+\; Z_k\, Y_0 .$$
The series $Z_k$ is $\succeq 0$ (`Parking.zr_nonneg`), and a product of two series $\succeq 0$ is $\succeq 0$; hence $Z_k Y_+ \succeq 0$ and $Z_k Y_0 \succeq 0$.

Now take the coefficient of $X^n$. On the left it is $\delta_n$, because $b(n,\ell)/n! = z^{(\ell+1)}_n - z^{(\ell)}_n$ for $\ell \ge 1$ (`Parking.bq_eq`, for $\ell = k$ and $\ell = k-1$). The coefficient of $X^t$ in $L_+ - L_0 = \Gamma_{k+1} - 2\Gamma_k + \Gamma_{k-1}$ is $\xi_t$, by the definition of `Parking.xi` and of $\Gamma_y$, so the coefficient of $X^n$ in $(L_+ - L_0)\, Z_k$ is $\sum_{t=0}^{n} \xi_t\, z^{(k)}_{n-t}$ (`Parking.TreeSeries.coeff_mul_range`, `Parking.coeff_Zs`). The other two coefficients are nonnegative. This gives $\delta_n \ge \sum_{t=0}^{n} \xi_t\, z^{(k)}_{n-t}$.
