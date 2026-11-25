---
weight: unit
short: pair–impulse criterion
---
## Description

For natural numbers $k$ and $R$ with $1 \le R \le k-2$, and $N = k+R$: if $k\, a_k\, \Lambda_R(k+1;N) < 2\,\mathcal{P}(k,R)$, then the step of column $k$ in the row $k+R-1$ is positive. Here $a_k = k^{k-1}/k!$, $\Lambda_R(k+1;N)$ is the chain sum of length $R$ with the cut factors $(k+1)/(N-s)$, and $\mathcal{P}(k,R)$ is the pair sum.

## Statement

Let $k$ and $R$ be natural numbers with $1 \le R \le k - 2$, so that $k \ge 3$, and put $N = k + R$ and $n = k + R - 1$. Let $a_k = k^{k-1}/k!$ (`Parking.cay`), let $\Lambda_R(k+1;N)$ be the total weight of the compositions of $R$ for the threshold profile $s \mapsto (k+1)/(N-s)$ (`Parking.Lam`, `Parking.thr`), and let $\mathcal{P}(k,R)$ be the pair sum of `Parking.pairSum`. If

$$k\; a_k\; \Lambda_R(k+1;N) \;<\; 2\,\mathcal{P}(k,R),$$

then the normalised step $\delta^{(k)}_n = \bigl(b(n,k) - b(n,k-1)\bigr)/n!$ of column $k$ in the row $n$ (`Parking.dq`) is positive, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$.

## Explanation

**What the criterion does.** It reduces the positivity of one step $d_{n,k} = b(n,k) - b(n,k-1)$ to an inequality between two explicit finite sums in which the numbers of parking functions occur only through the environment inside the pair sum. The conclusion $\delta^{(k)}_n > 0$ is the same as $b(n,k-1) < b(n,k)$. The criterion concerns a single position: it makes no assumption on the signs of the steps in other rows or columns.

**The two sides.** `Parking.dq_frozen` writes the normalised step as a curvature term minus a boundary term. The right side of the criterion comes from the curvature term: `Parking.curv_ge_pair` shows that $k^2$ times the curvature term is at least twice the pair sum. The left side is $k^2$ times the boundary term $(a_k/k)\,\Lambda_R(k+1;N)$. This boundary term is called the impulse in the estimates of the curve increase, and the criterion is named after the two sides.

**Why it decides the sign near the curve.** The two sides have different orders of magnitude in the deficit, and the curve $k^2 = r^3$ is where they meet. The following is a count of orders, and the exact statements are those of the two records named. By `Parking.pairSum_ge` the pair sum is at least $a_k\, e^{R}$ times an expression whose main term is the sum $\sum_{b \le R} \kappa_2(b)$ of the twofold convolution of the Poisson mass (`Parking.kc2`); $\kappa_2(b)$ tends to $\tfrac12$ as $b$ grows, so twice the pair sum is of the order $a_k\, e^{R}\cdot R$. On the other side, the cut factors $(k+1)/(N-s)$ of the chain sum $\Lambda_R(k+1;N)$ lie in $(0,1]$, so the chain sum is at most the total weight $R^R/R!$ of the compositions of $R$ for the cut factors $1$ (`Parking.Lam_one`). This is $e^{R}$ times the Poisson mass $e^{-R}R^R/R!$, which is about $1/\sqrt{2\pi R}$; `Parking.impulse_le` is the sharper bound that the proof uses. So the left side is of the order $a_k\, e^{R}\cdot k/\sqrt{R}$. The right side is the larger one when $R^{3/2}$ exceeds a multiple of $k$. The factors of order one that this count leaves out are what the estimates of the curve increase determine.

**Where it is applied.** To obtain `Parking.curve_crossing`, the curve increase applies the criterion in the row $n = k + r$ whose deficit $r = R - 1$ is the first one with $k^2 < r^3$. The left side is bounded from above by `Parking.impulse_le` and the right side from below by `Parking.pairSum_ge`, and the two bounds are then compared.

**The range.** The rows covered are $k \le n \le 2k - 3$. These are the rows of the first layer of the column $k - 1$, and all of them but the row $n = k$ lie in the first layer $k + 1 \le n \le 2k - 1$ of the column $k$ as well. The upper end comes from `Parking.dq_frozen`, which is applied to the column $k - 1$ with the deficit $R$ and requires $R \le (k-1) - 1$. The statement has no separate hypothesis on $k$; the two conditions on $R$ give $k \ge 3$, which is the hypothesis $k - 1 \ge 2$ of `Parking.dq_frozen` for the column $k - 1$. For $R = 1$ the hypothesis cannot hold: the pair sum $\mathcal{P}(k,1)$ is $0$, because a composition of $1$ has no cut point, while the left side is $k\,a_k > 0$. This agrees with the fact that the step in the row $n = k$ is negative.

**The Lean form.** The hypothesis is `(k : ℝ) * cay k * Lam (thr ((k : ℝ) + 1) ((k : ℝ) + R)) R < 2 * pairSum k R` and the conclusion is `0 < dq k (k + R - 1)`, an inequality between real numbers. The subtractions $k - 2$ and $k + R - 1$ of natural numbers are exact, because the hypotheses `1 ≤ R` and `R ≤ k - 2` give $k \ge 3$.

## Proof

Apply the second equation of `Parking.dq_frozen` with the column $k - 1$ in the place of its $k$ and with $r = R$; its hypotheses $k - 1 \ge 2$ and $1 \le R \le (k-1) - 1$ hold, the first because $1 \le R \le k - 2$ gives $k \ge 3$. The row is $(k-1) + R = n$, the number $n + 1$ is $N$, and the equation reads

$$\delta^{(k)}_n = \bigl(K(k+1) - 2K(k) + K(k-1)\bigr) - \frac{a_k}{k}\,\Lambda_R(k+1;N), \qquad K = K_{n,k-1},$$

where $K_{n,k-1}$ is the frozen polynomial of `Parking.Kpoly`. Multiply by $k^2 > 0$. By `Parking.curv_ge_pair`, $k^2\bigl(K(k+1) - 2K(k) + K(k-1)\bigr) \ge 2\,\mathcal{P}(k,R)$, and $k^2 \cdot (a_k/k)\,\Lambda_R(k+1;N) = k\,a_k\,\Lambda_R(k+1;N)$. Hence

$$k^2\,\delta^{(k)}_n \;\ge\; 2\,\mathcal{P}(k,R) - k\,a_k\,\Lambda_R(k+1;N) \;>\; 0$$

by the hypothesis, and therefore $\delta^{(k)}_n > 0$.
