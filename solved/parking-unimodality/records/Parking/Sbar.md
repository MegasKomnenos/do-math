---
weight: step
short: closed-form bound for the sum S_R
---
## Description

The closed form $\bar S=1+c_0\bigl[2\sqrt{R-1}-1+\tfrac{2\bar a}{3}R^{3/2}+\tfrac{2q\bar a^2}{5}R^{5/2}\bigr]$ with $c_0=1/\sqrt{2\pi}$, $\bar a=5/(2k)$, $q=0.633$; it bounds $S_R=\sum_{i<R}(ix)^i/i!$ from above.

## Statement

For natural numbers $k$ and $R$,
$$\bar S=\bar S(k,R)=1+c_0\Bigl[2\sqrt{R-1}-1+\frac{2\bar a}{3}\,R\sqrt R+\frac{2q\,\bar a^{2}}{5}\,R^{2}\sqrt R\Bigr],$$
where $c_0=1/\sqrt{2\pi}$ (`Parking.c0`), $\bar a=5/(2k)$ (`Parking.abar`) and $q=633/1000$.

## Explanation

For $k\ge2$, $R\ge2$ and $\bar aR\le0.6679$ one has $S_R\le\bar S$, where $S_R$ is the sum `Parking.SR` at the diagonal tilt $x$ of the column $k$; this is part (ii) of the proof of `Parking.cross_of_bounds`. Each term of $\bar S$ has one source. With $x=e^{\alpha-1}$ and $p_i=e^{-i}i^i/i!$ (`Parking.poissonMass`), the terms of $S_R$ are $p_ie^{\alpha i}\le p_i\,(1+\bar a\,i+q\,\bar a^2i^2)$. The leading $1$ is the term $i=0$. Stirling's bound $p_i\le c_0/\sqrt i$ turns the three sums into $c_0\sum i^{-1/2}$, $c_0\bar a\sum i^{1/2}$ and $c_0q\bar a^2\sum i^{3/2}$ over $1\le i\le R-1$, which are bounded by $2\sqrt{R-1}-1$, $\frac23R^{3/2}$ and $\frac25R^{5/2}$.

The constant $q=0.633$ and the threshold $0.6679$ belong together: $e^s\le1+s+0.633\,s^2$ holds for $0\le s\le0.6679$ (`Parking.exp_le_quad`), and the hypothesis $\bar aR\le0.6679$ of `Parking.cross_of_bounds` guarantees $\alpha i\le\bar aR$ in that range. Both numbers are chosen for the application in `Parking.crossing_strip`, where the estimate $\bar aR\le\frac{11}{2}u(1+u^2)$ used for all $k\ge265$ gives $0.66782$ (the value of $\bar aR$ itself at $k=265$, $R=70$ is $0.6604$).

In the application $R$ is of order $k^{2/3}$, so the three bracketed terms after the $-1$ are of orders $k^{1/3}$, $1$ and $k^{-1/3}$.

In Lean, `Sbar k R` is written with `Real.sqrt ((R : ℝ) - 1)`, `(R : ℝ) * Real.sqrt R` and `(R : ℝ) ^ 2 * Real.sqrt R`. The real square root of a negative number is $0$ in Lean, which only matters for $R=0$; the closed form is used for $R\ge2$.
