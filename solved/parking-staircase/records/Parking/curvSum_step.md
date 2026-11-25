---
weight: unit
short: the curvature sum along the diagonal
---
## Description

One step along the diagonal, from the threshold $k$ and size $k+q$ to $k+1$ and $k+q+1$, multiplies the curvature sum of the compositions of $m$ by at most $\frac{k}{k+1}\exp\bigl((1+\frac1{400})(D_m+1)(q-\frac m2)/(k(k+1))\bigr)$, for $k \ge 1$, $2 \le m < q$ and $401\,m^2 \le 12\,k^2$.

## Statement

For real numbers $y$, $N$ and a natural number $m$ let $\Lambda_m(y;N)$ be the chain sum, the total weight of the compositions of $m$ in which a part of size $p$ weighs $a_p = p^{p-1}/p!$ and a cut at the position $s$ weighs $y/(N-s)$ (`Parking.Lam`, `Parking.thr`), and let

$$\mathsf C_m(y;N) = (y+1)\,\Lambda_m(y+1;N) - 2y\,\Lambda_m(y;N) + (y-1)\,\Lambda_m(y-1;N)$$

be the curvature sum (`Parking.curvSum`). Let $D_m$ be the moment ratio of the birthday law (`Parking.Dbirth`): $D_m = 3\bigl((m+2)s_m - 3m\bigr)/\bigl(2(m - s_m)\bigr)$ with $s_m = \sum_{j=1}^{m}\prod_{i<j}(1 - i/m)$.

Let $k$, $q$, $m$ be natural numbers with $k \ge 1$, $2 \le m$, $m + 1 \le q$ and $401\,m^2 \le 12\,k^2$. Then

$$\mathsf C_m(k+1;\,k+q+1) \;\le\; \frac{k}{k+1}\,\exp\!\Bigl(\frac{\bigl(1+\frac1{400}\bigr)(D_m+1)\bigl(q-\frac m2\bigr)}{k\,(k+1)}\Bigr)\;\mathsf C_m(k;\,k+q).$$

## Explanation

**Its place.** The diagonal step compares the step of the array at a position $(k+r,k)$ with the step at $(k+r+1,k+1)$. With $q = r+1$, the curvature terms of the two positions are $\sum_m \frac{\kappa_k(N-m)}{N-m}\,\mathsf C_m(k;N)$ with $N = k+q$ and the same with $k+1$, $N+1$ (`Parking.dq_curv_sub_boundary`). The present statement compares the two curvature sums for one $m$. It is one of the three comparisons along the diagonal that `Parking.term_step` multiplies together; the others concern the coefficient (`Parking.kap_diag_le`) and the boundary term (`Parking.Lam_gain`).

**What changes along the diagonal.** At a cut point $s$ of a composition of $m$ call $h_s = q - s > 0$ its height. The profile of the first position is $P(s) = k/(k+q-s) = 1/(1+h_s/k)$ and that of the second is $P'(s) = (k+1)/(k+q+1-s) = 1/(1+h_s/(k+1))$: two members of the family $P_u(s) = 1/(1+h_s u)$, at $u = 1/k$ and $u = 1/(k+1)$, whose member at $u = 0$ is the constant profile $1$. A step along the diagonal moves $u$ a little towards $0$, so every cut factor grows, by more at the cut points of large height. The factor $\frac{k}{k+1}$ of the statement comes from the normalisation of the curvature sum and is smaller than $1$; the exponential bounds the growth of the cut factors.

