---
weight: unit
short: comparison of the composition sums of two cut profiles
---
## Description

For nonnegative weights $v_Q$ and cut profiles $g, w \ge 0$ on the cut points of $m$ with $g^{k+1} \le w^k$, the sums $X = \sum_Q v_Q V_Q(m;g)$ and $Y = \sum_Q v_Q V_Q(m;w)$ satisfy $X^k \le \rho^{-\mu}\,Y^k$, where $0 < \rho \le 1$ has $\rho^2 \le g(s)\,g(m-s)$ at every cut point and $\mu$ bounds the mean of $Q - 1$ under the weights $v_Q T_{m,Q}$.

## Statement

For a function $f : \mathbb{N} \to \mathbb{R}$ and natural numbers $Q$, $m$ let $V_Q(m;f)$ be the total weight of the compositions of $m$ with exactly $Q$ parts, in which a part of size $p$ weighs $a_p = p^{p-1}/p!$ and a cut at the position $s$ weighs $f(s)$ (`Parking.Vc`), and let $T_{m,Q} = V_Q(m;\mathbf 1)$ be its value for the constant profile $1$ (`Parking.Tq`).

Let $k \ge 1$ and $m$ be natural numbers, let $v, g, w : \mathbb{N} \to \mathbb{R}$ be functions and $\rho$, $\mu$ real numbers such that

- $v_Q \ge 0$ for $1 \le Q \le m$;
- $g(s) \ge 0$, $w(s) \ge 0$ and $g(s)^{k+1} \le w(s)^k$ for $0 < s < m$;
- $0 < \rho \le 1$, and $\rho^2 \le g(s)\,g(m-s)$ for $0 < s < m$;
- $Z := \sum_{Q=1}^{m} v_Q\,T_{m,Q} > 0$, and $\sum_{Q=1}^{m} v_Q\,T_{m,Q}\,(Q-1) \le \mu\,Z$.

Then

$$\Bigl(\sum_{Q=1}^{m} v_Q\,V_Q(m;g)\Bigr)^{k} \;\le\; \rho^{-\mu}\,\Bigl(\sum_{Q=1}^{m} v_Q\,V_Q(m;w)\Bigr)^{k}.$$

## Explanation

**What is compared.** The statement compares one weighted sum over the compositions of $m$ for two cut profiles, a smaller one $g$ and a larger one $w$, and bounds the loss in passing from $w$ to $g$. Call the two sums $X$ (for $g$) and $Y$ (for $w$), and let $Z$ be the same sum for the constant profile $1$. The hypothesis $g^{k+1} \le w^k$ says $g \le \mathbf 1^{1/(k+1)}\,w^{k/(k+1)}$: pointwise, $g$ lies below the geometric interpolation between the profile $1$ and the profile $w$ with the exponents $\frac1{k+1}$ and $\frac k{k+1}$. Since the sums are log-convex in the profile, $X \le Z^{1/(k+1)}\,Y^{k/(k+1)}$. This would be useless without a bound for $Z$, the sum for the profile $1$, which is larger than both. The second half of the argument bounds $Z$ by $X$ itself: $\rho^{\mu} Z \le X$. Eliminating $Z$ between the two leaves $X^k \le \rho^{-\mu}\,Y^k$.

**Why the hypotheses have this form.** The bound $\rho^{\mu} Z \le X$ needs a lower bound for $g$, and the profiles of the application, $g(s) = (k+1)/(N+1-s)$, have no good constant lower bound on the cut points: they are small at the first cut points and large at the last. What they have is a symmetric one, $g(s)\,g(m-s) \ge \rho^2$, because the sum of the two denominators does not depend on $s$. Reflection invariance of the sums turns this into a bound by the constant profile $\rho$: $V_Q(m;\rho) \le V_Q(m;g)$. A constant profile gives each of the $Q - 1$ cut points the factor $\rho$, so $X \ge \sum_Q v_Q T_{m,Q}\,\rho^{Q-1}$, and Jensen's inequality bounds this from below by $\rho^{\bar\mu} Z$ with $\bar\mu$ the mean of $Q - 1$ under the weights $v_Q T_{m,Q}$. The statement asks only for an upper bound $\mu$ of that mean, which is what the application can supply, and uses $\rho \le 1$ to pass from $\bar\mu$ to $\mu$.

**What it is used for.** `Parking.curvSum_step` applies it with $g$ and $w$ the threshold profiles of two consecutive positions on a diagonal, the weights $v_Q$ a normalised second difference of $y \mapsto y^Q$, and $\mu = (1 + \frac1{400})(D_m + 1)$ with $D_m$ the moment ratio of the birthday law (`Parking.Dbirth`). The conclusion is stated with $k$-th powers and the factor $\rho^{-\mu}$ so that no root has to be taken here.

**The Lean form.** The hypotheses on $g$, $w$, $\rho$ are asked for the cut points $s \in (0,m)$ and those on $v$ for $Q \in [1,m]$. The exponent $k$ on the two sides is a natural number, and $\rho^{-\mu}$ is a real power. The factor $Q - 1$ is the real number $(Q : \mathbb{R}) - 1$. The number $m - s$ is the truncated subtraction of natural numbers, ordinary at the cut points.

## Proof

