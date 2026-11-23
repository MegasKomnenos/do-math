---
weight: unit
short: the table of the rows up to 16
---
## Description

The computed fact about the rows $n\le16$ of the numbers $b(n,\ell)$: none of them has a strict descent followed by a strict ascent.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). For all natural numbers $n,i,j$ with $n\le16$ and $1\le i<j\le n-1$, it is not the case that both $b(n,i)<b(n,i-1)$ and $b(n,j-1)<b(n,j)$.

## Explanation

This is the statement `Parking.no_descent_ascent` for the rows $n\le16$, and by `Parking.unimodal_of_no_pair` it says that each of the rows $b(n,0),\dots,b(n,n-1)$, $1\le n\le16$, is unimodal. It is obtained by computing the sixteen rows, $136$ numbers in all, and inspecting them.

The general argument for a row uses two statements about columns that are available only from some row on: `Parking.left_half`, which holds for $n\ge17$ and whose inequality is false at some positions in smaller rows, and `Parking.right_tail`, which concerns the columns $i\ge9$. The main theorem therefore treats the rows $n\ge17$ by the general argument and the rows $n\le16$ by this table.

What the kernel checks is a little more than the statement: for each row it verifies directly that the row does not decrease up to some position and does not increase after it. The statement is put in the form "no descent followed by an ascent" because that is the form in which `Parking.no_descent_ascent` uses it. In Lean the conclusion is `False`, and $j\le n-1$ is written with the subtraction of natural numbers.

## Proof

The statement is established by an exact computation, which the kernel of the proof assistant performs, and by a proof of what the computation means.

**What is computed.** For $1\le n\le16$ and $0\le\ell\le n-1$ the computation forms the number $\tilde b(n,0)=\operatorname{hd}(0,n)$ and, for $\ell\ge1$, $\tilde b(n,\ell)=\operatorname{hd}(\ell,n)-\operatorname{hd}(\ell-1,n)$, where $\operatorname{hd}(l,n)$ is the number obtained by running the last-car recursion for the level $l$ up to the row $n$ (`Parking.Tab.hd`). By `Parking.Tab.hd_eq`, $\operatorname{hd}(l,n)=A(n,l)$, the number of parking functions of length $n$ with maximum displacement at most $l$; and by `Parking.b_zero` and `Parking.b_succ_add_A`, $b(n,0)=A(n,0)$ and $b(n,\ell)=A(n,\ell)-A(n,\ell-1)$ for $\ell\ge1$. Hence $\tilde b(n,\ell)=b(n,\ell)$. The arithmetic is that of natural numbers and is exact.

**What is checked.** For a row $f(0),\dots,f(m)$ the check goes through the positions from the left. As long as $f(a)\le f(a+1)$ it moves on. At the first position $a$ with $f(a+1)<f(a)$ it switches to the test that $f(a'+1)\le f(a')$ for all the remaining positions $a<a'<m$. The check succeeds if it reaches the end. The Boolean value that the kernel evaluates is the conjunction of this check for the sixteen rows $f=\tilde b(n,\cdot)$, $m=n-1$, $n=1,\dots,16$, and the kernel reduces it to true in one evaluation.

**What the check means.** If the check succeeds for $f(0),\dots,f(m)$, there are no $1\le i<j\le m$ with $f(i)<f(i-1)$ and $f(j-1)<f(j)$. This is proved by induction along the row: while the check is in its first phase at the position $a$, it has verified $f(a)\le f(a+1)$, so there is no strict descent at $i=a+1$, and a pair with $i>a+1$ lies in the rest of the row; once it has switched to the second phase at $a$, it verifies $f(j)\le f(j-1)$ for every later position $j$, so there is no strict ascent at any $j>a+1$, and every $j>i\ge a+1$ is such a position.

**Conclusion.** For $1\le n\le16$ the check succeeds for the row $b(n,0),\dots,b(n,n-1)$, which gives the statement for $1\le i<j\le n-1$. For $n=0$ there are no such $i,j$.
