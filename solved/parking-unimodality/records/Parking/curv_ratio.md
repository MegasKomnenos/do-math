---
weight: unit
short: curvature ratio of the frozen polynomial
---
## Description

At a position $n = k + r$ with $r \le k - 1$, the second difference of the frozen polynomial $K_{n,k}$ at $k+1$ is at most $e^{D_r/(k-1)}$ times its second difference at $k$, where $D_r$ is the ratio of the third to the second factorial moment of the birthday law on the compositions of $r$.

## Statement

Let $k \ge 2$ and $r \le k - 1$ be natural numbers, and let $K = K_{k+r,k}$ be the frozen polynomial of `Parking.Kpoly`. Then

$$K(k+2) - 2K(k+1) + K(k) \ \le\ \exp\Bigl(\frac{D_r}{k-1}\Bigr)\,\bigl(K(k+1) - 2K(k) + K(k-1)\bigr),$$

where $D_r = 3\bigl((r+2)s_r - 3r\bigr)/\bigl(2(r - s_r)\bigr)$ and $s_r = \sum_{j=1}^{r} r(r-1)\cdots(r-j+1)/r^j$ (`Parking.Dbirth`, `Parking.sbirth`).

For $r \ge 2$ the number $D_r$ is given by this formula with a positive denominator. For $r = 0$ and $r = 1$ the formula is $0/0$, to which Lean assigns the value $0$; in these two cases $K$ has degree at most $1$, both second differences vanish, and the inequality holds whatever value is put in the place of $D_r$.

## Explanation

In `Parking.dq_frozen` the steps of the columns $k$ and $k+1$ in the row $n = k + r$ are written as $C_- - B_-$ and $C_+ - B_+$, with $C_- = K(k+1) - 2K(k) + K(k-1)$ and $C_+ = K(k+2) - 2K(k+1) + K(k)$. The present statement is the comparison of the two curvatures, $C_+ \le e^{D_r/(k-1)} C_-$, one of the three comparisons that `Parking.step_neg_of_Gfun` assembles.

The reason for a bound of this form is the following. The polynomial $K(y) = \kappa + \sum_{q=1}^{r} p_q y^q$ has nonnegative coefficients. The second difference of $y^q$ at $x$ is of the size of its second derivative $q(q-1)x^{q-2}$, and moving $x$ to $x+1$ multiplies this by about $(1+1/x)^{q-2} \approx e^{(q-2)/x}$. So the growth of the curvature from $k$ to $k+1$ is governed by how large the degrees $q$ that carry the curvature are, and the right measure is the ratio

$$\frac{\sum_q q(q-1)(q-2)\,p_q y^q}{\sum_q q(q-1)\,p_q y^q}$$

of the third to the second factorial moment of the weights $p_q y^q$. The degree $q$ is a number of parts of a composition, the weights $p_q y^q$ are mixtures of the weights of the threshold profile, and under the threshold profile with values in $[0,1]$ the number of parts is smaller, in the likelihood-ratio order, than under the birthday law. The moment ratio is therefore at most its value $D_m$ for the birthday law, and $D_m \le D_r$.

Two features of the statement come from this argument. The four points $k-1, \dots, k+2$ at which $K$ is evaluated are all at most $k + 2$, which is exactly what keeps the threshold profile $y/(N-s)$ at most $1$ on the cut points that occur. And the denominator $k - 1$ is the left end of the interval on which the moment bound is converted into a bound for the logarithmic derivative of $K''$. The statement does not assert that the second differences are positive, and the use in `Parking.step_neg_of_Gfun` does not need it.

## Proof

Put $N = k + r + 1$, $x = k$ and $D = D_r$.

**The polynomial.** By `Parking.Lam_thr`, $\Lambda_m(y;N) = \sum_{q=1}^{m} y^{q-1} V_q(m;\lambda^{1,N})$, where $V_q(m;\lambda^{1,N})$ is the weight of the compositions of $m$ with $q$ parts for the profile $s \mapsto 1/(N-s)$ (`Parking.Vc`). Inserting this into the definition of `Parking.Kpoly` and exchanging the summations over $m$ and $q$, which is legitimate because $V_q(m;\cdot) = 0$ for $q > m$ (`Parking.Vc_eq_zero_of_lt`), gives

$$K(y) = \kappa_k(N) + \sum_{q=1}^{r} p_q\, y^q, \qquad p_q = \sum_{m=1}^{r} c_m\, V_q(m;\lambda^{1,N}), \qquad c_m = \frac{\kappa_k(N-m)}{N-m}.$$

For $1 \le m \le r$ we have $1 \le N - m \le 2k + 1$, so $c_m > 0$ by `Parking.kap_pos`; this uses $r \le k - 1$. The profile $1/(N-s)$ is nonnegative at the cut points, so $V_q(m;\lambda^{1,N}) \ge 0$ by `Parking.Vc_nonneg` and `Parking.thr_nonneg`. Hence $p_q \ge 0$.

**The moment inequality.** For every real $y$ with $0 < y \le k + 2$,

$$\sum_{q=1}^{r} q(q-1)(q-2)\,p_q y^q \ \le\ D_r \sum_{q=1}^{r} q(q-1)\,p_q y^q. \tag{$*$}$$

