---
weight: step
short: threshold K of the impulse bound
---
## Description

For real $s \ge 6.48$ and $R = s^2$, the number $K = (R-1)(2R-1)/(2s)$ satisfies $K \ge R$, and $K \ge k$ for every real $k$ with $k^2 \le (R-1)^3$.

## Statement

Let $s$, $R$, $K$ and $k$ be real numbers with $s \ge 6.48$, $R = s^2$,

$$K \cdot 2s = (R-1)(2R-1) \qquad\text{and}\qquad k^2 \le (R-1)^3.$$

Then $R \le K$ and $k \le K$.

## Explanation

The number $K$ is the threshold at which the upper bound of the impulse, `Parking.impulse_le`, is applied in the proof of `Parking.curve_step_pos`. That bound concerns $e^{-R}\Lambda_R(y+1;\,y+R)$ for a threshold $y$, where $\Lambda_R(y+1;\,y+R)$ is the chain sum of length $R$ with the cut factors $(y+1)/(y+R-c)$ at the cut points $c$ (in Lean `Lam (thr (y + 1) (y + R)) R`), and it holds for every real $K$ with $0 \le y \le K$ and $R \le K$; it is applied with $y = k$, the column. The two conclusions of the present statement are exactly these two conditions, and the hypothesis $k^2 \le (R-1)^3$ is the upper half of the window in which the column lies (see `Parking.k_window`).

The form of $K$ is explained by the identity $K = (R-1)\bigl(s - \frac{1}{2s}\bigr)$. Since $\bigl(s - \frac{1}{2s}\bigr)^2 = R - 1 + \frac{1}{4R} \ge R - 1$, the factor $s - \frac{1}{2s}$ is an upper bound of $\sqrt{R-1}$, so $K \ge (R-1)^{3/2} \ge k$. The number $K$ thus stands for $(R-1)^{3/2}$, the largest value the column can have in the window, with the square root $\sqrt{R-1}$ replaced by a rational function of $s$. Two things are gained: the bound of the impulse no longer depends on $k$, and it is a rational function of $s$, so that the final comparison `Parking.impulse_numeric` becomes an inequality between rational functions of the one variable $s$.

The Lean statement gives the definition of $K$ in the form $K \cdot 2s = (R-1)(2R-1)$, without a division. No sign condition on $k$ is needed: the hypothesis bounds $k^2$, and a negative $k$ is below $K > 0$ in any case.

## Proof

Substitute $R = s^2$. Then $s > 0$ and $s^2 \ge 6.48^2 = 41.9904 \ge 41.99$. Moreover $K > 0$: both factors of $(s^2-1)(2s^2-1)$ are positive, so $K \cdot 2s > 0$, and $2s > 0$ gives $K > 0$.

*$R \le K$.* It suffices to show $s^2 \cdot 2s \le K \cdot 2s = (s^2-1)(2s^2-1)$. The difference is

$$(s^2-1)(2s^2-1) - 2s^3 = s^2\,(2s^2 - 2s - 3) + 1,$$

and $2s^2 - 2s - 3 \ge 0$ for $s \ge 6.48$, so the difference is positive. Dividing by $2s > 0$ gives $s^2 \le K$.

*$k \le K$.* First,

$$(K \cdot 2s)^2 - (s^2-1)^3 (2s)^2 = (s^2-1)^2 \bigl((2s^2-1)^2 - 4s^2(s^2-1)\bigr) = (s^2-1)^2 \ge 0,$$

because $(2s^2-1)^2 - 4s^2(s^2-1) = 1$. Hence $(s^2-1)^3 (2s)^2 \le K^2 (2s)^2$. Suppose $k > K$. Since $K > 0$, both $k - K$ and $k + K$ are positive, so $K^2 < k^2 \le (s^2-1)^3$, and multiplying by $(2s)^2 > 0$ gives $K^2 (2s)^2 < (s^2-1)^3 (2s)^2$, a contradiction.
