---
weight: unit
short: peak of a row
---
## Description

For an array $f$ of natural numbers, the row $f(n,0),\dots,f(n,n-1)$ has its peak at the position $p\le n-1$ if it rises strictly up to $p$, the entry after $p$, if there is one, is not larger than $f(n,p)$, and from there on the row falls strictly.

## Statement

Let $f:\mathbb N\times\mathbb N\to\mathbb N$ be an array of natural numbers, read by rows: the *row* $n$ of $f$ consists of the $n$ entries $f(n,0),f(n,1),\dots,f(n,n-1)$. Let $n\ge1$ and $p$ be natural numbers. The row $n$ of $f$ *has its peak at the position* $p$ if the following four conditions hold.

1. $p\le n-1$.
2. $f(n,k-1)<f(n,k)$ for every $k$ with $1\le k\le p$.
3. If $p+1\le n-1$, then $f(n,p+1)\le f(n,p)$.
4. $f(n,k)<f(n,k-1)$ for every $k$ with $p+2\le k\le n-1$.

Written as one chain, the conditions say
$$f(n,0)<f(n,1)<\dots<f(n,p)\ \ge\ f(n,p+1)>f(n,p+2)>\dots>f(n,n-1).$$
The chain ends with $f(n,n-1)$: for $p=n-1$ the part after $f(n,p)$ is absent.

For $n=0$, where the row is empty, the Lean definition reads $n-1$ as $0$, and the four conditions then hold exactly for $p=0$. The library uses the notion only for rows $n\ge2$.

## Explanation

**The conditions in terms of steps.** Call the difference $f(n,k)-f(n,k-1)$, for $1\le k\le n-1$, the *step* of the row $n$ at the column $k$; the row $n$ has $n-1$ steps. The row has its peak at $p$ exactly when its steps $1,\dots,p$ are positive, its step $p+1$ is zero or negative, and its steps $p+2,\dots,n-1$ are negative. A step whose index exceeds $n-1$ does not exist, and the condition on it is empty. The two extreme cases are $p=n-1$, a row that rises strictly from its first entry to its last, and $p=0$, a row whose first step is not positive and whose later steps are all negative. The only place at which two neighbouring entries of the row may be equal is directly after the position $p$.

**The position is determined by the row.** If the row $n$ has its peak at $p$, its positive steps are exactly the steps $1,\dots,p$, so $p$ is the number of positive steps of the row. A row therefore has its peak at one position at most, and one can speak of the peak of a row. The largest entry of such a row is $f(n,p)$; it is attained at $p$, and also at $p+1$ if the step $p+1$ is zero. The library uses the uniqueness in no proof and does not state it as a theorem. Not every row has a peak: the row $(1,0,1)$ has a negative step followed by a positive one, and the row $(1,1,1)$ has two steps equal to zero.

**Why an equality is allowed, and why at this one place.** The definition has the form that the induction on the row, `Parking.peak_induction`, produces. In that induction the signs of the steps of the row $n+1$ are obtained from the signs of the steps of the row $n$ by two rules. The rules give a strict sign to every step of the row $n+1$ except one, the step directly after the peak position of the row $n$, and about that step they say nothing: it may be positive, zero or negative. A notion that asked for a strict inequality at that place as well is `Parking.IsStrictPeak`; for a row that has just been obtained from the row before, it would claim more than the rules give. A notion that allowed equalities at other places would claim less than they give.

**What the notion is used for.** The statement `Parking.peak_induction` is about an arbitrary array, and `Parking.staircase` applies it to the array $b(n,\ell)$ of the numbers of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`): every row $n\ge2$ of $b$ has a peak. A row that has its peak at $p$ does not decrease up to $p$ and does not increase from $p$ on, which is how `Parking.unimodal_via_staircase_proof` obtains the unimodality of the rows of $b$.

**The Lean form.** `IsPeak f n p` is the conjunction of the four conditions in the order given above: `p ≤ n - 1`, `∀ k, 1 ≤ k → k ≤ p → f n (k - 1) < f n k`, `p + 1 ≤ n - 1 → f n (p + 1) ≤ f n p`, and `∀ k, p + 2 ≤ k → k ≤ n - 1 → f n k < f n (k - 1)`. The differences `n - 1` and `k - 1` are differences of natural numbers, which stop at zero. The difference `k - 1` is the ordinary one in both places where it occurs, because $k\ge1$ there, and `n - 1` is the ordinary one for $n\ge1$. The sign of a step is written as a comparison of two entries, so no difference of entries is formed. The array is a function of two natural numbers, so that $f(n,k)$ is defined in Lean for $k\ge n$ as well; the definition does not mention these values.