By the same exchange of summations, both sides are the sums over $1 \le m \le r$, with the nonnegative weights $c_m y$, of the corresponding moments of the sequence $q \mapsto y^{q-1} V_q(m;\lambda^{1,N}) = V_q(m;\lambda^{y,N})$ (`Parking.Vc_thr`). It therefore suffices to prove, for each $1 \le m \le r$,

$$\sum_{q=1}^{m} q(q-1)(q-2)\,V_q(m;\lambda^{y,N}) \ \le\ D_r \sum_{q=1}^{m} q(q-1)\,V_q(m;\lambda^{y,N}).$$

For $m = 1$ both sides are $0$. Let $m \ge 2$. A cut point $s$ of a composition of $m$ satisfies $s \le m - 1 \le r - 1$, so $N - s \ge k + 2 \ge y$ and the profile $f = \lambda^{y,N}$ takes values in $[0,1]$ at the cut points. For such a profile `Parking.Vc_ratio_le` gives $q\,m\,V_{q+1}(m;f) \le (q+1)(m-q)\,V_q(m;f)$ for $q \ge 1$, while for the weights $T_{m,q}$ of the constant profile $1$ (`Parking.Tq`) the same relation holds with equality, $q\,m\,T_{m,q+1} = (q+1)(m-q)\,T_{m,q}$ (`Parking.Tq_ratio`). Multiplying the inequality by $T_{m,q} \ge 0$ (`Parking.Tq_nonneg`), using the equality and dividing by $q\,m > 0$ gives

$$V_{q+1}(m;f)\,T_{m,q} \le V_q(m;f)\,T_{m,q+1} \qquad (1 \le q,\ q + 1 \le m).$$

Since $T_{m,q} > 0$ for $1 \le q \le m$ (`Parking.Tq_pos`), `Parking.lr_of_consecutive` extends this to all pairs: $V_{q'}(m;f)\,T_{m,q} \le V_q(m;f)\,T_{m,q'}$ for $1 \le q \le q' \le m$. This says that the law of the number of parts under the profile $f$ is smaller in the likelihood-ratio order than the law proportional to $T_{m,q}$. For two sequences in this order `Parking.lr_factorial_moment_le` gives

$$\Bigl(\sum_q q(q-1)(q-2)\,V_q\Bigr)\Bigl(\sum_q q(q-1)\,T_{m,q}\Bigr) \le \Bigl(\sum_q q(q-1)(q-2)\,T_{m,q}\Bigr)\Bigl(\sum_q q(q-1)\,V_q\Bigr).$$

By `Parking.Dbirth_spec`, $\sum_q q(q-1)(q-2)\,T_{m,q} = D_m \sum_q q(q-1)\,T_{m,q}$, and the last sum is positive by `Parking.sum_qq_Tq_pos`; cancelling it gives the inequality for $m$ with the constant $D_m$. Finally $D_m \le D_r$ by `Parking.Dbirth_mono`, and the sum $\sum_q q(q-1)V_q(m;f)$ is nonnegative, so the constant can be raised to $D_r$.

**From the moment inequality to the curvature ratio.** Let $G_0(y) = \sum_{q=1}^{r} p_q y^q$ and let $G_1, G_2, G_3$ be its first three derivatives. The constant term of $K$ does not contribute to second differences, so it suffices to prove the inequality for $G_0$. Since $p_q \ge 0$, we have $G_3(y) \ge 0$ for $y \ge 0$. Since $y^2 G_2(y) = \sum_q q(q-1)p_q y^q$ and $y^3 G_3(y) = \sum_q q(q-1)(q-2)p_q y^q$, the inequality $(*)$, divided by $y^2 > 0$, reads $y\,G_3(y) \le D\,G_2(y)$ for $x - 1 \le y \le x + 2$; here $x - 1 = k - 1 > 0$ and $x + 2 = k + 2$. Put $c = D/(x-1)$. The argument has four steps.

1. On $[x-1, x+2]$ we have $G_3 \le c\,G_2$, because $(x-1)\,G_3(y) \le y\,G_3(y) \le D\,G_2(y)$; the first inequality uses $G_3 \ge 0$.
2. The function $t \mapsto e^{-ct} G_2(t)$ has the derivative $e^{-ct}\bigl(G_3(t) - c\,G_2(t)\bigr) \le 0$ on that interval, so it is nonincreasing there. Hence $G_2(y+1) \le e^{c} G_2(y)$ for $x - 1 \le y \le x + 1$.
3. The function $H(t) = e^{c} G_0(t) - G_0(t+1)$ has the second derivative $e^{c} G_2(t) - G_2(t+1) \ge 0$ on $[x-1, x+1]$ by step 2, so it is convex there.
4. Convexity at the midpoint $x$ of $x - 1$ and $x + 1$ gives $2H(x) \le H(x-1) + H(x+1)$, that is,

$$2e^{c} G_0(x) - 2G_0(x+1) \le e^{c} G_0(x-1) - G_0(x) + e^{c} G_0(x+1) - G_0(x+2),$$

which rearranges to $G_0(x+2) - 2G_0(x+1) + G_0(x) \le e^{c}\bigl(G_0(x+1) - 2G_0(x) + G_0(x-1)\bigr)$. With $x = k$ and $c = D_r/(k-1)$ this is the statement.
