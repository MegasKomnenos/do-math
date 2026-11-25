---
weight: unit
short: the Cayley sum at the critical tilt
---
## Description

For $k \ge 12$ the Cayley sum at the critical tilt is at most one: $x_k \sum_{j=1}^{k} c_j x_k^j \le 1$, where $c_j = (j+1)^{j-1}/j!$ and $x_k = (k/(k+1))^{k-1}$. Equivalently $\sum_{n=2}^{k+1} a_n x_k^n \le 1$ for the tree numbers $a_n = n^{n-1}/n!$.

## Statement

For every natural number $k \ge 12$,
$$x_k \sum_{j=1}^{k} c_j\, x_k^{\,j} \;\le\; 1 ,$$
where $c_j = (j+1)^{j-1}/j!$ (`Parking.cc`; $c_j x^j$ is the tilted Cayley mass `Parking.ccT`) and $x_k = (k/(k+1))^{k-1}$ is the critical tilt (`Parking.xcrit`).

## Explanation

Since $x \cdot c_j x^j = a_{j+1} x^{j+1}$ (`Parking.x_mul_ccT`), the left-hand side is $S(k) = \sum_{n=2}^{k+1} a_n x_k^n$, the total of the tilted tree numbers of the sizes $2, \dots, k+1$ at the critical tilt.

The inequality is the numerical input of the theorem that the tilted environment of the threshold $k$ does not increase at the critical tilt (`Parking.zrT_anti_crit`). The proof of that theorem reduces the monotonicity of the whole environment to two conditions on its free range $0 \le N \le k$, where the environment is $c_N x_k^N$: that it does not increase there, and that $x_k \sum_{j=1}^{k} c_j x_k^j \le 1$. The first is elementary. The second is the present statement, and it is the one place in the monotonicity theorem where a quantity has to be estimated.

The inequality is true with room to spare but is not a formality. At the tilt $e^{-1}$ the corresponding infinite sum is $\sum_{n \ge 2} a_n e^{-n} = 1 - e^{-1}$ (from `Parking.hasSum_borel`, $\sum_{n\ge1} a_n e^{-n} = 1$). The critical tilt is larger than $e^{-1}$, the term of size $n$ is larger by the factor $(e\,x_k)^n$, which for $n$ near $k$ is of the order $e^{3/2}$, and the series $\sum a_n x_k^n$ diverges. What keeps $S(k)$ below $1$ is that the sum stops at $n = k+1$. An exact evaluation (outside the library) gives $S(12) \approx 0.775$.

The proof is an estimate by hand and never evaluates $S(k)$. Its closed-form upper bound for $S(k)$ is about $0.91$ at $k = 12$ and decreases with $k$, but it is larger than $1$ for $k \le 7$ (values computed outside the library). A range of small columns therefore has to be treated in another way; the library puts the boundary at $12$ and settles $2 \le k \le 11$ by evaluating $S(k)$ exactly, inside the proof of `Parking.zrT_anti_crit`.

## Proof

Write $x = x_k$, which is positive (`Parking.xcrit_pos`), and $\beta = 3/(2k)$. Each term of the sum is $x \cdot c_j x^j = a_n x^n$ with $n = j+1$, so the left-hand side is $S(k) = \sum_{n=2}^{k+1} a_n x^n$ (in Lean the sum over $1 \le j \le k$ is first reindexed by `Parking.sum_Icc_one_eq_range`). The proof bounds each term and then three sums.

### The bound of one term

*Stirling.* For $n \ge 1$ and $x \ge 0$,
$$a_n x^n \;\le\; \frac{(e x)^n}{\sqrt{2\pi}\; n \sqrt{n}} .$$
Indeed $a_n x^n = (e x)^n \cdot p_n / n$, where $p_n = e^{-n} n^n/n!$ is the Poisson mass (`Parking.poissonMass`, `Parking.poissonMass_eq`; the identity is a rearrangement of the definition $a_n = n^{n-1}/n!$, `Parking.cay`; in Lean it is written for $c_{n-1} = a_n$ with `Parking.cc_eq`), and $p_n \le 1/\sqrt{2\pi n}$ by `Parking.poissonMass_le`, which is Stirling's lower bound for $n!$.

*The tilt.* By `Parking.exp_one_mul_xcrit_le`, $e\,x \le e^{\beta}$, hence $(e x)^n \le e^{\beta n}$. For $2 \le n \le k+1$ and $k \ge 12$, $0 \le \beta n \le 3(k+1)/(2k) \le 1.7$.