**How the growth is bounded.** The sum $g(u) = \sum_Q v_Q\,V_Q(m;P_u)$, for fixed weights $v_Q \ge 0$, is log-convex along the family, and $1/(k+1)$ lies between $0$ and $1/k$ at the fraction $k/(k+1)$. The chord of $\log g$ over these three points gives $g(\frac1{k+1})^{k+1} \le g(0)\,g(\frac1k)^k$. The value $g(0)$, for the profile $1$, is in turn bounded by $g(\frac1{k+1})$ divided by a power of a number $\rho < 1$: the profile $P'$ is not bounded below by a useful constant, but the product $P'(s)\,P'(m-s)$ is, by $\rho^2$ with $\rho = (k+1)/(k+1+q-\frac m2)$, because the heights of a cut point and of its mirror image add up to $2q - m$; and the composition sums do not change under reflection of the profile. The exponent of $\rho$ is the mean number of cuts under the weights $v_Q T_{m,Q}$. These three steps are the general statement `Parking.Vc_sum_pow_le`, and the present proof supplies its hypotheses.

**The exponent.** The weights are $v_Q = \sigma_Q(1/k)$, the second difference $(k+1)^Q - 2k^Q + (k-1)^Q$ divided by $k^{Q-2}$; they lie between $Q(Q-1)$ and $(1+\frac1{400})\,Q(Q-1)$ for $Q \le m$. So the mean number of cuts under $v_Q T_{m,Q}$ is at most $(1+\frac1{400})$ times its mean under the weights $Q(Q-1)\,T_{m,Q}$, and that mean is $D_m + 1$: by `Parking.Dbirth_spec`, $D_m$ is the ratio of $\sum_Q Q(Q-1)(Q-2)T_{m,Q}$ to $\sum_Q Q(Q-1)T_{m,Q}$, and $Q - 1 = (Q-2) + 1$. The number $q - \frac m2$ is the mean height of a cut point and its mirror image. `Parking.Dbirth_add_one_le` bounds $D_m + 1$ by $\frac32\sqrt{\pi m/2} - \frac85$, so the exponent is of the order $q\sqrt m/k^2$.

**Where the hypotheses are used.** $m < q$ makes every height positive. $401\,m^2 \le 12\,k^2$ is the condition $x^2(1+\theta)m^2 \le 12\,\theta$ at $x = 1/k$, $\theta = \frac1{400}$, under which the fourth-order term of the second difference of $y^Q$ is at most $\theta$ times the leading term $Q(Q-1)$ for all $Q \le m$. The statement has no hypothesis on a curve; in `Parking.term_step` the condition $401\,m^2 \le 12\,k^2$ is derived from $m \le r$, $r^3 \le k^2$ and $k \ge 265$. A larger $\theta$ would allow larger $m$ at the cost of the factor $1 + \theta$ in the exponent.

**How sharp it is.** The step from the chord to the statement loses in three places: the chord uses the exponent $k/(k+1)$, which is exact only for heights near $0$; the cut factors are replaced by the symmetric constant $\rho$; and $\log(1+t) \le t$ is used for $t = (q-\frac m2)/(k+1)$. A floating-point evaluation of the exact quantities at $k = 265$, which is not part of the proof, puts the largest part of what the final inequality between closed forms, `Parking.ledger`, gives away into this statement.

**The Lean form.** The thresholds and sizes are the casts of $k + 1$, $k + q + 1$, $k$, $k + q$ to real numbers, written `(k : ℝ) + 1`, `(k : ℝ) + q + 1` and so on; $m + 1 \le q$ and $401 m^2 \le 12 k^2$ are inequalities between natural numbers.

## Proof

Throughout, $V_Q(m;f)$ is the weight of the compositions of $m$ with $Q$ parts for the profile $f$ (`Parking.Vc`), $T_{m,Q} = V_Q(m;\mathbf 1)$ (`Parking.Tq`), and sums over $Q$ run over $1 \le Q \le m$. Put

$$\theta = \tfrac1{400}, \qquad \mu = (1+\theta)(D_m+1), \qquad \delta = q - \tfrac m2, \qquad \rho = \frac{k+1}{k+1+\delta}, \qquad E = \frac{\mu\,\delta}{k\,(k+1)},$$

