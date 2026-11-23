---
weight: step
short: the listed positive rows lie within 27k/100 of the column
---
## Description

$100\,(z(k)+1)\le27\,k$ for $82\le k\le264$, where $z(k)$ is the number listed for the column $k$ in the table of two signs.

## Statement

For every natural number $k$ with $82\le k\le264$, $\ 100\,(z(k)+1)\le27\,k$, where $z(k)$ is the number of `Parking.Tab.ztab`.

## Explanation

The table of two signs shows that the column $k$ is positive in the row $k+z(k)+1$ (`Parking.Tab.two_signs`). The statement bounds the distance $r=z(k)+1$ of that row from the row $k$ by $27k/100$. This is the form in which the analytic arguments for the columns $k\ge82$ need the position of a positive row (`Parking.crossing_row`): the persistence argument requires the first positive row within $k/3$ of the row $k$ (`Parking.persist`), and the left half requires it within $27k/100$ (`Parking.big_columns`, through `Parking.single_crossing`). For $k\ge265$ the same bound comes from the crossing theorem (`Parking.crossing_strip`, `Parking.strip_end_le`).

The statement is arithmetic on the list of the numbers $z(k)$ and involves no parking functions. The lower limit $82$ matters: for the columns $9\le k\le62$ the listed number does not satisfy the inequality (for $k=62$, $100\cdot17>27\cdot62$).

In Lean the range is written `k < 265` and `82 ≤ k`.

## Proof

The statement is a finite check on the list `Parking.Tab.zs`: for each of the $183$ numbers $k=82,\dots,264$ the two natural numbers $100(z(k)+1)$ and $27k$ are compared. The kernel of the proof assistant evaluates the bounded quantifier and finds it true. The check can be read off the table of `Parking.Tab.ztab`: $z(k)$ does not decrease in $k$, so within each range of columns with a constant value $z$ it suffices to look at the first column, and the comparison is tightest at $k=84$, where $100\cdot20=2000\le2268=27\cdot84$.
