---
weight: step
short: cross form of the log-convexity of the prime kernel
---
## Description

For $1 \le m \le r$ and every $t \ge 0$, the prime kernel satisfies $\varepsilon_{m+t}\,\varepsilon_r \le \varepsilon_m\,\varepsilon_{r+t}$.

## Statement

Let $m$, $r$, $t$ be natural numbers with $1 \le m \le r$. Then $\varepsilon_{m+t}\,\varepsilon_r \le \varepsilon_m\,\varepsilon_{r+t}$, where $\varepsilon_m = (m-1)^{m-1}/m!$ is the sequence of `Parking.eps`.

## Explanation

Dividing by the positive numbers $\varepsilon_m\varepsilon_r$, the statement says that the ratio $\varepsilon_{m+t}/\varepsilon_m$ over a step of length $t$ does not decrease in the starting index $m$. It is the form in which the log-convexity `Parking.eps_logconvex` is applied: the three-term inequality compares neighbours, and the arguments need two indices at an arbitrary distance. Its only use is `Parking.kapx_cross`, the same inequality for the tilted kernel.

## Proof

Apply `Parking.logConvex_cross` to the sequence $G_n = \varepsilon_{n+1}$, $n \ge 0$. That statement says: if $G$ is positive and $G_{n+1}^2 \le G_nG_{n+2}$ for all $n$, then $G_{a+c}\,G_b \le G_a\,G_{b+c}$ for $a \le b$ and every $c$. Its hypotheses are `Parking.eps_pos` and `Parking.eps_logconvex`. With $a = m - 1$, $b = r - 1$ and $c = t$ the conclusion is the claim.
