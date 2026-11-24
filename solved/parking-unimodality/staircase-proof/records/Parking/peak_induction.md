---
weight: unit
short: the induction on the row
---
## Description

If an array $f$ of natural numbers satisfies, for $n\ge2$ and $1\le k\le n-1$, the column rule ($f(n,k-1)<f(n,k)$ implies $f(n+1,k-1)<f(n+1,k)$) and the diagonal rule ($f(n,k)\le f(n,k-1)$ implies $f(n+1,k+1)<f(n+1,k)$), then every row $n\ge2$ has its peak at some position $p$, and the row $n+1$ has its peak at $p$ or a strict peak at $p+1$.

## Statement

Let $f:\mathbb N\times\mathbb N\to\mathbb N$ be an array of natural numbers; its row $n$ consists of the entries $f(n,0),\dots,f(n,n-1)$. Suppose that for all natural numbers $n\ge2$ and $k$ with $1\le k\le n-1$ the following two implications hold.

- **Column rule.** If $f(n,k-1)<f(n,k)$, then $f(n+1,k-1)<f(n+1,k)$.
- **Diagonal rule.** If $f(n,k)\le f(n,k-1)$, then $f(n+1,k+1)<f(n+1,k)$.

Then for every natural number $n\ge2$ there is a natural number $p$ such that the row $n$ of $f$ has its peak at $p$ (`Parking.IsPeak`), and the row $n+1$ has its peak at $p$ or a strict peak at $p+1$ (`Parking.IsStrictPeak`).

Written out, the conclusion says: $p\le n-1$,
$$f(n,0)<\dots<f(n,p)\ \ge\ f(n,p+1)>\dots>f(n,n-1),$$
and one of the two chains
$$f(n+1,0)<\dots<f(n+1,p)\ \ge\ f(n+1,p+1)>\dots>f(n+1,n),$$
$$f(n+1,0)<\dots<f(n+1,p+1)>f(n+1,p+2)>\dots>f(n+1,n)$$
holds. The first chain ends with $f(n,n-1)$ and the other two with $f(n+1,n)$; where the position of the peak is the last entry of its row, the part of the chain after it is absent.

## Explanation

**The rules in terms of steps.** Call $f(n,k)-f(n,k-1)$ the *step* of the row $n$ at the column $k$. The row $n$ has the steps $1,\dots,n-1$, and the hypotheses are asked for exactly the positions $(n,k)$, $n\ge2$, $1\le k\le n-1$, at which a step exists. The column rule says that a positive step is followed by a positive step one row down in the same column. The diagonal rule says that a step that is not positive, that is, zero or negative, is followed by a negative step one row down and one column to the right. Both conclusions are strict, and the hypothesis of the diagonal rule includes the step zero.

**Why the rules give the shape of every row.** The row $n+1$ has $n$ steps, one more than the row $n$. Suppose that the steps of the row $n$ are positive up to a position $p$ and not positive after it. The column rule carries the $p$ positive steps down, to the steps $1,\dots,p$ of the row $n+1$. The diagonal rule carries the $n-1-p$ other steps down and to the right, to the steps $p+2,\dots,n$ of the row $n+1$, and makes them negative. This accounts for $n-1$ of the $n$ steps of the row $n+1$. The remaining step, the step $p+1$, is the conclusion of neither rule, and its sign is the only freedom: if it is positive, the peak has moved to $p+1$ and every step of the row $n+1$ has a strict sign; if it is zero or negative, the peak has stayed at $p$. The statement records both cases, and the definitions `Parking.IsPeak` and `Parking.IsStrictPeak` are made so that they describe them.

**What follows about the peaks.** A row has its peak at one position at most (see `Parking.IsPeak`); write $p_n$ for the peak position of the row $n$. A row with a strict peak at $p+1$ has its peak at $p+1$, so the statement gives $p_{n+1}=p_n$ or $p_{n+1}=p_n+1$ for every $n\ge2$: when the length grows by one, the peak stays or moves one position to the right. Plotted against $n$, the positions $p_n$ form a staircase; the statement for the array of the numbers of parking functions, `Parking.staircase`, has its name from this. An equality between two neighbouring entries can occur only directly after the peak, and only in a row whose peak is at the same position as the peak of the row before.

**The statement is about arrays, and the rules are exactly its content.** Nothing about parking functions enters; the theorem separates the argument on finite sequences from the two facts about the numbers $b(n,\ell)$ that `Parking.staircase` feeds into it, `Parking.column_rule` and `Parking.diagonal_rule`. The two rules are also necessary for the conclusion. Suppose the conclusion holds for an array, and let $p$ be the position it gives for the row $n$. A positive step of the row $n$ is at a column $k\le p$, and the step $k$ of the row $n+1$ is positive whether that row has its peak at $p$ or a strict peak at $p+1$; this is the column rule. A step of the row $n$ that is not positive is at a column $k\ge p+1$, and the step $k+1\ge p+2$ of the row $n+1$ is negative in both cases; this is the diagonal rule. The library proves only the direction it uses, from the rules to the shape of the rows.

