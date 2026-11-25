---
weight: unit
short: the column rule beyond the first layer
---
## Description

For $k\ge1$, $n\ge k+1$ and $n+1\ge2k$: if $b(n,k-1)<b(n,k)$, then $b(n+1,k-1)<b(n+1,k)$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k\ge1$ and $n$ be natural numbers with $n\ge k+1$ and $n+1\ge2k$. If $b(n,k-1)<b(n,k)$, then $b(n+1,k-1)<b(n+1,k)$.

## Explanation

**Its place.** Write $d_{n,k}=b(n,k)-b(n,k-1)$ for the step of the column $k$ in the row $n$. The column rule, one of the two rules from which the staircase theorem `Parking.staircase` is derived, says that a positive step stays positive one row down in the same column: $d_{n,k}>0$ implies $d_{n+1,k}>0$, for $n\ge2$ and $1\le k\le n-1$ (`Parking.column_rule`). The first layer of the column $k$ consists of the rows $k+1\le n\le2k-1$. The present statement is the column rule in the cases in which the conclusion lies beyond the first layer, in a row $n+1\ge2k$. In the other cases, where the row $n+1$ belongs to the first layer, the rule is the persistence of the sign in the first layer: there a positive step of a column is followed by a positive step in the next row.

**Why it holds.** Beyond the first layer the conclusion needs the hypothesis at very few places. By `Parking.step_pos_beyond` the step $d_{n+1,k}$ is positive whatever the step of the row $n$ is, unless $(n+1,k)$ is one of eleven positions, $(2k,k)$ with $k\le7$ or $(2k+1,k)$ with $2\le k\le5$. Under the conditions of the statement ten of them can occur as $(n+1,k)$, those with $k\ge2$. At these ten the conclusion is false, since the step there is negative (`Parking.Tab.negative_cells`), and the rule holds because its hypothesis is false as well: the position $(n,k)$ directly above is $(2k-1,k)$ with $2\le k\le7$ or $(2k,k)$ with $2\le k\le5$, and the step there is negative too, by the same table. So the statement combines the sign pattern beyond the first layer with ten computed negative signs.

**The condition $n\ge k+1$.** For $k\ge2$ it follows from $n+1\ge2k$. For $k=1$ it says $n\ge2$ and excludes the row $n=1$, whose successor $(2,1)$ is the eleventh exceptional position. The column rule is used for $n\ge2$ only.

**The Lean form.** The signs are comparisons of natural numbers, `b n (k - 1) < b n k`; `k - 1` is exact because $k\ge1$. The condition $n+1\ge2k$ is written `2 * k ≤ n + 1`.

## Proof

Call a position $(m,k)$ *exceptional* if $m=2k$ and $k\le7$, or $m=2k+1$ and $2\le k\le5$.

*The position $(n+1,k)$ is not exceptional.* Then `Parking.step_pos_beyond`, applied to the column $k\ge1$ and the row $n+1\ge2k$, gives $b(n+1,k-1)<b(n+1,k)$. The hypothesis on the row $n$ is not used.

*The position $(n+1,k)$ is exceptional.* We show that the hypothesis $b(n,k-1)<b(n,k)$ fails, so that there is nothing to prove.

`Parking.Tab.negative_cells` states $b(n,k)<b(n,k-1)$ for $k\ge2$ and $n\ge k+1$ under each of four conditions, among them "$n\le2k-1$ and $k\le8$" and "$n\le2k$ and $k\le7$". The condition $n\ge k+1$ is a hypothesis of the present statement.

- If $n+1=2k$ and $k\le7$, then $n=2k-1$, and $n\ge k+1$ gives $k\ge2$. The condition "$n\le2k-1$ and $k\le8$" holds, so $b(n,k)<b(n,k-1)$.
- If $n+1=2k+1$ and $2\le k\le5$, then $n=2k$. The condition "$n\le2k$ and $k\le7$" holds, so $b(n,k)<b(n,k-1)$.

In both cases $b(n,k)<b(n,k-1)$ contradicts $b(n,k-1)<b(n,k)$.
