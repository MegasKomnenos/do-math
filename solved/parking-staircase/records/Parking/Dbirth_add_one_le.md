---
weight: unit
short: the moment ratio of the birthday law against a square root
---
## Description

For $m \ge 2$ the moment ratio $D_m$ of the birthday law satisfies $D_m + 1 \le \frac32\sqrt{\pi m/2} - \frac85$.

## Statement

For a natural number $m$ let $s_m = \sum_{j=1}^{m} P_{m,j}$ with $P_{m,j} = \prod_{i=0}^{j-1}\bigl(1 - \frac im\bigr)$ be the mean of the birthday law (`Parking.sbirth`, `Parking.Pb`), and let

$$D_m = \frac{3\bigl((m+2)\,s_m - 3m\bigr)}{2\,(m - s_m)}$$

(`Parking.Dbirth`). Then for every natural number $m \ge 2$,

$$D_m + 1 \;\le\; \frac32\sqrt{\frac{\pi m}{2}} - \frac85 .$$

## Explanation

**What $D_m + 1$ is.** Let $T_{m,Q}$ be the total weight $\prod a_{\text{part}}$, $a_p = p^{p-1}/p!$, of the compositions of $m$ with $Q$ parts (`Parking.Tq`). By `Parking.Dbirth_spec`, $D_m$ is the ratio of $\sum_Q Q(Q-1)(Q-2)\,T_{m,Q}$ to $\sum_Q Q(Q-1)\,T_{m,Q}$. Hence $D_m + 1$ is the mean of the number $Q - 1$ of cut points when a composition with $Q$ parts is weighted by $Q(Q-1)\,T_{m,Q}$. This is the weighting of the curvature sum, and $D_m + 1$ is the factor in the exponent of `Parking.curvSum_step`. The statement turns that exponent into a closed form in $m$; `Parking.scalar_step` uses it for this, and the closed form is the one that stands in `Parking.ledger`.

**How sharp it is.** The mean $s_m$ of the birthday law is $\sqrt{\pi m/2} - \frac13 + o(1)$ (Ramanujan), and `Parking.sbirth_le` gives the upper half of this with an explicit error, $s_m \le \sqrt{\pi m/2}\;e^{1/(12m)} - \frac13$. Writing $p = \sqrt{\pi m/2}$, the claim is equivalent to an inequality that is linear in $s_m$,

$$s_m\,\bigl(3m + 3p + \tfrac45\bigr) \;\le\; m\,\bigl(3p + \tfrac{19}5\bigr),$$

and after the bound for $s_m$ is inserted and $p^2 = \pi m/2$ is used, the coefficient of $m^2$ in the difference of the two sides is $\frac{24}5 - \frac{3\pi}2 \approx 0.088$. With a constant $c$ in the place of $\frac85$ that coefficient would be $8 - 2c - \frac{3\pi}2$, which is negative for $c > 4 - \frac{3\pi}4 \approx 1.644$. So from this bound for $s_m$ no constant larger than $4 - \frac{3\pi}4$ can be obtained for large $m$, and $\frac85$ uses most of what there is. The proof accordingly has little room: it needs $\pi \le 3.1416$, and the explicit bound for $s_m$ is good enough only from $m = 4$ on, so that $m = 2$ and $m = 3$ are checked with the exact values of $s_m$.

**The Lean form.** The statement is `Dbirth m + 1 ≤ 3 / 2 * Real.sqrt (Real.pi * m / 2) - 8 / 5` for `2 ≤ m`. For $m \ge 2$ the denominator $m - s_m$ of $D_m$ is positive (`Parking.sbirth_lt`), so the Lean quotient is the ordinary one.

## Proof

Let $m \ge 2$ and $p = \sqrt{\pi m/2}$.

**Reduction.** Since $s_m < m$ (`Parking.sbirth_lt`), the denominator $2(m - s_m)$ is positive, and $D_m \le \frac32 p - \frac{13}5$ is equivalent to $3\bigl((m+2)s_m - 3m\bigr) \le \bigl(3p - \frac{26}5\bigr)(m - s_m)$, that is, collecting the terms with $s_m$, to

$$s_m\,\bigl(3m + 3p + \tfrac45\bigr) \;\le\; m\,\bigl(3p + \tfrac{19}5\bigr). \tag{1}$$

The factor of $s_m$ on the left is positive, so the left side increases with $s_m$.

**$m = 2$.** $s_2 = 1 + \frac12 = \frac32$, and (1) reads $\frac32\bigl(\frac{34}5 + 3p\bigr) \le 2\bigl(3p + \frac{19}5\bigr)$, that is $p \ge \frac{26}{15}$. This holds because $p^2 = \pi$ and $\bigl(\frac{26}{15}\bigr)^2 = \frac{676}{225} < 3.14 < \pi$.

**$m = 3$.** $s_3 = 1 + \frac23 + \frac29 = \frac{17}9$, and (1) reads $\frac{17}9\bigl(\frac{49}5 + 3p\bigr) \le 3\bigl(3p + \frac{19}5\bigr)$, that is $p \ge \frac{32}{15}$. This holds because $p^2 = \frac{3\pi}2$ and $\bigl(\frac{32}{15}\bigr)^2 = \frac{1024}{225} < 4.71 = \frac32\cdot3.14 < \frac{3\pi}2$.

**$m \ge 4$.** Three facts are combined.

(a) $s_m \le p\,e^{1/(12m)} - \frac13$ (`Parking.sbirth_le`).

(b) $e^{1/(12m)} \le 1 + \frac{4}{47m}$. With $y = \frac1{12m} \le \frac1{48}$, the bound $e^y \le 1 + y + y^2$ for $0 \le y \le 1.7$ (`Parking.exp_le_quadratic`) gives $e^y \le 1 + \frac{49}{48}\,y \le 1 + \frac{48}{47}\,y = 1 + \frac{4}{47m}$.

(c) If $m \ge 4$, $p^2 = \pi' m/2$ and $\pi' \le 3.1416$, then

$$\Bigl(p\bigl(1 + \tfrac{4}{47m}\bigr) - \tfrac13\Bigr)\bigl(3m + 3p + \tfrac45\bigr) \;\le\; m\,\bigl(3p + \tfrac{19}5\bigr).$$

Multiply by $m > 0$ and expand, replacing $p^2$ by $\pi' m/2$: the right side minus the left side is

$$\Bigl(\frac{24}5 - \frac{3\pi'}2\Bigr)m^2 - \frac{13}{235}\,p\,m - \frac{6}{47}\,\pi' m - \frac{16}{235}\,p + \frac{4}{15}\,m .$$

Bound $\pi'$ by $3.1416$ and $p$ by the tangent of the parabola at $p = \frac52$: $p \le \frac{p^2}5 + \frac54 \le 0.31416\,m + 1.25$, which is $(p - \frac52)^2 \ge 0$. The expression is then at least a quadratic polynomial in $m$ with positive leading coefficient, about $0.0702\,m^2 - 0.225\,m - 0.085$, which is positive for $m \ge 4$ (its value at $m = 4$ is about $0.14$); the Lean proof verifies the resulting linear inequality in the quantities $m^2$, $m$, $pm$, $p$, $\pi' m$, $\pi' m^2$ with $m^2 \ge 4m$.

By (a) and (b), $s_m \le p\,(1 + \frac{4}{47m}) - \frac13$, where $p \ge 0$. Since the left side of (1) increases with $s_m$, (1) follows from (c) with $\pi' = \pi$, using $\pi < 3.1416$.
