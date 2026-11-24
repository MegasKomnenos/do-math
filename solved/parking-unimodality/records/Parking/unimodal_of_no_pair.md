---
weight: unit
short: no descent followed by an ascent implies unimodal
---
## Description

A finite sequence of elements of a linearly ordered set that has no strict descent followed, at a later position, by a strict ascent is unimodal: it is nondecreasing up to some position and nonincreasing from that position on.

## Statement

Let $X$ be a linearly ordered set, that is, a set with an order relation $\le$ in which any two elements are comparable; the natural numbers, the integers and the real numbers are examples. Let $N$ be a natural number and let $c_0,c_1,\dots,c_N$ be elements of $X$. Suppose that there are no indices $i,j$ with $1\le i<j\le N$, $c_i<c_{i-1}$ and $c_{j-1}<c_j$. Then there is $p$ with $0\le p\le N$ such that $c_{\ell-1}\le c_\ell$ for every $\ell$ with $1\le\ell\le p$, and $c_{\ell+1}\le c_\ell$ for every $\ell$ with $p\le\ell\le N-1$.

In the library the finite sequence is given as the first $N+1$ terms of a function $f$ from the natural numbers to $X$, $c_\ell=f(\ell)$. Hypothesis and conclusion contain only the terms $f(0),\dots,f(N)$, so the values of $f$ beyond $N$ play no role, and every finite sequence $c_0,\dots,c_N$ in $X$ is covered: continue it in any way, for instance by $f(\ell)=c_N$ for $\ell>N$.

## Explanation

The conclusion is the definition of unimodality of the finite sequence $(f(0),\dots,f(N))$ used in the root proposition, with equality allowed on both sides of $p$. The hypothesis speaks of the consecutive pairs $f(\ell-1),f(\ell)$, $1\le\ell\le N$: no strict descent is followed later by a strict ascent. For numbers this says that no negative step $f(\ell)-f(\ell-1)$ is followed later by a positive one. The converse is also true and is not needed.

The statement is what reduces the root proposition to a statement about signs of steps. Applied to the sequence of natural numbers $f(\ell)=b(n,\ell)$ and to $N=n-1$, its hypothesis is `Parking.no_descent_ascent` and its conclusion is `Parking.root_unimodal`. This is its only use in the library. It is elementary and has nothing to do with parking functions: the argument only compares neighbouring terms of the sequence, and what it needs of the order is that for any two elements $c,c'$ either $c\le c'$ or $c'<c$ holds. This is why the statement is made for an arbitrary linear order and not only for numbers.

In Lean, $X$ is a type `α` with an instance of `LinearOrder`, and $f$ is a function `ℕ → α`; the hypothesis is written as an implication to `False`; the range $p\le\ell\le N-1$ is written `p ≤ ℓ → ℓ + 1 ≤ N`, which avoids a subtraction; and `f (ℓ - 1)`, `f (i - 1)`, `f (j - 1)` use the subtraction of natural numbers on the indices, which is exact because $\ell,i,j\ge1$.

## Proof

By induction on $N$ we prove the statement together with one more property of $p$: if $p<N$, then $f(p+1)<f(p)$. In words, $p$ is chosen so that the sequence is nondecreasing on $0,\dots,p$ and, unless $p=N$, strictly decreases right after $p$.

For $N=0$ take $p=0$; all three conditions are empty.

Let the statement hold for $N$, and let $f$ have no pair $i<j\le N+1$ as in the hypothesis. Then it has none with $j\le N$, so there is $p\le N$ with the three properties for $N$.

*Case $p=N$.* The sequence is nondecreasing on $0,\dots,N$. Since the order is linear, either $f(N)\le f(N+1)$ or $f(N+1)<f(N)$. If $f(N)\le f(N+1)$, take $p'=N+1$: the sequence is nondecreasing on $0,\dots,N+1$, and the other two conditions are empty. If $f(N+1)<f(N)$, keep $p'=N$: the only index $\ell$ with $p'\le\ell\le N$ is $\ell=N$, where $f(N+1)\le f(N)$, and the additional property holds because $f(N+1)<f(N)$.

*Case $p<N$.* By the additional property $f(p+1)<f(p)$, a strict descent at the position $i=p+1\le N$. If $f(N+1)\le f(N)$ failed, then $f(N)<f(N+1)$ because the order is linear, and the pair $i=p+1<j=N+1$ would contradict the hypothesis; hence $f(N+1)\le f(N)$. Keep $p'=p$: the sequence is nondecreasing up to $p$, nonincreasing on $p,\dots,N$ by the induction hypothesis and from $N$ to $N+1$ by what was just shown, and $f(p+1)<f(p)$ still holds.
