---
weight: unit
short: shortening by one for the homogeneous law
---
## Description

Shortening by one: for $r \ge 1$ and $0 < h \le 1$, the total weights of the compositions of $r+1$ and of $r$ with constant cut weight $h$ satisfy $\tau_{r+1}(h) \le (1+\frac1r)^r\bigl(1 - \frac{1-h}{2h(r+1)}\,\mu_r(h)\bigr)\,\tau_r(h)$, where $\mu_r(h)$ is the mean number of cuts.

## Statement

For every natural number $r \ge 1$ and every real number $h$ with $0 < h \le 1$,

$$\tau_{r+1}(h) \;\le\; \Bigl(1+\frac1r\Bigr)^{r}\,\Bigl(1 - \frac{1-h}{2h\,(r+1)}\;\mu_r(h)\Bigr)\;\tau_r(h).$$

Here $\tau_m(h) = \sum_{q=1}^{m} T_{m,q}\,h^{q-1}$ is the total weight of all compositions of $m$ in which a part of size $p$ weighs $a_p = p^{p-1}/p!$ and every cut weighs $h$ (`Parking.tau`, `Parking.tau_eq`; $T_{m,q}$ is `Parking.Tq`), and $\mu_r(h) = \bigl(\sum_{q=1}^{r}(q-1)\,T_{r,q}\,h^{q-1}\bigr)/\tau_r(h)$ is the mean number of cuts (`Parking.muh`).

## Explanation

**What is compared.** At $h = 1$ the two totals are known exactly: $\tau_m(1) = m\,a_m$, by `Parking.Tq_eq` and the identity $\sum_{q=1}^{m} q\,P_{m,q} = m$ for the birthday tail $P_{m,q}$ of `Parking.Pb` (this is `Parking.Pb_moment` for $g = 1$), and $(r+1)\,a_{r+1} = (1+\frac1r)^r\, r\,a_r$ by `Parking.cay_ratio`. So at $h = 1$ the statement is an equality, with the bracket equal to $1$. For $h < 1$ it says that the quotient $\tau_{r+1}(h)/\tau_r(h)$ lies below its value $(1+\frac1r)^r$ at $h = 1$ by at least the factor $1 - \frac{1-h}{2h(r+1)}\mu_r(h)$. This factor is the gain that the later argument needs.

**Why it holds.** Let $Q$ follow the birthday law of $m$ (see `Parking.Pb`), and write $\mathbb{E}_m$ for the expectation with respect to it; then $\tau_m(h) = m\,a_m\,\mathbb{E}_m[h^{Q-1}]$ by `Parking.Tq_eq`. The statement is therefore

$$\mathbb{E}_{r+1}\bigl[h^{Q-1}\bigr] \;\le\; \Bigl(1 - \frac{1-h}{2h\,(r+1)}\;\mu_r(h)\Bigr)\;\mathbb{E}_{r}\bigl[h^{Q-1}\bigr].$$

With $r+1$ boxes in place of $r$ the first repetition comes later, so $Q$ is larger and $h^{Q-1}$, for $h \le 1$, is smaller. The size of the effect comes from a comparison of the tails: for $0 \le j \le r$,

$$P_{r+1,j+1} \;\ge\; \Bigl(1 + \frac{j(j+1)}{2r(r+1)}\Bigr)\,P_{r,j+1}.$$

The reason is that, for $j < r$, the quotient $P_{r+1,j+1}/P_{r,j+1}$ is the product over $i = 1, \dots, j$ of the factors $(1 - \frac{i}{r+1})/(1 - \frac{i}{r}) \ge 1 + \frac{i}{r(r+1)}$, that a product of such factors is at least $1$ plus the sum of the increments, and that $1 + 2 + \dots + j = j(j+1)/2$; for $j = r$ the right-hand side is $0$. The proof below obtains the comparison by induction on $j$ instead. A composition with $j$ cuts has $j + 1$ parts, so by `Parking.Tq_eq` the compositions of $r$ with $j$ cuts have the total weight $a_r\,(j+1)\,h^{j}\,P_{r,j+1}$ under the cut weight $h$. The excess $j(j+1)\,P_{r,j+1}$ of the comparison, summed against $h^{j}$, is therefore $\mu_r(h)\,\tau_r(h)/a_r$, and this is how the mean number of cuts enters.

