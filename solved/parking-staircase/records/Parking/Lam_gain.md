---
weight: unit
short: gain of the boundary chain sum along the diagonal
---
## Description

Raising the threshold and the size of a chain sum by one each raises the sum by a definite factor: for $k \ge 2$, $q \ge 1$ and $x = q/((k-1)(k+q))$, $(1+x)^{E_0}\,\Lambda_q(k-1;k+q) \le \Lambda_q(k;k+q+1)$ with $E_0 = \frac{q+2}{2q}\,\mu^0_q\bigl(q^2/(k-1)\bigr)$.

## Statement

For real numbers $y$, $N$ and a natural number $m$ let $\Lambda_m(y;N)$ be the chain sum: the total weight of the compositions of $m$ in which a part of size $p$ weighs $a_p = p^{p-1}/p!$ and a cut at the position $s$ weighs $y/(N-s)$ (`Parking.Lam` for the threshold profile `Parking.thr`). For a natural number $r$ and a real number $X$ let

$$\mu^0_r(X) = \frac{\sqrt{(4+X)^2 + 12\,(r-1)} - (4+X)}{3}$$

(`Parking.mu0`). Let $k \ge 2$ and $q \ge 1$ be natural numbers, and put

$$x = \frac{q}{(k-1)(k+q)}, \qquad E_0 = \frac{q+2}{2q}\;\mu^0_q\Bigl(\frac{q^2}{k-1}\Bigr).$$

Then

$$(1+x)^{E_0}\;\Lambda_q(k-1;\,k+q) \;\le\; \Lambda_q(k;\,k+q+1).$$

## Explanation

**Its place.** At a position $(k+r,k)$ of the first layer the step of the array is a curvature term minus the boundary term $B = \frac{a_k}{k}\,\Lambda_q(k-1;N)$, with $q = r+1$ and $N = k+q$ (`Parking.dq_curv_sub_boundary`). At the position one row down and one column to the right the boundary term is $B' = \frac{a_{k+1}}{k+1}\,\Lambda_q(k;N+1)$: the length $q$ of the chain sum is the same, and the threshold and the size have both grown by one. The diagonal step needs the boundary term to grow fast enough along the diagonal to keep ahead of the curvature term. The statement gives the growth of the chain sum; `Parking.term_step` uses it as one of its three comparisons, and the exponent $E_0$ and the base $1+x$ enter the inequality between closed forms `Parking.ledger` as its gain term.

**Where the gain comes from.** A composition of $q$ is given by its set $S \subseteq \{1,\dots,q-1\}$ of cut points, and the two chain sums differ only in the factors of the cuts: $\lambda_s = (k-1)/(k+q-s)$ before and $\lambda'_s = k/(k+q+1-s)$ after. Exactly,

