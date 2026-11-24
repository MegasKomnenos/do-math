---
weight: unit
short: persistence on the far rows, beyond k + 0.47k
---
## Description

Let $k \ge 82$. If $d_{j,k} = b(j,k) - b(j,k-1)$ is positive on the rows $k + r_q \le j < k + r$, where $r_q \le k/3$ and $0.47k < r \le k-1$, then $d_{k+r,k} > 0$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`), and $d_{j,k} = b(j,k) - b(j,k-1)$. Let $k \ge 82$, $r$ and $r_q$ be natural numbers with

$$47\,k < 100\,r, \qquad r + 1 \le k, \qquad 3\,r_q \le k.$$

Assume $d_{j,k} > 0$ for every $j$ with $k + r_q \le j < k + r$. Then $d_{k+r,\,k} > 0$.

The Lean statement is written with the normalised step $\delta_j = d_{j,k}/j!$ (`Parking.dq`, as `dq k j`), which has the same sign as $d_{j,k}$.

## Explanation

This is the second of the two regimes in the proof that a column $k \ge 82$ stays positive after its first positive row (`Parking.persist`); the first is `Parking.caseA`. The target row is $n = k + r$, and $r$ is called its offset.

**Why a different argument is needed and why it is available.** The two-point argument of `Parking.caseA` stops at the offset $0.47k$ (see `Parking.Fk_anti`). Beyond it the proof uses the persistence inequality `Parking.persistence_inequality`, which bounds $\delta_n$ from below by the profile $u_j = b(j,k-1)/j!$ of the level $k-1$:

$$\delta_n \ge \Bigl(\frac2n - \psi\Bigr)u_{n-1} + \sum_{m=t_0+1}^{r-1}\bigl(\gamma_k\varepsilon_m - \varepsilon_{m+1}\bigr)u_{n-1-m}, \qquad \psi = \varepsilon_{t_0+1}\,\gamma_k^{-t_0}.$$

It requires the column to be nonnegative on the $t_0$ rows before $n$, and the loss $\frac n2\psi$ is below $1$ only if $t_0$ is large; with $t_0$ proportional to $k$ it is of the order $k^{-1/2}$. Such a run is not available just after the crossing, which is why the near rows need the two-point argument. It is available here: the rows $k + r_q,\dots,n-1$ are positive, $r_q \le k/3$ and $r > 0.47k$, so the run has more than $(0.47 - \frac13)k = \frac{41}{300}k$ rows. This is the only use of the hypothesis $r_q \le k/3$, and nothing is assumed about the rows before $k + r_q$.

**The three regimes.** The sign of the coefficient $\gamma_k\varepsilon_m - \varepsilon_{m+1}$ is that of $\gamma_k - g_m$, with $g_m = \varepsilon_{m+1}/\varepsilon_m$ (`Parking.gs`): it is nonnegative for $m + 1 \le \frac35k$ (`Parking.eps_succ_le_gam`) and may be negative beyond.

- *Regime B, $0.47k < r \le \frac35k$.* All coefficients of the sum are nonnegative, the sum is dropped, and only $\frac n2\psi < 1$ has to be shown.
- *Regime α, $\frac35k < r \le \frac45k$,* and *regime β, $\frac45k < r \le k-1$.* The terms with $m \ge M = \lfloor\frac35k\rfloor$ form a far feedback that may be negative. All that is known about the profile $u$ is that it satisfies the column equation of the level $k-1$ with a nonnegative source. In the Borel scale this makes $v_\sigma = e^{-\sigma}u_{k+\sigma}$ a sequence with nonnegative innovations with respect to the frozen kernel $f$ (`Parking.fker`), and the extreme-column bound `Parking.extreme_column_le` bounds the far feedback, relative to $u_{n-1}$, by its value for the renewal sequence $G$ of $f$ (`Parking.Gres`). The result is $\frac n2\cdot(\text{far feedback}) \le q\cdot u_{n-1}$ with an explicit $q$, and positivity follows from $p + q < 1$, where $p \ge \frac n2\psi$.

The far feedback grows with $r$: its bound is proportional to $(k+r)\,r^{3/2}/k^{5/2}$. In regime β its bound takes half of the source or more ($q = 0.5$ or $0.56$), so the loss $p$ must be smaller than in regime α. This is possible because the positive run is longer there (more than $(\frac45 - \frac13)k = \frac7{15}k$ rows against $\frac4{15}k$), and it is the reason for separating α from β. Inside β the columns $82 \le k \le 109$ need one more refinement: the bound $\sum G_i \le 2e$ of `Parking.Gres_sum_le` is replaced by $1.747\,e$, obtained by subtracting a tail.

**The upper end.** The upper end $r \le k-1$, the row $2k-1$, is the end of the chain range: the column equation `Parking.dq_col` holds for $k+1 \le n \le 2k-1$, the column equation `Parking.bq_L0` of the level $k-1$ holds up to the row $2k-1$, and the coefficient $\frac{k-1}{j}$ of the latter is at least $\frac12$, the value frozen into $f$, only for $j \le 2k-2$.

**The constants.** In each regime the cut is $t_0 = \lfloor\sigma k\rfloor + 1$, where $\sigma$ is the lower end of the regime minus $\frac13$. The table lists the parameters with which `Parking.P1_le` (near term; it is the bound `Parking.near_term_le`, with $L = c$, compared with $p$) and the far bound are applied; $n \le ck$, $E_0 \ge e^{5\sigma}$, $\sum_{i\le\rho-M}G_i \le S\,e$, $r \le c'^2k$, $r \ge r_0$. The last column is the range of $k$ in which the numerical hypothesis of `Parking.P1_le` holds for the listed $p$.

| regime | offsets | $\sigma$ | $c$ | $E_0$ | $\lambda$ | $p$ | $S$ | $c'$ | $r_0$ | $q$ | $p+q$ | near term needs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B | $0.47k < r \le \frac35k$ | $\frac{41}{300}$ | $\frac85$ | $2$ | $1$ | $0.99$ | – | – | – | – | $0.99$ | $k \ge 81.47$ |
| α | $\frac35k < r \le \frac45k$ | $\frac4{15}$ | $\frac95$ | $3.8$ | $1$ | $0.57$ | $2$ | $0.8945$ | $50$ | $0.385$ | $0.955$ | $k \ge 79.56$ |
| β, $k \le 109$ | $\frac45k < r \le k-1$ | $\frac7{15}$ | $2$ | $10.32$ | $1.011$ | $0.455$ | $1.747$ | $1$ | $66$ | $0.50$ | $0.955$ | $k \ge 79.84$ |
| β, $k \ge 110$ | $\frac45k < r \le k-1$ | $\frac7{15}$ | $2$ | $10.32$ | $1.011$ | $0.395$ | $2$ | $1$ | $89$ | $0.56$ | $0.955$ | $k \ge 105.93$ |

The threshold $k \ge 82$ is where this bookkeeping closes. Regime B requires $k \ge 81.47$; and from $k = 82$ on one has $\lfloor\frac35k\rfloor \ge 49$, which `Parking.theta_f_le` needs, and $r \ge 50$ in regime α. The constants are not sharp, and the statement is not claimed to fail for smaller $k$; the columns $k \le 81$ are handled by a table (`Parking.Tab.small_table`).

## Proof

Throughout, $n = k + r$, $\delta_j = d_{j,k}/j!$, $u_j = \beta^{(k-1)}_j = b(j,k-1)/j!$ (`Parking.bq`), $\varepsilon$ is the prime kernel (`Parking.eps`), $\gamma = \gamma_k = (1+1/k)^{k-2}$ (`Parking.gam`) and $x = 1/\gamma$ (`Parking.xk`). The proof first derives two structural inequalities, (N) for $r \le \frac35k$ and (F) for $r > \frac35k$, and then closes each regime numerically.

### 1. The persistence inequality for the parking column

Let $t_0 \ge 1$ with $t_0 + 1 \le r$ and $5(t_0+1) \le 3k$, and suppose $\delta_j \ge 0$ for $n - t_0 \le j < n$. Then, with $\psi = \varepsilon_{t_0+1}x^{t_0}$,

$$\Bigl(\frac2n - \psi\Bigr)u_{n-1} + \sum_{m=t_0+1}^{r-1}\bigl(\gamma\varepsilon_m - \varepsilon_{m+1}\bigr)u_{n-1-m} \le \delta_n.$$

This inequality is called (P) below. It is `Parking.persistence_inequality` with the cut $\tau = t_0 + 1$. Its hypotheses hold: the column equation at $n$ is `Parking.dq_col` (valid since $k+1 \le n \le 2k-1$); the diagonal lower bound $\gamma u_{j-1} - u_j \le \delta_j$ is `Parking.dq_diag_lower`; $u_{k-1} = 0$ by `Parking.bq_eq_zero`; $\varepsilon_m > 0$ by `Parking.eps_pos`; and $\varepsilon_{m+1} \le \gamma\varepsilon_m$ for $m < \tau$ by `Parking.eps_succ_le_gam`, because $5(m+1) \le 5(t_0+1) \le 3k$.

### 2. The cut

The three regimes have the lower ends $r > \frac{47}{100}k$, $r > \frac35k$ and $r > \frac45k$. Put $\sigma = \frac{47}{100} - \frac13 = \frac{41}{300}$, $\sigma = \frac35 - \frac13 = \frac4{15}$ and $\sigma = \frac45 - \frac13 = \frac7{15}$ respectively, and $t_0 = \lfloor\sigma k\rfloor + 1$. From $3r_q \le k$ one gets $r - r_q > \sigma k$, hence $r - r_q \ge t_0$, so the rows $n - t_0,\dots,n-1$ lie in $[k + r_q, n)$ and are positive by assumption. Moreover $\sigma k \le t_0 \le \sigma k + 1$, and in all three cases $t_0 + 1 \le r$ and $5(t_0 + 1) \le 3k$, since $k \ge 82$. So (P) holds with this $t_0$.

### 3. Positivity of the profile

For $l \ge 1$ and $l + 1 \le j \le 2l+1$, $\beta^{(l)}_j > 0$. This follows by induction on $j$ from the column equation `Parking.bq_L0`, $\beta^{(l)}_j = z^{(l+1)}_{j-1}/j + \frac lj\beta^{(l)}_{j-1} + \sum_{m=1}^{j-l-1}\varepsilon_m\beta^{(l)}_{j-m}$, where $z^{(l+1)}_{j-1} = A(j-1,l)/(j-1)! \ge 0$ is the normalised count of `Parking.zr`. All terms are nonnegative: at $j = l+1$ the first term is $c_l/(l+1) > 0$ (`Parking.zr_eq_cc`, `Parking.cc_pos`), and for larger $j$ the second term is positive by induction. With $l = k-1$: $u_{n-1} > 0$, since $k \le n-1 \le 2k-1$.

### 4. Regime B: $0.47k < r \le \frac35k$

Every index $m \le r-1$ of the sum in (P) satisfies $5(m+1) \le 5r \le 3k$, so every coefficient is nonnegative by `Parking.eps_succ_le_gam`, and (P) gives

$$\Bigl(\frac2n - \psi\Bigr)u_{n-1} \le \delta_n.$$

This is the inequality (N). `Parking.P1_le` with $\sigma = \frac{41}{300}$, $c = \frac85$ (as $n \le \frac85k$), $E_0 = 2$ (`Parking.exp_41_60`), $\lambda = 1$ and $p = 0.99$ gives $\frac n2\psi \le 0.99$; its numerical hypothesis $(\frac85)^2\cdot2 \le 0.99^2\cdot8\cdot3.14\cdot(\frac{41}{300})^3k$ holds for $k \ge 82$. Hence $\frac2n - \psi > 0$, and with $u_{n-1} > 0$, $\delta_n > 0$.

### 5. The structural inequality for $r > \frac35k$

Write $r = \rho + 1$ and $M = \lfloor\frac35k\rfloor$, so that $49 \le M \le \rho \le k-2$, and $B_k = 1.05\,c_0\,k^{-5/2}$ with $c_0 = 1/\sqrt{2\pi}$ (`Parking.c0`). Let $f$ be the frozen kernel (`Parking.fker`) and $G$ its renewal sequence (`Parking.Gres`, `Parking.Gres_isRenewal`). The claim is

$$\Bigl[\Bigl(\frac2n - \psi\Bigr)G_\rho - B_k\sum_{i=0}^{\rho-M}G_i\Bigr]\,u_{n-1} \le \delta_n\,G_\rho,$$

which is called (F) below.

*Splitting the sum.* In (P) the terms with $t_0 + 1 \le m \le M-1$ have nonnegative coefficients, as in regime B, and are dropped. For $m \ge M$ put $\theta_m = \max(g_m - \gamma, 0)$, where $g_m = \varepsilon_{m+1}/\varepsilon_m$ (`Parking.gs`, `Parking.eps_step`); then $\gamma\varepsilon_m - \varepsilon_{m+1} \ge -\theta_m\varepsilon_m$. Hence

$$\Bigl(\frac2n - \psi\Bigr)u_{n-1} - S_1 \le \delta_n, \qquad S_1 = \sum_{m=M}^{\rho}\theta_m\,\varepsilon_m\,u_{n-1-m}.$$

*Innovations of the profile.* Let $v_\sigma = e^{-\sigma}u_{k+\sigma}$. For $\sigma \le k-2$,

$$\sum_{i=1}^{\sigma}f_i\,v_{\sigma-i} \le v_\sigma.$$

For $\sigma = 0$ this is $v_0 \ge 0$. For $\sigma \ge 1$, `Parking.bq_L0` at the level $k-1$ and the row $k + \sigma$ reads $u_{k+\sigma} = \frac{z}{k+\sigma} + \frac{k-1}{k+\sigma}u_{k+\sigma-1} + \sum_{m=1}^{\sigma}\varepsilon_mu_{k+\sigma-m}$ with $z = z^{(k)}_{k+\sigma-1} \ge 0$ (`Parking.zr_nonneg`). Since $\sigma \le k-2$, $\frac{k-1}{k+\sigma} \ge \frac12$. Dropping the source and multiplying by $e^{-\sigma}$ gives $v_\sigma \ge \frac12e^{-1}v_{\sigma-1} + \sum_{m=1}^{\sigma}e^{-m}\varepsilon_mv_{\sigma-m}$, which is the claim by the definition of $f$.

*The extreme column.* The weights $\theta$ are nonnegative and nondecreasing, because $g$ is nondecreasing (`Parking.gs_mono`). The kernel $f$ is positive and log-convex (`Parking.fker_pos`, `Parking.fker_logconvex`). So `Parking.extreme_column_le` applies to $f$, $G$, $v$, $\theta$, $\rho$ and $M$:

$$\Bigl(\sum_{m=M}^{\rho}\theta_mf_mv_{\rho-m}\Bigr)G_\rho \le \Bigl(\sum_{m=M}^{\rho}\theta_mf_mG_{\rho-m}\Bigr)v_\rho.$$

For $m \ge M \ge 2$, $f_mv_{\rho-m} = e^{-m}\varepsilon_m\cdot e^{-(\rho-m)}u_{k+\rho-m} = e^{-\rho}\varepsilon_mu_{n-1-m}$ (`Parking.fker_of_two_le`), and $v_\rho = e^{-\rho}u_{n-1}$. Cancelling $e^{-\rho}$: $S_1\,G_\rho \le \bigl(\sum_{m=M}^{\rho}\theta_mf_mG_{\rho-m}\bigr)u_{n-1}$.

*The weights against the kernel.* For $M \le m \le \rho$ we have $m \ge 49$, $m + 1 \le k$ and $3k < 5(m+1)$, so `Parking.theta_f_le` gives $\theta_mf_m \le B_k$ (when $\theta_m = 0$ the bound is trivial). With $G > 0$ (`Parking.Gres_pos`), $\sum_{m=M}^{\rho}\theta_mf_mG_{\rho-m} \le B_k\sum_{i=0}^{\rho-M}G_i$.

Multiplying $(\frac2n - \psi)u_{n-1} - S_1 \le \delta_n$ by $G_\rho > 0$ and inserting the two bounds gives (F).

### 6. Closing the far regimes

Suppose that for real numbers $p$, $q$ with $p + q < 1$,

$$\frac n2\,\psi \le p \qquad\text{and}\qquad \frac n2\,B_k\sum_{i=0}^{\rho-M}G_i \le q\,G_\rho.$$

Then $\frac n2\bigl[(\frac2n - \psi)G_\rho - B_k\sum G_i\bigr] \ge (1 - p - q)G_\rho > 0$, so the bracket of (F) is positive, and with $u_{n-1} > 0$ (Step 3) and $G_\rho > 0$, (F) gives $\delta_n > 0$.

The first bound comes from `Parking.P1_le`. The second is obtained as follows from four numbers $S$, $c'$, $r_0 \ge 6$, $q \ge 0$ with $\sum_{i\le\rho-M}G_i \le S\,e$, $r \le c'^2k$, $r \ge r_0$ and

$$1.05\cdot S\cdot(1 + c'^2)\,c'^3 \le 2q\,D, \qquad D = \Bigl(1 - \frac1{12r_0}\Bigr)\Bigl(4 - \frac{21}{r_0}\Bigr).$$

By `Parking.Gres_lower` at $s = \rho$ (so $s + 1 = r$), $G_\rho \ge e\,c_0\,r^{-3/2}\bigl(1 - \frac1{12r}\bigr)\bigl(4 - \frac{21}r\bigr)$, and the product of the two brackets is nondecreasing in $r \ge 6$, hence at least $D$. From $r \le c'^2k$: $(k + r)\,r^{3/2} \le (1 + c'^2)c'^3\,k^{5/2}$. Therefore

$$\frac n2\,B_k\sum G_i \le \frac{k+r}{2}\cdot\frac{1.05\,c_0}{k^{5/2}}\cdot S\,e \le \frac{1.05\,S\,(1+c'^2)c'^3}{2}\cdot\frac{e\,c_0}{r^{3/2}} \le q\,D\,\frac{e\,c_0}{r^{3/2}} \le q\,G_\rho.$$

### 7. Regime α: $\frac35k < r \le \frac45k$

Here $t_0 = \lfloor\frac4{15}k\rfloor + 1$, $n \le \frac95k$, and `Parking.P1_le` with $\sigma = \frac4{15}$, $c = \frac95$, $E_0 = 3.8$ (`Parking.exp_4_3`), $\lambda = 1$ gives $\frac n2\psi \le p = 0.57$; the numerical hypothesis $(\frac95)^2\cdot3.8 \le 0.57^2\cdot8\cdot3.14\cdot(\frac4{15})^3k$ holds for $k \ge 82$. For the far term take $S = 2$ (`Parking.Gres_sum_le`), $c' = 0.8945$ (as $r \le \frac45k \le 0.8945^2k$), $r_0 = 50$ (as $r > \frac35k \ge 49.2$) and $q = 0.385$; the condition of Step 6 reads $2.7056\ldots \le 2.7520\ldots$ Then $p + q = 0.955 < 1$.

### 8. Regime β: $\frac45k < r \le k-1$

Here $t_0 = \lfloor\frac7{15}k\rfloor + 1$, $n \le 2k$, and `Parking.P1_le` is applied with $\sigma = \frac7{15}$, $c = 2$, $E_0 = 10.32$ (`Parking.exp_7_3`) and $\lambda = 1.011$; the hypothesis $\sigma(k+3) \le \lambda(\sigma k + 1)$ holds for $k \ge 82$. Its numerical hypothesis is $1.011^2\cdot4\cdot10.32 \le p^2\cdot8\cdot3.14\cdot(\frac7{15})^3k$. For the far term $c' = 1$.

*Columns $k \ge 110$.* Take $p = 0.395$ (the numerical hypothesis holds for $k \ge 110$), $S = 2$, $r_0 = 89$ (as $r > \frac45k \ge 88$) and $q = 0.56$; the condition of Step 6 reads $4.2 \le 4.2117\ldots$, and $p + q = 0.955$.

*Columns $82 \le k \le 109$.* Take $p = 0.455$ (the numerical hypothesis holds for $k \ge 82$), $r_0 = 66$ (as $r > \frac45k \ge 65.6$) and $q = 0.5$. With $S = 2$ the condition of Step 6 would require $q \ge 0.571$, which exceeds $1 - p$, so the sum of $G$ is bounded more carefully. The number of its terms is $a = \rho - M + 1 = r - \lfloor\frac35k\rfloor$, and $17 \le a \le 43$ in this range of $k$ and $r$. For $i \ge 17$ the two brackets of `Parking.Gres_lower` at $s = i$ are at least $1 - \frac1{12\cdot18} = \frac{215}{216}$ and $4 - \frac{21}{18} = \frac{17}6$; with $c_0 \ge 0.39894$ (`Parking.c0_bounds`) and $0.39894\cdot\frac{215}{216}\cdot\frac{17}6 \ge 1.12$ this gives $G_i \ge 1.12\,e\,(i+1)^{-3/2}$. By `Parking.tail_sqrt` with $b + 1 = 16(a+1)$,

$$\sum_{i=a}^{b-1}G_i \ge 2\cdot1.12\,e\,\Bigl(\frac1{\sqrt{a+1}} - \frac1{4\sqrt{a+1}}\Bigr) = \frac{1.68\,e}{\sqrt{a+1}} \ge \frac{1.68\,e}{6.64} \ge 0.253\,e,$$

using $a + 1 \le 44 \le 6.64^2$. Since $\sum_{i<b}G_i \le 2e$ by `Parking.Gres_sum_le`, $\sum_{i<a}G_i \le (2 - 0.253)\,e$. So $S = 1.747$, and the condition of Step 6 reads $3.6687 \le 3.6771\ldots$; $p + q = 0.955$.

The three regimes cover all $r$ with $0.47k < r \le k-1$.
