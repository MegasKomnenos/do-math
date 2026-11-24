---
weight: step
short: √R ≥ 6.48 for R ≥ 42
---
## Description

For every natural number $R \ge 42$, $\sqrt{R} \ge 6.48$.

## Statement

For every natural number $R$ with $R \ge 42$,

$$6.48 \le \sqrt{R}.$$

## Explanation

The explicit estimates of the curve increase are carried out in the single real variable $s = \sqrt{R}$, where $R = r + 1$ and $r = n - k$ is the deficit of the position $(n,k)$ at which `Parking.curve_step_pos` proves a positive step. That theorem is proved for $R \ge 42$. The inequalities in $s$ that it rests on are stated for real $s \ge 6.48$ (`Parking.K_facts`, `Parking.rho_bound`, `Parking.Wsum_numeric`, `Parking.Asum_numeric`, `Parking.Gsum_numeric`, `Parking.pair_numeric`, `Parking.impulse_numeric`), with the one exception of `Parking.k_window`, which assumes $s > 0$ and $s^2 \ge 42$. The present statement is the passage from the natural number $R$ to that half-line, and the positivity of $s$ that `Parking.k_window` asks for is taken from it as well. It is used in the proofs of `Parking.Wsum_ge`, `Parking.Gsum_le`, `Parking.Asum_le` and `Parking.curve_step_pos`.

The number $6.48$ is $\sqrt{42} = 6.4807\ldots$ rounded down to two decimal places: $6.48^2 = 41.9904$.

The Lean statement takes the square root of the real number that the natural number $R$ casts to.

## Proof

Since $6.48 \ge 0$, the inequality $6.48 \le \sqrt{R}$ is equivalent to $6.48^2 \le R$. This holds because $6.48^2 = 41.9904 \le 42 \le R$.
