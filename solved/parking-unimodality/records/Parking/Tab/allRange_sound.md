---
weight: step
short: a block that evaluates to true holds column by column
---
## Description

If the Boolean check of a block of columns $k_0\le k<k_0+c$ has the value true, then the check has the value true for each column of the block.

## Statement

Let $p$ be a function from the natural numbers to the truth values, and let $k_0$, $c$ be natural numbers. If $\operatorname{allRange}(p,k_0,c)=\mathrm{true}$ (`Parking.Tab.allRange`), then $p(k)=\mathrm{true}$ for every $k$ with $k_0\le k<k_0+c$.

## Explanation

This is the step from a kernel evaluation to a statement with a quantifier. The kernel establishes, for each block, the single equation $\operatorname{allRange}(p,k_0,c)=\mathrm{true}$; the statement gives $p(k)=\mathrm{true}$ for every column $k$ of the block, to which the soundness theorem of the table is then applied. It is used once for each of the nineteen blocks of the table of the columns $2\le k\le81$ and once for each of the sixteen blocks of the table of two signs.

## Proof

By induction on $c$. For $c=0$ there is no $k$ with $k_0\le k<k_0$. For $c+1$, $\operatorname{allRange}(p,k_0,c+1)=\operatorname{allRange}(p,k_0,c)\wedge p(k_0+c)$, so both conjuncts are true. A column $k$ with $k_0\le k<k_0+c+1$ either satisfies $k<k_0+c$, where the induction hypothesis applies, or is $k=k_0+c$, where $p(k)$ is the second conjunct.
