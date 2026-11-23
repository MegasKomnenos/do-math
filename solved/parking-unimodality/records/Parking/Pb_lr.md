---
weight: step
short: likelihood-ratio order of the birthday tails of m and m + 1
---
## Description

The birthday tails of $m$ and of $m+1$ are in likelihood-ratio order: $P_{m,q'}\,P_{m+1,q} \le P_{m,q}\,P_{m+1,q'}$ for $q \le q' \le m+1$.

## Statement

For natural numbers $m$, $q$, $q'$ with $q \le q' \le m + 1$,

$$P_{m,q'}\;P_{m+1,q} \;\le\; P_{m,q}\;P_{m+1,q'},$$

where $P_{m,j} = \prod_{i=0}^{j-1}(1 - i/m)$ is the birthday tail of `Parking.Pb`. The statement includes $m = 0$, with $P_{0,j} = 1$ as in `Parking.Pb`.

## Explanation

Where $P_{m,q}$ and $P_{m,q'}$ are positive, the inequality says that the quotient $P_{m+1,j}/P_{m,j}$ does not decrease from $j = q$ to $j = q'$. The reason is visible in one step: passing from $j$ to $j+1$ multiplies $P_{m,j}$ by $1 - j/m$ and $P_{m+1,j}$ by the larger number $1 - j/(m+1)$. The inequality is written in cross-multiplied form so that it also holds at $q' = m+1$, where $P_{m,q'} = 0$ and a quotient would not be defined.

The statement is used once, in the proof of `Parking.Dbirth_mono`. Multiplied by $a_m a_{m+1}\, q\, q' \ge 0$ and combined with `Parking.Tq_eq`, it becomes $T_{m,q'}\,T_{m+1,q} \le T_{m,q}\,T_{m+1,q'}$: the numbers of parts of the compositions of $m$ and of $m+1$ are in likelihood-ratio order, which is the hypothesis of `Parking.lr_factorial_moment_le`.

## Proof

Fix $m$ and $q$ and argue by induction on $q'$, starting at $q' = q$, where the two sides are equal.

For the step from $q' = k$ to $q' = k+1$, assume $q \le k$ and $k + 1 \le m + 1$, so that $k \le m$, and assume $P_{m,k}\,P_{m+1,q} \le P_{m,q}\,P_{m+1,k}$. Put $\alpha = 1 - k/m$ and $\beta = 1 - k/(m+1)$. By `Parking.Pb_succ`, $P_{m,k+1} = P_{m,k}\,\alpha$ and $P_{m+1,k+1} = P_{m+1,k}\,\beta$. Since $k \le m$, we have $0 \le \alpha \le \beta$; for $m = 0$ this holds because then $k = 0$ and $\alpha = \beta = 1$. Therefore

$$P_{m,k+1}\,P_{m+1,q} = \bigl(P_{m,k}\,P_{m+1,q}\bigr)\,\alpha \;\le\; \bigl(P_{m,q}\,P_{m+1,k}\bigr)\,\alpha \;\le\; \bigl(P_{m,q}\,P_{m+1,k}\bigr)\,\beta = P_{m,q}\,P_{m+1,k+1}.$$

The first inequality multiplies the induction hypothesis by $\alpha \ge 0$. The second uses $\alpha \le \beta$ and $P_{m,q}\,P_{m+1,k} \ge 0$, which is `Parking.Pb_nonneg`.