*The exponential.* By `Parking.exp_le_quadratic`, $e^{y} \le 1 + y + y^2$ for $0 \le y \le 1.7$. With $y = \beta n$,
$$a_n x^n \;\le\; \frac{1 + \beta n + \beta^2 n^2}{\sqrt{2\pi}\; n\sqrt n} \;=\; \frac{1}{\sqrt{2\pi}} \Bigl( \frac{1}{n\sqrt n} + \frac{\beta}{\sqrt n} + \beta^2 \sqrt n \Bigr).$$

### The three sums

Summing over $2 \le n \le k+1$ gives $\sqrt{2\pi}\; S(k) \le \Sigma_1 + \beta\, \Sigma_2 + \beta^2\, \Sigma_3$ with $\Sigma_1 = \sum 1/(n\sqrt n)$, $\Sigma_2 = \sum 1/\sqrt n$, $\Sigma_3 = \sum \sqrt n$, each over $2 \le n \le k+1$.

*$\Sigma_1 \le 2/\sqrt{3/2} - 2/\sqrt{k + 3/2}$.* This follows by summation (induction on $k$, the sum telescopes) from the one-step inequality
$$\frac{1}{a\sqrt a} \;\le\; \frac{2}{\sqrt{a - 1/2}} - \frac{2}{\sqrt{a+1/2}} \qquad (a \ge 1),$$
which compares the value of the convex function $t^{-3/2}$ at $a$ with its integral over the interval of length $1$ centred at $a$. It is proved algebraically: with $s = \sqrt a$, $p = \sqrt{a-1/2}$, $q = \sqrt{a+1/2}$ one has $pq \le a$ (because $(pq)^2 = a^2 - 1/4$) and $p + q \le 2s$ (because $(p+q)^2 = 2a + 2pq \le 4a$), hence $pq\,(p+q) \le 2as$; and $(q-p)(q+p) = 1$, so the right-hand side equals $2(q-p)/(pq) = 2/(pq\,(p+q)) \ge 1/(as)$.

*$\Sigma_2 \le 2\sqrt{k+1} - 2$.* This is `Parking.sum_range_inv_sqrt_le`, $\sum_{i=1}^{m} 1/\sqrt i \le 2\sqrt m - 1$, for $m = k+1$, with the first term $1$ removed.

*$\Sigma_3 \le \tfrac23 (k+2)\sqrt{k+2}$.* This is `Parking.sum_range_sqrt_le`, $\sum_{i<R} \sqrt i \le \tfrac23 R\sqrt R$, for $R = k+2$; the terms $i = 0, 1$, which contribute $1$, are dropped.

### The final inequality

It remains to show, for real $k \ge 12$ and $\beta = 3/(2k)$,
$$\frac{2}{\sqrt{3/2}} - \frac{2}{\sqrt{k+3/2}} + \beta\,(2\sqrt{k+1} - 2) + \beta^2 \cdot \tfrac23 (k+2)\sqrt{k+2} \;\le\; \sqrt{2\pi} .$$
Put $r = \sqrt{k+2}$, so $r \ge 3.74$ (as $3.74^2 = 13.9876 \le 14$). The two constants are bounded by $2/\sqrt{3/2} \le 1.6331$ (as $\sqrt{3/2} \ge 1.2247$) and $\sqrt{2\pi} \ge 2.5066$ (as $2.5066^2 = 6.28304356 \le 2\pi$, using $\pi > 3.141592$). Since $\sqrt{k+1} \le r$ and $\sqrt{k+3/2} \le r$, and since $\beta^2 \cdot \tfrac23 (k+2)\, r = 3r^3/(2k^2)$, the part that depends on $k$ is at most
$$-\frac{2}{r} + \frac{3(r-1)}{k} + \frac{3 r^3}{2k^2} .$$
This is at most $0.87$. Over the common denominator $2rk^2$ and with $r^2 = k+2$, the claim is equivalent to $2.5\,k^2 + 12\,k + 6 \le r k\,(0.87\,k + 3)$; with $r \ge 3.74$ the right-hand side is at least $3.2538\,k^2 + 11.22\,k$, and $0.7538\,k^2 - 0.78\,k - 6 \ge 0$ for $k \ge 12$. These are routine verifications with polynomial inequalities. Altogether the left-hand side is at most $1.6331 + 0.87 = 2.5031 \le 2.5066 \le \sqrt{2\pi}$.

Dividing by $\sqrt{2\pi}$ gives $S(k) \le 1$.
