---
weight: step
short: numerical bound exp(4/3) ≤ 3.8
---
## Description

The numerical inequality $e^{4/3} \le 3.8$.

## Statement

$\exp(4/3) \le \frac{38}{10}$.

## Explanation

In `Parking.caseFar` the rows with offset $\frac35k < r \le \frac45k$ are treated with a run of $t_0 = \lfloor\frac{4}{15}k\rfloor + 1$ positive rows. The bound `Parking.P1_le` of the near term asks for a number $E_0 \ge e^{5\sigma}$ with $\sigma = \frac4{15}$, and $5\sigma = \frac43$. The value is $e^{4/3} = 3.7937\ldots$

## Proof

As for `Parking.exp_41_60`: from $e \le 2.7183$, the inequality $2.7183^p \le B^q$ between rational numbers implies $e^{p/q} \le B$. Here $p = 4$, $q = 3$, $B = 3.8$, and $2.7183^4 \le 3.8^3$ is checked by exact arithmetic ($54.60\ldots \le 54.872$).
