---
weight: step
short: positivity of the curvature sum
---
## Description

For $m \ge 2$, a real threshold $y > 0$ and a real $N \ge m$ the curvature sum is positive: $\mathsf C_m(y;N) > 0$.

## Statement

Let $m \ge 2$ be a natural number and let $y$, $N$ be real numbers with $y > 0$ and $N \ge m$. Then

$$\mathsf C_m(y;N) > 0,$$

where $\mathsf C_m(y;N) = (y+1)\,\Lambda_m(y+1;N) - 2y\,\Lambda_m(y;N) + (y-1)\,\Lambda_m(y-1;N)$ is the curvature sum (`Parking.curvSum`) and $\Lambda_m(y;N)$ is the chain sum, the total weight of the compositions of $m$ for the threshold profile $s \mapsto y/(N-s)$ (`Parking.Lam`, `Parking.thr`).

## Explanation

The curvature sum is $\sum_Q \bigl((y+1)^Q - 2y^Q + (y-1)^Q\bigr) V_Q(m;\lambda^{1,N})$, a sum over the number $Q$ of parts (see `Parking.curvSum`). The statement says that every term is nonnegative and that the term of two parts is positive. For $0 < y < 1$ this is not visible from the second differences $(y+1)^Q - 2y^Q + (y-1)^Q$ as they stand, since $y - 1$ is negative; the proof writes them as $y^{Q-2}$ times a number $\sigma_Q(1/y)$ that is a polynomial in $(1/y)^2$ with nonnegative coefficients.

The positivity is used in `Parking.term_step`: the strict inequality between the scalar factors is multiplied by the term $m$ of the curvature term of the position $(k+r,k)$, and stays strict because that term is positive.

In the Lean statement the hypothesis $N \ge m$ reads `(m : ℝ) ≤ N`. It makes the profile $y/(N-s)$ positive at the cut points $0 < s < m$.

## Proof

**The normalised second difference.** For a real number $x$ define two sequences by $\sigma_0(x) = \eta_0(x) = 0$ and

$$\sigma_{n+1}(x) = \sigma_n(x) + \eta_n(x), \qquad \eta_{n+1}(x) = \eta_n(x) + x^2\,\sigma_n(x) + 2 .$$

By induction on $n$, $(1+x)^n + (1-x)^n - 2 = x^2\,\sigma_n(x)$ and $(1+x)^n - (1-x)^n = x\,\eta_n(x)$: multiplying the two quantities for $n$ by $1 \pm x$ shows that the first for $n+1$ is the first for $n$ plus $x$ times the second, and the second for $n+1$ is the second for $n$ plus $x$ times the first plus $2x$. By the same induction $\sigma_n(x) \ge 0$, $\eta_n(x) \ge 0$, and $\sigma_n(x) \ge n(n-1)$, $\eta_n(x) \ge 2n$ (for the last: $n(n-1) + 2n = (n+1)n$ and $2n + 2 = 2(n+1)$, the term $x^2 \sigma_n$ being nonnegative). In particular $\sigma_2(x) \ge 2$.

**The curvature sum in terms of its own profile.** For $y \ne 0$, dividing by $y^Q$ and using the first identity at $x = 1/y$,

$$(y+1)^Q - 2y^Q + (y-1)^Q = y^{Q}\,y^{-2}\,\sigma_Q(1/y).$$

By `Parking.Lam_thr`, $y\,\Lambda_m(y;N) = \sum_{Q=1}^{m} y^Q\,V_Q(m;\lambda^{1,N})$, where $V_Q(m;f)$ is the weight of the compositions of $m$ with $Q$ parts for the profile $f$ (`Parking.Vc`) and $\lambda^{y,N}(s) = y/(N-s)$; so $\mathsf C_m(y;N) = \sum_Q \bigl((y+1)^Q - 2y^Q + (y-1)^Q\bigr) V_Q(m;\lambda^{1,N})$ (`Parking.curvSum_eq_sum`). Since $V_Q(m;\lambda^{y,N}) = y^{Q-1}\,V_Q(m;\lambda^{1,N})$ (`Parking.Vc_thr`),

$$\mathsf C_m(y;N) = \frac1y \sum_{Q=1}^{m} \sigma_Q(1/y)\;V_Q\bigl(m;\lambda^{y,N}\bigr).$$

**Positivity.** Let $y > 0$ and $N \ge m \ge 2$. At a cut point $0 < s < m$ we have $N - s > 0$, so the profile $\lambda^{y,N}$ is positive there. Hence $V_Q(m;\lambda^{y,N}) \ge 0$ for all $Q$ (`Parking.Vc_nonneg`) and $V_2(m;\lambda^{y,N}) > 0$ (`Parking.Vc_pos`, as $1 \le 2 \le m$). Every term of the sum is nonnegative, and the term $Q = 2$ is at least $2\,V_2(m;\lambda^{y,N}) > 0$. The sum is positive, and so is its product with $1/y$.