and $P(s) = k/(k+q-s)$, $P'(s) = (k+1)/(k+q+1-s)$. Then $\mu \ge 0$ because $D_m \ge 0$ (`Parking.Dbirth_nonneg`), $\delta \ge 0$, and $0 < \rho \le 1$. The claim is $\mathsf C_m(k+1;k+q+1) \le \frac{k}{k+1}\,e^{E}\,\mathsf C_m(k;k+q)$.

**Step 1: the normalised second difference of $y^Q$.** For a real number $x$ define $\sigma_0(x) = \eta_0(x) = 0$ and

$$\sigma_{n+1}(x) = \sigma_n(x) + \eta_n(x), \qquad \eta_{n+1}(x) = \eta_n(x) + x^2\,\sigma_n(x) + 2 .$$

By induction on $n$ one has $(1+x)^n + (1-x)^n - 2 = x^2 \sigma_n(x)$ and $(1+x)^n - (1-x)^n = x\,\eta_n(x)$ (multiply by $1 \pm x$ and add, respectively subtract). Four properties follow by induction on $n$ from the recursion:

(a) $\sigma_n(x) \ge 0$ and $\eta_n(x) \ge 0$;

(b) for $0 \le x \le x'$: $\sigma_n(x) \le \sigma_n(x')$ and $\eta_n(x) \le \eta_n(x')$;

(c) $\sigma_n(x) \ge n(n-1)$ and $\eta_n(x) \ge 2n$, the values at $x = 0$;

(d) if $\theta \ge 0$, $n \le m$ and $x^2(1+\theta)\,m^2 \le 12\,\theta$, then $\sigma_n(x) \le (1+\theta)\,n(n-1)$.

For (d) one proves together, for $n \le m$,

$$\sigma_n \le n(n-1) + x^2(1+\theta)\,\frac{n(n-1)(n-2)(n-3)}{12}, \qquad \eta_n \le 2n + x^2(1+\theta)\,\frac{n(n-1)(n-2)}{3}.$$

The first bound implies $\sigma_n \le (1+\theta)\,n(n-1)$: this is trivial when $n(n-1) = 0$, and for $n \ge 2$ one has $(n-2)(n-3) \le m^2$, so the second term is at most $x^2(1+\theta)m^2\,n(n-1)/12 \le \theta\,n(n-1)$. In the induction step, $\sigma_{n+1} = \sigma_n + \eta_n$ is bounded by the sum of the two bounds, which is the first bound for $n + 1$ because $(n-3) + 4 = n + 1$; and $\eta_{n+1} = \eta_n + x^2 \sigma_n + 2$ is bounded with $\sigma_n \le (1+\theta)n(n-1)$, which gives the second bound for $n+1$ because $(n-2) + 3 = n + 1$.

For $y \ne 0$, the first identity at $x = 1/y$ gives $(y+1)^Q - 2y^Q + (y-1)^Q = y^{Q-2}\,\sigma_Q(1/y)$.

**Step 2: the curvature sum in terms of its own profile.** By `Parking.Lam_thr`, $y\,\Lambda_m(y;N) = \sum_Q y^Q\,V_Q(m;\lambda^{1,N})$ with $\lambda^{y,N}(s) = y/(N-s)$, hence $\mathsf C_m(y;N) = \sum_Q \bigl((y+1)^Q - 2y^Q + (y-1)^Q\bigr)V_Q(m;\lambda^{1,N})$ (`Parking.curvSum_eq_sum`). With Step 1 and $V_Q(m;\lambda^{y,N}) = y^{Q-1}V_Q(m;\lambda^{1,N})$ (`Parking.Vc_thr`), for $y \ne 0$,

$$\mathsf C_m(y;N) = \frac1y\sum_Q \sigma_Q(1/y)\;V_Q\bigl(m;\lambda^{y,N}\bigr).$$

So $\mathsf C_m(k;k+q) = \frac1k\,Y$ and $\mathsf C_m(k+1;k+q+1) = \frac1{k+1}\sum_Q \sigma_Q(\frac1{k+1})\,V_Q(m;P')$, where, with the weights $v_Q = \sigma_Q(1/k)$,

$$X = \sum_Q v_Q\,V_Q(m;P'), \qquad Y = \sum_Q v_Q\,V_Q(m;P).$$

At the cut points $0 < s < m$ both profiles are positive, since $q - s > 0$; so $V_Q(m;P'), V_Q(m;P) \ge 0$ (`Parking.Vc_nonneg`). By (b) with $\frac1{k+1} \le \frac1k$, $\sigma_Q(\frac1{k+1}) \le v_Q$, and therefore

$$\mathsf C_m(k+1;k+q+1) \;\le\; \frac{1}{k+1}\,X .$$

It remains to prove $X \le e^{E}\,Y$; then $\frac{1}{k+1}X \le \frac{k}{k+1}\,e^E \cdot \frac1k Y$, which is the claim.

**Step 3: the hypotheses of the comparison of two profiles.** We verify the hypotheses of `Parking.Vc_sum_pow_le` for the weights $v$, the profiles $g = P'$ and $w = P$, and $\rho$, $\mu$ as above.

*Weights.* $v_Q \ge 0$ by (a).

*$P'(s)^{k+1} \le P(s)^k$ at each cut point.* Let $h = q - s > 0$, so $P = k/(k+h)$ and $P' = (k+1)/(k+1+h)$. Put $t = -h/((k+1)(k+h))$. Then $1 + (k+1)\,t = P$ and $1 + t = P/P'$, and $t \ge -2$. Bernoulli's inequality $1 + (k+1)t \le (1+t)^{k+1}$ gives $P \le (P/P')^{k+1}$, that is $P'^{\,k+1} \le P^{k}$.

*$\rho^2 \le P'(s)\,P'(m-s)$ at each cut point.* The product is $(k+1)^2$ divided by $(k+q+1-s)(k+q+1-(m-s))$. The two factors of the denominator are positive and their sum is $2(k+1+\delta)$, so their product is at most $(k+1+\delta)^2$.

*The mean of $Q - 1$.* By (c) and $T_{m,Q} \ge 0$ (`Parking.Tq_nonneg`),

$$\sum_Q Q(Q-1)\,T_{m,Q} \;\le\; \sum_Q v_Q\,T_{m,Q} =: Z,$$

and the left side is positive for $m \ge 2$ (`Parking.sum_qq_Tq_pos`); so $Z > 0$. The hypothesis $401\,m^2 \le 12\,k^2$ is $x^2(1+\theta)m^2 \le 12\,\theta$ for $x = 1/k$, so by (d) $v_Q \le (1+\theta)\,Q(Q-1)$ for $Q \le m$. With $Q - 1 = (Q - 2) + 1$ and `Parking.Dbirth_spec`, which says $\sum_Q Q(Q-1)(Q-2)\,T_{m,Q} = D_m\sum_Q Q(Q-1)\,T_{m,Q}$,

$$\sum_Q v_Q\,T_{m,Q}\,(Q-1) \;\le\; (1+\theta)\sum_Q Q(Q-1)\bigl((Q-2)+1\bigr)T_{m,Q} = \mu\sum_Q Q(Q-1)\,T_{m,Q} \;\le\; \mu\,Z,$$

the last step because $\mu \ge 0$.

**Step 4: conclusion.** `Parking.Vc_sum_pow_le` gives $X^k \le \rho^{-\mu}\,Y^k$. Now $\rho^{-1} = 1 + \frac{\delta}{k+1} \le \exp\bigl(\frac{\delta}{k+1}\bigr)$, and $\mu \ge 0$, so

$$\rho^{-\mu} \;\le\; \exp\Bigl(\frac{\mu\,\delta}{k+1}\Bigr) = e^{kE} .$$

Hence $X^k \le (e^{E}\,Y)^k$. Both $X$ and $e^E Y$ are nonnegative and $k \ge 1$, so $X \le e^{E}\,Y$.
