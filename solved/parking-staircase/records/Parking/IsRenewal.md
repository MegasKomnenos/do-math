---
weight: unit
short: renewal sequence of a kernel
---
## Description

$u$ is the renewal sequence of the kernel $f$: $u_0=1$ and $u_n=\sum_{i=1}^{n}f_iu_{n-i}$ for every $n\ge1$.

## Statement

Let $f=(f_i)_{i\ge0}$ and $u=(u_n)_{n\ge0}$ be sequences of real numbers. $u$ is *the renewal sequence of the kernel $f$* if
$$u_0=1\qquad\text{and}\qquad u_n=\sum_{i=1}^{n}f_i\,u_{n-i}\quad\text{for every } n\ge1.$$
The term $f_0$ does not occur.

## Explanation

For a given kernel the two conditions determine $u$, term by term: $u_1=f_1$, $u_2=f_1^2+f_2$, and so on. In terms of generating series, $\sum u_nX^n=1/(1-\sum_{i\ge1}f_iX^i)$. When the $f_i$ are probabilities of the lengths of the steps of a renewal process, $u_n$ is the probability that a renewal occurs at time $n$, which gives the notion its name; the library makes no probabilistic assumption, and $\sum f_i$ need not be $1$.

The notion is stated as a property of a pair of sequences, and not as a function that produces $u$ from $f$, because it is applied to a sequence that is given by a closed formula: the library shows that the explicit sequence `Parking.Gres` is the renewal sequence of the frozen kernel `Parking.fker` (`Parking.Gres_isRenewal`). The general results about renewal sequences are `Parking.renewal_pos`, `Parking.renewal_logConvex` and `Parking.resolvent`; they are used in the persistence argument for the far rows of a column (`Parking.extreme_column_le`).

In Lean, `IsRenewal f u` is the conjunction `u 0 = 1 ∧ ∀ n, 1 ≤ n → u n = ∑ i ∈ Icc 1 n, f i * u (n - i)`, with the subtraction of natural numbers, exact since $i\le n$.
