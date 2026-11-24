---
weight: unit
short: the number z(k) locating a positive row of a column k from 9 to 264
---
## Description

For $9\le k\le264$, $z(k)$ is the listed number for which the table of two signs shows that the column $k$ is positive in the row $k+z(k)+1$ and the column $k+1$ is negative in the row $k+z(k)$; it grows from $z(9)=7$ to $z(264)=35$.

## Statement

For $9\le k\le264$ the number $z(k)$ is given by the following table: $z(k)$ is the value $z$ in whose range of columns $k$ lies.

| $z$ | columns $k$ | $z$ | columns $k$ | $z$ | columns $k$ |
|---|---|---|---|---|---|
| 7 | 9 | 17 | 67–74 | 27 | 163–174 |
| 8 | 10–14 | 18 | 75–83 | 28 | 175–185 |
| 9 | 15–20 | 19 | 84–91 | 29 | 186–197 |
| 10 | 21–25 | 20 | 92–101 | 30 | 198–210 |
| 11 | 26–31 | 21 | 102–110 | 31 | 211–222 |
| 12 | 32–37 | 22 | 111–120 | 32 | 223–235 |
| 13 | 38–44 | 23 | 121–130 | 33 | 236–248 |
| 14 | 45–51 | 24 | 131–141 | 34 | 249–261 |
| 15 | 52–58 | 25 | 142–151 | 35 | 262–264 |
| 16 | 59–66 | 26 | 152–162 | | |

In Lean, `Parking.Tab.ztab k` is the entry number $k-9$ (counted from $0$) of the list `Parking.Tab.zs`.

## Explanation

**What the number means.** Write $d_{n,k}=b(n,k)-b(n,k-1)$ for the step of the column $k$ in the row $n$. The table of two signs (`Parking.Tab.two_signs`) proves, for $z=z(k)$: $z+2\le k$, $d_{k+z+1,k}>0$ and $d_{k+z,k+1}<0$. So $k+z(k)+1$ is a row in which the column $k$ is positive, and it lies in the chain range $k+1\le n\le2k-1$ of the column. This one number per column serves two purposes. For $9\le k\le264$ it bounds the rows that the diagonal rule in the chain range has to consider (`Parking.diagonal_rule_small`): a step of the column $k$ that is not positive lies in a row before $k+z+1$, and the table `Parking.Tab.next_column_neg` shows that the column $k+1$ is negative in every row from $k+2$ to $k+z+1$. And for $82\le k\le264$ it gives the positive row that the analytic arguments for large columns start from (`Parking.positive_row_early`), with the bound $100(z(k)+1)\le27k$ (`Parking.Tab.ztab_27`).

**What the library does not say.** The library proves that the column $k$ is positive in the row $k+z(k)+1$. It does not prove that this is the first positive row of the column, and its arguments do not need that. An exact computation made for this record, outside the library (the last-car recursion in integer arithmetic), found that for every $9\le k\le264$ the row $k+z(k)+1$ is in fact the first row $n\ge k+1$ with $d_{n,k}>0$.

**The Lean form.** The function is defined for every natural number $k$ as `nth zs (k - 9)` (`Parking.Tab.nth`). Outside the range $9\le k\le264$ its values are artefacts of that definition ($7$ for $k<9$, by the subtraction of natural numbers, and $0$ for $k>264$, beyond the end of the list) and are never used.
