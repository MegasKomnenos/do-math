---
weight: unit
short: lower bound for the mean number of cuts
---
## Description

For $r \ge 1$ and $0 < h \le 1$, the mean number of cuts $\mu_r(h)$ of the compositions of $r$ with constant cut weight $h$ is at least $\mu^0_r(X) = \bigl(\sqrt{(4+X)^2 + 12(r-1)} - (4+X)\bigr)/3$ with $X = r(1/h - 1)$.

## Statement

For every natural number $r \ge 1$ and every real number $h$ with $0 < h \le 1$,

$$\mu^0_r\bigl(r\,(1/h - 1)\bigr) \;\le\; \mu_r(h).$$

Here $\mu_r(h) = \bigl(\sum_{q=1}^{r}(q-1)\,T_{r,q}\,h^{q-1}\bigr)/\tau_r(h)$ is the mean number of cuts of a composition of $r$ when a part of size $p$ weighs $a_p = p^{p-1}/p!$ and every cut weighs $h$ (`Parking.muh`, with $T_{r,q}$ from `Parking.Tq` and $\tau_r(h) = \sum_{q=1}^{r} T_{r,q}\,h^{q-1}$ from `Parking.tau`), and

$$\mu^0_r(X) \;=\; \frac{\sqrt{(4+X)^2 + 12\,(r-1)} - (4+X)}{3}$$

(`Parking.mu0`).

## Explanation

**What the bound is.** The number $\mu = \mu^0_r(X)$ is the nonnegative solution of $\frac32\mu^2 + (4+X)\,\mu = 2(r-1)$. What the proof establishes is the quadratic inequality

$$2\,(r-1) \;\le\; \tfrac32\,\mu_r(h)^2 + (4+X)\,\mu_r(h), \qquad X = r\,(1/h - 1),$$

and the statement is its solution for $\mu_r(h)$. The bound is explicit in $r$ and $h$, which is what the criterion needs: the exact mean is a quotient of two sums of $r$ terms.

**Where the quadratic inequality comes from.** Let $J$ be the number of cuts of a composition of $r$ drawn with probability proportional to its weight with cut weight $h$, so that $\mu_r(h) = \mathbb{E}[J]$. By `Parking.Tq_eq` the compositions with $j$ cuts have the total weight $a_r\,(j+1)\,v_j$ with $v_j = h^{j} P_{r,j+1}$, where $P_{r,j}$ is the birthday tail (`Parking.Pb`). Two facts about this law are combined.

The first is an exact identity. The recursion $P_{r,j+2} = P_{r,j+1}(1 - \frac{j+1}{r})$ relates the weights of $j+1$ and of $j$ cuts by a factor that is a polynomial in $j$, and summing it over $j$ gives

$$\mathbb{E}[J^2] + (3+X)\,\mathbb{E}[J] \;=\; 2\,(r-1).$$

The second is an inequality, $\mathbb{E}[J(J-1)] \le \frac32\,\mathbb{E}[J]^2$, and it is the step that needs an idea. The factor $j+1$ in the weight of $j$ cuts is the number of ways of writing $j = i + l$ with nonnegative integers $i$ and $l$. So $J$ has the law of $I + L$ for a pair $(I, L)$ with weight $v_{i+l}$. The sequence $v_j$ is log-concave, because its consecutive ratios $h\,(1 - \frac{j+1}{r})$ decrease, and for a weight of the form $v_{i+l}$ with log-concave $v$ the two coordinates are negatively correlated: $\mathbb{E}[IL] \le \mathbb{E}[I]\,\mathbb{E}[L]$. Since $\sum_{i+l=j} i\,l = (j-1)j(j+1)/6$ and $\sum_{i+l=j} i = j(j+1)/2$, this reads $\frac16\,\mathbb{E}[J(J-1)] \le \frac14\,\mathbb{E}[J]^2$.

Since $\mathbb{E}[J^2] = \mathbb{E}[J(J-1)] + \mathbb{E}[J]$, the identity can be written $2(r-1) = \mathbb{E}[J(J-1)] + (4+X)\,\mathbb{E}[J]$, and inserting the inequality gives $2(r-1) \le \frac32\mu^2 + (4+X)\,\mu$ with $\mu = \mathbb{E}[J] = \mu_r(h)$.

