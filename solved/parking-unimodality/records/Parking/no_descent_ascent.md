---
weight: unit
short: no row has a descent followed by an ascent
---
## Description

No row of the numbers $b(n,\ell)$ has a strict descent followed by a strict ascent: there are no $1\le i<j\le n-1$ with $b(n,i)<b(n,i-1)$ and $b(n,j-1)<b(n,j)$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). For all natural numbers $n,i,j$ with $1\le i<j\le n-1$, it is not the case that both $b(n,i)<b(n,i-1)$ and $b(n,j-1)<b(n,j)$.

## Explanation

With $d_{n,k}=b(n,k)-b(n,k-1)$, the step of the column $k$ in the row $n$, the statement is that $d_{n,i}<0<d_{n,j}$ is impossible for $i<j$. By `Parking.unimodal_of_no_pair` this implies the unimodality of the row, and it is the form in which the main theorem `Parking.root_unimodal` is proved.

The proof is where the three statements about columns meet, and its case distinction shows what each of them is for. Take a strict descent at the column $i$ of the row $n$. If the row is long compared with the column, $n\ge2i$, there can be no descent at all, because the column $i$ has become nonnegative by then (`Parking.left_half`). If $n\le2i-1$, the row lies in the chain range of the column $i$ (the rows $i+1,\dots,2i-1$) and of every later column, and there a nonpositive step is followed only by nonpositive ones (`Parking.right_tail`, which rests on `Parking.chain_column_iter` and `Parking.mono`). So a row $n\ge17$ is nondecreasing on its left half, up to the column $\lfloor n/2\rfloor$, and to the right of that it can turn downwards only once.

Both column statements used here are available only from some row on, and this is why the constant $17$ appears. The inequality of `Parking.left_half` is false in some small rows: for instance $b(5,1)=421>b(5,2)=377$ although $2\cdot2\le5$. `Parking.right_tail` needs the column $i\ge9$, and for $n\ge17$ the condition $n\le2i-1$ forces $i\ge9$. The library draws the line at the row $17$: `Parking.left_half` is proved for $n\ge17$, and the rows $n\le16$ are checked directly, by an exact computation of these sixteen rows (`Parking.Tab.small_rows`).

In Lean the conclusion is `False` under the two hypotheses, $j\le n-1$ is written with the subtraction of natural numbers (for $n=0$ it reads $j\le0$, which contradicts $1\le i<j$), and `b n (i - 1)`, `b n (j - 1)` are exact since $i,j\ge1$.

## Proof

Suppose $1\le i<j\le n-1$, $b(n,i)<b(n,i-1)$ and $b(n,j-1)<b(n,j)$.

*Rows $n\le16$.* `Parking.Tab.small_rows` states that no row $n\le16$ has such a pair.

*Rows $n\ge17$ with $n\le2i-1$.* Then $2i\ge18$, so $i\ge9$. `Parking.right_tail` applies to $n$ and $i$ with the hypothesis $b(n,i)\le b(n,i-1)$: for every column $j'\ge i$ and every row $m$ with $j'+1\le m\le n$ one has $b(m,j')\le b(m,j'-1)$. Take $j'=j$ and $m=n$, which is allowed because $j\le n-1$. This gives $b(n,j)\le b(n,j-1)$, against the strict ascent at $j$.

*Rows $n\ge17$ with $n\ge2i$.* `Parking.left_half` states that $b(n,k-1)\le b(n,k)$ for $n\ge17$ and $k\ge1$ with $2k\le n$. With $k=i$ this contradicts the strict descent at $i$.