**The Lean form.** The array is `f : ℕ → ℕ → ℕ`. The two hypotheses are `∀ n k, 2 ≤ n → 1 ≤ k → k ≤ n - 1 → f n (k - 1) < f n k → f (n + 1) (k - 1) < f (n + 1) k` and `∀ n k, 2 ≤ n → 1 ≤ k → k ≤ n - 1 → f n k ≤ f n (k - 1) → f (n + 1) (k + 1) < f (n + 1) k`, and the conclusion is `∀ n, 2 ≤ n → ∃ p, IsPeak f n p ∧ (IsPeak f (n + 1) p ∨ IsStrictPeak f (n + 1) (p + 1))`. The differences `n - 1` and `k - 1` are differences of natural numbers; they are the ordinary ones because $n\ge2$ and $k\ge1$. The sign of a step is written as a comparison of two entries: `f n (k - 1) < f n k` for a positive step and `f n k ≤ f n (k - 1)` for a step that is not positive.

## Proof

The proof has three parts: the passage from a row with a peak to the next row, the existence of a peak in every row $n\ge2$ by induction, and the conclusion.

**Part 1: from the row $n$ to the row $n+1$.** Let $n\ge2$, and suppose that the row $n$ has its peak at $p$. By the definition `Parking.IsPeak` this means: $p\le n-1$; (i) $f(n,k-1)<f(n,k)$ for $1\le k\le p$; (ii) $f(n,p+1)\le f(n,p)$ if $p+1\le n-1$; (iii) $f(n,k)<f(n,k-1)$ for $p+2\le k\le n-1$. We show that the row $n+1$ has its peak at $p$ or a strict peak at $p+1$.

*(a) The steps $1,\dots,p$ of the row $n+1$ are positive.* Let $1\le k\le p$. Then $k\le n-1$, and $f(n,k-1)<f(n,k)$ by (i). The column rule at $(n,k)$ gives $f(n+1,k-1)<f(n+1,k)$.

*(b) Every step of the row $n$ from $p+1$ on is not positive.* Let $p+1\le j\le n-1$. If $j=p+1$, then $f(n,j)\le f(n,j-1)$ is (ii). If $j\ge p+2$, then $f(n,j)<f(n,j-1)$ by (iii).

*(c) The steps $p+2,\dots,n$ of the row $n+1$ are negative.* Let $p+2\le k\le n$ and put $j=k-1$. Then $1\le p+1\le j\le n-1$, so $f(n,j)\le f(n,j-1)$ by (b), and the diagonal rule at $(n,j)$ gives $f(n+1,j+1)<f(n+1,j)$, which is $f(n+1,k)<f(n+1,k-1)$.

*(d) The step $p+1$ decides.* The row $n+1$ has the entries $f(n+1,0),\dots,f(n+1,n)$, and $p+1\le n$. If $f(n+1,p)<f(n+1,p+1)$, the row $n+1$ has a strict peak at $p+1$: its steps $1,\dots,p$ are positive by (a), its step $p+1$ is positive by the case assumption, and its steps $p+2,\dots,n$ are negative by (c). Otherwise $f(n+1,p+1)\le f(n+1,p)$, and the row $n+1$ has its peak at $p$: $p\le n$, its steps $1,\dots,p$ are positive by (a), the entry after $p$ is not larger than $f(n+1,p)$, and its steps $p+2,\dots,n$ are negative by (c).

**Part 2: every row $n\ge2$ has a peak.** By induction on $n$. The row $2$ consists of $f(2,0)$ and $f(2,1)$ and has one step. If $f(2,0)<f(2,1)$, it has its peak at $1$: the step $1$ is positive, and conditions (ii) and (iii) are empty because $p+1=2>n-1=1$. Otherwise $f(2,1)\le f(2,0)$, and it has its peak at $0$: condition (i) is empty, (ii) is the inequality just stated, and (iii) is empty. No rule is used here; the row $1$ has no step, and the rules are assumed only from $n=2$ on.

Suppose now that $n\ge2$ and that the row $n$ has its peak at some $p$. By Part 1 the row $n+1$ has its peak at $p$, and then nothing is to prove, or it has a strict peak at $p+1$. A row with a strict peak at $q$ has its peak at $q$: the bound on the position and the strict rise up to $q$ are the same in the two definitions; the strict fall from $q+1$ on gives $f(n+1,q+1)<f(n+1,q)$, hence $\le$, if there is an entry after $q$; and it gives the strict fall from $q+2$ on. So in both cases the row $n+1$ has a peak.

**Part 3: conclusion.** Let $n\ge2$. By Part 2 the row $n$ has its peak at some $p$, and by Part 1 the row $n+1$ has its peak at this $p$ or a strict peak at $p+1$.
