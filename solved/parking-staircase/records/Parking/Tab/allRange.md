---
weight: step
short: a Boolean check on a block of consecutive columns
---
## Description

The Boolean value of "the check $p$ holds for every $k$ with $k_0\le k<k_0+c$".

## Statement

Let $p$ be a function from the natural numbers to the truth values $\{\mathrm{true},\mathrm{false}\}$, and let $k_0$ and $c$ be natural numbers. Then
$$\operatorname{allRange}(p,k_0,c)=p(k_0)\wedge p(k_0+1)\wedge\dots\wedge p(k_0+c-1),$$
the conjunction of $c$ truth values; for $c=0$ it is $\mathrm{true}$. In Lean it is defined by recursion on $c$: $\operatorname{allRange}(p,k_0,0)=\mathrm{true}$ and $\operatorname{allRange}(p,k_0,c+1)=\operatorname{allRange}(p,k_0,c)\wedge p(k_0+c)$.

## Explanation

A table of the library is a Boolean function $p$ of the column $k$, which the kernel of the proof assistant evaluates, together with a theorem that says what $p(k)=\mathrm{true}$ means for the numbers $b(n,k)$. The columns are not evaluated one by one and not all at once: the range of columns is divided into blocks of consecutive columns, and each block is one closed Boolean expression $\operatorname{allRange}(p,k_0,c)$ that the kernel reduces to $\mathrm{true}$. The table of the columns $2\le k\le81$ has nineteen blocks, of $7,17,10,7,5,4,4,3,3,3,2,2,2,2,2,2,2,2$ and $1$ columns; from the second block on they become shorter as the columns and the numbers in them grow (`Parking.Tab.small_table`); the table of two signs has sixteen blocks of sixteen columns (`Parking.Tab.two_signs`).

`Parking.Tab.allRange_sound` turns the value $\mathrm{true}$ of a block into the statement for each of its columns, and `Parking.Tab.glue` joins adjacent blocks.
