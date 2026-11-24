---
weight: unit
short: strict peak of a row
---
## Description

For an array $f$ of natural numbers, the row $f(n,0),\dots,f(n,n-1)$ has a strict peak at the position $p\le n-1$ if it rises strictly up to $p$ and falls strictly after $p$, so that no two neighbouring entries are equal.

## Statement

Let $f:\mathbb N\times\mathbb N\to\mathbb N$ be an array of natural numbers, read by rows: the *row* $n$ of $f$ consists of the $n$ entries $f(n,0),f(n,1),\dots,f(n,n-1)$. Let $n\ge1$ and $p$ be natural numbers. The row $n$ of $f$ *has a strict peak at the position* $p$ if the following three conditions hold.

1. $p\le n-1$.
2. $f(n,k-1)<f(n,k)$ for every $k$ with $1\le k\le p$.
3. $f(n,k)<f(n,k-1)$ for every $k$ with $p+1\le k\le n-1$.

Written as one chain, the conditions say
$$f(n,0)<f(n,1)<\dots<f(n,p)>f(n,p+1)>\dots>f(n,n-1).$$
The chain ends with $f(n,n-1)$: for $p=n-1$ the part after $f(n,p)$ is absent.

For $n=0$, where the row is empty, the Lean definition reads $n-1$ as $0$, and the three conditions then hold exactly for $p=0$. The library uses the notion only for rows $n\ge3$.

## Explanation

**The relation to a peak.** `Parking.IsPeak` defines when a row has its peak at $p$: the row rises strictly up to $p$, the entry after $p$ is not larger than $f(n,p)$, and from there on the row falls strictly. A strict peak is the same with the one possible equality excluded. In terms of the steps $f(n,k)-f(n,k-1)$, $1\le k\le n-1$, of the row: the steps $1,\dots,p$ are positive and the steps $p+1,\dots,n-1$ are negative, so no step is zero, and $f(n,p)$ is the largest entry of the row and is attained only at $p$. A row with a strict peak at $p$ has its peak at $p$: the first two conditions are the same, and the third gives $f(n,p+1)<f(n,p)$ if $p+1\le n-1$ and the strict fall from $p+2$ on. In the other direction, a row with its peak at $p$ has a strict peak at $p$ exactly when $p=n-1$ or $f(n,p+1)<f(n,p)$. The library uses the first implication inside the proof of `Parking.peak_induction` and states neither as a theorem.

**Why the strict notion is needed beside the other.** The statement of `Parking.peak_induction`, and with it `Parking.staircase`, offers two alternatives for the row $n+1$ when the row $n$ has its peak at $p$: the row $n+1$ has its peak at $p$ as well, or it has a strict peak at $p+1$. The second alternative is the case in which the peak has moved by one position, and in that case the induction gives a strict sign to every step of the row $n+1$: the steps up to $p+1$ are positive, and the steps from $p+2$ on are negative, the step $p+2$ included, because the step $p+1$ of the row $n$ was not positive. A row whose peak has just moved therefore has no two equal neighbours at all. Stated with a peak at $p+1$ in the place of a strict peak, the second alternative would allow an equality after the new peak position, which the argument excludes. So an equality can occur only directly after the peak of a row whose peak is at the same position as that of the row before.

**The Lean form.** `IsStrictPeak f n p` is the conjunction `p ≤ n - 1 ∧ (∀ k, 1 ≤ k → k ≤ p → f n (k - 1) < f n k) ∧ (∀ k, p + 1 ≤ k → k ≤ n - 1 → f n k < f n (k - 1))`. The differences `n - 1` and `k - 1` are differences of natural numbers, which stop at zero; `k - 1` is the ordinary difference in both places, because $k\ge1$ there, and `n - 1` is the ordinary one for $n\ge1$. The sign of a step is written as a comparison of two entries. In the library the notion occurs with the row $n+1$ and the position $p+1$, for $n\ge2$.
