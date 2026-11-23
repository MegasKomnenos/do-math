---
weight: step
short: upper bound for the tilt exponent
---
## Description

The number $\bar a=5/(2k)$, an upper bound for $1+\log x$ where $x=1/\gamma_k$ is the diagonal tilt of the column $k$.

## Statement

For a natural number $k$, $\bar a=\bar a(k)=\dfrac{5}{2k}$.

## Explanation

Write the diagonal tilt (`Parking.xk`) as $x=e^{\alpha-1}$, that is $\alpha=1+\log x=1-(k-2)\log(1+1/k)$ for $k\ge2$. The number $\alpha$ measures how far the tilt lies above $e^{-1}$, and every closed-form bound of the crossing criterion is expressed through it: the terms of $S_R$ (`Parking.SR`) are $e^{-i}i^i/i!$ times $e^{\alpha i}$, and the tilted kernel masses (`Parking.kapx`) are $e^{-m}\varepsilon_m$ times $e^{\alpha m}$. Expanding the logarithm gives $\alpha=\frac{5}{2k}-\frac{4}{3k^2}+O(k^{-3})$ (an expansion that the library does not state; it proves the two-sided bound that follows), and for $k\ge2$
$$\underline a\le\alpha\le\bar a,\qquad\underline a=\frac{5}{2k}-\frac{4}{3k^2}\ \text{(`Parking.alow`)}.$$
The proof is in the record of `Parking.xk_bounds`. The upper bound $\bar a$ is used wherever a quantity increases with $\alpha$: in $\bar S$ (`Parking.Sbar`), in the lower bound $\underline t$ for the kernel deficit (`Parking.tlow`), and in the bound $x\le e^{-1}e^{\bar a}$.

In Lean, `abar k = 5 / (2 * (k : ℝ))`, which is $0$ at $k=0$ by the convention for division by zero; it is used for $k\ge2$.
