---
weight: unit
short: persistence on the near rows, up to k + 0.47k
---
## Description

Let $k \ge 42$. If $d_{j,k} = b(j,k) - b(j,k-1)$ is nonpositive on the rows $k \le j < q$ and positive on the rows $q \le j < n$, where $q = k + r_q$, $n = q + t$, $r_q, t \ge 1$ and $n - k \le 0.47k$, then $d_{n,k} > 0$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`), and $d_{j,k} = b(j,k) - b(j,k-1)$. Let $k \ge 42$, $r_q \ge 1$ and $t \ge 1$ be natural numbers with $100\,(r_q + t) \le 47\,k$. Assume

- $d_{j,k} \le 0$ for every $j$ with $k \le j < k + r_q$, and
- $d_{j,k} > 0$ for every $j$ with $k + r_q \le j < k + r_q + t$.

Then $d_{k+r_q+t,\,k} > 0$.

The Lean statement is written with the normalised step $\delta_j = d_{j,k}/j!$ (`Parking.dq`, as `dq k j`), which has the same sign as $d_{j,k}$.

## Explanation

This is the first of the two regimes in the proof that a column $k \ge 82$ stays positive after its first positive row (`Parking.persist`). It covers the target rows $n = k + r$ with offset $r \le 0.47k$, and it is the only argument available for the rows immediately after the crossing row $q$, because it makes no demand on the length $t$ of the positive run before $n$.

The proof places the parking column into the abstract statement `Parking.two_point`. Three properties of the tilted prime kernel $\kappa_m = \varepsilon_m/\gamma_k^m$ are required there. Log-convexity holds for all indices. Monotonicity holds for indices up to $\frac35k$ (`Parking.kapx_succ_le`). The two-point condition is $(k+r)\kappa_r \le (k+r_q)\kappa_{r_q}$, and the library obtains it from the monotonicity of $\rho \mapsto (k+\rho)\kappa_\rho$, which is proved for $\rho \le 0.47k$ and $k \ge 42$ (`Parking.Fk_anti`). The bound $0.47k$ on the offset of the target row, and the hypothesis $k \ge 42$, are those of that statement; the record of `Parking.Fk_anti` explains why $0.47$ is essentially the end of the range in which this monotonicity holds. Rows with larger offset are the subject of `Parking.caseFar`.

All rows involved lie in the chain range $k+1 \le j \le 2k-1$ of the column, where the column equation `Parking.dq_col` is available.

## Proof

Let $x = 1/\gamma_k$ be the diagonal tilt (`Parking.xk`), $\gamma_k = (1+1/k)^{k-2}$, and put

$$\eta_j = x^j\,\delta_j, \qquad U_j = x^j\,\beta^{(k-1)}_j, \qquad \kappa_m = x^m\varepsilon_m,$$

where $\delta_j = d_{j,k}/j!$, $\beta^{(k-1)}_j = b(j,k-1)/j!$ (`Parking.bq`) and $\varepsilon$ is the prime kernel of `Parking.eps`; these are `Parking.stepD`, `Parking.profD` and `Parking.kapx`. Since $x > 0$ (`Parking.CrossCrit.xk_pos`), $\eta_j$ has the sign of $d_{j,k}$. We verify the hypotheses of `Parking.two_point` for these sequences, with $q = k + r_q$, $n = q + t$, $c_j = 2x/j$ and $\varphi_j = (k+1)x/j$ for $j \in \{q, n\}$; its conclusion $\eta_n > 0$ is the claim.

*Column equation.* For $k+1 \le j \le 2k-1$, `Parking.dq_col` states $\delta_j = \frac{k+1}{j}\delta_{j-1} + \frac2j\beta^{(k-1)}_{j-1} + \sum_{m=1}^{j-k}\varepsilon_m\delta_{j-m}$. Multiplying by $x^j = x\cdot x^{j-1} = x^m x^{j-m}$ gives

$$\eta_j = \frac{2x}{j}\,U_{j-1} + \frac{(k+1)x}{j}\,\eta_{j-1} + \sum_{m=1}^{j-k}\kappa_m\,\eta_{j-m}.$$

The rows $q$ and $n$ satisfy $k + 1 \le q < n \le 1.47k \le 2k-1$. The coefficients $c_q$, $\varphi_q$ are nonnegative and $\varphi_n$ is positive.

*Bottom row.* $\beta^{(k)}_k = 0$ by `Parking.bq_eq_zero` (no parking function of length $k$ has a displacement $k$), so $\delta_k = -\beta^{(k-1)}_k$ and $\eta_k = -U_k$.

*Diagonal bound.* By `Parking.bq_diag_lower`, $\gamma_k\,\beta^{(k-1)}_{j-1} \le \beta^{(k)}_j$ for $j \ge 1$. Multiplying by $x^j$ and using $x\gamma_k = 1$ (`Parking.CrossCrit.xk_mul_gam`) gives $U_{j-1} \le x^j\beta^{(k)}_j$, that is, $U_{j-1} - U_j \le \eta_j$. This is the purpose of the diagonal tilt: it removes the factor $\gamma_k$ from the diagonal bound.

*Profile and kernel.* $U_j \ge 0$ since $\beta^{(k-1)}_j \ge 0$. The kernel is positive (`Parking.kapx_pos`); it satisfies $\kappa_{m+1} \le \kappa_m$ for $m + 1 \le r_q + t$ by `Parking.kapx_succ_le`, whose hypothesis $5(m+1) \le 3k$ follows from $m + 1 \le 0.47k$; and it satisfies the cross inequality by `Parking.kapx_cross`.

*Two-point condition.* It reads $\kappa_{r_q+t}\cdot\frac{2x}{q} \le \kappa_{r_q}\cdot\frac{2x}{n}$, which after multiplication by $qn/(2x)$ is $(k + r_q + t)\,\kappa_{r_q+t} \le (k+r_q)\,\kappa_{r_q}$. This is `Parking.Fk_anti` with $a = r_q$ and $b = r_q + t$, whose hypothesis is $100\,b \le 47\,k$.

*Signs.* They are the two assumptions, multiplied by $x^j > 0$.