Write $X = \sum_Q v_Q V_Q(m;g)$, $Y = \sum_Q v_Q V_Q(m;w)$, $Z = \sum_Q v_Q T_{m,Q}$, all sums over $1 \le Q \le m$. The numbers $V_Q(m;g)$, $V_Q(m;w)$, $T_{m,Q}$ are nonnegative (`Parking.Vc_nonneg`, `Parking.Tq_nonneg`), so $X, Y \ge 0$. The proof uses, besides `Parking.Vc_rpow_mul_rpow_le` and `Parking.Vc_reverse`, two elementary facts about the sums, each proved by induction on the number of parts along the recursion `Parking.Vc_succ_succ` on the last part:

- *monotonicity*: if $0 \le f \le h$ on the cut points of $m$, then $V_Q(m;f) \le V_Q(m;h)$ (in the recursion every factor of a term is nonnegative and increases);
- *homogeneity*: $V_Q(m;\,y f) = y^{Q-1}\,V_Q(m;f)$ for a real number $y$ (each of the $Q-1$ cut points carries one factor); in particular $V_Q(m;\rho) = \rho^{Q-1}\,T_{m,Q}$ for the constant profile $\rho$.

It also uses Hölder's inequality for finite sums, $\sum_i x_i^\alpha y_i^\beta \le (\sum_i x_i)^\alpha (\sum_i y_i)^\beta$ for $x_i, y_i \ge 0$ and $\alpha, \beta > 0$ with $\alpha + \beta = 1$.

**Step 1: $X^{k+1} \le Z\,Y^k$.** Put $\beta = k/(k+1)$, so $0 < \beta < 1$. At a cut point $s$, taking the $(k+1)$-th root of $g(s)^{k+1} \le w(s)^k$ gives $g(s) \le w(s)^\beta = 1^{1-\beta}\,w(s)^\beta$. By monotonicity and by `Parking.Vc_rpow_mul_rpow_le` with the profiles $\mathbf 1$ and $w$ and the exponents $1 - \beta$, $\beta$,

$$V_Q(m;g) \;\le\; V_Q\bigl(m;\,\mathbf 1^{1-\beta} w^\beta\bigr) \;\le\; T_{m,Q}^{\,1-\beta}\;V_Q(m;w)^\beta .$$

Multiply by $v_Q = v_Q^{1-\beta} v_Q^\beta$ and sum over $Q$; Hölder's inequality with $x_Q = v_Q T_{m,Q}$ and $y_Q = v_Q V_Q(m;w)$ gives $X \le Z^{1-\beta}\,Y^\beta$. Raising to the power $k + 1$, with $(1-\beta)(k+1) = 1$ and $\beta(k+1) = k$, gives $X^{k+1} \le Z\,Y^k$.

**Step 2: $\rho^{\mu}\,Z \le X$.** First, $V_Q(m;\rho) \le V_Q(m;g)$ for every $Q$. Indeed, at a cut point $s$ the hypothesis $\rho^2 \le g(s)\,g(m-s)$ gives $\rho \le g(s)^{1/2}\,g(m-s)^{1/2}$, the point $m - s$ being a cut point as well. By monotonicity, by `Parking.Vc_rpow_mul_rpow_le` with the profiles $g$ and $s \mapsto g(m-s)$ and the exponents $\frac12$, $\frac12$, and by `Parking.Vc_reverse`,

$$V_Q(m;\rho) \;\le\; V_Q\bigl(m;\,g^{1/2}\,g(m-\cdot)^{1/2}\bigr) \;\le\; V_Q(m;g)^{1/2}\;V_Q\bigl(m;\,g(m-\cdot)\bigr)^{1/2} = V_Q(m;g).$$

With homogeneity, $v_Q\,T_{m,Q}\,\rho^{Q-1} \le v_Q\,V_Q(m;g)$, and summing, $\sum_Q v_Q T_{m,Q}\,\rho^{Q-1} \le X$.

Next let $\bar\mu = \bigl(\sum_Q v_Q T_{m,Q}(Q-1)\bigr)/Z$, which is defined because $Z > 0$, and which satisfies $\bar\mu \le \mu$ by hypothesis. `Parking.jensen_rpow` with the weights $v_Q T_{m,Q} \ge 0$, the exponents $Q - 1$, the base $\rho > 0$, the total $Z$ and the mean $\bar\mu$ gives $\rho^{\bar\mu}\,Z \le \sum_Q v_Q T_{m,Q}\,\rho^{Q-1}$. Since $0 < \rho \le 1$ and $\bar\mu \le \mu$, $\rho^{\mu} \le \rho^{\bar\mu}$. Together,

$$\rho^{\mu}\,Z \;\le\; \rho^{\bar\mu}\,Z \;\le\; \sum_Q v_Q\,T_{m,Q}\,\rho^{Q-1} \;\le\; X .$$

In particular $X > 0$, because $\rho^\mu > 0$ and $Z > 0$.

**Step 3: conclusion.** By the two steps,

$$X \cdot \rho^{\mu} X^k = \rho^{\mu}\,X^{k+1} \;\le\; \rho^{\mu} Z \cdot Y^k \;\le\; X \cdot Y^k ,$$

and dividing by $X > 0$ gives $\rho^{\mu} X^k \le Y^k$, that is $X^k \le \rho^{-\mu}\,Y^k$.
