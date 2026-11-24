---
weight: unit
short: log-convexity of the Cayley coefficients
---
## Description

The Cayley coefficients $a_j = j^{j-1}/j!$ are log-convex on $j \ge 1$, in the cross-multiplied form $a_{u+c}\,a_v \le a_u\,a_{v+c}$ for $1 \le u \le v$ and $c \ge 0$.

## Statement

For all natural numbers $u$, $v$, $c$ with $1 \le u \le v$,

$$a_{u+c}\, a_v \le a_u\, a_{v+c},$$

where $a$ denotes the Cayley coefficients (`Parking.cay`).

## Explanation

Since the $a_j$ with $j \ge 1$ are positive, the statement says that the growth factor $a_{u+c}/a_u$ over $c$ steps does not decrease when the starting index $u$ increases. For $c = 1$ and $v = u+1$ it is the usual log-convexity $a_{u+1}^2 \le a_u\,a_{u+2}$, and the general case is equivalent to that. It holds because the ratio of consecutive coefficients, $(1+1/j)^{j-1}$ (`Parking.cay_ratio`), is nondecreasing (`Parking.psi_mono`). The cross-multiplied form with a general shift $c$ is the one in which the property is applied.

The restriction $u \ge 1$ cannot be dropped: for $u = 0$ the right-hand side is $0$ because $a_0 = 0$, while the left-hand side is positive when $c, v \ge 1$.

The statement is used in three places: in the comparison of the two last-car position laws behind the diagonal monotonicity `Parking.zr_diag_mono`; for the log-convexity of the tilted sequence $c_n x^n$, $c_n = a_{n+1}$ (`Parking.FirstLayer.ccT_logconvex`); and as the log-supermodularity of the weights of the parts of a composition, as a function of its set of cut points, that the correlation inequality in the proof of `Parking.Lam_gain` requires.

## Proof

By induction on $c$, for fixed $u \le v$. For $c = 0$ both sides are $a_u a_v$. Suppose $a_{u+c}\,a_v \le a_u\,a_{v+c}$. Write $\psi(j) = (1+1/j)^{j-1}$. By `Parking.cay_ratio`, applied at the indices $u + c \ge 1$ and $v + c \ge 1$,

$$a_{u+c+1} = \psi(u+c)\, a_{u+c}, \qquad a_{v+c+1} = \psi(v+c)\, a_{v+c}.$$

By `Parking.psi_mono`, $\psi(u+c) \le \psi(v+c)$, since $1 \le u + c \le v + c$. All quantities are nonnegative (`Parking.cay_nonneg`), so the two inequalities can be multiplied:

$$a_{u+c+1}\, a_v = \psi(u+c)\,\bigl(a_{u+c}\, a_v\bigr) \le \psi(v+c)\,\bigl(a_u\, a_{v+c}\bigr) = a_u\, a_{v+c+1}.$$
