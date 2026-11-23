---
weight: step
short: entry of a list of data
---
## Description

The $i$-th entry of a finite list of natural numbers, counted from $0$, with the value $0$ when $i$ is beyond the end of the list.

## Statement

For a finite list $l=(l_0,l_1,\dots,l_{r-1})$ of natural numbers and a natural number $i$,
$$\operatorname{nth}(l,i)=\begin{cases}l_i,& i<r,\\ 0,& i\ge r.\end{cases}$$

## Explanation

The tables of the library carry one number of data for each column: the row $n_0(k)$ at which the table of the columns $2\le k\le81$ checks the column $k$ (`Parking.Tab.n0`), and the number $z(k)$ of the table of two signs (`Parking.Tab.ztab`). The numbers are written into the source as lists (`Parking.Tab.n0tab`, `Parking.Tab.zs`), and `nth` reads the entry of a column from its list.

The definition is a recursion on the list with no reference to any library, so that the kernel of the proof assistant can evaluate it inside the Boolean checks. The value $0$ beyond the end is a convention that makes the function total; no statement of the library uses an index beyond the end of a list.
