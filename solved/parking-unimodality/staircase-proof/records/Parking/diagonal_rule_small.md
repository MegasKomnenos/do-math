---
weight: unit
short: the diagonal rule in the first layer of the columns 2 to 264
---
## Description

For $2\le k\le264$ and $k+1\le n\le2k-1$: if $b(n,k)\le b(n,k-1)$, then $b(n+1,k+1)<b(n+1,k)$, where $b(n,\ell)$ is the number of parking functions of length $n$ with maximum displacement exactly $\ell$.

## Statement

Let $b(n,\ell)$ be the number of parking functions of length $n$ with maximum displacement exactly $\ell$ (`Parking.b`). Let $k$ and $n$ be natural numbers with $2\le k\le264$ and $k+1\le n\le2k-1$. If $b(n,k)\le b(n,k-1)$, then $b(n+1,k+1)<b(n+1,k)$.

## Explanation

**Its place.** Write $d_{n,k}=b(n,k)-b(n,k-1)$ for the step of the column $k$ in the row $n$. The diagonal rule, one of the two rules from which the staircase theorem `Parking.staircase` is derived, says that a step that is not positive is followed by a negative step one row down and one column to the right: $d_{n,k}\le0$ implies $d_{n+1,k+1}<0$, for $n\ge2$ and $1\le k\le n-1$ (`Parking.diagonal_rule`). The first layer of the column $k$ consists of the rows $k+1\le n\le2k-1$ (also called the chain range of the column). The present statement is the diagonal rule at the positions of the first layer of the columns $2\le k\le264$. The positions beyond the first layer are covered by `Parking.diagonal_rule_beyond`, and the first layer of the columns $k\ge265$ by the analytic argument along the diagonal.

**Why it holds.** For the columns $k\ge9$ the first layer contains a row in which the column is positive, and the rule is governed by that row. For $9\le k\le264$ the table of two signs `Parking.Tab.two_signs` gives a row $q=k+z(k)+1$ of the first layer in which the column $k$ is positive, where $z(k)$ is the number listed for the column (`Parking.Tab.ztab`). By the persistence of the sign in the first layer (`Parking.step_persists_iter`) the column is positive in every later row of the layer as well. A step of the first layer that is not positive therefore lies in a row $n\le q-1$. The table `Parking.Tab.next_column_neg` shows that the column $k+1$ is negative in every row from $k+2$ to $q$, and $n+1$ is one of them. So the rule holds because the column $k+1$ is still negative one row below every row in which the column $k$ has not yet turned positive, including the row $q$ itself.

For $2\le k\le8$ the situation is simpler, and the hypothesis is not used: the column $k+1$ is negative in every row $k+2\le n+1\le2k$. These positions are cells of the table `Parking.Tab.negative_cells`, which gives the negative sign of each column $c\le9$ in the rows from $c+1$ to at least $2c-2$.

**The bound $264$.** The statement ends at the column $264$ because the two tables it rests on for the columns $k\ge9$, `Parking.Tab.two_signs` and `Parking.Tab.next_column_neg`, do. From the column $265$ on the proof of the diagonal rule replaces the listed row $q$ by a theorem that locates a positive row of the column, and the table of the next column by an analytic comparison of the positions $(n,k)$ and $(n+1,k+1)$.

**The Lean form.** The hypothesis is `b n k ≤ b n (k - 1)` and the conclusion `b (n + 1) (k + 1) < b (n + 1) k`, comparisons of natural numbers. The bound $n\le2k-1$ is written `n ≤ 2 * k - 1` with the subtraction of natural numbers, which is the ordinary one because $k\ge2$.

## Proof

**The columns $2\le k\le8$.** Put $k'=k+1$ and $n'=n+1$. Then $2\le k'\le9$, and $k+1\le n\le2k-1$ gives $k'+1\le n'\le2k'-2$. `Parking.Tab.negative_cells` states $b(n',k')<b(n',k'-1)$ for $k'\ge2$ and $n'\ge k'+1$ under each of four conditions, one of which is $n'\le2k'-2$ and $k'\le9$. This is $b(n+1,k+1)<b(n+1,k)$. The hypothesis $b(n,k)\le b(n,k-1)$ is not used.

**The columns $9\le k\le264$.** Let $z=z(k)$ and $q=k+z+1$. By the second part of `Parking.Tab.two_signs`, $b(q,k-1)<b(q,k)$.

*The row $n$ lies before $q$.* Suppose $n\ge q$. Then $k+1\le q\le n\le2k-1$, and `Parking.step_persists_iter`, which states for $k\ge2$ and $k+1\le m\le n\le2k-1$ that $b(m,k-1)<b(m,k)$ implies $b(n,k-1)<b(n,k)$, gives $b(n,k-1)<b(n,k)$ with $m=q$. This contradicts the hypothesis $b(n,k)\le b(n,k-1)$. Hence $n\le k+z$.

*The next column in the row $n+1$.* Now $k+2\le n+1\le k+z+1$, and `Parking.Tab.next_column_neg` gives $b(n+1,k+1)<b(n+1,k)$.
