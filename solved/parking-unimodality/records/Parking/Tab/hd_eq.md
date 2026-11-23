---
weight: step
short: the computed lists contain the numbers A(n,l)
---
## Description

The number $\operatorname{hd}(l,n)$ that the table computes by the last-car recursion equals $A(n,l)$, the number of parking functions of length $n$ with maximum displacement at most $l$.

## Statement

For all natural numbers $l$ and $n$, $\operatorname{hd}(l,n)=A(n,l)$, where $\operatorname{hd}$ is the computed number of `Parking.Tab.hd` and $A$ is the count of `Parking.A`.

## Explanation

This is the soundness of the list computation on which the table of the columns $2\le k\le81$ and the table of the rows $n\le16$ rest: what the kernel computes are the numbers of the mathematical statement. The public statement speaks of the head of a list, and in this form the table of the rows $n\le16$ and the column $k=1$ use it. The table of the columns $2\le k\le81$ uses the statement for the whole list, which is what the proof below establishes. The reason is simply that the computation runs the recursion `Parking.A_succ` with the starting value `Parking.A_zero`, and these two determine the numbers $A(n,l)$.

## Proof

Fix $l$. The list built by the computation up to the row $N$ is $[x_N,x_{N-1},\dots,x_0]$ with the numbers $x_m$ of `Parking.Tab.hd`. The claim is that this list is $[A(N,l),A(N-1,l),\dots,A(0,l)]$ for every $N$; `hd l n` is its first entry for $N=n$.

*One row.* Suppose the list built so far is $[f(m),\dots,f(0)]$ for some function $f$. The new entry is computed from this list and its reversal $[f(0),\dots,f(m)]$ by going through both in parallel: at the position $j$ it adds $\min(j+1,l+1)\cdot c\cdot f(j)\,f(m-j)$, where $c$ starts as $1$ and is replaced by $\lfloor c\,(m-j)/(j+1)\rfloor$ after each position. By induction on the position, $c=\binom mj$ at the position $j$, since $\binom mj(m-j)=\binom m{j+1}(j+1)$ makes the division exact. Hence the new entry is
$$\sum_{j=0}^{m}\min(j+1,l+1)\binom mj f(j)\,f(m-j).$$

*All rows.* The computation starts from the list $[1]$, and $A(0,l)=1$ by `Parking.A_zero`. If the list built so far is $[A(m,l),\dots,A(0,l)]$, then by the previous paragraph the new entry is $\sum_{j\le m}\min(j+1,l+1)\binom mjA(j,l)A(m-j,l)$, which is $A(m+1,l)$ by the last-car recursion `Parking.A_succ`. By induction on the number of rows the list is $[A(N,l),\dots,A(0,l)]$.
