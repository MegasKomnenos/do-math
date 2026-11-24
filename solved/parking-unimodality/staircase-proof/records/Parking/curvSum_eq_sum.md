---
weight: unit
short: the curvature sum by the number of parts
---
## Description

For all real $y$, $N$ and every natural number $m$: $\mathsf C_m(y;N) = \sum_{Q=1}^{m}\bigl((y+1)^Q - 2y^Q + (y-1)^Q\bigr)\,V_Q(m;\lambda^{1,N})$, the curvature sum as a sum over the number $Q$ of parts, where $V_Q(m;\lambda^{1,N})$ is the weight of the compositions of $m$ with $Q$ parts for the cut factors $1/(N-s)$.

## Statement

For real numbers $y$, $N$ and a natural number $m$ let $\Lambda_m(y;N)$ be the chain sum, the total weight of the compositions of $m$ in which a part of size $p$ weighs $a_p = p^{p-1}/p!$ and a cut at the position $s$ weighs $y/(N-s)$ (`Parking.Lam` for the threshold profile $\lambda^{y,N}(s) = y/(N-s)$ of `Parking.thr`), and let

$$\mathsf C_m(y;N) = (y+1)\,\Lambda_m(y+1;N) - 2y\,\Lambda_m(y;N) + (y-1)\,\Lambda_m(y-1;N)$$

be the curvature sum (`Parking.curvSum`). Let $V_Q(m;f)$ be the weight of the compositions of $m$ with exactly $Q$ parts for the cut profile $f$ (`Parking.Vc`).

For all real numbers $y$ and $N$ and every natural number $m$,

$$\mathsf C_m(y;N) \;=\; \sum_{Q=1}^{m} \bigl((y+1)^Q - 2\,y^Q + (y-1)^Q\bigr)\;V_Q\bigl(m;\lambda^{1,N}\bigr).$$

## Explanation

**What it says.** A composition with $Q$ parts has $Q - 1$ cuts, and each cut of the threshold profile carries one factor $y$. So $y\,\Lambda_m(y;N) = \sum_{Q=1}^{m} y^{Q}\,V_Q(m;\lambda^{1,N})$ is a polynomial in $y$ in which the compositions with $Q$ parts make up the coefficient of $y^Q$, and this coefficient, their weight for the cut factors $1/(N-s)$, does not contain $y$. The curvature sum is the second difference of this polynomial in $y$, and the statement takes the second difference power by power. The threshold then occurs only in the factors $(y+1)^Q - 2y^Q + (y-1)^Q$, and the compositions only in the weights $V_Q(m;\lambda^{1,N})$, which are nonnegative when $N \ge m$ (`Parking.Vc_nonneg`, `Parking.thr_nonneg`). The statement holds for all real $y$ and $N$ and has no hypothesis.

**What follows from the form.** The second difference of $y \mapsto y^Q$ is $2\sum_{j \ge 1}\binom{Q}{2j}\,y^{Q-2j}$. It is $0$ for $Q = 1$, and its leading term is $Q(Q-1)\,y^{Q-2}$: to leading order the curvature sum weighs a composition by the number of ordered pairs of its parts. The statements about the curvature sum are read off from this.

- `Parking.curvSum_one`: for $m = 1$ the sum has the single term $Q = 1$, which vanishes.
- `Parking.curvSum_pos` and `Parking.curvSum_step` write the factor of $y^Q$ as $y^{Q-2}$ times a number that depends on $1/y$ and is at least $Q(Q-1)$; with it the curvature sum is positive for $m \ge 2$, $y > 0$ and $N \ge m$, and the curvature sums of two positions on a diagonal are compared through their expansions over $Q$.
- In the proof of `Parking.curv_ge_pair` the factor of $y^Q$ at $y = k > 0$, multiplied by $k^2$, is bounded from below by $Q(Q-1)\,k^Q$, and `Parking.sum_qq_Vc` turns the resulting sum into the weight of the compositions with one or two marked cut points.

**The Lean form.** The right side is the sum over `Finset.Icc 1 m` of `((y + 1) ^ Q - 2 * y ^ Q + (y - 1) ^ Q) * Vc (thr 1 N) Q m`, with real numbers $y$ and $N$. For $m = 0$ both sides are $0$.

## Proof

By `Parking.Lam_thr`, for every real number $z$,

$$\Lambda_m(z;N) = \sum_{Q=1}^{m} z^{Q-1}\,V_Q\bigl(m;\lambda^{1,N}\bigr).$$

Multiply by $z$. Since $z \cdot z^{Q-1} = z^{Q}$ for $Q \ge 1$,

$$z\,\Lambda_m(z;N) = \sum_{Q=1}^{m} z^{Q}\,V_Q\bigl(m;\lambda^{1,N}\bigr).$$

Apply this with $z = y+1$, $z = y$ and $z = y-1$ in the definition of the curvature sum (`Parking.curvSum`). The three sums run over the same indices $Q$ with the same weights $V_Q(m;\lambda^{1,N})$, so

$$\mathsf C_m(y;N) = \sum_{Q=1}^{m} \bigl((y+1)^Q - 2\,y^Q + (y-1)^Q\bigr)\;V_Q\bigl(m;\lambda^{1,N}\bigr).$$