$$\frac{\lambda'_s}{\lambda_s} = 1 + \frac{q+1-s}{(k-1)(k+q+1-s)},$$

so every cut gains, and a cut near the beginning gains most. A composition with the cut set $S$ gains at least $(1+x)^{U(S)/q}$, where $U(S) = \sum_{s \in S}(q+1-s)$. The gain of the chain sum is therefore at least the mean of $(1+x)^{U/q}$ over the compositions, weighted as in the old chain sum, and by Jensen's inequality at least $(1+x)$ to the power of the mean of $U/q$. What remains is a lower bound for the mean of $U$ under the old profile $\lambda$.

**The mean of $U$.** For a constant profile $\rho$ the mean of $U$ can be computed. Reading a composition backwards keeps its weight and sends a cut point $s$ to $q - s$, so $q + 1 - s$ and $s + 1$ have the same mean, namely $\frac{q+2}{2}$ per cut; the mean of $U$ is $\frac{q+2}{2}$ times the mean number of cuts $\mu_q(\rho)$ (`Parking.muh`), for which `Parking.mu0_le_muh` gives the explicit lower bound $\mu^0_q(q(1/\rho-1))$. The old profile is not constant, but on the cut points it is at least the constant $\rho = (k-1)/(k-1+q)$, which is its value at the first cut point $s = 1$ and its smallest value on the cut points. A larger profile makes cuts more likely, and $U$ grows when cuts are added; so the mean of $U$ under $\lambda$ should be at least its mean under $\rho$. This is a correlation inequality of FKG type on the lattice of cut sets. It holds because the weight $\prod a_{\text{part}}$ of a composition is log-supermodular as a function of the cut set, which in turn rests on the log-convexity of the numbers $a_p$ (`Parking.cay_logconvex`). With $q(1/\rho - 1) = q^2/(k-1)$ this gives the exponent $E_0$.

**Remarks on the form.** The statement has no hypothesis relating $q$ and $k$. For $q = 1$ there is no cut point, both chain sums are $a_1 = 1$, and $\mu^0_1 = 0$, so it is an equality. The reflection symmetry of the compositions is used here to compute a mean exactly; in `Parking.Vc_sum_pow_le`, on which `Parking.curvSum_step` rests, the same symmetry together with log-convexity bounds a composition sum from below by its value for a constant profile. The correlation inequality is asked for profiles that are comparable on the cut points only, because a threshold profile $y/(N-s)$ is negative for $s > N$, far outside the cut points. A floating-point evaluation at $k = 265$, $q = 42$, which is not part of the proof, finds the logarithm of the true ratio of the two chain sums about a fifth larger than the logarithm of the bound.

**The Lean form.** The thresholds and sizes are real numbers, `(k : ℝ) - 1`, `(k : ℝ) + q` and so on, and $(1+x)^{E_0}$ is a real power of a number $\ge 1$. The argument of $\mu^0_q$ is `(q : ℝ) ^ 2 / ((k : ℝ) - 1)`.

## Proof

The proof has two parts. Part A is about compositions as sets of cut points: the representation of $\Lambda$, the cut sets through a point, the log-supermodularity of the part weights, and the FKG inequality. Part B applies it to the two profiles.

Throughout, a profile is a function $f : \mathbb{N} \to \mathbb{R}$, $f(c+\cdot)$ is the shifted profile $s \mapsto f(c+s)$, $\Lambda_r[f]$ is the total weight of the compositions of $r$ for the profile $f$ (`Parking.Lam`), and $\tau_r(h) = \Lambda_r[h]$ for a constant profile $h$ (`Parking.tau`).

### Part A: compositions as sets of cut points

**A1. The scan.** For a finite set $S$ of natural numbers, a position $p$, a base point $x < p$ and a number $n$ of positions still to be inspected, let $G_S(n,p,x)$ be the product of the numbers $a$ of the parts that $S$ cuts out of the segment from $x$ to $p+n$ when only the positions $p,\dots,p+n-1$ are inspected, $x$ being the last cut seen so far:

$$G_S(0,p,x) = a_{p-x}, \qquad G_S(n+1,p,x) = \begin{cases} a_{p-x}\,G_S(n,p+1,p) & p \in S,\\ G_S(n,p+1,x) & p \notin S.\end{cases}$$

It is nonnegative and depends only on the elements of $S$ that are $\ge p$. For $r \ge 1$ and $S \subseteq \{1,\dots,r-1\}$ put $w(S) = G_S(r-1,1,0)$, the product of the weights of the parts of the composition of $r$ with the cut set $S$, and $W_f(S) = w(S)\prod_{s\in S} f(s)$, its weight for the profile $f$. For $p + n = r$ let

$$Z_f(r;n,p,x) = \sum_{S \subseteq \{p,\dots,r-1\}} G_S(n,p,x)\prod_{s \in S} f(s).$$

*One step of the scan.* Let $p < r$ and let $h$ be any real function of finite sets. Splitting the subsets of $\{p,\dots,r-1\}$ into those without $p$ and those of the form $S \cup \{p\}$ with $S \subseteq \{p+1,\dots,r-1\}$, and using the recursion of $G$ and $G_{S\cup\{p\}}(n,p+1,\cdot) = G_S(n,p+1,\cdot)$,

$$\sum_{S \subseteq \{p,\dots,r-1\}} G_S(n+1,p,x)\prod_S f\;h(S) = \sum_{S \subseteq \{p+1,\dots,r-1\}} G_S(n,p+1,x)\prod_S f\;h(S) \;+\; a_{p-x}\,f(p)\sum_{S \subseteq \{p+1,\dots,r-1\}} G_S(n,p+1,p)\prod_S f\;h(S\cup\{p\}). \tag{1}$$

With $h = 1$: $Z_f(r;n+1,p,x) = Z_f(r;n,p+1,x) + a_{p-x}\,f(p)\,Z_f(r;n,p+1,p)$.

**A2. The representation.** For $x + 1 + n = r$,

$$Z_f(r;n,x+1,x) = \Lambda_{n+1}\bigl[f(x+\cdot)\bigr], \qquad\text{in particular}\qquad \sum_{S \subseteq \{1,\dots,r-1\}} W_f(S) = \Lambda_r[f] \quad (r \ge 1). \tag{2}$$

Iterating the step of the scan from $p$ to $r$ sorts the cut sets by their first point $g$: $Z_f(r;n,p,x) = a_{r-x} + \sum_{p \le g < r} a_{g-x}\,f(g)\,Z_f(r;r-g-1,g+1,g)$ (induction on $n$). For $p = x+1$ this is the recursion on the first part of `Parking.Lam_first`, $\Lambda_m[f] = a_m + \sum_{0<g<m} a_g\,f(g)\,\Lambda_{m-g}[f(g+\cdot)]$, applied to $f(x+\cdot)$ and $m = r - x$, with $Z_f(r;r-g-1,g+1,g)$ in the place of $\Lambda_{r-g}[f(g+\cdot)]$; so (2) follows by induction on the length $n$.

**A3. The cut sets through a point.** For $0 < s < r$,

$$\sum_{S \subseteq \{1,\dots,r-1\},\ s \in S} W_f(S) = \Lambda_s[f]\;f(s)\;\Lambda_{r-s}\bigl[f(s+\cdot)\bigr]. \tag{3}$$

A composition of $r$ with a cut at $s$ is a composition of $s$, the cut, and a composition of $r - s$ for the shifted profile. Formally one proves, for $p \le s$ and $p + n = r$,

$$\sum_{S \subseteq \{p,\dots,r-1\},\ s \in S} G_S(n,p,x)\prod_S f = Z_f(s;s-p,p,x)\;f(s)\;Z_f(r;r-s-1,s+1,s)$$

by induction on $n$, applying (1) with $h$ the indicator of $s \in S$. If $p = s$, the first sum of (1) is empty of sets containing $s$, the second is $a_{s-x}\,f(s)\,Z_f(r;n,s+1,s)$, and $Z_f(s;0,s,x) = a_{s-x}$. If $p < s$, adding $p$ to a set does not change whether it contains $s$; the induction hypothesis applies to both sums of (1), with the base points $x$ and $p$, and the two results combine by the step of the scan for $Z_f(s;\cdot)$. Then (3) is the case $p = 1$, $x = 0$, by (2).

**A4. Log-supermodularity of the part weights.** For all cut sets $S$, $T$ of a composition of $r$,

$$w(S)\;w(T) \;\le\; w(S \cap T)\;w(S \cup T). \tag{4}$$

This is the case $x = x' = 0$, $p = 1$, $n = r-1$ of

$$G_S(n,p,x)\;G_T(n,p,x') \;\le\; G_{S\cap T}(n,p,\min(x,x'))\;G_{S\cup T}(n,p,\max(x,x')) \qquad (x, x' < p),$$

proved by induction on $n$. For $n = 0$ both sides are $a_{p-x}\,a_{p-x'}$. For the step there are four cases. If $p$ lies in neither set, the scan moves on with the same base points. If it lies in both, each side acquires the factor $a_{p-x}\,a_{p-x'}$ and all base points become $p$. If $p \in S$ and $p \notin T$, the left side is $a_{p-x}\,G_S(n,p+1,p)\,G_T(n,p+1,x')$; the induction hypothesis with the base points $p$ and $x'$ bounds it by $a_{p-x}\,G_{S\cap T}(n,p+1,x')\,G_{S\cup T}(n,p+1,p)$, while the right side is $G_{S\cap T}(n,p+1,\min(x,x'))\cdot a_{p-\max(x,x')}\,G_{S\cup T}(n,p+1,p)$. So it suffices that

$$a_{p-x}\;G_{I}(n,p+1,x') \;\le\; a_{p-\max(x,x')}\;G_{I}(n,p+1,\min(x,x')) \qquad (I = S \cap T).$$

For $x \ge x'$ this is an equality. For $x \le x'$ it is a case of the base-change inequality: for every finite set $I$ and $x \le x' < c \le p'$, $a_{c-x}\,G_I(n,p',x') \le a_{c-x'}\,G_I(n,p',x)$. That inequality is proved by induction on $n$: the part that begins at the base point ends at the first element $e \ge p'$ of $I$ or at the endpoint, the rest of the scan is the same on both sides, and what is left is $a_{c-x}\,a_{e-x'} \le a_{c-x'}\,a_{e-x}$ for $x \le x' < c \le e$, which is the log-convexity `Parking.cay_logconvex` ($a_{u+d}\,a_v \le a_u\,a_{v+d}$ for $1 \le u \le v$, with $u = c - x'$, $v = e - x'$, $d = x' - x$). The case $p \in T$, $p \notin S$ is symmetric.

**A5. The FKG inequality for cut sets.** Let $r \ge 1$, let $f$, $g$ be profiles with $0 \le g(s) \le f(s)$ for $0 < s < r$, and let $F$ be a real function of the subsets of $\{1,\dots,r-1\}$ that is nonnegative and monotone for inclusion. Then

$$\Bigl(\sum_S W_g(S)\,F(S)\Bigr)\,\Lambda_r[f] \;\le\; \Lambda_r[g]\,\sum_S W_f(S)\,F(S), \tag{5}$$

the sums over all $S \subseteq \{1,\dots,r-1\}$: the mean of $F$ under the weights of the smaller profile is at most its mean under the weights of the larger one.

The four functions theorem of Ahlswede and Daykin (Mathlib's `Finset.four_functions_theorem`) says: if $f_1,\dots,f_4$ are nonnegative functions on the subsets of a finite set with $f_1(S)\,f_2(T) \le f_3(S\cap T)\,f_4(S \cup T)$ for all $S$, $T$, then $(\sum_S f_1(S))(\sum_T f_2(T)) \le (\sum_S f_3(S))(\sum_S f_4(S))$. Mathlib asks the nonnegativity for all finite sets of natural numbers; replacing each $f_i$ by $S \mapsto f_i(S \cap \{1,\dots,r-1\})$ reduces this to the subsets of the cut points. Apply it with

$$f_1 = W_g\,F, \qquad f_2 = W_f, \qquad f_3 = W_g, \qquad f_4 = W_f\,F .$$

By (2) the conclusion is (5). The hypothesis $W_g(S)\,F(S)\,W_f(T) \le W_g(S \cap T)\,W_f(S\cup T)\,F(S \cup T)$ is the product of three inequalities between nonnegative numbers: (4) for the part weights; $\prod_{T} f \prod_{S} g \le \prod_{S \cap T} g \prod_{S \cup T} f$, which holds because $\prod_{S\cup T} f = \prod_T f \prod_{S \setminus T} f$, $\prod_S g = \prod_{S\cap T} g\prod_{S \setminus T} g$ and $g \le f$ on $S \setminus T$; and $F(S) \le F(S \cup T)$.

### Part B: the two profiles

Fix $k \ge 2$ and $q \ge 1$. Write $\lambda_s = (k-1)/(k+q-s)$ and $\lambda'_s = k/(k+q+1-s)$ for the two threshold profiles, $c = 1 + x \ge 1$, $\rho = (k-1)/(k-1+q)$, so $0 < \rho \le 1$, and $U(S) = \sum_{t \in S}(q+1-t)$ for $S \subseteq \{1,\dots,q-1\}$. Sums over $S$ run over these subsets. The claim is $c^{E_0}\,\Lambda_q[\lambda] \le \Lambda_q[\lambda']$.

**B1. The gain at one cut point.** For $0 < s < q$,

$$\lambda_s\;c^{(q+1-s)/q} \;\le\; \lambda'_s .$$

The exponent $\theta = (q+1-s)/q$ lies in $[0,1]$, so $(1+x)^\theta \le 1 + \theta x$ (Bernoulli's inequality for an exponent between $0$ and $1$), and $\theta x = \frac{q+1-s}{(k-1)(k+q)} \le \frac{q+1-s}{(k-1)(k+q+1-s)}$ because $s \ge 1$. A direct calculation gives $\lambda_s\bigl(1 + \frac{q+1-s}{(k-1)(k+q+1-s)}\bigr) = \lambda'_s$.

**B2. Every cut set gains.** On the cut points $\lambda_s \ge \rho > 0$, since $k + q - s \le k - 1 + q$. For a cut set $S$, $c^{U(S)/q} = \prod_{t \in S} c^{(q+1-t)/q}$, and the part weight $w(S)$ is the same for both profiles; so by B1, $W_\lambda(S)\,c^{U(S)/q} \le W_{\lambda'}(S)$. Summing and using (2) for $\lambda'$,

$$\sum_S W_\lambda(S)\,c^{U(S)/q} \;\le\; \Lambda_q[\lambda'] .$$

**B3. Jensen.** Let $\bar e = \bigl(\sum_S W_\lambda(S)\,U(S)/q\bigr)/\Lambda_q[\lambda]$; the denominator is positive (`Parking.Lam_thr_pos`) and equals $\sum_S W_\lambda(S)$ by (2). The weights $W_\lambda(S)$ are nonnegative. `Parking.jensen_rpow` with these weights, the exponents $U(S)/q$ and the base $c$ gives

$$c^{\bar e}\,\Lambda_q[\lambda] \;\le\; \sum_S W_\lambda(S)\,c^{U(S)/q}.$$

**B4. The statistic for a constant profile.** For $\rho \ge 0$,

$$\sum_S W_\rho(S)\,U(S) = \frac{q+2}{2}\;\mu_q(\rho)\,\tau_q(\rho), \tag{6}$$

where $\mu_q(\rho)$ is the mean number of cuts for the constant profile $\rho$ (`Parking.muh`). Exchanging the sum over $S$ with the sum over $t \in S$ and using (3), the left side is $\sum_{0<t<q}(q+1-t)\,\omega_t$ with $\omega_t = \tau_t(\rho)\,\rho\,\tau_{q-t}(\rho)$, a shifted constant profile being the same constant. Since $\omega_{q-t} = \omega_t$, the substitution $t \mapsto q - t$ shows $\sum_t (q+1-t)\,\omega_t = \sum_t (t+1)\,\omega_t$, so each equals $\frac{q+2}{2}\sum_t \omega_t$. The sum $\sum_{0<t<q}\omega_t$ is by definition `Parking.Lam1` for the constant profile, the weight of the compositions of $q$ with one marked cut point, and `Parking.Lam1_eq_sum` evaluates it as $\sum_{Q=1}^{q}(Q-1)\,V_Q(q;\rho)$, where $V_Q(q;\rho)$ is the weight of the compositions with $Q$ parts (`Parking.Vc`). Each of the $Q-1$ cuts carries the factor $\rho$, so $V_Q(q;\rho) = \rho^{Q-1}\,T_{q,Q}$ with $T_{q,Q}$ the value for the profile $1$ (`Parking.Tq`), and $\sum_Q (Q-1)\,T_{q,Q}\,\rho^{Q-1} = \mu_q(\rho)\,\tau_q(\rho)$ by `Parking.muh_mul_tau`.

**B5. FKG against the constant profile.** The function $U$ is nonnegative and monotone for inclusion, because every summand $q + 1 - t$ is positive for $t < q$. Apply (5) with $f = \lambda$, $g = \rho$ and $F = U$, and insert (6) and $\sum_S W_\lambda(S)\,U(S) = q\,\bar e\,\Lambda_q[\lambda]$:

$$\frac{q+2}{2}\,\mu_q(\rho)\,\tau_q(\rho)\,\Lambda_q[\lambda] \;\le\; \tau_q(\rho)\cdot q\,\bar e\,\Lambda_q[\lambda].$$

Dividing by $\tau_q(\rho)\,\Lambda_q[\lambda] > 0$ (`Parking.tau_pos`) gives $\frac{q+2}{2}\,\mu_q(\rho) \le q\,\bar e$.

**B6. Conclusion.** By `Parking.mu0_le_muh`, $\mu^0_q\bigl(q(1/\rho - 1)\bigr) \le \mu_q(\rho)$, and $q(1/\rho - 1) = q^2/(k-1)$. With B5, $E_0 = \frac{q+2}{2q}\,\mu^0_q\bigl(\frac{q^2}{k-1}\bigr) \le \bar e$. Since $c \ge 1$, $c^{E_0} \le c^{\bar e}$, and by B3 and B2

$$c^{E_0}\,\Lambda_q[\lambda] \;\le\; c^{\bar e}\,\Lambda_q[\lambda] \;\le\; \sum_S W_\lambda(S)\,c^{U(S)/q} \;\le\; \Lambda_q[\lambda'] .$$
