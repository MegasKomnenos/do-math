---
weight: step
short: numerical bound exp(7/3) ≤ 10.32
---
## Description

The numerical inequality $e^{7/3} \le 10.32$.

## Statement

$\exp(7/3) \le \frac{1032}{100}$.

## Explanation

In `Parking.caseFar` the rows with offset $\frac45k < r \le k - 1$ are treated with a run of $t_0 = \lfloor\frac{7}{15}k\rfloor + 1$ positive rows. The bound `Parking.P1_le` of the near term asks for a number $E_0 \ge e^{5\sigma}$ with $\sigma = \frac7{15}$, and $5\sigma = \frac73$. The value is $e^{7/3} = 10.3122\ldots$

## Proof

As for `Parking.exp_41_60`: from $e \le 2.7183$, the inequality $2.7183^p \le B^q$ between rational numbers implies $e^{p/q} \le B$. Here $p = 7$, $q = 3$, $B = 10.32$, and $2.7183^7 \le 10.32^3$ is checked by exact arithmetic.
