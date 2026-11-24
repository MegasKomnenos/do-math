---
weight: unit
short: the column rule
---
## Description

For $n\ge2$ and $1\le k\le n-1$: if $b(n,k-1)<b(n,k)$, then $b(n+1,k-1)<b(n+1,k)$, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$. A positive step stays positive one row down in the same column.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ whose maximum displacement is exactly $\ell$ (`Parking.b`). Let $n\ge2$ and $k$ be natural numbers with $1\le k\le n-1$. If $b(n,k-1)<b(n,k)$, then $b(n+1,k-1)<b(n+1,k)$.

## Explanation

**What the rule says.** Arrange the numbers $b(n,k)$ in an array whose rows are indexed by the length $n$ and whose columns by the displacement $k$, $0\le k\le n-1$, and write
$$d_{n,k}=b(n,k)-b(n,k-1),\qquad 1\le k\le n-1,$$
for the *step of the column $k$ in the row $n$*. The rule is $d_{n,k}>0\Rightarrow d_{n+1,k}>0$. Applied repeatedly it says that a column which is positive in one row is positive in every later row: the sign of a column changes at most once, from not positive to positive. The rule starts from a positive step and says nothing when $d_{n,k}$ is zero or negative. Together with `Parking.diagonal_rule` it leaves one step of the row $n+1$ undecided. If the steps of the row $n$ are positive up to the column $p$ and not positive from the column $p+1$ on, the step $d_{n+1,p+1}$ is the conclusion of neither rule: the column rule would need $d_{n,p+1}>0$, and the diagonal rule, whose conclusion lies one column to the right of its hypothesis, would need $d_{n,p}\le0$ (for $p=0$ there is no step $d_{n,0}$ at all). That step may be positive, zero or negative, and this is the reason why the shape of a row that the two rules give, `Parking.IsPeak`, allows one equality between neighbouring entries.

**What it is used for.** It is the first of the two hypotheses of `Parking.peak_induction`, taken for the array $b$; the second is `Parking.diagonal_rule`. From the two, `Parking.staircase` obtains the shape of every row of $b$. In that induction the column rule is what carries the rising part of the row $n$ over to the row $n+1$.

**How it is assembled.** The rule is put together from two statements, according to the row $n+1$ in which the conclusion lies. The rows $k+1\le m\le2k-1$ are called the *first layer* of the column $k$; some records call them the chain range of the column.

- If the conclusion lies in the first layer, $n+1\le2k-1$, the rule is the persistence of the sign in the first layer, `Parking.step_persists`: for $k\ge2$ and $k+1\le n\le2k-2$, $d_{n,k}>0$ implies $d_{n+1,k}>0$. It asks for a positive step in its hypothesis, which is all that the column rule asks, so nothing about a step that is zero is needed.
- If the conclusion lies in a row $n+1\ge2k$, beyond the first layer, the rule is `Parking.column_rule_beyond`.

The two cases differ in kind. In the first layer the content of the rule is that a column which has turned positive does not turn back, and its proof is an argument about the course of the column. Beyond the first layer the step is positive at every position but eleven, which lie in the columns $k\le7$. There the rule holds because its conclusion holds whatever the row before looks like; and where the conclusion would lie at one of the eleven positions, the step in the row before is negative, so that the hypothesis fails. The account of the whole argument, with the statements behind each case, is in the record of `Parking.staircase`.

**The Lean form.** The statement is `(n k : ℕ) (hn : 2 ≤ n) (hk1 : 1 ≤ k) (hk2 : k ≤ n - 1) (h : b n (k - 1) < b n k) : b (n + 1) (k - 1) < b (n + 1) k`. The sign of a step is written as a comparison of the two natural numbers, so no difference is formed. The differences `n - 1` and `k - 1` are differences of natural numbers and are the ordinary ones because $n\ge2$ and $k\ge1$. The hypothesis $n\ge2$ follows from $1\le k\le n-1$; it is stated so that the rule has the form of the first hypothesis of `Parking.peak_induction`.

## Proof

Let $n\ge2$, $1\le k\le n-1$ and $b(n,k-1)<b(n,k)$. Distinguish two cases.

*Case $n+1<2k$.* Then $k\ge2$, because $k=1$ would give $n<1$. Also $k+1\le n$ and $n\le2k-2$. So `Parking.step_persists` applies to $k$ and $n$: it states that for $k\ge2$ and $k+1\le n\le2k-2$, $b(n,k-1)<b(n,k)$ implies $b(n+1,k-1)<b(n+1,k)$. This is the claim.

*Case $n+1\ge2k$.* `Parking.column_rule_beyond` states that for $k\ge1$, $n\ge k+1$ and $n+1\ge2k$, $b(n,k-1)<b(n,k)$ implies $b(n+1,k-1)<b(n+1,k)$. Its hypotheses hold, since $k\le n-1$ gives $k+1\le n$. This is the claim.
