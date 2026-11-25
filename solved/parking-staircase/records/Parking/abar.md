---
weight: step
short: upper bound for the tilt exponent
---
## Description

The number $\bar a=5/(2k)$, an upper bound for $1+\log x$ where $x=1/\gamma_k$ is the diagonal tilt of the column $k$.

## Statement

For a natural number $k$, $\bar a=\bar a(k)=\dfrac{5}{2k}$.

## Explanation

Write the diagonal tilt (`Parking.xk`) as $x=e^{\alpha-1}$, that is $\alpha=1+\log x=1-(k-2)\log(1+1/k)$ for $k\ge2$. The number $\alpha$ measures how far the tilt lies above $e^{-1}$, and the closed-form bounds for the tilted kernel are expressed through it: the tilted kernel masses (`Parking.kapx`) are $e^{-m}\varepsilon_m$ times $e^{\alpha m}$. Expanding the logarithm gives $\alpha=\frac{5}{2k}-\frac{4}{3k^2}+O(k^{-3})$ (an expansion that the library does not state; it proves the two-sided bound that follows), and for $k\ge2$
$$\underline a\le\alpha\le\bar a,\qquad\underline a=\frac{5}{2k}-\frac{4}{3k^2}\ \text{(`Parking.alow`)}.$$
The proof is in the record of `Parking.xk_bounds`. The upper bound $\bar a$ is used through the bound $x\le e^{-1}e^{\bar a}$ of `Parking.xk_bounds`: in the form $e^{1-\bar a}\le\gamma_k$ for the comparisons of the kernel $\varepsilon$ with $\gamma_k$ (`Parking.eps_succ_le_gam`, `Parking.Fk_anti`, `Parking.theta_f_le`), and in the form $x^t\le e^{-t}e^{\bar a t}$ for the bound `Parking.P1_le`.

In Lean, `abar k = 5 / (2 * (k : ℝ))`, which is $0$ at $k=0$ by the convention for division by zero; it is used for $k\ge2$.
