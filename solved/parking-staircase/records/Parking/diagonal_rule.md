---
weight: unit
short: the diagonal rule
---
## Description

For $n\ge2$ and $1\le k\le n-1$: if $b(n,k)\le b(n,k-1)$, then $b(n+1,k+1)<b(n+1,k)$, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$. A step that is not positive is followed by a negative step one row down and one column to the right.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ whose maximum displacement is exactly $\ell$ (`Parking.b`). Let $n\ge2$ and $k$ be natural numbers with $1\le k\le n-1$. If $b(n,k)\le b(n,k-1)$, then $b(n+1,k+1)<b(n+1,k)$.

## Explanation

**What the rule says.** Arrange the numbers $b(n,k)$ in an array whose rows are indexed by the length $n$ and whose columns by the displacement $k$, $0\le k\le n-1$, and write
$$d_{n,k}=b(n,k)-b(n,k-1),\qquad 1\le k\le n-1,$$
for the *step of the column $k$ in the row $n$*. The rule is $d_{n,k}\le0\Rightarrow d_{n+1,k+1}<0$. The position $(n+1,k+1)$ is the neighbour of $(n,k)$ along the diagonal, one row down and one column to the right. The conclusion is strict although the hypothesis is not: a step that is zero is followed along the diagonal by a negative step, as a negative step is.

**The rule read for columns.** The column $k$ begins in the row $k+1$. Suppose that it is not positive in the rows $k+1,\dots,n$. The rule, applied in each of these rows, shows that the column $k+1$ is negative in the rows $k+2,\dots,n+1$, that is, from its first row to one row beyond $n$. So the column $k+1$ turns positive strictly later than the column $k$: the first positive rows of the columns increase strictly with the column. For a row this means that the peak cannot move by more than one position when the length grows by one.

**What it is used for.** It is the second of the two hypotheses of `Parking.peak_induction`, taken for the array $b$; the first is `Parking.column_rule`. From the two, `Parking.staircase` obtains the shape of every row of $b$. In that induction the diagonal rule is what carries the part of the row $n$ after its peak over to the row $n+1$, shifted by one column, and makes it strictly falling.

**How it is assembled.** The rule is put together from statements about three regions of the array, according to the position $(n,k)$ at which the hypothesis is made. The rows $k+1\le m\le2k-1$ are called the *first layer* of the column $k$.

- *Beyond the first layer, $n\ge2k$.* The rule is `Parking.diagonal_rule_beyond`. In this region the step is positive at every position but eleven, so the hypothesis can hold only there, and the diagonal neighbours of the eleven positions have negative steps.
- *In the first layer of a column $k\le264$.* The rule is `Parking.diagonal_rule_small`, which rests on tables of exactly computed signs and, for $k\ge9$, on the persistence `Parking.step_persists_iter`.
- *In the first layer of a column $k\ge265$.* Here two analytic statements are combined. The curve increase `Parking.curve_crossing` gives a row $j>k$ with $(j-k-1)^3\le k^2$ in which the column $k$ is positive. By the persistence of the sign in the first layer, `Parking.step_persists_iter`, the column is then positive in every later row of its first layer. A step that is not positive therefore lies in a row $n<j$, and then $(n-k)^3\le k^2$: the position lies *behind the curve* $k^2=(n-k)^3$. At a position behind the curve the rule is the diagonal step `Parking.diagonal_step_curve`.

The third region is where the rule is hardest. The diagonal step is proved only behind the curve, so the argument needs to know that the column has turned positive by the time it leaves that region, to within one row; this is what the curve increase supplies, and a weaker bound for the first positive row would not do. In these columns the curve increase enters a second time, because the persistence used here rests on an early positive row of the column, which in these columns is the row of the curve increase (`Parking.positive_row_early`); the curve increase itself is proved without persistence. The account of the whole argument, with the statements behind each region and the reason why the columns divide at $265$, is in the record of `Parking.staircase`.

**The Lean form.** The statement is `(n k : ℕ) (hn : 2 ≤ n) (hk1 : 1 ≤ k) (hk2 : k ≤ n - 1) (h : b n k ≤ b n (k - 1)) : b (n + 1) (k + 1) < b (n + 1) k`. The sign of a step is written as a comparison of the two natural numbers: `b n k ≤ b n (k - 1)` for a step that is not positive and `b (n + 1) (k + 1) < b (n + 1) k` for a negative step. The differences `n - 1` and `k - 1` are differences of natural numbers and are the ordinary ones because $n\ge2$ and $k\ge1$. The hypothesis $n\ge2$ follows from $1\le k\le n-1$; it is stated so that the rule has the form of the second hypothesis of `Parking.peak_induction`.

## Proof

Let $n\ge2$, $1\le k\le n-1$ and $b(n,k)\le b(n,k-1)$. Distinguish three cases.

*Case $n\ge2k$.* `Parking.diagonal_rule_beyond` states that for $k\ge1$ and $n\ge2k$, $b(n,k)\le b(n,k-1)$ implies $b(n+1,k+1)<b(n+1,k)$. This is the claim.

*Case $n<2k$ and $k\le264$.* Then $k\ge2$, because $k=1$ would give $n<2$. Also $k+1\le n\le2k-1$. `Parking.diagonal_rule_small` states that for $2\le k\le264$ and $k+1\le n\le2k-1$, $b(n,k)\le b(n,k-1)$ implies $b(n+1,k+1)<b(n+1,k)$. This is the claim.

*Case $n<2k$ and $k\ge265$.* Again $k+1\le n\le2k-1$. By `Parking.curve_crossing` there is a natural number $j$ with
$$k<j,\qquad(j-k-1)^3\le k^2,\qquad b(j,k-1)<b(j,k).$$
We show $n<j$. Suppose $j\le n$. `Parking.step_persists_iter` states that for $k\ge2$ and $k+1\le m\le n\le2k-1$, $b(m,k-1)<b(m,k)$ implies $b(n,k-1)<b(n,k)$. With $m=j$ it gives $b(n,k-1)<b(n,k)$, which contradicts the hypothesis $b(n,k)\le b(n,k-1)$. Hence $n<j$, so $n-k\le j-k-1$ and
$$(n-k)^3\le(j-k-1)^3\le k^2 .$$
Put $r=n-k$; then $r\ge1$, because $k\le n-1$, and $r^3\le k^2$. `Parking.diagonal_step_curve` states that for $k\ge265$, $r\ge1$ and $r^3\le k^2$, $b(k+r,k)\le b(k+r,k-1)$ implies $b(k+r+1,k+1)<b(k+r+1,k)$. Since $k+r=n$, its hypothesis is the hypothesis of the rule and its conclusion is the claim.