**An example.** For $h = 1$ we have $X = 0$ and $\mu_r(1) = s_r - 1$, with $s_r$ the mean of the birthday law (`Parking.sbirth`). For $r = 3$ the number of cuts takes the values $0, 1, 2$ with probabilities $\frac13, \frac49, \frac29$, so $\mu_3(1) = \frac89$, while $\mu^0_3(0) = (\sqrt{40} - 4)/3 \approx 0.775$. The identity reads $\frac{12}{9} + 3\cdot\frac{8}{9} = 4$, and the inequality reads $\frac49 \le \frac32\cdot\frac{64}{81}$.

**Where it is used.** The proof of the criterion `Parking.step_neg_of_Gfun` applies the bound twice: at $h = (k-1)/(k+r)$, where $X = r(r+1)/(k-1)$, for the mean that appears in `Parking.Lam_shorten`, and at $h = k/(k+1+r/2)$, where $X = r(r+2)/(2k)$, for the mean that appears in `Parking.Lam_raise`. These are the two arguments of $\mu^0_r$ in the criterion function `Parking.Gfun`.

**The hypotheses.** The hypothesis $h > 0$ is needed for $1/h$ and for dividing the combined inequality by $h$. The hypothesis $h \le 1$ gives $X \ge 0$, which is used in the last step to know the sign of $3\mu + 4 + X$.

## Proof

Fix $r \ge 1$ and $0 < h \le 1$, and write $\mu = \mu_r(h)$ and $X = r(1/h - 1)$. For $j \ge 0$ put

$$v_j = h^{j}\,P_{r,j+1},$$

with $P_{r,j}$ the birthday tail (`Parking.Pb`). Then $v_j \ge 0$ (`Parking.Pb_nonneg`), $v_j = 0$ for $j \ge r$ (`Parking.Pb_eq_zero`), and $v_{j+1} = \rho_j\,v_j$ with $\rho_j = h\,(1 - \frac{j+1}{r})$ (`Parking.Pb_succ`). Put

$$M_0 = \sum_{j=0}^{r-1}(j+1)\,v_j, \qquad M_1 = \sum_{j=0}^{r-1} j\,(j+1)\,v_j, \qquad M_2 = \sum_{j=0}^{r-1} j^2\,(j+1)\,v_j.$$

**Step 0: the mean in terms of these sums.** By `Parking.tau_eq` and `Parking.Tq_eq`, with $q = j+1$, $\tau_r(h) = a_r\,M_0$; by `Parking.muh_mul_tau` and `Parking.Tq_eq`, $\mu\,\tau_r(h) = a_r\,M_1$. Since $a_r > 0$ (`Parking.cay_pos`) and $\tau_r(h) > 0$ (`Parking.tau_pos`), it follows that $M_0 > 0$ and $\mu\,M_0 = M_1$.

**Step 1: the recursion.** We show

$$r\,M_1 \;=\; h\,\bigl(2(r-1)\,M_0 + (r-3)\,M_1 - M_2\bigr).$$

The term with $j = 0$ of $M_1$ is zero and $v_r = 0$, so shifting the index gives $M_1 = \sum_{j=0}^{r-1}(j+1)(j+2)\,v_{j+1}$. For each $j$, the relation $v_{j+1} = \rho_j v_j$ gives

$$r\,(j+1)(j+2)\,v_{j+1} \;=\; h\,(j+1)(j+2)(r-1-j)\,v_j \;=\; h\,(j+1)\,v_j\,\bigl(2(r-1) + (r-3)\,j - j^2\bigr),$$

and summing over $0 \le j \le r-1$ gives the claim.

**Step 2: negative correlation.** We show

$$\tfrac16\,(M_2 - M_1)\,M_0 \;\le\; \tfrac14\,M_1^2 .$$