**Where it is used.** `Parking.Lam_shorten` combines the statement with `Parking.Lam_first_cell`, which compares the chain sums $\Lambda_{r+1}(k-1;N)$ and $\Lambda_r(k;N)$ of the threshold profile, $N = k+r+1$, with $\tau_{r+1}(h)$ and $\tau_r(h)$ at $h = (k-1)/(k+r)$. For this $h$ the coefficient $\frac{1-h}{2h(r+1)}$ equals $\frac{1}{2(k-1)}$, and the result is $\Lambda_{r+1}(k-1;N) \le (1+\frac1r)^r\,(1 - \frac{\mu_r(h)}{2(k-1)})\,\Lambda_r(k;N)$. In the criterion `Parking.step_neg_of_Gfun` the mean is then bounded below by `Parking.mu0_le_muh`, which produces the term $\frac12\,\mu^0_r\bigl(\frac{r(r+1)}{k-1}\bigr)$ of the criterion function `Parking.Gfun`.

**The hypotheses.** The hypothesis $h > 0$ is needed because the statement divides by $h$. The hypothesis $h \le 1$ is used once, for the sign of $1 - h$ in the last step of the proof.

**The Lean form.** The power $(1 + 1/r)^r$ has a real base and a natural exponent, and the bracket is written `1 - (1 - h) / (2 * h * (r + 1)) * muh r h`.

## Proof

Throughout, $P_{m,j}$ is the birthday tail (`Parking.Pb`) and $h$ is fixed. The proof expresses $\tau_r(h)$, $\tau_{r+1}(h)$ and $\mu_r(h)\,\tau_r(h)$ through three sums of tails,

$$A = \sum_{j=1}^{r} h^{j-1} P_{r,j+1}, \qquad B = \sum_{j=1}^{r} h^{j-1} P_{r+1,j+1}, \qquad K = \sum_{j=1}^{r} j(j+1)\,h^{j}\,P_{r,j+1},$$

proves $K \le 2h\,r(r+1)\,(B - A)$ from a comparison of the tails for $r$ and $r+1$, and finishes with an algebraic identity.

**Step 1: the totals.** For every $m \ge 1$,

$$\tau_m(h) \;=\; m\,a_m\,\Bigl(1 - (1-h)\sum_{j=1}^{m} h^{j-1} P_{m,j+1}\Bigr).$$

By `Parking.tau_eq` and `Parking.Tq_eq`, $\tau_m(h) = a_m \sum_{q=1}^{m} q\,P_{m,q}\,h^{q-1}$. Apply `Parking.Pb_moment` to the function $g$ with $g(0) = 1$ and $g(q) = h^{q-1}$ for $q \ge 1$. Then $g(1) - g(0) = 0$ and $g(q) - g(q-1) = -(1-h)\,h^{q-2}$ for $q \ge 2$, so the sum equals $m\,\bigl(1 - (1-h)\sum_{q=2}^{m} h^{q-2} P_{m,q}\bigr)$. With $q = j+1$ this is the sum over $1 \le j \le m-1$, and the term with $j = m$ may be added because $P_{m,m+1} = 0$ (`Parking.Pb_succ_self`).

For $m = r$ this gives $\tau_r(h) = r\,a_r\,(1 - (1-h)A)$. For $m = r+1$ the term with $j = r+1$ is zero, again by `Parking.Pb_succ_self`, and $\tau_{r+1}(h) = (r+1)\,a_{r+1}\,(1 - (1-h)B)$.

