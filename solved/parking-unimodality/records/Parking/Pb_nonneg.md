---
weight: step
short: nonnegativity of the birthday tail
---
## Description

The birthday tail is nonnegative: $P_{m,j} \ge 0$.

## Statement

For all natural numbers $m$ and $j$, $P_{m,j} \ge 0$, where $P_{m,j} = \prod_{i=0}^{j-1}(1 - i/m)$ is the birthday tail of `Parking.Pb`.

## Explanation

The statement needs an argument only because the factors $1 - i/m$ of the defining product are negative for $i > m$; the product is then $0$ because it also contains the factor with $i = m$. Nonnegativity is what allows the inequalities between tails to be multiplied and summed: it is used in `Parking.Pb_lr`, `Parking.one_le_sbirth`, in the variance argument of `Parking.Dbirth_le`, and in the proofs of `Parking.tau_succ_le` and `Parking.mu0_le_muh`. The statement includes $m = 0$, where $P_{0,j} = 1$.

## Proof

If $m = 0$, every factor of the product is $1$ under the convention of `Parking.Pb`. Let $m \ge 1$. If $j \le m$, every factor has $i < j \le m$, so $i/m \le 1$ and the factor $1 - i/m$ is nonnegative; a product of nonnegative factors is nonnegative. If $j > m$, then $P_{m,j} = 0$ by `Parking.Pb_eq_zero`.
