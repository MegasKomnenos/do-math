---
weight: unit
short: the diagonal rule beyond the first layer
---
## Description

For $k\ge1$ and $n\ge2k$: if $b(n,k)\le b(n,k-1)$, then $b(n+1,k+1)<b(n+1,k)$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k\ge1$ and $n\ge2k$ be natural numbers. If $b(n,k)\le b(n,k-1)$, then $b(n+1,k+1)<b(n+1,k)$.

## Explanation

**Its place.** Write $d_{n,k}=b(n,k)-b(n,k-1)$ for the step of the column $k$ in the row $n$. The diagonal rule, one of the two rules from which the staircase theorem `Parking.staircase` is derived, says that a step that is not positive is followed by a negative step one row down and one column to the right: $d_{n,k}\le0$ implies $d_{n+1,k+1}<0$, for $n\ge2$ and $1\le k\le n-1$ (`Parking.diagonal_rule`). The first layer of the column $k$ consists of the rows $k+1\le n\le2k-1$. The present statement is the diagonal rule at the positions $(n,k)$ beyond the first layer, $n\ge2k$. In the first layer the rule is proved by other means: for the columns $k\le264$ in `Parking.diagonal_rule_small`, and for the columns $k\ge265$ by the analytic argument along the diagonal.

**Why it holds.** Beyond the first layer the rule has almost no cases. By `Parking.step_pos_beyond` the step $d_{n,k}$ is positive for $n\ge2k$ unless $(n,k)$ is one of eleven positions, so the hypothesis $d_{n,k}\le0$ can hold only there. What remains is that the step is negative at the eleven positions diagonally after them. These are

- $(2k+1,k+1)$ for $1\le k\le7$, the successors of the positions $(2k,k)$: the positions $(3,2),(5,3),(7,4),(9,5),(11,6),(13,7),(15,8)$, each of which is in the last row $2(k+1)-1$ of the first layer of the column $k+1$;
- $(2k+2,k+1)$ for $2\le k\le5$, the successors of the positions $(2k+1,k)$: the positions $(6,3),(8,4),(10,5),(12,6)$, each of which is in the row $2(k+1)$ of the column $k+1$.

All eleven are among the computed negative cells of `Parking.Tab.negative_cells`. So in this region the rule says nothing about how a sign moves along a diagonal in general. Its content is that no step beyond the first layer is zero or negative outside the eleven positions, together with eleven computed signs.

**The Lean form.** The hypothesis is `b n k ≤ b n (k - 1)` and the conclusion `b (n + 1) (k + 1) < b (n + 1) k`, comparisons of natural numbers; `k - 1` is exact because $k\ge1$.

## Proof

*The position $(n,k)$ is one of the eleven.* Suppose that neither $n=2k$ and $k\le7$, nor $n=2k+1$ and $2\le k\le5$. Then `Parking.step_pos_beyond`, applied to $k\ge1$ and $n\ge2k$, gives $b(n,k-1)<b(n,k)$, against the hypothesis $b(n,k)\le b(n,k-1)$. Hence $n=2k$ and $k\le7$, or $n=2k+1$ and $2\le k\le5$.

*The successor is a negative cell.* Put $k'=k+1\ge2$ and $n'=n+1$. Then $n'\ge k'+1$, because $n\ge2k\ge k+1$. `Parking.Tab.negative_cells` states $b(n',k')<b(n',k'-1)$ for $k'\ge2$ and $n'\ge k'+1$ under each of four conditions, among them "$n'\le2k'-1$ and $k'\le8$" and "$n'\le2k'$ and $k'\le7$".

- If $n=2k$ and $k\le7$, then $n'=2k'-1$ and $k'\le8$; the condition "$n'\le2k'-1$ and $k'\le8$" holds.
- If $n=2k+1$ and $2\le k\le5$, then $n'=2k'$ and $k'\le6$; the condition "$n'\le2k'$ and $k'\le7$" holds.

In both cases $b(n',k')<b(n',k'-1)$, that is, $b(n+1,k+1)<b(n+1,k)$.
