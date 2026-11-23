---
weight: step
short: the computed value of A(n,l)
---
## Description

The number that the table computes for the row $n$ of the level $l$ by running the last-car recursion from the row $0$; it equals $A(n,l)$, the number of parking functions of length $n$ with maximum displacement at most $l$.

## Statement

Let $l$ and $n$ be natural numbers. Define natural numbers $x_0,x_1,x_2,\dots$ (depending on $l$) by $x_0=1$ and
$$x_{m+1}=\sum_{j=0}^{m}\min(j+1,\,l+1)\;c_{m,j}\;x_j\,x_{m-j},\qquad c_{m,0}=1,\quad c_{m,j+1}=\Bigl\lfloor\frac{c_{m,j}\,(m-j)}{j+1}\Bigr\rfloor .$$
Then $\operatorname{hd}(l,n)=x_n$. The numbers $c_{m,j}$ are the binomial coefficients $\binom mj$, because $\binom mj(m-j)=\binom m{j+1}(j+1)$, so the division is exact.

## Explanation

**What it is for.** `hd` is a definition by computation: it says how a number is produced, by natural-number additions, multiplications and exact divisions, and nothing about parking functions. `Parking.Tab.hd_eq` states that the number produced is $A(n,l)$ (`Parking.A`). Together they make single values of $A$, and with them of $b$, available to the kernel of the proof assistant, which can evaluate `hd l n` for given numerals $l$ and $n$ but cannot evaluate the definition of $A$, a count over all $n^n$ preference sequences. The table of the rows $n\le16$ reads its values $b(n,\ell)$ from `hd` (`Parking.Tab.small_rows`), and so does the one comparison $2A(3,0)\le A(3,1)$ from which the column $k=1$ starts (`Parking.column_one`).

**The Lean form.** The table of the columns $2\le k\le81$ works with whole lists: for a level $l$ it builds the list $[x_N,x_{N-1},\dots,x_0]$ row by row, each new entry being computed from the list built so far and put on top of it. `hd l n` is the first entry of the list built up to the row $n$ (written with `headD 0`, the first entry or $0$ for an empty list; the list is never empty). The sum for the new entry is taken over the list and its reversal in parallel, and the binomial coefficient is carried along as the running product $c_{m,j}$. The functions are written with the recursors of the natural numbers and of lists, and the new entry is passed through an auxiliary function that returns its second argument only after its first argument has been reduced to a numeral; both serve to make the kernel evaluate each entry once, when it is produced. These auxiliary definitions are private; their content is what the statement above says.