**Step 2: the mean.** $\mu_r(h)\,\tau_r(h) = a_r\,K$. By `Parking.muh_mul_tau` (applicable since $h \ge 0$) and `Parking.Tq_eq`, the left-hand side is $a_r \sum_{q=1}^{r} (q-1)\,q\,P_{r,q}\,h^{q-1}$. The term with $q = 1$ is zero; with $q = j+1$ the rest is the sum of $j(j+1)\,h^{j} P_{r,j+1}$ over $1 \le j \le r-1$, and the term with $j = r$ is zero.

**Step 3: comparison of the tails.** For $0 \le j \le r$,

$$\bigl(2r(r+1) + j(j+1)\bigr)\,P_{r,j+1} \;\le\; 2r(r+1)\,P_{r+1,j+1}.$$

This is proved by induction on $j$. For $j = 0$ both tails are $1$ (`Parking.Pb_one`) and the two sides are equal. For the step from $j = k$ to $j = k+1 \le r$, write $x = P_{r,k+1} \ge 0$ (`Parking.Pb_nonneg`), $y = P_{r+1,k+1}$, $\alpha = 1 - \frac{k+1}{r}$ and $\beta = 1 - \frac{k+1}{r+1} \ge 0$, so that $P_{r,k+2} = x\alpha$ and $P_{r+1,k+2} = y\beta$ by `Parking.Pb_succ`. Put $c = 2r(r+1)$. Using $\alpha r = r - k - 1$ and $\beta(r+1) = r - k$, a direct calculation gives

$$\Bigl[\bigl(c + k(k+1)\bigr)\beta - \bigl(c + (k+1)(k+2)\bigr)\alpha\Bigr]\; r(r+1) \;=\; (k+1)^2\,(2r + k + 2) \;\ge\; 0,$$

hence $(c + (k+1)(k+2))\,\alpha \le (c + k(k+1))\,\beta$. Multiplying this by $x \ge 0$, and the induction hypothesis $(c + k(k+1))\,x \le c\,y$ by $\beta \ge 0$,

$$\bigl(c + (k+1)(k+2)\bigr)\,x\alpha \;\le\; \bigl(c + k(k+1)\bigr)\,x\beta \;\le\; c\,y\beta,$$

which is the assertion for $j = k+1$.

**Step 4: $K \le 2h\,r(r+1)\,(B - A)$.** Step 3 can be written $j(j+1)\,P_{r,j+1} \le 2r(r+1)\,(P_{r+1,j+1} - P_{r,j+1})$. Multiply by $h^{j} = h\cdot h^{j-1} \ge 0$ and sum over $1 \le j \le r$.

**Step 5: the algebra.** Put $e = \frac{1-h}{2h(r+1)}$. The identity

$$\Bigl[\bigl(1 + \tfrac1r\bigr)\bigl(r\,(1 - (1-h)A) - e\,K\bigr) - (r+1)\bigl(1 - (1-h)B\bigr)\Bigr]\cdot 2hr \;=\; (1-h)\,\bigl(2h\,r(r+1)\,(B - A) - K\bigr)$$

holds because $(1 + \frac1r)\,r = r+1$ and $2h(r+1)\,e = 1 - h$. Its right-hand side is nonnegative by Step 4 and $h \le 1$, and $2hr > 0$, so

$$(r+1)\bigl(1 - (1-h)B\bigr) \;\le\; \bigl(1 + \tfrac1r\bigr)\bigl(r\,(1 - (1-h)A) - e\,K\bigr).$$

Multiply by $(1+\frac1r)^{r-1} a_r \ge 0$. By `Parking.cay_ratio`, $a_{r+1} = (1+\frac1r)^{r-1} a_r$, so by Step 1 the left-hand side becomes $\tau_{r+1}(h)$. By Steps 1 and 2 the right-hand side becomes $(1+\frac1r)^{r}\,\bigl(\tau_r(h) - e\,\mu_r(h)\,\tau_r(h)\bigr)$, which is the right-hand side of the statement.
