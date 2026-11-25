---
weight: unit
short: persistence of the sign in the first layer, iterated
---
## Description

For $k\ge2$ and $k+1\le m\le n\le2k-1$: if $b(m,k-1)<b(m,k)$, then $b(n,k-1)<b(n,k)$, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$. A positive step in a row of the first layer of a column is followed by positive steps in all the later rows of that layer.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k\ge2$, $m$ and $n$ be natural numbers with $k+1\le m\le n\le2k-1$. If $b(m,k-1)<b(m,k)$, then $b(n,k-1)<b(n,k)$.

## Explanation

**What the statement says.** Write $d_{n,k}=b(n,k)-b(n,k-1)$ for the step of the column $k$ in the row $n$. The rows $k+1\le n\le2k-1$ are the *first layer* of the column $k$ (some records call them the chain range of the column). The statement is `Parking.step_persists` applied repeatedly: a column whose step is positive in one row of its first layer has a positive step in every later row of the layer. Read in the other direction it says: if $d_{n,k}\le0$ in a row $n$ of the first layer, then $d_{m,k}\le0$ in every earlier row $k+1\le m\le n$ of the layer. So within the first layer the rows in which the step is not positive come first, and the rows in which it is positive come after them.

**What it is used for.** Both uses are in the diagonal rule `Parking.diagonal_rule`, which says that a step that is not positive is followed by a negative step one row down and one column to the right, and both concern a position in the first layer. They have the same form. A row of the first layer is known in which the column $k$ is positive. The present statement then shows that a step of the column that is not positive lies in an earlier row, and this is what locates the step.

- In `Parking.diagonal_rule_small`, for $9\le k\le264$, the known row is the row $k+z(k)+1$ of the table of two signs (`Parking.Tab.two_signs`), where $z(k)$ is the number that the table lists for the column (`Parking.Tab.ztab`). A step that is not positive lies in a row $n\le k+z(k)$, and for these rows a second table, `Parking.Tab.next_column_neg`, gives the negative step of the column $k+1$ in the row $n+1$.
- In `Parking.diagonal_rule`, for $k\ge265$, the known row is the row $j$ of the curve increase `Parking.curve_crossing`, which satisfies $(j-k-1)^3\le k^2$. A step that is not positive lies in a row $n<j$, so that $(n-k)^3\le k^2$, and at such a position the rule is the diagonal step `Parking.diagonal_step_curve`.

**The Lean form.** The statement is `{k m n : ℕ} (hk : 2 ≤ k) (hm : k + 1 ≤ m) (hmn : m ≤ n) (hn : n ≤ 2 * k - 1) (h : b m (k - 1) < b m k) : b n (k - 1) < b n k`. The signs are comparisons of natural numbers. The differences `2 * k - 1` and `k - 1` are differences of natural numbers and are the ordinary ones because $k\ge2$.

## Proof

By induction on $n$, starting from $n=m$, where the claim is the assumption. Suppose that the claim holds for some $n\ge m$, and let $n+1\le2k-1$. Then $n\le2k-1$, so the induction hypothesis gives $b(n,k-1)<b(n,k)$. Moreover $k+1\le m\le n\le2k-2$. `Parking.step_persists` states that for $k\ge2$ and $k+1\le n\le2k-2$, $b(n,k-1)<b(n,k)$ implies $b(n+1,k-1)<b(n+1,k)$. This is the claim for $n+1$.