*(i) Log-concavity.* For all natural numbers $d$ and $a \le b$, $v_a\,v_{b+d} \le v_{a+d}\,v_b$. This holds for every sequence $v \ge 0$ with $v_{j+1} = \rho_j v_j$ and $\rho$ nonincreasing, by induction on $d$. For $d = 0$ the two sides are equal. For the step, $v_a\,v_{b+d+1} = \rho_{b+d}\,v_a\,v_{b+d}$. If $\rho_{b+d} \ge 0$, the induction hypothesis and $\rho_{b+d} \le \rho_{a+d}$ give $\rho_{b+d}\,v_a\,v_{b+d} \le \rho_{b+d}\,v_{a+d}\,v_b \le \rho_{a+d}\,v_{a+d}\,v_b = v_{a+d+1}\,v_b$. If $\rho_{b+d} < 0$, then $v_{b+d+1} = \rho_{b+d}\,v_{b+d}$ is both nonpositive and nonnegative, hence $0$, and the left-hand side is $0$ while the right-hand side is nonnegative. Here $\rho_j = h(1 - \frac{j+1}{r})$ is nonincreasing because $h \ge 0$.

*(ii) Sums along diagonals.* Let $g$ be a function of two natural numbers. Because $v_j = 0$ for $j \ge r$,

$$\sum_{i=0}^{r-1}\sum_{l=0}^{r-1} v_{i+l}\;g(i,l) \;=\; \sum_{j=0}^{r-1} v_j \sum_{i=0}^{j} g(i, j-i).$$

The inner sum is $j+1$ for $g = 1$, it is $j(j+1)/2$ for $g(i,l) = l$ and for $g(i,l) = i$, and it is $(j-1)\,j\,(j+1)/6$ for $g(i,l) = i\,l$. Writing $\Sigma[g]$ for the double sum, we get

$$\Sigma[1] = M_0, \qquad \Sigma[l] = \Sigma[i] = \tfrac12 M_1, \qquad \Sigma[i\,l] = \tfrac16\,(M_2 - M_1).$$

*(iii) Two applications of the weighted Chebyshev inequality.* For $0 \le i \le r-1$ put $U(i) = \sum_{l=0}^{r-1} v_{i+l}\;l$ and $W(i) = \sum_{l=0}^{r-1} v_{i+l}$. Let $i \le i'$. For $l \le l'$, (i) with $a = i+l$, $b = i'+l$ and $d = l'-l$ gives $v_{i'+l'}\,v_{i+l} \le v_{i'+l}\,v_{i+l'}$. This is the first hypothesis of `Parking.lr_sum_le_finset` on the set $\{0, \dots, r-1\}$ for the functions $l \mapsto v_{i'+l}$ and $l \mapsto v_{i+l}$, and with $\varphi(l) = l$ that statement gives

$$U(i')\,W(i) \;\le\; U(i)\,W(i') \qquad (i \le i').$$

This in turn is the first hypothesis of `Parking.lr_sum_le_finset` for the functions $U$ and $W$, and with $\varphi(i) = i$ it gives

$$\Bigl(\sum_{i} U(i)\;i\Bigr)\Bigl(\sum_{i} W(i)\Bigr) \;\le\; \Bigl(\sum_{i} W(i)\;i\Bigr)\Bigl(\sum_{i} U(i)\Bigr),$$

that is, $\Sigma[i\,l]\;\Sigma[1] \le \Sigma[i]\;\Sigma[l]$. By (ii) this is the claim of Step 2.

**Step 3: the quadratic inequality.** Multiply Step 2 by $6h \ge 0$ to get $h\,(M_2 - M_1)\,M_0 \le \frac32\,h\,M_1^2$, and replace $h\,M_2$ by its value from Step 1, $h\,M_2 = h\,(2(r-1)M_0 + (r-3)M_1) - r\,M_1$. The result is

$$0 \;\le\; \tfrac32\,h\,M_1^2 + (4h + r - rh)\,M_1 M_0 - 2\,(r-1)\,h\,M_0^2 .$$

Divide by $h\,M_0^2 > 0$ and use $M_1 = \mu\,M_0$ and $(4h + r - rh)/h = 4 + X$:

$$2\,(r-1) \;\le\; \tfrac32\,\mu^2 + (4+X)\,\mu .$$

**Step 4: solving for $\mu$.** Six times the last inequality is $(4+X)^2 + 12(r-1) \le (3\mu + 4 + X)^2$. Since $h \le 1$ we have $X \ge 0$, and $\mu \ge 0$ by `Parking.muh_nonneg`, so $3\mu + 4 + X \ge 0$ and therefore $\sqrt{(4+X)^2 + 12(r-1)} \le 3\mu + 4 + X$. This is $\mu^0_r(X) \le \mu$.
